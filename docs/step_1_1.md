# Step 1.1 — Create the research repository

## What and why
A repository is a project folder managed by Git, which records snapshots of file changes called commits. The four research parts have separate homes, while shared functions will prevent duplicated logic. A README explains how to understand a folder. `.gitkeep` is a conventional empty marker because Git tracks files, not empty directories.

## Use the supplied scaffold
Download and extract `organizational-authenticity-step-1.1.zip`. Open the extracted `organizational-authenticity` folder in your editor. Its README should be directly inside the folder you open.

No Python packages, API keys or environment variables are needed for this step. The next step configures Python.

## Initialize Git on your computer
Open a terminal inside the extracted project folder and run these commands one at a time:

```sh
git --version
git init -b main
git status --short
```

The archive intentionally excludes `.git`, so it contains portable project files rather than another environment's Git metadata. Expected result: a new repository on `main`, with project files shown as untracked (`??`). Nothing has been pushed to GitHub.

## Verify protections
```sh
git check-ignore .env .venv/example.txt part1_stated_values/data/raw/example.html
git check-ignore .env.example
```

The first command should print all three paths. The second should print nothing and exit with status 1: the safe example must remain eligible for tracking. `.gitignore` only affects untracked files; it does not remove a previously committed secret.

## Optional first local commit
After inspecting the files:

```sh
git add .
git diff --cached --stat
git commit -m "Create research repository scaffold"
```

If Git asks for your identity, configure your own name and chosen commit email with repository-local `git config user.name` and `git config user.email`, then retry. Do not copy someone else's identity. A first commit and remote GitHub setup are not prerequisites for this scaffold checkpoint.

## Troubleshooting
- “git not recognized”: install Git, reopen the terminal, and retry; extracted files remain usable meanwhile.
- “not a git repository”: ensure the terminal is inside the extracted project root and run `git init -b main`.
- If an older Git rejects `-b`, run `git init` followed by `git symbolic-ref HEAD refs/heads/main` in the new repository.
- Seeing no downloaded data is expected: collection has not started.
- Never extract over another working project without checking for conflicting files.

## Completion criteria
Four part folders and their READMEs exist; data layers are separated; scope and decisions are documented; Git initializes successfully; sensitive/local paths are ignored while final outputs remain trackable.

Stop here. Step 1.2 will select and configure the Python environment.
