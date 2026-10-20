"""Narrow, audited cleanup for the inspected Apple 2016 pilot capture only.

Run: python -m part1_stated_values.src.clean_apple_2016
"""
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from bs4 import BeautifulSoup
from part1_stated_values.src.extract_pilot import readable_text

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = "AAPL_20160101124138"
VERSION = "apple_2016_narrow_cleanup_v1"
PROMPT = "Want to search for a job now? Get started"
INCLUSION = "At Apple, we believe inclusion inspires innovation."


def normalize(text):
    """Collapse whitespace for checks while leaving saved wording unchanged."""
    return re.sub(r"\s+", " ", text).strip()


def clean():
    """Verify the archive, remove five inspected elements, and save an audit."""
    data = ROOT / "part1_stated_values/data"
    raw_path = data / "raw/html" / f"{CAPTURE}.html"
    raw = raw_path.read_bytes()
    source = json.loads(raw_path.with_suffix(".json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(raw).hexdigest()
    snapshot = "https://web.archive.org/web/20160101124138/https://www.apple.com/jobs/us/"
    expected = {"sha256": digest, "byte_count": len(raw), "ticker": "AAPL",
                "requested_capture_timestamp": "20160101124138", "target_year": 2016,
                "original_url": "https://www.apple.com/jobs/us/",
                "requested_snapshot_url": snapshot, "final_response_url": snapshot,
                "replay_http_status": 200}
    for key, value in expected.items():
        if source.get(key) != value:
            raise ValueError(f"Source metadata mismatch: {key}")

    soup = BeautifulSoup(raw.decode("utf-8", errors="strict"), "html.parser")
    # Preserve nav: this capture puts substantial descriptions inside it.
    for selector in ("#wm-ipp-base", "#wm-ipp", "#donato", "script", "style",
                     "footer", "iframe", "template"):
        for element in reversed(soup.select(selector)):
            element.decompose()
    roots = soup.select("main.content")
    if len(roots) != 1:
        raise ValueError("Expected exactly one main.content region.")
    root = roots[0]
    before = readable_text(root)
    # Collect every substantive paragraph and heading for preservation checks.
    protected = [normalize(e.get_text(" ", strip=True))
                 for e in root.select("p, h1, h2, h3")
                 if normalize(e.get_text(" ", strip=True)) not in ("", "Learn more")]
    protected.append(INCLUSION)
    if INCLUSION not in normalize(before):
        raise ValueError("Expected inclusion statement is absent before cleanup.")

    removed = []
    banners = root.select("div.cta-banner")
    if len(banners) != 1 or normalize(banners[0].get_text(" ", strip=True)) != PROMPT:
        raise ValueError("Job-search banner differs from inspected structure.")
    banner = banners[0]
    removed.append({"selector": "div.cta-banner", "text": PROMPT,
                    "reason": "Job-search navigation prompt"})
    banner.decompose()

    # Three spans inside linked cards, plus one standalone diversity link.
    # Deleting the parent card links would also delete their descriptions.
    labels = root.select("span.block-link, a.block-link")
    if len(labels) != 4 or any(normalize(e.get_text(" ", strip=True)) != "Learn more"
                               for e in labels):
        raise ValueError("Expected exactly four inspected Learn more labels.")
    for element in labels:
        parent_link = element if element.name == "a" else element.find_parent("a")
        removed.append({"selector": f"{element.name}.block-link", "text": "Learn more",
                        "href": parent_link.get("href") if parent_link else None,
                        "reason": "Navigation label only; surrounding content retained"})
        element.decompose()

    text = readable_text(root)
    preserved = all(phrase in normalize(text) for phrase in protected)
    # This exact transformation check guards against unintended extra deletions.
    expected_text = normalize(normalize(before).replace(PROMPT, "").replace("Learn more", ""))
    only_planned_changes = normalize(text) == expected_text
    if not preserved or not only_planned_changes:
        raise ValueError("Preservation check failed; no output written.")

    output = data / "processed/apple_2016_cleanup"
    output.mkdir(parents=True, exist_ok=True)
    text_path = output / f"{CAPTURE}.txt"
    text_path.write_text(text + "\n", encoding="utf-8")
    report = {
        "capture_id": CAPTURE, "extraction_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_html": raw_path.relative_to(ROOT).as_posix(), "source_sha256": digest,
        "source_snapshot_url": snapshot, "region_selector": "main.content",
        "beautifulsoup_version": version("beautifulsoup4"), "python_version": sys.version,
        "removed_elements": removed, "protected_passages": protected,
        "protected_passages_preserved": preserved, "only_planned_text_changes": only_planned_changes,
        "character_count": len(text), "output_sha256": hashlib.sha256(text_path.read_bytes()).hexdigest(),
        "quality_status": "pending_manual_review", "annual_selection_final": False,
        "limitations": ["Capture-specific rules; not validated on other pages.",
                        "Recruitment descriptions remain to preserve culture language and context.",
                        "No JavaScript or CSS evaluation; archive completeness is not established."]}
    report_path = text_path.with_suffix(".json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Text file: {text_path}")
    print(f"Metadata file: {report_path}")
    print(f"Characters: {len(text)}")
    print("Job-search prompts removed: 1")
    print("Learn more labels removed: 4")
    print(f"Protected passages preserved: {preserved}")
    print(f"Only planned text changes: {only_planned_changes}")
    print("Candidate cleanup saved; manual review is required.")


def main():
    try:
        clean()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Cleanup stopped: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
