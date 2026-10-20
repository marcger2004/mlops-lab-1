# Lab 2: Train a model with MLflow

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Answers](answers.md)

Run these commands from the project root after completing the
[Lab 1 data preparation](../lab1/README.md). The original handout has not
been added yet; this guide follows the training code in this repository.

## Start MLflow

Keep this command running in a separate terminal:

```powershell
uv run mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```

Open <http://127.0.0.1:5000> to view your runs.

## Train on the mini dataset

```powershell
uv run python -m food11.train --dataset mini --epochs 5 --lr 0.001 --batch-size 32
```

The first run downloads the pretrained ResNet18 weights. The script logs
parameters, training and validation metrics, evaluation accuracy, and the
trained model to the `food11` experiment.

Use `--dataset processed` to train on the full prepared dataset. Run
`uv run python -m food11.train --help` for the other options.

## Compare runs

In MLflow, open the `food11` experiment and compare validation accuracy
across runs. The [Lab 3 guide](../lab3/README.md) explains how to register
a model and serve it through the API.

The local database and artifacts are ignored by Git. Keep them available
if you want to revisit or serve those models.
