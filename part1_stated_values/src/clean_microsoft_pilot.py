"""Audited cleanup of three inspected Microsoft pilot captures, offline.
Run: python -m part1_stated_values.src.clean_microsoft_pilot
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
VERSION = 'microsoft_pilot_cleanup_v1'
CAPTURES = [
    ('20160101214549', 'http://www.microsoft.com/en-us/about', 'div.pagebody'),
    ('20200102053409', 'https://www.microsoft.com/en-us/about', '[role="main"]'),
    ('20240101141329', 'https://www.microsoft.com/en-us/about/', '[role="main"]'),
]
COMMON_LINKS = ['Explore the world of Microsoft', 'Meet the people of Microsoft',
                'Learn about our values', 'Explore By the Numbers',
                'Learn about our approach', 'Explore Microsoft AI']


def norm(text):
    """Collapse whitespace for preservation checks only."""
    return re.sub(r'\s+', ' ', text).strip()


def save_json(path, value):
    """Save an auditable generated report."""
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def clean_one(timestamp, original, selector, output):
    """Verify a source pair, apply its layout rules, and check every deletion."""
    capture = 'MSFT_' + timestamp
    path = ROOT / 'part1_stated_values/data/raw/html' / (capture + '.html')
    raw = path.read_bytes()
    source = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    digest = hashlib.sha256(raw).hexdigest()
    snapshot = f'https://web.archive.org/web/{timestamp}/{original}'
    expected = dict(sha256=digest, byte_count=len(raw), ticker='MSFT',
                    requested_capture_timestamp=timestamp, target_year=int(timestamp[:4]),
                    original_url=original, requested_snapshot_url=snapshot,
                    final_response_url=snapshot, replay_http_status=200)
    for key, value in expected.items():
        if source.get(key) != value:
            raise ValueError(f'Source metadata mismatch: {key}')
    soup = BeautifulSoup(raw.decode('utf-8', errors='strict'), 'html.parser')
    for exclusion in ('#wm-ipp-base', '#wm-ipp', '#donato', 'script', 'style', 'footer', 'iframe', 'template'):
        for element in reversed(soup.select(exclusion)):
            element.decompose()
    roots = soup.select(selector)
    if len(roots) != 1:
        raise ValueError(f'Expected exactly one {selector}')
    root = roots[0]
    before = readable_text(root)
    removed = []

    def remove(element, reason):
        """Record the exact visible text and HTML selector context before removal."""
        removed.append(dict(tag=element.name, classes=element.get('class', []),
                            text=readable_text(element), href=element.get('href'), reason=reason))
        element.decompose()

    if not timestamp.startswith('2016'):
        contacts = [e for e in root.select('div.m-content-placement-item')
                    if e.find('h2') and norm(e.find('h2').get_text()) == 'Contact us']
        expected_contact = 'Contact us Get in touch. We’re here to help. Get the support you need'
        if len(contacts) != 1 or norm(readable_text(contacts[0])) != expected_contact:
            raise ValueError('Contact block differs from inspected source.')
        remove(contacts[0], 'Contact/support navigation block')
        social = root.select('section.m-social.f-follow')
        if len(social) != 1 or norm(readable_text(social[0])) != 'Follow Microsoft':
            raise ValueError('Social-follow block differs from inspected source.')
        remove(social[0], 'Social-follow navigation')
        story_link = 'Check out Story Labs' if timestamp.startswith('2020') else 'View their stories'
        labels = COMMON_LINKS + [story_link]
        links = root.select('a.c-call-to-action')
        if len(links) != 7 or sorted(norm(a.get_text(' ', strip=True)) for a in links) != sorted(labels):
            raise ValueError('Call-to-action labels differ from inspected source.')
        for link in links:
            remove(link, 'Standalone call-to-action label')
    # In 2016, preserve all headings and descriptions, including directory content.
    text = readable_text(root)
    expected_text = norm(before)
    for item in removed:
        fragment = norm(item['text'])
        if not fragment or expected_text.count(fragment) != 1:
            raise ValueError('Removed text is not uniquely traceable in the region.')
        expected_text = norm(expected_text.replace(fragment, '', 1))
    if norm(text) != expected_text or not text:
        raise ValueError('Unexpected text change; output rejected.')
    text_path = output / (capture + '.txt')
    text_path.write_text(text + '\n', encoding='utf-8')
    report = dict(capture_id=capture, extraction_version=VERSION,
                  created_at_utc=datetime.now(timezone.utc).isoformat(),
                  source_html=path.relative_to(ROOT).as_posix(), source_sha256=digest,
                  source_snapshot_url=snapshot, region_selector=selector,
                  beautifulsoup_version=version('beautifulsoup4'), python_version=sys.version,
                  removed_elements=removed, only_planned_text_changes=True,
                  character_count=len(text), output_sha256=hashlib.sha256(text_path.read_bytes()).hexdigest(),
                  quality_status='pending_manual_review', annual_selection_final=False,
                  limitations=['Capture-specific rules, not a general annual extractor.',
                               '2016 retains directory descriptions; later layouts exclude an inspected contact block. This scope difference must be considered in comparisons.',
                               'Some retained descriptions mix promotion, navigation, and value language.',
                               'No JavaScript or CSS evaluation; archive completeness remains unverified.'])
    save_json(output / (capture + '.json'), report)
    print(f'{capture} | characters={len(text)} | removed_elements={len(removed)} | preservation=True')
    return report


def main():
    """Continue other captures after a failure and record current outcomes."""
    output = ROOT / 'part1_stated_values/data/processed/microsoft_pilot_cleanup'
    output.mkdir(parents=True, exist_ok=True)
    reports, failures = [], 0
    for timestamp, original, selector in CAPTURES:
        capture = 'MSFT_' + timestamp
        # Clear only outputs owned by this script to prevent stale success files.
        for ext in ('.txt', '.json'):
            (output / (capture + ext)).unlink(missing_ok=True)
        try:
            reports.append(clean_one(timestamp, original, selector, output))
        except Exception as exc:
            failures += 1
            failure = dict(capture_id=capture, status='processing_error', error=f'{type(exc).__name__}: {exc}')
            save_json(output / (capture + '.json'), failure)
            reports.append(failure)
            print(f'{capture} | processing_error: {exc}')
    save_json(output / 'inventory.json', dict(version=VERSION, records=reports))
    print(f'Output folder: {output}')
    print('Candidate cleanup saved; manual review is required.')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
