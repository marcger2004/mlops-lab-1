from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.pytorch
import torch
from torch import nn
from torch.optim import Adam
from torch.utils.data import DataLoader
from torchvision import datasets, models


DATASET_ROOTS = {
    "processed": Path("data/food11_processed"),
    "mini": Path("data/food11_processed_mini"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a ResNet18 on Food-11.")
    parser.add_argument("--dataset", choices=sorted(DATASET_ROOTS), default="mini")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5000")
    parser.add_argument("--experiment", default="food11")
    parser.add_argument("--num-workers", type=int, default=0)
    return parser.parse_args()


def build_dataloaders(
    dataset_root: Path, batch_size: int, num_workers: int
) -> tuple[dict[str, DataLoader], list[str]]:
    weights = models.ResNet18_Weights.DEFAULT
    transform = weights.transforms()
    datasets_by_split = {
        split: datasets.ImageFolder(dataset_root / split, transform=transform)
        for split in ("training", "validation", "evaluation")
    }

    classes = datasets_by_split["training"].classes
    if len(classes) != 11:
        raise ValueError(f"Expected 11 Food-11 classes, found {len(classes)}")
    for split, dataset in datasets_by_split.items():
        if dataset.classes != classes:
            raise ValueError(f"Class ordering differs in the {split} split")

    loaders = {
        split: DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=split == "training",
            num_workers=num_workers,
        )
        for split, dataset in datasets_by_split.items()
    }
    return loaders, classes


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    loss_function: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None = None,
) -> tuple[float, float]:
    is_training = optimizer is not None
    model.train(is_training)
    total_loss = 0.0
    correct = 0
    total = 0

    with torch.set_grad_enabled(is_training):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            if is_training:
                optimizer.zero_grad()

            outputs = model(images)
            loss = loss_function(outputs, labels)
            if is_training:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * labels.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += labels.size(0)

    if total == 0:
        raise ValueError("The dataset split is empty")
    return total_loss / total, correct / total


def train(args: argparse.Namespace) -> None:
    if args.epochs < 1 or args.lr <= 0 or args.batch_size < 1:
        raise ValueError("epochs, lr, and batch-size must be positive")

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)
    dataset_root = DATASET_ROOTS[args.dataset]
    loaders, classes = build_dataloaders(dataset_root, args.batch_size, args.num_workers)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    weights = models.ResNet18_Weights.DEFAULT
    model = models.resnet18(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, len(classes))
    model.to(device)
    loss_function = nn.CrossEntropyLoss()
    optimizer = Adam(model.parameters(), lr=args.lr)

    with mlflow.start_run():
        mlflow.log_params(
            {
                "dataset": args.dataset,
                "epochs": args.epochs,
                "lr": args.lr,
                "batch_size": args.batch_size,
                "model": "resnet18",
                "device": str(device),
            }
        )
        for epoch in range(1, args.epochs + 1):
            train_loss, _ = run_epoch(
                model, loaders["training"], loss_function, device, optimizer
            )
            validation_loss, validation_accuracy = run_epoch(
                model, loaders["validation"], loss_function, device
            )
            mlflow.log_metrics(
                {
                    "train_loss": train_loss,
                    "val_loss": validation_loss,
                    "val_accuracy": validation_accuracy,
                },
                step=epoch,
            )
            print(
                f"epoch {epoch}/{args.epochs} - "
                f"train_loss={train_loss:.4f} "
                f"val_loss={validation_loss:.4f} "
                f"val_accuracy={validation_accuracy:.4f}"
            )

        _, test_accuracy = run_epoch(model, loaders["evaluation"], loss_function, device)
        mlflow.log_metric("test_accuracy", test_accuracy)
        input_example = next(iter(loaders["training"]))[0][:1].to(device)
        mlflow.pytorch.log_model(
            model,
            "model",
            input_example=input_example,
            serialization_format="pickle",
        )
        print(f"test_accuracy={test_accuracy:.4f}")


if __name__ == "__main__":
    train(parse_args())