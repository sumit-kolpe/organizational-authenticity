"""Summarize limited CDX discovery samples; never select annual captures.

Run from the project root with python -m part1_stated_values.src.check_cdx_coverage.
Uses only the Python standard library and the existing collect_cdx module.
"""
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit

from . import collect_cdx as collector

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def cache_path_for(url, year, limit):
    """Reproduce the existing collector's query key for cache-only checks."""
    params = {"url": url, "matchType": "exact", "from": str(year),
              "to": str(year), "output": "json",
              "fl": ",".join(collector.FIELDS), "limit": str(limit)}
    request_url = collector.ENDPOINT + "?" + urlencode(params)
    key = hashlib.sha256(request_url.encode("utf-8")).hexdigest()
    return collector.CACHE_DIR / (key + ".json")


def inspect_year(url, year, limit, cache_only=False):
    """Return one result; missing/failed requests have null capture counts."""
    row = {"year": year, "status": None, "capture_records": None,
           "html_200_records": None, "used_cache": None,
           "source_file": None, "source_sha256": None,
           "source_retrieved_at_utc": None, "returned_original_urls": [],
           "captures": [], "inventory_complete": False, "error": None}
    if cache_only and not cache_path_for(url, year, limit).exists():
        row["status"] = "not_checked_cache_missing"
        return row
    try:
        path, count, cached = collector.collect_cdx(url, year, limit)
        raw = path.read_bytes()
        saved = json.loads(raw)
        if saved["api_http_status"] != 200:
            raise ValueError("Cached API response is not HTTP 200.")
        table = saved["cdx_response"]
        collector.validate_response(table, year)
        captures = [dict(zip(collector.FIELDS, values)) for values in table[1:]]
        row.update(status="records_found" if count else "no_records_returned",
                   capture_records=count,
                   html_200_records=sum(c["statuscode"] == "200" and
                                        c["mimetype"] == "text/html" for c in captures),
                   used_cache=cached,
                   source_file=path.relative_to(PROJECT_ROOT).as_posix(),
                   source_sha256=hashlib.sha256(raw).hexdigest(),
                   source_retrieved_at_utc=saved["retrieved_at_utc"],
                   returned_original_urls=sorted({c["original"] for c in captures}),
                   captures=captures)
    except HTTPError as exc:
        row.update(status="request_failed", error=f"HTTP {exc.code}: {exc.reason}",
                   http_status=exc.code)
    except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError) as exc:
        row.update(status="request_failed", error=f"{type(exc).__name__}: {exc}")
    return row


def save_report(path, report):
    """Atomically checkpoint after each year so an interrupted run is traceable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year", type=int, default=2024)
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--cache-only", action="store_true",
                        help="Never request the network; report missing caches separately.")
    args = parser.parse_args(argv)
    if not 2016 <= args.start_year <= args.end_year <= 2024:
        parser.error("Years must be ordered and within 2016–2024.")
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100.")
    if not args.ticker or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-" for c in args.ticker):
        parser.error("Use an assignment ticker such as MSFT or BRK.B.")
    args.url = args.url.strip()
    parsed = urlsplit(args.url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        parser.error("Use a complete HTTP(S) page URL without credentials or a fragment.")
    settings = vars(args).copy()
    run_key = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:16]
    path = PROJECT_ROOT / "part1_stated_values" / "outputs" / "cdx_coverage" / f"{args.ticker}_{run_key}.json"
    report = {"schema_version": 1, "purpose": "limited_discovery_coverage",
              "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "settings": settings, "run_complete": False,
              "inventory_complete": False, "annual_selection_final": False,
              "interpretation": "Counts refer only to returned samples. Empty queries do not establish historical absence. HTTP 200 HTML records still require content inspection.",
              "results": []}
    save_report(path, report)
    failed = False
    stopped = False
    for year in range(args.start_year, args.end_year + 1):
        if stopped:
            row = {"year": year, "status": "not_checked_after_access_error",
                   "capture_records": None, "inventory_complete": False}
        else:
            # Pace uncached requests. The existing collector retains its 30s timeout.
            if not args.cache_only and not cache_path_for(args.url, year, args.limit).exists():
                time.sleep(3)
            row = inspect_year(args.url, year, args.limit, args.cache_only)
            if row["status"] == "request_failed":
                failed = True
            # Stop rather than repeatedly hitting an access denial or rate limit.
            if row.get("http_status") in (403, 429):
                stopped = True
        report["results"].append(row)
        save_report(path, report)
        print(f"{year}: {row['status']} | records={row['capture_records']}"
              + (f" | cache={row['used_cache']}" if row.get("used_cache") is not None else ""))
        if row.get("error"):
            print("  " + row["error"], file=sys.stderr)
    report["run_complete"] = not stopped
    save_report(path, report)
    print(f"Report: {path}")
    print("Discovery samples only; no page content validated or annual captures selected.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
