# Lab 1: Git, DVC, and Data Preparation

[Lab index](../../../README.md#lab-documentation) | [Instructions](instructions.md)

## Overview

This lab uses Git for the code and DVC for the dataset.

## Question 1: Files Created by `uv init`

`uv init` sets up the Python project: `pyproject.toml` for settings and
dependencies, `README.md` for documentation, and `.python-version` for the
Python version. This project keeps its code in `src/`.

## Question 2: Files Created by `dvc init`

`dvc init` creates `.dvc/` and `.dvcignore`. The settings are in
`.dvc/config`. Passwords and local cache files should not be added to Git.

## Question 3: DVC Credentials and Configuration Scopes

`--global` saves settings for my user account, `--system` for everyone on
the computer, and `--local` just for this repository. The remote URL goes in `.dvc/config`, while
credentials go in the untracked `.dvc/config.local` file.

## Question 4: Changes to `.gitignore` After `dvc add data`

`dvc add data` adds `/data` to `.gitignore` and creates `data.dvc`.
Git only needs to track `data.dvc`; DVC takes care of the images.

## Question 5: Contents of `data.dvc`

`data.dvc` records the folder path, hash, size, and number of files.
DVC uses it to find the right version of the data. The images are not inside
this file.

## Question 6: GitHub and DagsHub Contents

GitHub stores the code, configuration, and `data.dvc` file. DagsHub stores
the actual dataset after a successful `dvc push`.

## Question 7: Restoring Data in a New Clone

After cloning, the images are still missing. With DVC and the remote access
set up, this command downloads them:

```powershell
dvc pull
```

## Question 8: Switching Between Code and Data Versions

To go back to an older version, first find its commit, then run:

```powershell
git log --oneline -- data.dvc
git checkout <old-commit-hash>
dvc checkout
```

If the processed folders did not exist in that version, they disappear.
To return to the current version:

```powershell
git checkout main
dvc checkout
```

## Submission checklist

- Commit the source code, tests, README, lab answers, DVC metadata, and pointer
  files to GitHub.
- Run `dvc push` to upload the dataset content to DagsHub.
- Confirm that `dvc pull` works from a clean clone when the full workflow is
  being assessed.
- Never commit raw images, DVC caches, passwords, access tokens, or secret keys.
