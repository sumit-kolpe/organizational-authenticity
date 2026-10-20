"""Audit the six documented pilot downloads without network requests."""

import hashlib
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = (
    PROJECT_ROOT / "part1_stated_values" / "data" / "raw" / "html"
)
REPORT_PATH = (
    PROJECT_ROOT
    / "part1_stated_values"
    / "outputs"
    / "pilot_download_audit.json"
)

# These are inspected pilot examples, not final annual selections.
EXPECTED = [
    ("MSFT", "20160101214549", "http://www.microsoft.com/en-us/about"),
    ("MSFT", "20200102053409", "https://www.microsoft.com/en-us/about"),
    ("MSFT", "20240101141329", "https://www.microsoft.com/en-us/about/"),
    ("AAPL", "20160101124138", "https://www.apple.com/jobs/us/"),
    ("AAPL", "20200115042328", "https://www.apple.com/jobs/us/about.html"),
    ("AAPL", "20240319041941", "https://www.apple.com/careers/us/"),
]


def audit_capture(ticker, timestamp, original_url):
    """Return findings for one expected HTML/metadata pair."""
    stem = f"{ticker}_{timestamp}"
    html_path = RAW_DIR / f"{stem}.html"
    metadata_path = RAW_DIR / f"{stem}.json"

    result = {
        "capture_id": stem,
        "errors": [],
        "warnings": [],
        "actual_bytes": None,
        "toolbar_marker_present": None,
        "content_quality_status": "not_assessed_by_this_audit",
    }
    errors = result["errors"]
    warnings = result["warnings"]

    for path in (html_path, metadata_path):
        if not path.is_file():
            errors.append(f"Missing file: {path.name}")

    if errors:
        result["audit_status"] = "fail"
        return result

    try:
        content = html_path.read_bytes()
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            raise ValueError("Metadata must be a JSON object.")

        expected_url = (
            f"https://web.archive.org/web/{timestamp}/{original_url}"
        )
        expected_fields = {
            "schema_version": 1,
            "ticker": ticker,
            "target_year": int(timestamp[:4]),
            "requested_capture_timestamp": timestamp,
            "original_url": original_url,
            "requested_snapshot_url": expected_url,
            "final_response_url": expected_url,
            "replay_http_status": 200,
        }

        for field, expected_value in expected_fields.items():
            actual_value = metadata.get(field)
            if (
                type(actual_value) is not type(expected_value)
                or actual_value != expected_value
            ):
                errors.append(f"Missing or unexpected field: {field}")

        result["actual_bytes"] = len(content)
        if not content:
            errors.append("HTML file is empty.")

        if metadata.get("byte_count") != len(content):
            errors.append("Byte count does not match metadata.")

        actual_hash = hashlib.sha256(content).hexdigest()
        if metadata.get("sha256") != actual_hash:
            errors.append("SHA-256 checksum does not match metadata.")

        content_type = metadata.get("content_type")
        if not isinstance(content_type, str):
            errors.append("Content-Type is missing or invalid.")
        elif content_type.split(";", 1)[0].strip().lower() not in (
            "text/html", "application/xhtml+xml"
        ):
            errors.append("Recorded Content-Type is not HTML.")

        # Missing evidence is a warning; contradictory evidence is an error.
        memento = metadata.get("memento_datetime")
        if not memento:
            warnings.append("Memento-Datetime was not recorded.")
        else:
            try:
                observed_date = parsedate_to_datetime(memento)
                expected_date = datetime.strptime(
                    timestamp, "%Y%m%d%H%M%S"
                ).replace(tzinfo=timezone.utc)

                if observed_date.tzinfo is None:
                    errors.append("Memento-Datetime has no timezone.")
                elif observed_date.astimezone(timezone.utc) != expected_date:
                    errors.append("Memento-Datetime contradicts capture time.")
            except (TypeError, ValueError, OverflowError):
                errors.append("Memento-Datetime cannot be parsed.")

        # This is a marker check, not HTML parsing or text extraction.
        result["toolbar_marker_present"] = b"wm-ipp" in content.lower()

    except (OSError, ValueError, TypeError) as exc:
        errors.append(f"Could not audit file pair: {exc}")

    result["audit_status"] = (
        "fail" if errors else "pass_with_warning" if warnings else "pass"
    )
    return result


def main():
    """Audit expected captures and write a separate, rerunnable report."""
    results = [
        audit_capture(ticker, timestamp, url)
        for ticker, timestamp, url in EXPECTED
    ]

    expected_names = {
        f"{ticker}_{timestamp}.{extension}"
        for ticker, timestamp, _ in EXPECTED
        for extension in ("html", "json")
    }
    actual_names = (
        {path.name for path in RAW_DIR.iterdir() if path.is_file()}
        if RAW_DIR.is_dir()
        else set()
    )
    unexpected_files = sorted(actual_names - expected_names)

    report = {
        "audit_version": 1,
        "audited_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "six manually inspected pilot captures",
        "unexpected_files": unexpected_files,
        "captures": results,
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = REPORT_PATH.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    temporary_path.replace(REPORT_PATH)

    for result in results:
        print(
            f"{result['capture_id']}: {result['audit_status']} | "
            f"bytes={result['actual_bytes']} | "
            f"toolbar_marker={result['toolbar_marker_present']}"
        )
        for message in result["errors"] + result["warnings"]:
            print(f"  - {message}")

    if unexpected_files:
        print("Additional files requiring review:", ", ".join(unexpected_files))

    print(f"Report: {REPORT_PATH}")
    print("Content quality remains subject to separate inspection.")
    return 1 if any(r["errors"] for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())