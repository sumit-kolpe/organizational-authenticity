"""Narrow, audited cleanup for the inspected Apple 2020 pilot capture only.

Run: python -m part1_stated_values.src.clean_apple_2020
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
CAPTURE = "AAPL_20200115042328"
VERSION = "apple_2020_narrow_cleanup_v1"

INCLUSION = "Different together. At Apple, we’re not all the same. And that’s our greatest strength."


def normalize(text):
    """Collapse whitespace for checks while leaving saved wording unchanged."""
    return re.sub(r"\s+", " ", text).strip()


def clean():
    """Verify the archive, apply inspected cleanup rules, and save an audit."""
    data = ROOT / "part1_stated_values/data"
    raw_path = data / "raw/html" / f"{CAPTURE}.html"
    raw = raw_path.read_bytes()
    source = json.loads(raw_path.with_suffix(".json").read_text(encoding="utf-8"))
    digest = hashlib.sha256(raw).hexdigest()
    snapshot = "https://web.archive.org/web/20200115042328/https://www.apple.com/jobs/us/about.html"
    expected = {"sha256": digest, "byte_count": len(raw), "ticker": "AAPL",
                "requested_capture_timestamp": "20200115042328", "target_year": 2020,
                "original_url": "https://www.apple.com/jobs/us/about.html",
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
    roots = soup.select("main#main")
    if len(roots) != 1:
        raise ValueError("Expected exactly one main#main region.")
    root = roots[0]
    before = readable_text(root)
    # Capture-specific structure checks happen before removing anything.
    navs = root.select('nav.dotnav[aria-label="Gallery pager navigation"]')
    if len(navs) != 1:
        raise ValueError("Expected exactly one gallery pager.")
    pager = navs[0]
    labels = [normalize(e.get_text(" ", strip=True)) for e in pager.select("a.dotnav-item")]
    captions = [normalize(e.get_text(" ", strip=True))
                for e in root.select("#slides-2 .figcaption-wrapper")]
    if len(labels) != 6 or labels != captions or len(set(labels)) != 6:
        raise ValueError("Gallery pager labels do not match six unique retained captions.")
    if normalize(pager.get_text(" ", strip=True)) != " ".join(labels):
        raise ValueError("Gallery pager contains additional unexpected text.")

    links = root.select(".pre-footer a")
    if len(links) != 2 or any(normalize(e.get_text(" ", strip=True)) != "Learn more" for e in links):
        raise ValueError("Expected exactly two pre-footer Learn more links.")
    boundaries = [e for e in root.select("strong.pre-footer__mobile-block")
                  if e.get_text() == "The people at Apple create more than products."]
    if len(boundaries) != 1:
        raise ValueError("Expected exactly one inspected sentence boundary.")
    boundary = boundaries[0]
    if (boundary.get_text() != "The people at Apple create more than products."
            or not str(boundary.next_sibling).startswith("They create jobs")):
        raise ValueError("Sentence boundary differs from inspected source.")

    # Keep paragraphs/headings, but exclude CTA labels from preservation targets.
    protected = [normalize(readable_text(e)).replace(" Learn more", "").replace("products.They", "products. They")
                 for e in root.select("p, h1, h2, h3")
                 if normalize(e.get_text(" ", strip=True)) not in ("", "Learn more")]
    protected += [INCLUSION, "Johny Srouji", "Lisa Jackson", "Deirdre O’Brien",
                  "Senior Vice President of Hardware Technologies",
                  "Vice President of Environment, Policy, and Social Initiatives",
                  "Senior Vice President of Retail + People",
                  "800+ Engineers and specialists collaborating solely on camera technologies.",
                  "* Apple benefits programs vary by country and are subject to eligibility requirements."]
    removed = [{"selector": "nav.dotnav", "text": normalize(pager.get_text(" ", strip=True)),
                "reason": "Duplicate gallery navigation captions; matching slide captions retained"}]
    pager.decompose()
    for link in links:
        removed.append({"selector": ".pre-footer a", "text": "Learn more", "href": link.get("href"),
                        "reason": "Navigation label only"})
        link.decompose()
    boundary.insert_after(" ")

    text = readable_text(root)
    preserved = all(phrase in normalize(text) for phrase in protected)
    # Check the entire normalized region against only the documented edits.
    expected_text = normalize(before)
    for label in labels:
        if expected_text.count(label) != 2:
            raise ValueError("Expected two copies of each gallery caption before cleanup.")
        expected_text = expected_text.replace(label, "", 1)
    expected_text = normalize(expected_text.replace("Learn more", "").replace("products.They", "products. They"))
    only_planned_changes = normalize(text) == expected_text
    captions_once = all(normalize(text).count(label) == 1 for label in labels)
    if not preserved or not only_planned_changes or not captions_once:
        raise ValueError("Preservation check failed; no output written.")

    output = data / "processed/apple_2020_cleanup"
    output.mkdir(parents=True, exist_ok=True)
    text_path = output / f"{CAPTURE}.txt"
    text_path.write_text(text + "\n", encoding="utf-8")
    report = {
        "capture_id": CAPTURE, "extraction_version": VERSION,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_html": raw_path.relative_to(ROOT).as_posix(), "source_sha256": digest,
        "source_snapshot_url": snapshot, "region_selector": "main#main",
        "beautifulsoup_version": version("beautifulsoup4"), "python_version": sys.version,
        "removed_elements": removed,
        "spacing_correction": "Inserted space at inspected strong/text boundary: products.They",
        "gallery_captions_retained_once": captions_once, "protected_passages": protected,
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
    print("Duplicate gallery navigation blocks removed: 1")
    print("Learn more labels removed: 2")
    print("Sentence boundaries repaired: 1")
    print(f"Gallery captions retained once: {captions_once}")
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
