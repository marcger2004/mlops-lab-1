"""Register the best finished run, preserving its original model artifacts."""
import os
from pathlib import Path

import mlflow
from mlflow import MlflowClient


def main():
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    client = MlflowClient()
    experiment = client.get_experiment_by_name("food11")
    if experiment is None:
        raise RuntimeError("Train a food11 experiment first")
    runs = client.search_runs(
        [experiment.experiment_id], "attributes.status = 'FINISHED'",
        order_by=["metrics.val_accuracy DESC"], max_results=1,
    )
    if not runs or "val_accuracy" not in runs[0].data.metrics:
        raise RuntimeError("No finished run with val_accuracy found")
    run = runs[0]
    # Copy through the artifact proxy so Linux containers never need a Windows path.
    source = mlflow.artifacts.download_artifacts(artifact_uri=f"runs:/{run.info.run_id}/model")
    serving = client.get_experiment_by_name("food11-serving")
    experiment_id = serving.experiment_id if serving else client.create_experiment(
        "food11-serving", artifact_location="mlflow-artifacts:/food11-serving"
    )
    with mlflow.start_run(experiment_id=experiment_id, tags={"source_run_id": run.info.run_id}):
        mlflow.log_artifacts(str(Path(source)), artifact_path="model")
        version = mlflow.register_model(mlflow.get_artifact_uri("model"), "food11")
    client.set_model_version_tag("food11", version.version, "source_run_id", run.info.run_id)
    client.set_registered_model_alias("food11", "champion", version.version)
    print(f"source_run={run.info.run_id} val_accuracy={run.data.metrics['val_accuracy']}")
    print(f"food11 version={version.version} alias=champion")


if __name__ == "__main__":
    main()
