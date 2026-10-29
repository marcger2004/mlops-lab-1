# Lab 5: verification report

[Run guide](../README.md) | [Answers](../answers.md)

## Local checks

| Check | Result |
| --- | --- |
| Python tests | 13 passed |
| Ruff | Passed |
| Git whitespace check | Passed |
| Dataset class directories | Passed |
| RGB mode and 128 x 128 image dimensions | Passed |
| Minimum images per class | Passed |
| Training/validation class balance | Passed |
| No duplicate images across splits | Failed: 43 duplicate occurrences |

The evaluation split contains 1096 images. The existing duplicate occurrences
are listed in the [content-hash audit](data-validation.txt). Training now checks
the data contract before creating data loaders, so existing leakage blocks new
training runs until the dataset is corrected and tracked with DVC.

The deliberate-copy experiment also failed the cross-split duplicate check.
The temporary copy was removed afterward. The two legacy nested class folders
were renamed locally to Noodles-Pasta and Vegetable-Fruit. Existing DVC metadata
was not changed; restoring an older dataset revision can restore the old layout.

The test suite emitted two upstream TestClient deprecation warnings.

## Experiments still to complete

| Experiment | Status |
| --- | --- |
| Local container smoke test and registry pull | Docker engine was stopped |
| Real candidate training and promotion | MLflow was stopped; dataset leakage also blocks training |
| First/second Actions timing comparison | Not measured |
| Required checks and failing-then-fixed pull request | Not demonstrated |
| GHCR image publication | Awaiting verification of the Actions result |

The [initial Actions run](https://github.com/marcger2004/mlops-lab-1/actions/runs/40890938161)
was queued after commit 55a82cb was pushed. These pending experiments are not
claimed as successful results.
