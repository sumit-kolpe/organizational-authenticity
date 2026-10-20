"""Load reusable company metadata, then optionally enforce the assignment sample."""
import csv
import json
from pathlib import Path

from shared.utils.errors import ProjectError
from shared.utils.paths import PROJECT_ROOT, project_path

FIELDS = ("ticker", "company_name", "sector")


class CompanyMetadataError(ProjectError):
    """Company data are unreadable or violate the declared data contract."""


def _source_path(path: str | Path) -> Path:
    """Interpret relative paths from the project root, as configuration does."""
    source = Path(path)
    return source if source.is_absolute() else PROJECT_ROOT / source


def load_companies(path: str | Path = "config/companies.csv") -> list[dict[str, str]]:
    """Read CSV as strings and validate its structure without fixing data silently.

    This general loader does not hardcode a 50-company limit. The separate
    assignment check enforces the recruitment task's fixed sample.
    """
    source = _source_path(path)
    try:
        # utf-8-sig also accepts an optional BOM from Windows CSV editors.
        with source.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, strict=True)
            if reader.fieldnames != list(FIELDS):
                raise CompanyMetadataError(f"CSV header must be exactly {','.join(FIELDS)}")
            rows = []
            seen = set()
            for row in reader:
                if set(row) != set(FIELDS):
                    raise CompanyMetadataError(f"Incorrect column count near line {reader.line_num}.")
                for field in FIELDS:
                    value = row[field]
                    if not isinstance(value, str) or not value.strip():
                        raise CompanyMetadataError(f"Missing {field} near line {reader.line_num}.")
                    if value != value.strip():
                        raise CompanyMetadataError(f"Unexpected surrounding whitespace in {field} near line {reader.line_num}.")
                if row["ticker"] in seen:
                    raise CompanyMetadataError(f"Duplicate ticker: {row['ticker']}")
                seen.add(row["ticker"])
                rows.append(row)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise CompanyMetadataError(f"Cannot read company metadata at {source}: {exc}") from exc
    if not rows:
        raise CompanyMetadataError("Company metadata must contain at least one company.")
    return rows


def validate_assignment_sample(companies: list[dict[str, str]]) -> None:
    """Check exact names, tickers and sectors against the PDF-derived reference.

    Row ordering is irrelevant. The reference is a transcription, not an
    independent external data source; its agreement with the PDF was audited.
    """
    source = project_path("docs", "assignment_company_reference.json")
    try:
        reference = json.loads(source.read_text(encoding="utf-8"))["companies"]
        if not isinstance(reference, list) or len(reference) != 50:
            raise ValueError("Reference must contain the 50 assignment companies.")
        expected = {}
        for row in reference:
            if not isinstance(row, dict) or set(row) != set(FIELDS):
                raise ValueError("Invalid reference row.")
            if any(not isinstance(row[k], str) or not row[k] for k in FIELDS):
                raise ValueError("Invalid reference value.")
            if row["ticker"] in expected:
                raise ValueError("Duplicate reference ticker.")
            expected[row["ticker"]] = row
    except (OSError, UnicodeError, ValueError, KeyError, TypeError) as exc:
        raise CompanyMetadataError(f"Cannot use assignment reference: {exc}") from exc

    actual = {}
    for row in companies:
        if not isinstance(row, dict) or set(row) != set(FIELDS):
            raise CompanyMetadataError("Invalid company row supplied to assignment validation.")
        if any(not isinstance(row[k], str) or not row[k] for k in FIELDS):
            raise CompanyMetadataError("Invalid company value supplied to assignment validation.")
        if row["ticker"] in actual:
            raise CompanyMetadataError(f"Duplicate ticker: {row['ticker']}")
        actual[row["ticker"]] = row
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise CompanyMetadataError(f"Assignment tickers differ: missing={missing}, extra={extra}")
    for ticker, row in expected.items():
        if actual[ticker] != row:
            raise CompanyMetadataError(f"Name or sector differs from assignment for {ticker}.")
