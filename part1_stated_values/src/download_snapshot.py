"""Download one inspected Microsoft snapshot and preserve provenance."""

import hashlib
import json
import sys
import argparse
import re
from urllib.parse import urlsplit
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import (
    HTTPRedirectHandler,
    Request,
    build_opener,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = (
    PROJECT_ROOT / "part1_stated_values" / "data" / "raw" / "html"
)

USER_AGENT = "OrganizationalAuthenticityResearch/0.1"
MAX_BYTES = 10 * 1024 * 1024  # A protective 10 MiB pilot limit.


class NoRedirects(HTTPRedirectHandler):
    """Reject redirects instead of silently changing the capture."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def checksum(content):
    """Return a SHA-256 fingerprint of the downloaded bytes."""
    return hashlib.sha256(content).hexdigest()


def save_atomic(path, content):
    """Replace a destination only after its temporary file is written."""
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_bytes(content)
    temporary_path.replace(path)


def download_snapshot(ticker, timestamp, original_url):
    """Download an inspected capture, or verify and reuse its saved files."""
    # Validate inputs before constructing URLs or filesystem paths.
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9.-]{0,19}", ticker):
        raise ValueError("ticker must contain uppercase letters, digits, dots or hyphens.")

    if not re.fullmatch(r"[0-9]{14}", timestamp):
        raise ValueError("timestamp must contain exactly 14 digits.")

    capture_date = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    if not 2016 <= capture_date.year <= 2024:
        raise ValueError("Capture year must be within 2016–2024.")

    parsed = urlsplit(original_url)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Provide a full original HTTP or HTTPS URL.")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Original URL cannot contain credentials or a fragment.")
    if any(character.isspace() for character in original_url):
        raise ValueError("Original URL cannot contain whitespace.")

    snapshot_url = (
        f"https://web.archive.org/web/{timestamp}/{original_url}"
    )
    stem = f"{ticker}_{timestamp}"
    html_path = OUTPUT_DIR / f"{stem}.html"
    metadata_path = OUTPUT_DIR / f"{stem}.json"

    # A complete cache consists of both HTML and its metadata.
    if html_path.exists() or metadata_path.exists():
        if not (html_path.exists() and metadata_path.exists()):
            raise ValueError(
                "Incomplete saved file pair. Stop and inspect the files "
                "before downloading again."
            )

        metadata = json.loads(
            metadata_path.read_text(encoding="utf-8")
        )
        if metadata["requested_snapshot_url"] != snapshot_url:
            raise ValueError("Saved metadata belongs to a different URL.")

        content = html_path.read_bytes()
        if checksum(content) != metadata["sha256"]:
            raise ValueError("Saved HTML does not match its checksum.")
        if len(content) != metadata["byte_count"]:
            raise ValueError("Saved HTML byte count does not match.")

        print("Source: existing cache; checksum verified")
        return html_path, metadata_path, len(content)

    request = Request(
        snapshot_url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Encoding": "identity",
        },
    )
    opener = build_opener(NoRedirects())

    with opener.open(request, timeout=30) as response:
        if response.status != 200:
            raise ValueError(
                f"Unexpected replay HTTP status: {response.status}"
            )

        final_url = response.geturl()
        if final_url != snapshot_url:
            raise ValueError(f"Unexpected final URL: {final_url}")

        media_type = response.headers.get_content_type()
        if media_type not in ("text/html", "application/xhtml+xml"):
            raise ValueError(f"Unexpected content type: {media_type}")

        encoding = response.headers.get("Content-Encoding", "identity")
        if encoding.lower() != "identity":
            raise ValueError(f"Unexpected content encoding: {encoding}")

        # Read one extra byte so oversized responses are detected.
        content = response.read(MAX_BYTES + 1)
        if not content:
            raise ValueError("The replay returned an empty body.")
        if len(content) > MAX_BYTES:
            raise ValueError("The response exceeds the pilot size limit.")

        content_type = response.headers.get("Content-Type")
        memento_datetime = response.headers.get("Memento-Datetime")
        replay_status = response.status

    metadata = {
        "schema_version": 1,
        "ticker": ticker,
        "target_year": capture_date.year,
        "requested_capture_timestamp": timestamp,
        "original_url": original_url,
        "requested_snapshot_url": snapshot_url,
        "final_response_url": final_url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "replay_http_status": replay_status,
        "content_type": content_type,
        "memento_datetime": memento_datetime,
        "byte_count": len(content),
        "sha256": checksum(content),
        "user_agent": USER_AGENT,
        "retrieval_mode": "ordinary_wayback_replay",
        "archive_interface_may_be_present": True,
        "selection_basis": "manually_inspected_pilot_capture",
        "content_quality_status": "pending_inspection",
        "annual_selection_final": False,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    save_atomic(html_path, content)
    save_atomic(
        metadata_path,
        (json.dumps(metadata, indent=2) + "\n").encode("utf-8"),
    )

    print("Source: Wayback replay")
    return html_path, metadata_path, len(content)


def main():
    """Read capture settings and report download results."""
    parser = argparse.ArgumentParser(
        description="Download one manually inspected Wayback capture."
    )
    parser.add_argument("--ticker", required=True)
    parser.add_argument("--timestamp", required=True)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()

    try:
        html_path, metadata_path, byte_count = download_snapshot(
            ticker=args.ticker,
            timestamp=args.timestamp,
            original_url=args.url,
        )
    except HTTPError as exc:
        print(
            f"Download stopped: HTTP {exc.code} {exc.reason}",
            file=sys.stderr,
        )
        if 300 <= exc.code < 400:
            print(
                f"Redirect destination: {exc.headers.get('Location')}",
                file=sys.stderr,
            )
            print(
                "This prototype does not follow redirects.",
                file=sys.stderr,
            )
        return 1
    except (URLError, TimeoutError, OSError, ValueError, KeyError) as exc:
        print(f"Download stopped: {exc}", file=sys.stderr)
        return 1

    print(f"HTML file: {html_path}")
    print(f"Metadata file: {metadata_path}")
    print(f"Bytes: {byte_count}")
    print("Download checks passed; content quality is not yet verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())