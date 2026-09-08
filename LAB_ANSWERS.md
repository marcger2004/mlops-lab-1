# Lab 1 Answers

## Question 1

`uv init` creates the Python project metadata (`pyproject.toml`), the Python
version file, a README, and the source package structure. The metadata defines
the project name, Python version, dependencies, build backend, and commands.

## Question 2

The `.dvc` directory contains DVC configuration and internal files. The
`.dvcignore` file lists files that DVC should skip while scanning. These files
are useful to share with the project and should be committed to Git, except for
local caches and temporary files that are not part of the repository.

## Question 3

With `--global`, DVC stores the remote credentials in the user's global DVC
configuration, outside this repository. Other scopes are `--system` for the
machine-wide configuration and `--local` for the current repository. Passwords
and access tokens must never be committed to GitHub. Only the non-secret remote
URL in `.dvc/config` should be committed.

## Question 4

`dvc add data` adds `/data` to `.gitignore`. Git therefore ignores the actual
dataset files, while DVC tracks them in its cache and Git tracks the pointer
file. This prevents the large images from being committed to GitHub.

## Question 5

`data.dvc` is the DVC pointer file. It records the path (`data`), the content
hash, the size, and the number of files. It lets DVC retrieve the exact data
version associated with a Git commit.

## Question 6

GitHub contains the source code, project configuration, `.dvc` metadata, and
`data.dvc`, but not the image files themselves. DagsHub contains the image data
only after `dvc push` has completed successfully. The `data.dvc` file points to
the data version, while `.dvc/config` points DVC to the DagsHub remote.

## Question 7

After cloning the GitHub repository, the data directory is not restored by Git
because it is ignored. Run the following commands to retrieve it:

```powershell
dvc pull
```

This requires DVC credentials and a successful earlier `dvc push` to the
configured DagsHub remote.

## Question 8

After checking out an older Git commit, run:

```powershell
dvc checkout
```

DVC then changes the working data to match the `data.dvc` pointer in that
commit. If that commit predates the processed datasets, the
`food11_processed` and `food11_processed_mini` directories disappear. After
returning to `main` and running `dvc checkout`, the data from the main commit is
restored.

## Submission checklist

Commit and push the code, tests, README, lab answers, DVC configuration, and
pointer files to GitHub. Run `dvc push` separately to upload the image content
to DagsHub. Do not commit DVC credentials or the raw image files to GitHub.