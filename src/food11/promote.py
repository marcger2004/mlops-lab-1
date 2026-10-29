"""Apply a two-standard-error quality gate to the food11 registry."""
import argparse
import json
import math
import os

import mlflow
from mlflow import MlflowClient


def accuracy(client, version, metric):
    # Earlier registration copied artifacts into a separate serving run.
    run_id = version.tags.get("source_run_id", version.run_id)
    value = float(client.get_run(run_id).data.metrics[metric])
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"Invalid {metric}: {value}")
    return value


def promote(client, version: str, n: int, metric: str = "test_accuracy", name: str = "food11"):
    if n < 1:
        raise ValueError("Test-set size must be positive")
    candidate = client.get_model_version(name, version)
    champion = client.get_model_version_by_alias(name, "champion")
    candidate_acc = accuracy(client, candidate, metric)
    champion_acc = accuracy(client, champion, metric)
    margin = 2 * math.sqrt(champion_acc * (1 - champion_acc) / n)
    decision = "champion" if candidate_acc >= champion_acc + margin else "challenger"
    report = {"decision": decision, "candidate_accuracy": candidate_acc,
              "champion_accuracy": champion_acc, "two_se": margin,
              "test_size": n, "previous_champion": champion.version, "metric": metric}
    # Record the evidence before moving the alias; missing metrics fail closed.
    for key, value in report.items():
        client.set_model_version_tag(name, version, f"gate.{key}", str(value))
    client.set_registered_model_alias(name, decision, version)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--n", type=int, required=True, help="Number of evaluation images")
    parser.add_argument("--metric", default="test_accuracy")
    parser.add_argument("--name", default="food11")
    args = parser.parse_args()
    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
    print(json.dumps(promote(MlflowClient(), args.version, args.n, args.metric, args.name), indent=2))


if __name__ == "__main__":
    main()
