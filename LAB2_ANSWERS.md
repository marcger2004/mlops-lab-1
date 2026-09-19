# Lab 2: Model Training and MLflow

## Question 1: Changes to `pyproject.toml` and `uv.lock`

The project dependencies now include MLflow, PyTorch, torchvision, and
scikit-learn. The project uses the PyTorch CPU package index so that the CPU
wheels are installed instead of the much larger CUDA-enabled wheels.

`uv.lock` records the exact resolved versions and dependencies so the training
environment can be reproduced.

## Question 2: MLflow storage locations

`--backend-store-uri sqlite:///mlflow.db` tells MLflow where to store run
metadata, including experiments, run IDs, parameters, metrics, and tags.

`--default-artifact-root ./mlruns` tells MLflow where to store larger run
artifacts, such as the trained model and its environment files.

Metadata describes and tracks a run. Artifacts are files produced by the run.
They are stored separately because artifacts can be much larger than metadata.

## Question 3: Why ignore `mlflow.db` and `mlruns/`?

These files are local MLflow outputs, not source code. They change whenever a
run is created and can become large. They should not be committed to GitHub.
They should not be tracked by DVC either because DVC is used for the Food-11
dataset, not for temporary local experiment outputs.

## Question 4: Creating the `food11` experiment

When `mlflow.set_experiment("food11")` is called and the experiment does not
exist, MLflow creates it automatically. It then appears in the MLflow UI and
new runs are recorded inside it.

## Question 5: Parameters versus metrics

A parameter is a value chosen before training and normally remains fixed for a
run, such as the learning rate or batch size.

A metric is a value produced during or after training, such as loss or
accuracy. Metrics can be logged repeatedly during training. The `step`
argument identifies the epoch or iteration associated with each metric value,
which allows MLflow to draw a chart over time. Parameters do not need a step
because they are logged once for the run.

## Question 6: Run contents and model location

The MLflow run contains the parameters `dataset`, `epochs`, `lr`, and
`batch_size`, along with the metrics `train_loss`, `val_loss`,
`val_accuracy`, and `test_accuracy`.

The trained model is visible under `Artifacts` in the `model` artifact. The
local artifact files are stored below the project's `mlruns/` directory, with
metadata in `mlflow.db`.

## Question 7: Best learning rate

Using one epoch on the mini dataset, the observed validation accuracies were:

| Learning rate | Batch size | Validation accuracy |
| --- | ---: | ---: |
| `0.01` | 32 | `0.0958` |
| `0.001` | 32 | `0.3869` |
| `0.0001` | 32 | `0.6962` |
| `0.001` | 64 | `0.2190` |

In these runs, `0.0001` gave the best validation accuracy. A higher learning
rate is not always better; `0.01` performed the worst in this comparison.

## Question 8: Parallel coordinates pattern

The best observed result used the smaller learning rate, `0.0001`, with batch
size `32`. The run with learning rate `0.01` had very low validation accuracy,
which suggests that the learning rate was too large for this training setup.

The comparison between batch sizes also favored batch size `32` in these runs,
but the experiments used only one epoch, so more epochs and repeated runs
would give a more reliable conclusion.

## Question 9: Best run

The best run from the tested commands was:

- Run name: `spiffy-shoat-227`
- Run ID: `8bc2509809e240d297392b4e57a6c6e0`
- Learning rate: `0.0001`
- Batch size: `32`
- Validation accuracy: `0.6962`
- Test accuracy: `0.7427`

MLflow run URL:

http://127.0.0.1:5000/#/experiments/1/runs/8bc2509809e240d297392b4e57a6c6e0

## Lab 2 submission checklist

- [x] Training script added at `src/food11/train.py`.
- [x] MLflow experiment `food11` created.
- [x] Parameters and metrics logged.
- [x] Trained model logged as an artifact.
- [x] Several runs created and compared.
- [ ] Commit and push the Lab 2 code and this answer file to GitHub.
