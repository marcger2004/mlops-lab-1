# Lab 3: Docker model serving

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Answers](answers.md)

Original handout: [instructions.md](instructions.md). Its `hello-word` command
contains a typo; the Docker smoke-test image is `hello-world`.

Docker Desktop must be running with Linux containers. No Docker Hub login is
needed to build and run locally. Run all commands from the repository root.

## 1. Start MLflow on the host

```powershell
uv sync
uv run mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --serve-artifacts --artifacts-destination ./mlartifacts --allowed-hosts "localhost:*,127.0.0.1:*,host.docker.internal:*"
```

Keep this terminal open. This replaces the Lab 2 server command for serving.
The host binding and allowed host names let Docker Desktop reach the server.

## 2. Register the best completed training run

In another terminal:

```powershell
uv run python -m food11.register
```

This selects the finished run with the highest final logged `val_accuracy`,
downloads its logged model, and copies it to a `food11-serving` experiment
using HTTP-proxied artifacts. It registers `food11` and assigns `champion`.
The original training run and artifacts are preserved; `source_run_id` tags
record provenance. Rerunning registration creates another model version.

The copy is necessary because the existing Lab 2 experiment stores absolute
Windows file paths. Those paths cannot be opened inside a Linux container.
Simply restarting the server with `--serve-artifacts` does not update old
experiment artifact locations. See the
[MLflow server documentation](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/).

## 3. Test locally

```powershell
uv run uvicorn food11.serve:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
curl.exe http://127.0.0.1:8000/health
$sample = Get-ChildItem data/food11_processed_mini/validation/Bread -Filter *.jpg | Select-Object -First 1
curl.exe -F "file=@$($sample.FullName)" http://127.0.0.1:8000/predict
```

Stop the local API with Ctrl+C before using port 8000 for Docker.

## 4. Build and run

```powershell
docker build -t food11-api:latest .
docker run -d --name food11-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 food11-api:latest
docker logs food11-api
```

Wait for application startup to complete, then repeat the health and image
requests above. Interactive API documentation: http://127.0.0.1:8000/docs.

The dependency layer uses `--no-install-project` because this project has a
build backend that requires source files. Uvicorn imports the source copied
into the runtime image. Both build stages use Python 3.14 and CPU PyTorch.

## 5. Test a fresh container and inspect size

```powershell
docker stop food11-api
docker rm food11-api
docker run -d --name food11-api -p 8000:8000 -e MLFLOW_TRACKING_URI=http://host.docker.internal:5000 food11-api:latest
docker history food11-api:latest
docker image inspect food11-api:latest --format '{{.Size}}'
```

Repeat the requests after startup. A new container fetches the current champion
from MLflow; keep MLflow and `mlartifacts/` available. Moving the alias requires
restarting the API to load the new version.

For the single-stage comparison, build the provided deliberately naive image:

```powershell
docker build -f docker/Dockerfile.single -t food11-api:single .
docker image inspect food11-api:single --format '{{.Size}}'
docker history food11-api:single
```

The baseline retains uv and its dependency cache. Use the same dependencies,
base image, and source for a meaningful comparison.

## 6. Save your work

Review `git diff`, then commit the source, Dockerfiles, lockfile, and docs.
Model artifacts and the MLflow database remain local and ignored by Git.
Pushing the image to a registry is a separate step from pushing Git commits.

```powershell
git add Dockerfile docker/Dockerfile.single .dockerignore .gitignore src/food11/serve.py src/food11/register.py tests/test_serve.py pyproject.toml uv.lock README.md docs/labs/lab3
git commit -m "Containerize model serving with Docker"
git push
```
