"""Copy the local champion into the Compose registry without changing Lab 3."""
import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

import mlflow
from mlflow import MlflowClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-uri", default="sqlite:///mlflow.db")
    parser.add_argument("--target-uri", default="http://127.0.0.1:5000")
    parser.add_argument("--new-version", action="store_true")
    args = parser.parse_args()
    source = MlflowClient(tracking_uri=args.source_uri)
    target = MlflowClient(tracking_uri=args.target_uri)
    existing = target.search_model_versions("name = 'food11'")
    if existing and not args.new_version:
        champion = target.get_model_version_by_alias("food11", "champion")
        print(f"Compose already has champion version {champion.version}; nothing changed.")
        return

    champion = source.get_model_version_by_alias("food11", "champion")
    mlflow.set_tracking_uri(args.source_uri)
    with TemporaryDirectory(prefix="food11-model-") as temporary:
        # Lab 3 proxy artifacts live on disk even when its HTTP server is stopped.
        if champion.source.startswith("mlflow-artifacts:/") and args.source_uri.startswith("sqlite:"):
            artifact = Path("mlartifacts") / champion.source.removeprefix("mlflow-artifacts:/")
            if not (artifact / "MLmodel").is_file():
                raise FileNotFoundError(f"Local Lab 3 model not found at {artifact}")
        else:
            artifact = Path(mlflow.artifacts.download_artifacts(
                artifact_uri=f"models:/food11/{champion.version}", dst_path=temporary,
            ))
        mlflow.set_tracking_uri(args.target_uri)
        mlflow.set_experiment("food11-serving")
        with mlflow.start_run(tags={"source_model_version": str(champion.version), "source_run_id": champion.run_id or ""}):
            mlflow.log_artifacts(str(artifact), artifact_path="model")
            version = mlflow.register_model(mlflow.get_artifact_uri("model"), "food11")
        target.set_registered_model_alias("food11", "champion", version.version)
        print(f"Compose champion is now version {version.version}.")


if __name__ == "__main__":
    main()
