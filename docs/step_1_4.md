# Step 1.4 — Assignment company metadata

## Goal and source
Create config/companies.csv from the required company table in the original assignment PDF. These are assignment labels, not independently verified current corporate names, GICS classifications, memberships or market-cap rankings. No firm is replaced. BRK.B is preserved exactly.

## Columns
| Column | Type | Meaning |
| --- | --- | --- |
| ticker | string | Unique assignment identifier, retained across all parts. |
| company_name | string | Name printed in the assignment. |
| sector | string | Assignment-provided sector group. |

The CSV has 50 rows: ten firms in each of five groups. Company-year scope is 50 times nine = 450 targets; this is not data coverage. Companies with renamed brands remain identifiable by assignment ticker. Verified historical domains and page candidates will be maintained in a separate one-to-many URL mapping during Phases 2–3, with dates, evidence and selection notes. No unverified URLs are inserted here.

## Copy update first
Extract organizational-authenticity-step-1.4-update.zip. Copy its config/, docs/, shared/ and tests/ folders into the existing project root, merging the folders. The six files are new. Do not replace your .venv, .git or requirements.txt. If an intended new filename already exists due to your own work, inspect it before overwriting.

Open config/companies.csv in VS Code and confirm its header is ticker,company_name,sector. No new packages, API keys or environment variables are needed.

## Run only when ready
In Command Prompt at the project root with the .venv active:

```bat
python -m shared.check_companies
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected company check: 50 unique companies; ten per sector; 2016–2024; 450 target observations; Company metadata check passed. Expected complete test run at this stage: 20 tests, OK. The checker also appends messages to logs/research.log.

## Implementation walkthrough
load_companies() uses Python's built-in csv.DictReader: each data row becomes a dictionary with the header names as keys. All values stay strings. It requires the three named columns in the documented order, rejects empty values, surrounding whitespace, extra cells and duplicate tickers, and never silently repairs data. UTF-8 with an optional BOM supports common Windows editor output.

validate_assignment_sample() compares the working metadata to docs/assignment_company_reference.json, an audited transcription of the PDF roster. It catches changed tickers, names and sectors even when the row count remains 50. The reference and CSV originate from the same PDF: their mutual agreement alone is not independent proof of transcription accuracy. A separate PDF audit checks the initial transcription. Do not edit the reference to make an incorrect CSV pass.

The reusable loader accepts other sample sizes; assignment-specific validation is separate. This permits future larger studies without rewriting CSV loading logic. A new research design needs its own sample contract.

check_companies.main() loads configuration, initializes the existing logger, validates the metadata, counts sector membership and reports the target scope. Failure returns status 1; success returns 0. No archive requests occur.

## Troubleshooting
- No module named shared: check terminal folder and that update files were merged into the existing project.
- CSV header error: preserve exact column names/order; use comma-separated UTF-8 text.
- Duplicate or missing ticker: correct the CSV using the assignment; do not substitute companies.
- File not found: check config/companies.csv and docs/assignment_company_reference.json are in the existing project.
- Changing BRK.B to BRK-B is not allowed here. External-source identifier mappings will be stored separately.

## Progress
Steps 1.1–1.3 verified by the user on Windows. Step 1.4 implementation tested in the assistant environment; local Windows verification pending. Historical URL discovery has not started. After local validation, update docs/progress.md. Next: Step 1.5, a consolidated environment checkpoint.
