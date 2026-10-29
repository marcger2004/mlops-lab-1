"""Train and gate two real candidates against the local food11 champion.

Run from the repository root with MLflow running and the corrected data present:
    uv run python scripts/run_lab5_experiment.py
"""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import mlflow
from mlflow import MlflowClient
import torch

from food11.promote import accuracy, promote
from food11.train import train


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracking-uri", default="http://127.0.0.1:5000")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--threads", type=int, default=4)
    parser.add_argument("--report", type=Path, default=Path("docs/labs/lab5/reports/model-gate.json"))
    args = parser.parse_args()
    torch.set_num_threads(args.threads)
    mlflow.set_tracking_uri(args.tracking_uri)
    client = MlflowClient()
    champion = client.get_model_version_by_alias("food11", "champion")
    n = sum(1 for path in Path("data/food11_processed_mini/evaluation").rglob("*") if path.is_file())
    report = {"test_size": n, "initial_champion": champion.version,
              "initial_champion_accuracy": accuracy(client, champion, "test_accuracy"),
              "seed": 42, "epochs": args.epochs, "candidates": []}
    for lr in (0.000001, 0.001):
        train(argparse.Namespace(dataset="mini", epochs=args.epochs, lr=lr, batch_size=32,
                                 tracking_uri=args.tracking_uri, experiment="food11-lab5",
                                 num_workers=0, seed=42))
        experiment = client.get_experiment_by_name("food11-lab5")
        run = client.search_runs([experiment.experiment_id], "attributes.status = 'FINISHED'",
                                 order_by=["attributes.start_time DESC"], max_results=1)[0]
        version = mlflow.register_model(f"runs:/{run.info.run_id}/model", "food11")
        decision = promote(client, version.version, n)
        result = {"learning_rate": lr, "run_id": run.info.run_id, "version": version.version, **decision}
        report["candidates"].append(result)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
