"""Extract a reviewable text baseline from the Apple 2024 pilot page."""

import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import bs4
from bs4 import BeautifulSoup, Comment, NavigableString, Tag


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = (
    PROJECT_ROOT
    / "part1_stated_values"
    / "data"
    / "raw"
    / "html"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "part1_stated_values"
    / "data"
    / "processed"
    / "extraction_baseline"
)

CAPTURE_ID = "AAPL_20240319041941"
EXTRACTION_VERSION = "bs4_main_baseline_v3"

# Block boundaries prevent headings and paragraphs from running together.
BLOCK_TAGS = {
    "address",
    "article",
    "aside",
    "blockquote",
    "dd",
    "div",
    "dl",
    "dt",
    "figcaption",
    "figure",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "li",
    "main",
    "ol",
    "p",
    "section",
    "table",
    "tr",
    "ul",
}


def readable_text(root):
    """Walk the HTML once, preserving text order and block boundaries."""
    pieces = []

    def visit(node):
        """Collect text from one node and its children."""
        if isinstance(node, Comment):
            return

        if isinstance(node, NavigableString):
            # Normalize source whitespace without splitting inline text.
            pieces.append(re.sub(r"\s+", " ", str(node)))
            return

        if not isinstance(node, Tag):
            return

        if node.name == "br":
            pieces.append("\n")
            return

        is_block = node.name in BLOCK_TAGS

        if is_block:
            pieces.append("\n")

        for child in node.children:
            visit(child)

        if is_block:
            pieces.append("\n")
        elif node.name in {"td", "th"}:
            pieces.append(" ")

    visit(root)

    # Keep separate nonempty blocks, with normalized whitespace.
    lines = []

    for line in "".join(pieces).splitlines():
        normalized = re.sub(r"\s+", " ", line).strip()
        if normalized:
            lines.append(normalized)

    return "\n\n".join(lines)


def extract():
    """Verify the source, extract main text, and save review outputs."""
    html_path = RAW_DIR / f"{CAPTURE_ID}.html"
    metadata_path = RAW_DIR / f"{CAPTURE_ID}.json"

    # Check the raw file before processing it.
    raw = html_path.read_bytes()
    source = json.loads(metadata_path.read_text(encoding="utf-8"))

    if not isinstance(source, dict):
        raise ValueError("Source metadata must be a JSON object.")

    source_hash = hashlib.sha256(raw).hexdigest()

    if source_hash != source["sha256"]:
        raise ValueError("Raw HTML checksum mismatch; extraction stopped.")

    # This specific capture's recorded Content-Type specifies UTF-8.
    html = raw.decode("utf-8", errors="strict")
    soup = BeautifulSoup(html, "html.parser")

    # Remove known archive containers from the in-memory HTML tree.
    removed_archive_ids = []

    for element_id in ("wm-ipp-base", "wm-ipp", "donato"):
        for element in soup.find_all(id=element_id):
            element.decompose()
            removed_archive_ids.append(element_id)

    # These baseline exclusions remain subject to source comparison.
    removal_counts = {}

    for tag_name in (
        "script",
        "style",
        "nav",
        "footer",
        "iframe",
        "template",
    ):
        elements = soup.find_all(tag_name)
        removal_counts[tag_name] = len(elements)

        # Remove nested elements before their parents.
        for element in reversed(elements):
            element.decompose()

    # Prefer an explicit <main>; otherwise try role="main".
    roots = soup.find_all("main")
    root_method = "main"

    if not roots:
        roots = soup.find_all(attrs={"role": "main"})
        root_method = "role=main"

    if len(roots) != 1:
        raise ValueError(
            f"Expected one main-content region; found {len(roots)}. "
            "Manual review is required."
        )

    # Assign root before searching within it.
    root = roots[0]

    # Verified on this Apple capture only. Keep removed text for audit.
    removed_content_blocks = []
    for selector, reason in (
        ("article.difference-carousel", "Job-category navigation carousel"),
        ("aside.landing-page-footer", "Apple Vision Pro vacancy promotion"),
    ):
        blocks = root.select(selector)
        if len(blocks) != 1:
            raise ValueError(f"Expected one {selector}; found {len(blocks)}.")
        block = blocks[0]
        removed_content_blocks.append({
            "selector": selector,
            "reason": reason,
            "text": readable_text(block),
        })
        block.decompose()

    # Remove only inspected navigation types with matching labels.
    removed_navigation_links = []
    for link in root.select(
        "a.more.callout-anchor, a.more.text-items__link, "
        "a.more.learn-more-link, a.video-cta"
    ):
        label = " ".join(link.get_text(" ", strip=True).split())
        if (label.casefold().startswith("learn about ")
                or label.casefold() == "watch the film"):
            removed_navigation_links.append({
                "text": label,
                "href": link.get("href"),
            })
            link.decompose()

    text = readable_text(root)

    if not text:
        raise ValueError("Main-content extraction produced no text.")

    headings = [
        heading.get_text(" ", strip=True)
        for heading in root.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6"]
        )
    ]

    # A diagnostic check, not a completeness or quality assessment.
    spot_check = "our goal is to leave the planet better"
    normalized_text = " ".join(text.lower().split())
    spot_check_found = spot_check in normalized_text

    extraction_metadata = {
        "capture_id": CAPTURE_ID,
        "extraction_version": EXTRACTION_VERSION,
        "extracted_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_html": html_path.relative_to(PROJECT_ROOT).as_posix(),
        "source_sha256": source_hash,
        "source_snapshot_url": source["final_response_url"],
        "beautifulsoup_version": bs4.__version__,
        "python_version": sys.version,
        "parser": "html.parser",
        "decoding": "utf-8-strict",
        "main_region_selection": root_method,
        "removed_archive_ids": removed_archive_ids,
        "removed_element_counts": removal_counts,
        "removed_navigation_links": removed_navigation_links,
        "removed_content_blocks": removed_content_blocks,
        "headings": headings,
        "character_count": len(text),
        "whitespace_token_count": len(text.split()),
        "environment_spot_check_found": spot_check_found,
        "quality_status": "pending_manual_review",
        "limitations": [
            "Does not execute JavaScript or evaluate CSS visibility.",
            "Navigation-link cleanup is specific to this Apple pilot.",
            "Recruitment framing remains in retained culture statements.",
            "Two inspected job-listing blocks are excluded from this baseline.",
            "Completeness and relevance have not been established.",
        ],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    text_path = OUTPUT_DIR / f"{CAPTURE_ID}.txt"
    report_path = OUTPUT_DIR / f"{CAPTURE_ID}.json"

    text_path.write_text(text + "\n", encoding="utf-8")
    report_path.write_text(
        json.dumps(
            extraction_metadata,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

    print(f"Text file: {text_path}")
    print(f"Extraction metadata: {report_path}")
    print(f"Characters: {len(text)}")
    print(f"Navigation links removed: {len(removed_navigation_links)}")
    print(f"Job-listing blocks removed: {len(removed_content_blocks)}")
    print(f"Environment spot-check found: {spot_check_found}")
    print("Candidate extraction saved; manual review is required.")


def main():
    """Report extraction errors and return an appropriate exit code."""
    try:
        extract()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Extraction stopped: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())