# Lab 3: Model Serving with Docker

[Lab index](../index.md) | [Instructions](instructions.md)

## Overview

This lab puts the best model behind an API and runs it with Docker.

## Question 1: Registered model version and artifacts

The model got **version 1** and the alias `champion`. The logged artifact
is the model saved in a run. Registering it gives it a name and version
that the API can load.

## Question 2: Model aliases and versioning

Aliases like `champion` and `challenger` are names we choose instead of
using the old stages. Versions keep track of the models from different runs.
An alias can point to a newer version, or back to an older one if needed.

## Question 3: Loading and updating the model

`models:/food11@champion` lets MLflow find the model, so the code does not
need a local `.pth` path. For a newer compatible model, just change which
version `champion` points to and restart the API.

## Question 4: Dependency layers and build cache

Installing the packages takes time, so Docker saves that step in its cache.
If only `serve.py` changes, the packages do not need to be installed again.
Only the source layer needs updating.

## Question 5: Single-stage versus multi-stage image size

The multi-stage image was **49.1% smaller**:

| Image | Size reported by Docker |
| --- | ---: |
| Multi-stage | 2.00 GB |
| Single-stage | 3.93 GB |

`docker history` showed a 1.43 GB environment layer in the multi-stage image,
versus a 2.90 GB installation layer in the single-stage one. Leaving uv and
its cache out of the final image explains most of the saving.

## Question 6: The role of `.dockerignore`

Without `.dockerignore`, Docker has to receive extra files like the dataset
and local environment. This takes longer and makes the image bigger if they
are copied in. Sending them alone does not break the build, but copying the
Windows `.venv` over the Linux one can stop the app from working.

## Question 7: Connecting the container to MLflow

`127.0.0.1` inside the container points to the container itself.
`host.docker.internal` is the address Docker Desktop provides to reach the
host computer, where MLflow is running.

## Question 8: Restarting without rebuilding

Yes, the new container loaded the model and gave the same prediction. The
code and packages are in the image, but the model is downloaded from MLflow
when the app starts. MLflow still needs to be running.

## Question 9: Publishing a reproducible image

The image still needs to be uploaded to a container registry so another
machine can download it. A tag names the release, and a digest identifies
the exact image. That machine also needs access to MLflow; use a fixed model
version for the same predictions, since `champion` can change.

## Validation results

- Local and Docker APIs: health and prediction checks passed.
- Invalid image: HTTP 400.
- Fresh container: same prediction without rebuilding.
- Tests: **4 passed**.
