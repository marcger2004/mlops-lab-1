## MLOps Lab Series

This project prepares the Food-11 image dataset for training workflows. It
reads the label prefix from each image filename, copies images into
class-named directories, resizes them to 128x128, and creates a reduced
dataset with a configurable maximum number of images per class.

## Where to find things

The lab notes are in `docs/labs/`, with a folder for each lab. Here's where
the rest of the project lives:

```text
docs/labs/          Lab instructions, answers, and run guides
src/food11/        Code to prepare data, train models, and serve predictions
tests/             Tests for data preparation, the API, and the frontend
frontend/          The web app for uploading an image and seeing its prediction
mlflow/            Dockerfile for the MLflow tracking server
docker/            Single-stage Dockerfile used for the Lab 3 comparison
data/              Datasets managed with DVC
Dockerfile         Builds the prediction API image
docker-compose.yml Starts MLflow, the API, and the frontend together
```

Run the commands below from the project root. The main configuration files
stay there so uv, Docker, and DVC can find them.

To keep the VS Code sidebar tidy, `.vscode/settings.json` hides the virtual
environment, Python caches, and local MLflow files. They're still on your
machine. You can show them again by turning off their `files.exclude`
settings.

Related configuration files are grouped in the sidebar: expand
`pyproject.toml`, `Dockerfile`, or `data.dvc` to see their companion files.

## Lab documentation

| Lab | Instructions | Answers |
| --- | --- | --- |
| Lab 1 | [Instructions](docs/labs/lab1/instructions.md) · [Run guide](docs/labs/lab1/README.md) | [Answers](docs/labs/lab1/answers.md) |
| Lab 2 | [Instructions](docs/labs/lab2/instructions.md) · [Run guide](docs/labs/lab2/README.md) | [Answers](docs/labs/lab2/answers.md) |
| Lab 3 | [Instructions](docs/labs/lab3/instructions.md) · [Run guide](docs/labs/lab3/README.md) | [Answers](docs/labs/lab3/answers.md) |
| Lab 4 | [Instructions](docs/labs/lab4/instructions.md) · [Run guide](docs/labs/lab4/README.md) | [Answers](docs/labs/lab4/answers.md) |

The Lab 1 and Lab 2 instruction files are placeholders until their original
handouts are added. The Lab 3 and Lab 4 handouts and run guides are available.

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
uv run python -m food11.train --dataset mini --epochs 5 --lr 0.001 --batch-size 32
```

The training script logs parameters, per-epoch training and validation metrics,
final evaluation accuracy, and the trained PyTorch model to the `food11`
experiment. Use `--dataset processed` for the full processed dataset.

## Lab 5: CI/CD

See [Lab 5 answers and pipeline](lab/lab5.md). Run `uv run ruff check src tests`, `uv run pytest -q`, and `uv run python -m food11.validate_data data/food11_processed_mini`. The GitHub workflow tests, smoke-checks the container, and publishes SHA-tagged images on main. Promote registered candidates with `uv run python -m food11.promote --version N --n TEST_SIZE`.
