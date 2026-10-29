# Lab 5: CI/CD with GitHub Actions

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Answers](answers.md)

This lab adds automated code checks, a container smoke test, SHA-tagged GHCR
images, a data contract, and an MLflow model promotion gate.

## Files

| Location | Purpose |
| --- | --- |
| `.github/workflows/ci.yml` | Test, smoke, and image publication jobs |
| `src/food11/data.py` | Pure image preprocessing functions |
| `src/food11/serve.py` | API and model-free smoke mode |
| `src/food11/validate_data.py` | Dataset contract checks |
| `src/food11/promote.py` | Model promotion quality gate |
| `tests/` | Unit and API tests, including a committed image fixture |
| [answers.md](answers.md) | Answers to the 12 lab questions and pipeline diagram |
| [reports/verification.md](reports/verification.md) | Observed results and pending experiments |
| [reports/data-validation.txt](reports/data-validation.txt) | Existing cross-split duplicate audit |

## Run the local checks

Run from the repository root:

```powershell
uv sync --frozen
uv run ruff check src tests
uv run pytest -q
uv run python -m food11.validate_data data/food11_processed_mini
```

The current local dataset fails the duplicate check. Resolve the leakage and
track the corrected dataset with DVC before training new candidates.

## Build and probe the API

Start Docker Desktop with Linux containers, then run:

```powershell
docker build -t food11-api:local .
docker run -d --name food11-api-check -p 8000:8000 -e SKIP_MODEL=1 food11-api:local
Invoke-RestMethod http://localhost:8000/health
docker rm -f food11-api-check
```

Allow time for startup before probing. Model-free mode returns a healthy status
at `/health` and HTTP 503 at `/predict` until a model is available.

## Promote a registered candidate

Start MLflow and register the candidate without changing champion. Use the actual
number of evaluation images shared by the candidate and champion:

```powershell
uv run python -m food11.promote --version 8 --n 1096
```

Version 8 is an example; replace it with the registered candidate version.
The script records the gate evidence and updates champion only when the candidate
passes the two-standard-error threshold. Otherwise it assigns challenger.

## GitHub workflow

Every push and pull request runs test, then smoke. Pushes to main also publish
`ghcr.io/marcger2004/mlops-lab-1:<commit-SHA>` after both checks pass.
See [Actions](https://github.com/marcger2004/mlops-lab-1/actions) for live results.

Configure main to require a pull request and the test and smoke checks after
those checks have appeared in Actions. The [verification report](reports/verification.md)
distinguishes completed checks from the remaining lab experiments.
