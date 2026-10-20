"""Extract two review candidates for the five remaining pilot captures.

Offline, deliberately conservative, and not approved for annual production.
Run: python -m part1_stated_values.src.extract_remaining_pilot
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from importlib.metadata import version
from pathlib import Path

from bs4 import BeautifulSoup
import trafilatura

# Reuse only the text walker; importing this module does not run extract().
from part1_stated_values.src.extract_pilot import readable_text

ROOT = Path(__file__).resolve().parents[2]
VERSION = "remaining_pilot_candidates_v1"
# Selectors and diagnostic excerpts were inspected in these exact captures.
# They are not rules for all years or all pages on these domains.
CAPTURES = [
    ("MSFT_20160101214549", "http://www.microsoft.com/en-us/about", "div.pagebody",
     ["Empower every person and every organization on the planet to achieve more",
      "Microsoft believes that diversity enriches our performance and products"]),
    ("MSFT_20200102053409", "https://www.microsoft.com/en-us/about", '[role="main"]',
     ["Our mission is to empower every person and organization on the planet to achieve more.",
      "We believe technology is a powerful force for good"]),
    ("MSFT_20240101141329", "https://www.microsoft.com/en-us/about/", '[role="main"]',
     ["Our mission is to empower every person and every organization on the planet to achieve more.",
      "Microsoft will be carbon negative by 2030."]),
    ("AAPL_20160101124138", "https://www.apple.com/jobs/us/", "main",
     ["It’s the diversity of those people and their ideas that inspires the innovation",
      "We’ve created a whole different kind of store: creative, collaborative, and fun."]),
    ("AAPL_20200115042328", "https://www.apple.com/jobs/us/about.html", "main",
     ["help safeguard the human rights of the people who make our products",
      "Apple benefits help further the well-being of our employees and their families"]),
]
SETTINGS = dict(output_format="txt", include_comments=False, include_tables=True,
                include_images=False, include_links=False, include_formatting=False,
                deduplicate=False, favor_precision=False, favor_recall=False,
                fast=False, with_metadata=False)


def normalized(text):
    """Normalize whitespace for diagnostic phrase checks, not stored text."""
    return re.sub(r"\s+", " ", text).strip().casefold()


def write_json(path, value):
    """Replace one generated JSON file using a temporary sibling file."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def extract_one(capture_id, original_url, selector, phrases, output):
    """Verify one source pair and save independent candidate texts."""
    ticker, timestamp = capture_id.split("_")
    raw_path = ROOT / "part1_stated_values/data/raw/html" / f"{capture_id}.html"
    raw = raw_path.read_bytes()
    source = json.loads(raw_path.with_suffix(".json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(raw).hexdigest()
    expected_url = f"https://web.archive.org/web/{timestamp}/{original_url}"
    expected = {"ticker": ticker, "requested_capture_timestamp": timestamp,
                "target_year": int(timestamp[:4]), "original_url": original_url,
                "requested_snapshot_url": expected_url, "final_response_url": expected_url,
                "sha256": digest, "byte_count": len(raw), "replay_http_status": 200}
    for key, value in expected.items():
        if source.get(key) != value:
            raise ValueError(f"Source metadata mismatch: {key}")
    if "text/html" not in source.get("content_type", "").lower():
        raise ValueError("Source Content-Type is not HTML.")
    warnings = []
    if source.get("memento_datetime"):
        observed = parsedate_to_datetime(source["memento_datetime"])
        expected_date = datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        if observed != expected_date:
            raise ValueError("Memento date differs from requested capture.")
    else:
        warnings.append("missing_memento_datetime")

    soup = BeautifulSoup(raw.decode("utf-8", errors="strict"), "html.parser")
    removed_ids = []
    for element_id in ("wm-ipp-base", "wm-ipp", "donato"):
        for element in soup.find_all(id=element_id):
            element.decompose()
            removed_ids.append(element_id)
    # Automatic extraction receives the whole page minus archive overlays.
    automatic_html = str(soup)

    removed_tags = {}
    # Keep nav inside the selected region: Apple 2016 embeds culture text there.
    for tag in ("script", "style", "footer", "iframe", "template"):
        elements = soup.find_all(tag)
        removed_tags[tag] = len(elements)
        for element in reversed(elements):
            element.decompose()
    regions = soup.select(selector)
    if len(regions) != 1:
        raise ValueError(f"Expected one region for {selector}; found {len(regions)}")
    region = regions[0]
    if not all(normalized(p) in normalized(region.get_text(" ", strip=True)) for p in phrases):
        raise ValueError("An inspected diagnostic phrase is absent from the source region.")

    report = {"capture_id": capture_id, "version": VERSION,
              "created_at_utc": datetime.now(timezone.utc).isoformat(),
              "source_sha256": digest, "source_snapshot_url": expected_url,
              "source_html": raw_path.relative_to(ROOT).as_posix(),
              "region_selector": selector, "removed_archive_ids": removed_ids,
              "removed_tag_counts_for_region": removed_tags,
              "diagnostic_phrases": phrases, "warnings": warnings,
              "annual_selection_final": False, "quality_status": "pending_manual_review",
              "versions": {p: version(p) for p in ("beautifulsoup4", "trafilatura", "lxml")},
              "python_version": sys.version, "automatic_settings": SETTINGS,
              "methods": {},
              "limitations": ["Only two exploratory source-inspected phrases per page; not accuracy estimates.",
                              "Main-region candidate deliberately retains links and recruitment content.",
                              "Automatic extraction can omit meaningful text or retain boilerplate.",
                              "No JavaScript execution or guarantee of complete historical page content."]}
    # A failure of one method does not discard the other method's evidence.
    methods = {"bs4_region": lambda: readable_text(region),
               "trafilatura_balanced": lambda: trafilatura.extract(automatic_html, **SETTINGS)}
    for name, run in methods.items():
        path = output / f"{capture_id}_{name}.txt"
        try:
            text = (run() or "").strip()
            found = [normalized(p) in normalized(text) for p in phrases] if text else None
            status = "candidate" if text else "empty_extraction"
            if found is not None and not all(found):
                status = "review_phrase_missing"
            path.write_text(text + ("\n" if text else ""), encoding="utf-8")
            report["methods"][name] = {
                "status": status, "character_count": len(text), "phrase_checks": found,
                "text_file": path.relative_to(ROOT).as_posix(),
                "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        except Exception as exc:
            # Continue the small batch; record unexpected parser errors too.
            path.unlink(missing_ok=True)
            report["methods"][name] = {"status": "processing_error", "phrase_checks": None,
                                       "error": f"{type(exc).__name__}: {exc}"}
    write_json(output / f"{capture_id}.json", report)
    return report


def main():
    """Process all five pairs and retain a current inventory, including failures."""
    output = ROOT / "part1_stated_values/data/processed/remaining_pilot_candidates"
    output.mkdir(parents=True, exist_ok=True)
    records = []
    failures = 0
    for capture_id, url, selector, phrases in CAPTURES:
        # Remove only this script's old outputs to avoid stale success on failure.
        for suffix in (".json", "_bs4_region.txt", "_trafilatura_balanced.txt"):
            (output / f"{capture_id}{suffix}").unlink(missing_ok=True)
        try:
            report = extract_one(capture_id, url, selector, phrases, output)
            parts = []
            for name, result in report["methods"].items():
                found = result["phrase_checks"]
                count = f"{sum(found)}/{len(found)}" if found is not None else "NA"
                parts.append(f"{name}: {result['status']}, checks={count}")
                failures += result["status"] in ("processing_error", "empty_extraction")
            print(capture_id + " | " + " | ".join(parts))
            records.append(report)
        except Exception as exc:
            failures += 1
            record = {"capture_id": capture_id, "status": "processing_error",
                      "error": f"{type(exc).__name__}: {exc}"}
            write_json(output / f"{capture_id}.json", record)
            records.append(record)
            print(f"{capture_id} | processing_error: {exc}")
    write_json(output / "inventory.json", {"version": VERSION, "records": records})
    print(f"Output folder: {output}")
    print("All candidate texts require manual review; no final clean dataset was created.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
