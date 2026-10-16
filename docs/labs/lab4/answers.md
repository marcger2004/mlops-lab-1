# Lab 4: Docker Compose

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Run guide](README.md)

## Question 1: Running without a volume

The files stay while the container exists, even if it is stopped. Removing
the container removes its data too. A new container starts with an empty
registry. If nothing was registered, both UIs look empty anyway.

## Question 2: Named volume or bind mount

A named volume is managed by Docker and does not depend on a folder path
on my computer. A bind mount would also work, but its path and permissions
need to be set up on each machine.

## Question 3: The `mlflow` hostname

Compose puts the services on the same network and provides DNS names for
them. That is why inference can reach the tracking server at `mlflow:5000`.

## Question 4: Configuring the frontend URL

The environment variable lets the same image work with different API
addresses. Outside Compose, the name `inference` may not exist, so the URL
needs to point to a reachable API instead.

## Question 5: No published inference port

Only the browser-facing services need host ports. The Streamlit server can
reach inference directly on the Compose network using `inference:8000`.

## Question 6: Startup order

With basic `depends_on`, inference can start too early and fail while loading
the model. This setup waits for MLflow's health check and retries failed
inference starts. The model must also be registered before the first start.

## Question 7: Published ports

`docker compose ps` showed MLflow on port 5000 and the frontend on 8501,
as expected. Inference showed `8000/tcp`, with no host port mapping.

## Question 8: Loading a new version

Refreshing the page still uses the model already loaded in memory. After
moving `champion` to another version, reload it with:

```powershell
docker compose restart inference
```

This project uses the `champion` alias instead of the handout's old `Staging` stage.

## Question 9: Why no rebuild is needed

The image contains the code and packages. The model is downloaded from
MLflow when inference starts, so restarting loads the current champion.

## Question 10: Keeping the model after shutdown

`docker compose down` keeps the named volume, so the registry and alias
survived the next start. Testing `-v` in a separate disposable project removed
its model. Without a registered model, inference cannot start.

## Question 11: Scaling and machine failures

Compose can run three inference replicas on one machine, but a load balancer
still needs to route requests to them. Surviving a machine failure needs
multiple hosts, failover, a durable database, and shared artifact storage;
this local Compose setup does not provide those.

## Checks

- All three services healthy; frontend prediction: `Fried food (36.3%)`.
- Restart loaded champion version 2, with no image rebuild.
- Model and predictions survived `down` / `up`.
- No-volume replacement and disposable `down -v` both removed their test data.
- Invalid uploads returned 400; the frontend handled an unavailable API.
