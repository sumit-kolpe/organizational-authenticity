"""Compare the inspected Apple baseline with automatic extraction, offline.

Run from the project root:
    python -m part1_stated_values.src.compare_extraction
This is a one-capture diagnostic, not an extraction accuracy benchmark.
"""

import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from bs4 import BeautifulSoup
import trafilatura


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CAPTURE_ID = "AAPL_20240319041941"
COMPARISON_VERSION = "apple_extraction_comparison_v1"

# Source-inspected examples, fixed before running the automatic extractor.
# These are diagnostic anchors, not a complete gold-standard annotation.
VALUE_STATEMENTS = {
    "accessibility": "Technology is most powerful when everyone can make their mark.",
    "education": "Education is the great equalizer and a powerful source of opportunity for all.",
    "environment": "Our goal is to leave the planet better than we found it.",
    "inclusion": "We’re committed to making Apple more inclusive and the world more just.",
    "privacy": "We design Apple products to protect your privacy and give you control over your information.",
    "racial_equity": "This is a long-term effort to help ensure more positive outcomes for communities of color.",
    "supplier_responsibility": "We believe in a safe, respectful, and supportive workplace for everyone.",
}
CULTURE_STATEMENTS = {
    "culture": "Explore a collaborative culture of inclusion, growth, and originality, supported by resources that make a difference in your life.",
    "employee_quote_ehsan": "We aren’t merely creating products. We’re creating something magical for the person who uses it.",
    "employee_quote_sujin": "At Apple, you can unapologetically be yourself and grow and thrive.",
}
ATTRIBUTIONS = {
    "ehsan": "Ehsan, Engineering Manager",
    "sujin": "Sujin, Apple Store",
}
UNWANTED_MARKERS = {
    "accessibility_link": "Learn about accessibility",
    "education_link": "Learn about Apple and education",
    "environment_link": "Learn about Apple’s environmental efforts",
    "inclusion_link": "Learn about inclusion and diversity",
    "privacy_link": "Learn about privacy",
    "racial_equity_link": "Learn about Apple’s Racial Equity and Justice Initiative",
    "supplier_link": "Learn about supplier responsibility",
    "film_link": "Watch the film",
    "work_link": "Learn about work at Apple",
    "life_link": "Learn about life at Apple",
    "vacancy_link": "Explore all roles",
    "job_list": "Apps and Frameworks, Core Operating Systems",
}


def normalize(text):
    """Ignore whitespace and common punctuation differences for spot checks."""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(str.maketrans({"’": "'", "‘": "'", "–": "-", "—": "-"}))
    return re.sub(r"\s+", " ", text).strip().casefold()


def checks(text, phrases):
    """Return one Boolean per source phrase; False alone is not a quality score."""
    normalized = normalize(text)
    return {name: normalize(phrase) in normalized for name, phrase in phrases.items()}


def describe(text, status):
    """Summarize an output without equating length with quality."""
    return {
        "status": status,
        "character_count": len(text),
        "whitespace_token_count": len(text.split()),
        "normalized_text_sha256": hashlib.sha256(normalize(text).encode("utf-8")).hexdigest(),
        "value_statement_checks": checks(text, VALUE_STATEMENTS),
        "culture_statement_checks": checks(text, CULTURE_STATEMENTS),
        "attribution_checks": checks(text, ATTRIBUTIONS),
        "unwanted_marker_checks": checks(text, UNWANTED_MARKERS),
    }


def compare():
    """Verify inputs, run two fixed settings, and write separate review files."""
    data = PROJECT_ROOT / "part1_stated_values" / "data"
    raw_path = data / "raw" / "html" / f"{CAPTURE_ID}.html"
    baseline_dir = data / "processed" / "extraction_baseline"
    output_dir = data / "processed" / "extraction_comparison"
    raw = raw_path.read_bytes()
    source = json.loads(raw_path.with_suffix(".json").read_text(encoding="utf-8"))
    source_hash = hashlib.sha256(raw).hexdigest()
    if source_hash != source["sha256"]:
        raise ValueError("Raw HTML checksum mismatch.")

    baseline_path = baseline_dir / f"{CAPTURE_ID}.txt"
    baseline_metadata = json.loads(
        baseline_path.with_suffix(".json").read_text(encoding="utf-8")
    )
    baseline = baseline_path.read_text(encoding="utf-8").rstrip("\r\n")
    if (baseline_metadata["source_sha256"] != source_hash
            or baseline_metadata["extraction_version"] != "bs4_main_baseline_v3"
            or baseline_metadata["character_count"] != len(baseline)):
        raise ValueError("Baseline mismatch: rerun extract_pilot before comparing.")

    # Both approaches exclude archive overlays. Do not give Trafilatura the
    # Apple-specific cleaned baseline: it must select content independently.
    soup = BeautifulSoup(raw.decode("utf-8", errors="strict"), "html.parser")
    removed_archive_ids = []
    for element_id in ("wm-ipp-base", "wm-ipp", "donato"):
        for element in soup.find_all(id=element_id):
            element.decompose()
            removed_archive_ids.append(element_id)
    html = str(soup)
    source_text = soup.get_text(" ", strip=True)
    if not all(checks(source_text, {**VALUE_STATEMENTS, **CULTURE_STATEMENTS}).values()):
        raise ValueError("An expected diagnostic phrase is absent from the source.")

    settings = {
        "output_format": "txt",
        "include_comments": False,
        "include_tables": True,
        "include_links": False,
        "include_images": False,
        "include_formatting": False,
        "deduplicate": False,
        "favor_precision": False,
        "fast": False,
        "with_metadata": False,
    }
    results = {"bs4_baseline_v3": describe(baseline, "ok")}
    results["bs4_baseline_v3"]["text_file"] = baseline_path.relative_to(PROJECT_ROOT).as_posix()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, favor_recall in (("trafilatura_balanced", False), ("trafilatura_recall", True)):
        parameters = {**settings, "favor_recall": favor_recall}
        extracted = trafilatura.extract(html, **parameters)
        text = extracted.strip() if extracted else ""
        # An empty result is an extraction failure, never theme absence.
        status = "ok" if text else "empty_extraction"
        path = output_dir / f"{CAPTURE_ID}_{name}.txt"
        path.write_text(text + ("\n" if text else ""), encoding="utf-8")
        results[name] = {**describe(text, status), "parameters": parameters,
                         "text_file": path.relative_to(PROJECT_ROOT).as_posix()}

    report = {
        "comparison_version": COMPARISON_VERSION,
        "diagnostic_design_note": "Expanded navigation and attribution checks after inspecting the first automatic output; exploratory, not held-out validation.",
        "capture_id": CAPTURE_ID,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_sha256": source_hash,
        "source_snapshot_url": source["final_response_url"],
        "source_html": raw_path.relative_to(PROJECT_ROOT).as_posix(),
        "baseline_text_file_sha256": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
        "versions": {name: version(name) for name in ("trafilatura", "beautifulsoup4", "lxml")},
        "python_version": sys.version,
        "removed_archive_ids": removed_archive_ids,
        "diagnostic_phrases": {"values": VALUE_STATEMENTS, "culture": CULTURE_STATEMENTS,
                               "unwanted": UNWANTED_MARKERS, "attributions": ATTRIBUTIONS},
        "methods": results,
        "review_status": "pending_manual_comparison",
        "limitations": [
            "One inspected Apple capture; no cross-company performance claim.",
            "The BS4 baseline has hand-tuned Apple rules; this compares pipelines, not libraries alone.",
            "Phrase checks are incomplete diagnostics, not precision or recall estimates.",
            "A failed phrase check may reflect punctuation or wording boundaries; inspect text.",
            "Neither method executes JavaScript or establishes archive completeness.",
        ],
    }
    report_path = output_dir / f"{CAPTURE_ID}_comparison.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name, result in results.items():
        counts = [sum(result[key].values()) for key in
                  ("value_statement_checks", "culture_statement_checks", "unwanted_marker_checks")]
        print(f"{name}: status={result['status']} | chars={result['character_count']} | "
              f"values={counts[0]}/7 | culture={counts[1]}/3 | "
              f"attributions={sum(result['attribution_checks'].values())}/2 | "
              f"unwanted={counts[2]}/{len(UNWANTED_MARKERS)}")
    print(f"Report: {report_path}")
    print("Phrase checks are diagnostic only; inspect both extracted text files.")


def main():
    try:
        compare()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Comparison stopped: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
