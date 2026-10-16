# Lab 2: Model Training and MLflow

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md)

## Overview

This lab trains the Food-11 model and uses MLflow to compare the runs.

## Question 1: Changes to `pyproject.toml` and `uv.lock`

`pyproject.toml` now includes MLflow, PyTorch, torchvision, and scikit-learn.
PyTorch uses the CPU version here. `uv.lock` keeps the package versions so
they can be installed again later.

## Question 2: MLflow storage locations

`--backend-store-uri sqlite:///mlflow.db` puts the run details, parameters,
and metrics in the database. `--default-artifact-root ./mlruns` is where the
model files are saved.

## Question 3: Why ignore `mlflow.db` and `mlruns/`?

MLflow creates these files during the experiments. They change often and
can get large, so they are ignored by Git. DVC is only used for the dataset
in this lab.

## Question 4: Creating the `food11` experiment

`mlflow.set_experiment("food11")` creates the experiment if it does not
exist. The training runs then appear under `food11` in the MLflow interface.

## Question 5: Parameters versus metrics

A parameter is something set before training, like the learning rate. A
metric is a result, like accuracy. `step` tells MLflow which epoch the result
comes from; the fixed parameters do not need it.

## Question 6: Run contents and model location

The run saves `dataset`, `epochs`, `lr`, and `batch_size`, plus the loss
and accuracy metrics. The model is saved as the `model` artifact under
`mlruns/`, with run details in `mlflow.db`.

## Question 7: Best learning rate

Here are the results after one epoch:

| Learning rate | Batch size | Validation accuracy |
| --- | ---: | ---: |
| `0.01` | 32 | `0.0958` |
| `0.001` | 32 | `0.3869` |
| `0.0001` | 32 | `0.6962` |
| `0.001` | 64 | `0.2190` |

`0.0001` gave the best score here. A bigger learning rate did not help.

## Question 8: Parallel coordinates pattern

The best result used learning rate `0.0001` and batch size `32`.
At `0.001`, batch size `32` also beat `64`. These were only one-epoch runs,
so this is not enough to say it will always work better.

## Question 9: Best run

The best run was `spiffy-shoat-227`, with learning rate `0.0001` and batch
size `32`. It reached **69.62% validation accuracy** and **74.27% test accuracy**.

Run ID: `8bc2509809e240d297392b4e57a6c6e0`.
[View it in MLflow](http://127.0.0.1:5000/#/experiments/1/runs/8bc2509809e240d297392b4e57a6c6e0).

## Submission checklist

- [x] Training script added at `src/food11/train.py`.
- [x] MLflow experiment `food11` created.
- [x] Parameters and metrics logged.
- [x] Trained model logged as an artifact.
- [x] Several runs created and compared.
- [ ] Commit and push the Lab 2 code and this answer file to GitHub.
