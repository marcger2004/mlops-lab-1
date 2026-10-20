# Lab 1: Prepare the Food-11 data

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Answers](answers.md)

Run these commands from the project root. The original handout has not been
added yet; this guide covers the workflow available in the repository.

## Set up the project

Install the Python dependencies, then restore the dataset from the configured
DVC remote. DVC needs to be installed separately, with access to that remote.

```powershell
uv sync
dvc pull
```

## Prepare the images

```powershell
uv run mlops-lab-1
```

This reads `data/food11_raw`, sorts the images into class folders, resizes
them to 128x128, and writes `data/food11_processed`. It also creates
`data/food11_processed_mini` with up to 100 images per class in each split.

To choose a different limit:

```powershell
uv run mlops-lab-1 --max-per-class 50
```

You can also run the same command as `uv run python -m food11`. Use
`uv run mlops-lab-1 --help` to see all the path options.

## Check the result

```powershell
uv run pytest tests/test_data_preparation.py
```

Keep datasets under `data/` and track them with DVC rather than adding the
image files to Git.
