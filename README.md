# MLOps Lab 1

This project prepares the Food-11 image dataset for training workflows. It
reads the label prefix from each image filename, copies images into
class-named directories, resizes them to 128x128, and creates a reduced
dataset with a configurable maximum number of images per class.

The written answers to the lab questions are in [LAB_ANSWERS.md](LAB_ANSWERS.md).

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
