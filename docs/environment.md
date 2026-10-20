# Development environment

## Verified setup

- Operating system: Windows 11
- Editor: Visual Studio Code
- Terminal: Command Prompt (cmd)
- Python: 3.12.6
- Virtual environment: .venv
- PyYAML: 6.0.3

On this computer, `python` resolves to Python 3.12.6.
The `py` launcher did not recognize that installation, so the
environment was created using `python -m venv .venv`.

## Recreate the environment on Windows

From the project root, first confirm that `python --version`
reports the intended Python version. Then run:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements-lock.txt
python -m pip check
```

In VS Code, select `.venv\Scripts\python.exe` using
“Python: Select Interpreter.”

The dependency snapshot records package versions, not the Python
interpreter itself. Recreating the environment on a fresh machine
has not yet been tested.

## Verification commands

```bat
python -m shared.check_setup
python -m shared.check_companies
python -m unittest discover -s tests -p "test_*.py" -v
```

## Verified results

- Configuration and logging checks passed.
- Exact 50-company assignment roster validated.
- Ten companies per assignment sector.
- Configured scope: 2016–2024, nine years.
- Target: 450 company-year observations.
- All 20 automated tests passed.
- Virtual environment and generated logs are ignored by Git.

No historical pages or corporate disclosures have been collected.