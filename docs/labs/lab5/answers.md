# Lab 5: CI/CD with GitHub Actions

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md) | [Run guide](README.md)

## Question 1: Why avoid loading the real model in unit tests?
A stopped MLflow server or unavailable network makes correct code fail. Missing credentials, a moved champion alias, deleted artifacts, and incompatible model dependencies also cause unrelated failures. A fake model makes the test deterministic and independent of training infrastructure.

## Question 2: What does the fake-model API test prove?
It checks multipart upload handling, image decoding, the training-compatible tensor shape, model invocation, class mapping, stable softmax, and the JSON response. It checks Bread and approximately 0.90 confidence using log probabilities as fake logits. It does not establish real-model accuracy, generalization, registry availability, or successful loading of actual artifacts.

## Question 3: Which check catches a copied image?
The content-hash check detects the same bytes in two splits, regardless of filename. A corrupt image causes a visible failure; leakage silently inflates evaluation accuracy and can cause an unsuitable model to pass promotion. The regression test builds a valid miniature contract, introduces a cross-split duplicate, and verifies rejection. Actual dataset validation and the duplicate experiment are recorded in the [verification report](reports/verification.md).

## Question 4: Where should data validation run?
Run it after preprocessing or DVC pull and before training on the machine with the data. Also run it in a data pipeline or a self-hosted CI runner with authenticated DVC access before registration/promotion. Cloud CI tests the validator against generated data without downloading the real dataset.

## Question 5: What does needs: test do?
A failed test job skips smoke, and consequently skips publishing. Without needs, smoke could run in parallel and succeed even while unit tests fail.

## Question 6: First versus second CI run
Actual GitHub durations have not yet been measured. setup-uv caches downloaded dependencies; the second uv sync usually gets faster through cache restoration. Registry publishing uses GitHub Actions build-layer caching. The smoke job currently rebuilds without a persistent layer cache, so a faster Docker smoke build is not guaranteed.

## Question 7: Why tag images with the commit SHA?
The SHA identifies the source revision and supports audit and rollback. With latest, machine A can retain yesterday's cached image while machine B pulls today's image, even though both configurations say latest. Use the published SHA tag when deploying; an image digest provides an even stronger content identifier.

## Question 8: Why explicit token permissions?
The publishing job needs package write access and repository read access. Other jobs receive only repository read permission. An overprivileged compromised step could modify source, releases, or repository settings within the granted scopes and publish malicious artifacts.

## Question 9: Branch protection and the deliberately failing PR
With required test and smoke checks and a pull-request requirement, a failing PR shows failed checks and is blocked from normal merging. Administrators may retain bypass privileges depending on rule settings. Central enforcement prevents reliance on every developer remembering local tests. Branch protection and a failing-then-fixed PR have not been demonstrated here; GitHub CLI is unavailable. Configure required checks test and smoke in the repository settings after their first run.

## Question 10: Model promotion decisions
The script reads test_accuracy, follows source_run_id tags used by the earlier registration script, and computes 2*sqrt(p*(1-p)/n). It records both accuracies, the margin, metric, test size, prior champion and decision as candidate-version tags. Missing metrics fail before changing aliases.

Deterministic unit-test example (not trained-model results): p=0.80 and n=1000 give a
margin of 0.02529822, or 2.5298 percentage points. Candidate 0.85 becomes champion;
candidate 0.81 becomes challenger. Actual trained-candidate results are pending because
the MLflow server is not running. The local evaluation split contains 1096 images; --n
must match the split used to measure both model accuracies.

Example commands after starting MLflow and training/registering candidates:

```bash
uv run python -m food11.train --lr 0.000001
uv run python -m food11.train --lr 0.001
# Register each candidate's model artifact without assigning champion first:
# mlflow.register_model("runs:/<run-id>/model", "food11")
uv run python -m food11.promote --version <candidate-version> --n <evaluation-image-count>
```

The existing register.py directly selects champion; do not use that shortcut to register
gate candidates. The champion must remain fixed until the gate evaluates them. Use the
same held-out evaluation split for both candidates and champion.

## Question 11: How can promotion run automatically?
Call the script after training from a local orchestrator or a self-hosted runner that can reach MLflow. Alternatively host MLflow on a reachable authenticated server (for example DagsHub) and run the promotion job with credentials stored as CI secrets. Serialize promotions to avoid two candidates racing to update champion.

## Question 12: Pipeline and version decisions

```text
Human edits code
  -> git push [human; commit SHA chooses code revision]
  -> test [automatic: frozen dependency install, Ruff, pytest]
  -> smoke [automatic after test: build, SKIP_MODEL=1, /health]
  -> publish on main [automatic after smoke]
  -> ghcr.io/marcger2004/mlops-lab-1:<commit-SHA>
  -> pull and start container [human deployment]
  -> resolve food11@champion at startup [automatic]
  -> running API with fixed resolved model version

Data preprocessing / DVC pull [human/local pipeline]
  -> validate_data [run before training where data is accessible]
  -> train and register candidate [human/local pipeline]
  -> promote --version N --n TEST_SIZE [human invocation]
  -> quality gate [automatic decision; selects model alias/version]
```

Code and model releases are independent. A running API resolves champion once;
restart/redeploy to adopt a newly promoted model. CI smoke bypasses model loading and
therefore does not certify registry connectivity.
