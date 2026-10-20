# Step 1.3 — Configuration, paths and logging

## Status
Implementation passed ten unittest tests and a setup smoke check in the assistant's Linux environment. Windows verification by the user remains pending. Step 1.2 was verified on the user's Windows 11 system: Python 3.12.6, pip 24.2, active .venv, VS Code interpreter selected and Git ignore confirmed.

## Apply this incremental update
Extract organizational-authenticity-step-1.3-update.zip outside your working project. Copy its CONTENTS into your existing organizational-authenticity folder, merging config/, shared/, tests/ and docs/. All eleven delivered files are new relative to Step 1.1. Keep your existing .venv, .git, READMEs and other files. If a destination file already exists because of your own edits, compare it before replacing it. Do not open the extracted update as a second project.

## Run in Windows Command Prompt from the existing project root
Run each line separately, stopping on an error:

```bat
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m pip check
python -m shared.check_setup
python -m unittest discover -s tests -p test_infrastructure.py -v
git check-ignore logs/research.log
```

No API keys or custom environment variables are needed. Only PyYAML==6.0.3 is installed at this stage; other modules are from Python's standard library. This is the current direct dependency list, not a claim of a complete future pipeline lockfile.

Expected evidence: pip check reports no broken requirements; setup prints 2016 through 2024 (nine years), root and log path, and a passed message; ten tests end in OK; Git prints logs/research.log as ignored. The log file contains the setup messages. No company metadata or real research observations are generated.

## Files and concepts
- config/research_config.yaml: four explicit settings; scope 2016–2024 and INFO logging. Indentation uses spaces.
- requirements.txt: exact tested version of the YAML parser.
- shared/__init__.py and shared/utils/__init__.py: mark Python packages.
- shared/utils/errors.py: ConfigurationError distinguishes invalid settings from other errors; ProjectError is its base.
- shared/utils/paths.py: PROJECT_ROOT comes from this module's file location, not the shell working directory. project_path() joins paths and rejects escapes outside the root.
- shared/utils/config.py: load_config() reads UTF-8 YAML, rejects duplicate/unknown/missing keys and invalid types/ranges, then returns a frozen ResearchConfig. years includes the end year. The custom loader extends yaml.SafeLoader; it does not enable arbitrary Python objects.
- shared/utils/logging_utils.py: setup_logging() creates logs/ when needed, appends UTF-8 messages to research.log and sends messages to the terminal. UTC timestamps end with Z. INFO is normal progress, WARNING is an issue requiring attention, ERROR is failure, DEBUG is extra troubleshooting detail. Repeated setup replaces handlers rather than duplicating messages. Do not log credentials, authorization headers or full remote responses.
- shared/check_setup.py: main() connects configuration and logging. It returns 0 on success and 1 for expected configuration or filesystem setup errors. Missing third-party dependencies must first be installed. Unexpected programming errors remain visible rather than being silently swallowed.
- tests/test_infrastructure.py: ten tests with synthetic temporary inputs; no external requests. Temporary logs are closed and removed. Uses Python's built-in unittest, so no extra test dependency is needed yet.

## Why these choices
The configuration contains only implemented settings, avoiding the appearance that future selection rules are already applied. The assignment dates live in YAML; changing them is technically possible but requires explicit research-scope justification. Paths are based on the repository layout, so Windows usernames are never hardcoded. Logs append so repeated checks preserve earlier runs. A single log file is sufficient for this stage; per-run metadata and collection error categories will be added when needed.

## Common errors
- No module named yaml: install requirements using this environment's python -m pip.
- No module named shared: run the module command from the repository root; do not run python shared/check_setup.py.
- Cannot read valid configuration: check that config/research_config.yaml was copied and has the exact four keys.
- No tests found: verify tests/test_infrastructure.py exists in the working project.
- PermissionError opening log: check that the project/log file is writable.
- Date appears different: logs use UTC for consistency across machines, not local New York time.

## Progress
Steps 1.1 and 1.2 complete. Step 1.3 implemented and tested in the assistant environment; awaiting Windows output. Step 1.4 (exact company metadata) has not started.

After local checks pass, append this milestone to docs/progress.md. Do not replace that document with an older scaffold version.
