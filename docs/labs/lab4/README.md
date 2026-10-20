# Lab 4: Docker Compose

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Answers](answers.md)

The stack has three services: MLflow, the inference API, and a Streamlit upload
page. Docker Desktop must be running with Linux containers.

## First start

Run these commands from the repository root:

```powershell
docker compose build
docker compose up -d --wait mlflow
uv run python -m food11.bootstrap_compose
docker compose up -d --wait
```

The import command copies the local Lab 3 champion into the new MLflow server.
It reads `mlflow.db` and `mlartifacts/`; the old host server does not need to
be running. Existing Lab 3 data is kept. If the Compose registry already has
a model, the command leaves it alone.

Open the [upload page](http://127.0.0.1:8501) and
[MLflow](http://127.0.0.1:5000). Choose an image and click **Predict**.
For example, use `data/food11_processed_mini/validation/Bread/0_0.jpg`.

The inference API has no published host port. Streamlit sends requests from
its server to `http://inference:8000` on the Compose network.

## Changes from the handout

- This project keeps the `champion` alias from Lab 3 instead of the deprecated
  `Staging` model stage.
- Model artifacts are served over HTTP. A path such as `/mlflow-data/mlruns`
  would only exist inside MLflow, so inference could not read it directly.
- Health checks make inference wait for MLflow, and the frontend wait for
  inference. Inference also retries failed container starts up to five times.
- The empty registry needs a model before inference can start. The import
  command above handles this first-time setup.

References: [MLflow artifact serving](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/)
and [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/).

## Register another version and reload

Re-register the same model to demonstrate the version update:

```powershell
uv run python -m food11.bootstrap_compose --new-version
docker compose restart inference
docker compose logs --tail 20 inference
```

The logs show which champion version was loaded. Refreshing Streamlit alone
does not reload the model. Since this example reuses the same weights, its
prediction should stay the same after the restart.

## Persistence

```powershell
docker compose down
docker compose up -d --wait
docker compose ps
```

The `mlflow-data` named volume keeps both the database and artifacts. Avoid
`docker compose down -v` on the working stack: it deletes that volume and
removes its registry and model files. After a deliberate reset, repeat the
first-start commands to import the model again.

## Ports and troubleshooting

Only MLflow (5000) and Streamlit (8501) are published, on localhost. Stop a
previous host MLflow server if it is using port 5000, or choose another port:

```powershell
$env:MLFLOW_PORT = "5001"
docker compose up -d --wait mlflow
uv run python -m food11.bootstrap_compose --target-uri http://127.0.0.1:5001
docker compose up -d --wait
```

`FRONTEND_PORT` can similarly override 8501. Keep the same settings when
running later Compose commands. Internal URLs do not change.

If inference cannot start, check `docker compose logs inference`. A missing
`champion` means the import has not completed. Once it is registered, run
`docker compose up -d --wait` again.

## Repeat the frontend check

This runs Streamlit's test harness inside its container, submitting a sample
image to the real API and checking that the prediction appears. It also
checks the message shown for a connection failure.

```powershell
docker compose cp tests/smoke_frontend.py frontend:/tmp/smoke_frontend.py
docker compose cp data/food11_processed_mini/validation/Bread/0_0.jpg frontend:/tmp/food11-sample.jpg
docker compose exec -T frontend python /tmp/smoke_frontend.py /tmp/food11-sample.jpg
```

For the local Python tests, run `uv run pytest -q`.
