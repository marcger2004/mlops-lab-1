# Lab 1: Git, DVC, and Data Preparation

## Overview

This lab demonstrates how Git and DVC work together in a machine-learning
project. Git versions source code and lightweight metadata, while DVC versions
the datasets and stores their content in remote storage.

## Question 1: Files Created by `uv init`

`uv init` creates the initial Python project structure. The main files are:

- `pyproject.toml`: project metadata, Python version, dependencies, build
	configuration, and command-line entry points.
- `README.md`: project documentation.
- `.python-version`: the selected Python version.
- `src/`: the source-code package directory when the project uses the `src`
	layout.

Together, these files define how the project is installed and executed.

## Question 2: Files Created by `dvc init`

`dvc init` creates the DVC configuration directory and supporting files:

- `.dvc/config`: repository-level configuration, including non-sensitive
	remote definitions.
- `.dvcignore`: patterns for files DVC should skip while scanning.
- `.dvc/`: DVC internal metadata and local state.

The configuration files and `.dvcignore` should be committed to Git. Local
caches, temporary files, and credentials must remain outside the repository.

## Question 3: DVC Credentials and Configuration Scopes

With `--global`, DVC stores settings in the user's global configuration. Other
scopes are:

- `--system`: applies to all users on the machine.
- `--local`: applies only to the current repository.

Passwords, access tokens, and secret keys must never be committed to GitHub.
Only the non-sensitive remote URL belongs in `.dvc/config`. Repository-specific
credentials should be stored in `.dvc/config.local`, which must remain
untracked.

## Question 4: Changes to `.gitignore` After `dvc add data`

Running `dvc add data` adds `/data` to `.gitignore`. Git therefore ignores the
large image files. DVC calculates their hashes, stores the content in its local
cache, and creates a lightweight pointer file for Git to version.

This keeps the Git repository small while preserving data versioning and
reproducibility.

## Question 5: Contents of `data.dvc`

`data.dvc` is the pointer file for the `data` directory. It records the tracked
path, content hash, dataset size, and number of files. It does not contain the
images; it allows DVC to restore the corresponding data from its cache or a
configured remote.

## Question 6: GitHub and DagsHub Contents

GitHub contains the source code, tests, project configuration, DVC metadata,
and pointer files such as `data.dvc`. It does not contain the image files
because the `data` directory is ignored by Git.

DagsHub contains the actual dataset after `dvc push` completes successfully.
The `data.dvc` file identifies the data version, while `.dvc/config` identifies
the DVC remote used for storage.

## Question 7: Restoring Data in a New Clone

After cloning the GitHub repository, the ignored data directory is not restored
by Git. After installing DVC and configuring the remote credentials, run:

```powershell
dvc pull
```

This requires valid DVC credentials and a successful earlier `dvc push`.

## Question 8: Switching Between Code and Data Versions

First, list the commits that changed the data pointer:

```powershell
git log --oneline -- data.dvc
```

After checking out an older Git commit, synchronize the working data with it:

```powershell
git checkout <old-commit-hash>
dvc checkout
```

DVC then changes the working data to match the `data.dvc` pointer in that
commit. If that commit predates the processed datasets, the
`food11_processed` and `food11_processed_mini` directories disappear. Return
to `main` and restore its data version with:

```powershell
git checkout main
dvc checkout
```

Git selects the project revision and DVC synchronizes the corresponding data
revision.

## Submission Checklist

- Commit the source code, tests, README, lab answers, DVC metadata, and pointer
	files to GitHub.
- Run `dvc push` to upload the dataset content to DagsHub.
- Confirm that `dvc pull` works from a clean clone when the full workflow is
	being assessed.
- Never commit raw images, DVC caches, passwords, access tokens, or secret keys.