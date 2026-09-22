## MLOps Lab Series

This project prepares the Food-11 image dataset for training workflows. It
reads the label prefix from each image filename, copies images into
class-named directories, resizes them to 128x128, and creates a reduced
dataset with a configurable maximum number of images per class.

## Lab documentation

| Lab | Instructions | Answers |
| --- | --- | --- |
| Lab 1 | [Instructions](docs/labs/lab1/instructions.md) | [Answers](docs/labs/lab1/answers.md) |
| Lab 2 | [Instructions](docs/labs/lab2/instructions.md) | [Answers](docs/labs/lab2/answers.md) |

The instruction files are placeholders until the original lab handouts are added.

## Setup

Install the project and its development dependencies with uv:

```powershell
uv sync
```

The dataset is tracked with DVC. Restore it before preparing the data:

```powershell
dvc pull
```

## Prepare the data

The default command reads `data/food11_raw` and writes both processed
datasets:

```powershell
uv run mlops-lab-1
```

Customize the locations or mini-dataset size when needed:

```powershell
uv run mlops-lab-1 --raw-root data/food11_raw --max-per-class 100
```

Use `--max-per-class 0` to create empty mini-dataset class directories, or
pass `None` through the Python API to copy every image.

## Test

```powershell
uv run pytest
```

## Train with MLflow

Start the local MLflow tracking server in a separate terminal:

```powershell
uv run mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```

Then train on the mini dataset:

```powershell
uv run python .\src\food11\train.py --dataset mini --epochs 5 --lr 0.001 --batch-size 32
```

The training script logs parameters, per-epoch training and validation metrics,
final evaluation accuracy, and the trained PyTorch model to the `food11`
experiment. Use `--dataset processed` for the full processed dataset.
