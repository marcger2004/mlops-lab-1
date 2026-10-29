# Lab 5: verification report

[Answers](../answers.md)

## Local checks

| Check | Result |
| --- | --- |
| Python tests | 19 tests covered by passing pull-request CI; deprecation warnings treated as errors |
| Ruff | Passed |
| Git whitespace check | Passed |
| Dataset class directories | Passed |
| RGB mode and 128 x 128 image dimensions | Passed |
| Minimum images per class | Passed |
| Training/validation class balance | Passed |
| No duplicate images across splits | Passed for full and mini processed datasets |

The mini evaluation split still contains 1096 images. All five contract checks
pass on both processed datasets. The [machine-readable contract results](data-contract.json)
record split counts and check outcomes.

## Duplicate cleanup

The cleanup removed 43 duplicate copies from the mini dataset and 612 from the
full processed dataset. It preserves evaluation first, then validation, and
removes overlapping copies from lower-priority splits. Raw source images are
unchanged. The [cleanup manifest](deduplication.json) records every removed path,
its retained counterpart, and the file hash. The [initial audit](data-validation.txt)
is retained as historical evidence of the original mini dataset issue.

Preprocessing now applies the same cleanup automatically. Regression tests cover
dry runs, evaluation preservation, repeat runs, preprocessing, and raw-data
preservation. Old model accuracies are not re-certified by this cleanup; retrain
and evaluate candidates on the corrected datasets.

## Dependency compatibility

The test client now uses httpx2 and the lockfile selects Starlette 1.10.0.
Both original deprecation warnings are resolved without suppressing warnings.
Verification uses `python -W error::DeprecationWarning -m pytest -q`.

## DVC publication

`dvc add data` recorded the corrected dataset locally:

- Directory hash: `b38c87deafd98a0d322d43f803586737.dir`.
- File count: 35923.
- Total size: 1274306970 bytes.

Upload to the configured DagsHub DVC remote is pending explicit user approval.
The GitHub data pointer remains at the previous revision until the corrected
content has been uploaded successfully. Do not expect `dvc pull` to restore the
corrected version yet. Existing raw dataset contents remain unchanged.

To rebuild processed datasets from the raw images restored by DVC (including
correcting the two legacy nested class names):

```powershell
uv run mlops-lab-1
uv run python -m food11.validate_data data/food11_processed
uv run python -m food11.validate_data data/food11_processed_mini
```

## Experiments still to complete

| Experiment | Status |
| --- | --- |
| Local container smoke test and registry pull | Docker started; pull attempt failed when the signed layer URL expired; cloud container smoke passed |
| Real candidate training and promotion | Completed: two real runs; both challenger; champion 1 retained |
| First/second Actions timing comparison | Measured: 5m28s and 6m34s; see ci-runs.json |
| Required checks and failing-then-fixed pull request | Protection enabled; failing and blocked PR recorded; corrected test and smoke checks passed |
| GHCR image publication | Passed in the initial Actions run |

The [initial Actions run](https://github.com/marcger2004/mlops-lab-1/actions/runs/40890938161)
completed successfully for commit 55a82cb: test, smoke, and registry publication
all passed. The container is published as
`ghcr.io/marcger2004/mlops-lab-1:55a82cb40cffcec952ae75d15a1a724fa8e5141f`.
The exact image tag is the full commit SHA shown by that run. The local pull,
branch-protection experiment, and real-model promotion remain unverified.

## Protected branch experiment

[Pull request #1](https://github.com/marcger2004/mlops-lab-1/pull/1) contains the
intentional failing commit and its correction. The [captured evidence](pull-request.json)
shows test failure, smoke skipped, and a blocked merge, followed by successful
checks for the corrected expectation. Main now requires a pull request with test
and smoke checks, including for administrators. No approving review is required
for this individual repository.

## Real model-gate experiment

The [model-gate report](model-gate.json) records candidate versions 2 and 3,
learning rates 0.000001 and 0.001, actual accuracies, run IDs, and tags read back
from MLflow. Both were rejected against champion 1. With 1096 evaluation images,
the margin was 2.6409 percentage points and the threshold was 76.9110% accuracy.

The historical champion predates data cleanup. The candidates use corrected
data; the historical metric is not a claim of leakage-free baseline training.
The run script uses a fixed seed, logs the seed and evaluation count, registers
without moving champion first, and invokes the gate after each training run.

The [empty-commit comparison](ci-empty-commit.json) also records the repeat CI
experiment with identical code: 1m32s before the empty commit and 1m40s after it.
