"""Collect and cache a small CDX discovery sample.

Run from the project root:
    python -m part1_stated_values.src.collect_cdx
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = (
    PROJECT_ROOT / "part1_stated_values" / "data" / "raw" / "cdx"
)
ENDPOINT = "https://web.archive.org/cdx/search/cdx"
FIELDS = ["timestamp", "original", "statuscode", "mimetype"]
USER_AGENT = "OrganizationalAuthenticityResearch/0.1"


def validate_response(data, year):
    """Check the CDX table without discarding redirects or revisit records."""
    if not isinstance(data, list):
        raise ValueError("Expected a JSON list from CDX.")

    # An empty response is a valid negative discovery result.
    if not data:
        return

    if data[0] != FIELDS:
        raise ValueError(f"Unexpected CDX header: {data[0]!r}")

    for row in data[1:]:
        if not isinstance(row, list) or len(row) != len(FIELDS):
            raise ValueError(f"Malformed CDX row: {row!r}")

        if not all(isinstance(value, str) for value in row):
            raise ValueError("CDX row values must be strings.")

        timestamp = row[0]
        if len(timestamp) != 14 or not timestamp.isdigit():
            raise ValueError(f"Invalid timestamp: {timestamp!r}")

        capture_date = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
        if capture_date.year != year:
            raise ValueError(f"Capture outside requested year: {timestamp}")


def collect_cdx(url, year, limit):
    """Return the saved response path, record count, and cache-use flag."""
    params = {
        "url": url,
        "matchType": "exact",
        "from": str(year),
        "to": str(year),
        "output": "json",
        "fl": ",".join(FIELDS),
        "limit": str(limit),
    }
    request_url = ENDPOINT + "?" + urlencode(params)

    # Different queries receive different filenames.
    query_hash = hashlib.sha256(
        request_url.encode("utf-8")
    ).hexdigest()
    cache_path = CACHE_DIR / f"{query_hash}.json"

    if cache_path.exists():
        saved = json.loads(cache_path.read_text(encoding="utf-8"))
        if saved["request_url"] != request_url:
            raise ValueError("Cached request does not match this query.")
        data = saved["cdx_response"]
        validate_response(data, year)
        return cache_path, max(0, len(data) - 1), True

    request = Request(
        request_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )

    # Read bytes before parsing: an empty body is not a valid [] result.
    with urlopen(request, timeout=30) as response:
        raw_body = response.read()
        final_url = response.geturl()
        api_status = response.status
        content_type = response.headers.get("Content-Type", "")

    diagnostic = {
        "schema_version": 1,
        "purpose": "cdx_response_diagnostic",
        "request_url": request_url,
        "request_parameters": params,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_response_url": final_url,
        "api_http_status": api_status,
        "content_type": content_type,
        "response_byte_count": len(raw_body),
        "response_sha256": hashlib.sha256(raw_body).hexdigest(),
        "body_preview": raw_body[:500].decode("utf-8", errors="replace"),
        "body_preview_truncated": len(raw_body) > 500,
        "coverage_status": "unresolved",
        "valid_cdx_cache": False,
    }

    def fail_response(reason, detail):
        """Save response evidence outside the cache, then report the failure."""
        diagnostic["reason"] = reason
        diagnostic["detail"] = detail
        diagnostic_dir = PROJECT_ROOT / "part1_stated_values" / "outputs" / "cdx_diagnostics"
        diagnostic_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        diagnostic_path = diagnostic_dir / f"{query_hash}_{stamp}.json"
        temporary = diagnostic_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(diagnostic, indent=2, ensure_ascii=False) + "\n",
                             encoding="utf-8")
        temporary.replace(diagnostic_path)
        raise ValueError(
            f"{reason}: {detail} Coverage unresolved; no valid CDX cache saved. "
            f"Diagnostic: {diagnostic_path}"
        )

    if api_status != 200:
        fail_response("unexpected_http_status", f"Received HTTP {api_status}.")
    if not raw_body.strip():
        fail_response("empty_response_body", "The response body is empty or whitespace-only.")
    try:
        data = json.loads(raw_body)
    except (ValueError, UnicodeError) as exc:
        fail_response("invalid_json_response", str(exc))
    try:
        validate_response(data, year)
    except ValueError as exc:
        fail_response("invalid_cdx_response", str(exc))

    saved = {
        "schema_version": 1,
        "purpose": "limited_discovery_sample",
        "request_url": request_url,
        "request_parameters": params,
        "user_agent": USER_AGENT,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "api_response_url": final_url,
        "api_http_status": api_status,
        "response_byte_count": len(raw_body),
        "content_type": content_type,
        "inventory_complete": False,
        "cdx_response": data,
    }

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first to avoid a half-written cache file.
    temporary_path = cache_path.with_suffix(".tmp")
    temporary_path.write_text(
        json.dumps(saved, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(cache_path)

    return cache_path, max(0, len(data) - 1), False


def main():
    """Read command-line settings and report success or a useful error."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url", default="www.microsoft.com/en-us/about"
    )
    parser.add_argument("--year", type=int, default=2020)
    parser.add_argument("--limit", type=int, default=3)
    args = parser.parse_args()

    if not 2016 <= args.year <= 2024:
        parser.error("--year must be between 2016 and 2024.")
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100.")
    if not args.url.strip():
        parser.error("--url cannot be empty.")

    try:
        path, count, cached = collect_cdx(
            args.url.strip(), args.year, args.limit
        )
    except HTTPError as exc:
        print(
            f"CDX HTTP error {exc.code}: {exc.reason}. "
            "No new cache file was saved.",
            file=sys.stderr,
        )
        return 1
    except (URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
        print(f"Collection failed: {exc}", file=sys.stderr)
        return 1

    print("Source: existing cache" if cached else "Source: CDX API")
    print(f"Capture records: {count}")
    print(f"Saved file: {path}")
    print("Discovery sample only; annual inventory is not complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())