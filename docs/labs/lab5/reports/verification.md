# Lab 5: verification report

[Answers](../answers.md)

## Local checks

| Check | Result |
| --- | --- |
| Python tests | 15 passed; deprecation warnings treated as errors |
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

To correct an older local processed dataset without rebuilding it:

```powershell
uv run python -m food11.deduplicate data/food11_processed data/food11_processed_mini --apply
uv run python -m food11.validate_data data/food11_processed
uv run python -m food11.validate_data data/food11_processed_mini
```

## Experiments still to complete

| Experiment | Status |
| --- | --- |
| Local container smoke test and registry pull | Docker engine was stopped |
| Real candidate training and promotion | MLflow was stopped; dataset contract now passes |
| First/second Actions timing comparison | Measured: 5m28s and 6m34s; see ci-runs.json |
| Required checks and failing-then-fixed pull request | Protection enabled; failing check and blocked PR recorded; fixed checks pending |
| GHCR image publication | Passed in the initial Actions run |

The [initial Actions run](https://github.com/marcger2004/mlops-lab-1/actions/runs/40890938161)
completed successfully for commit 55a82cb: test, smoke, and registry publication
all passed. The container is published as
`ghcr.io/marcger2004/mlops-lab-1:55a82cb40cffcec952ae75d15a1a724fa8e5141f`.
The exact image tag is the full commit SHA shown by that run. The local pull,
branch-protection experiment, and real-model promotion remain unverified.
