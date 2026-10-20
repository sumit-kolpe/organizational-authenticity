"""Audit the six fixed pilot captures without downloading or changing research data.
Run: python -m part1_stated_values.src.validate_pilot
Technical consistency is separate from manual content and methodology review.
"""
import hashlib
import json
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VERSION = 'pilot_validation_v1'
# These are reviewed engineering captures, not final annual selections.
CAPTURES = [
    ('MSFT_20160101214549', 'http://www.microsoft.com/en-us/about', 'microsoft_pilot_cleanup', 'microsoft_pilot_cleanup_v1', 2778),
    ('MSFT_20200102053409', 'https://www.microsoft.com/en-us/about', 'microsoft_pilot_cleanup', 'microsoft_pilot_cleanup_v1', 1264),
    ('MSFT_20240101141329', 'https://www.microsoft.com/en-us/about/', 'microsoft_pilot_cleanup', 'microsoft_pilot_cleanup_v1', 1225),
    ('AAPL_20160101124138', 'https://www.apple.com/jobs/us/', 'apple_2016_cleanup', 'apple_2016_narrow_cleanup_v1', 924),
    ('AAPL_20200115042328', 'https://www.apple.com/jobs/us/about.html', 'apple_2020_cleanup', 'apple_2020_narrow_cleanup_v1', 4906),
    ('AAPL_20240319041941', 'https://www.apple.com/careers/us/', 'extraction_baseline', 'bs4_main_baseline_v3', 1491),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_object(path):
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError(f'Expected a JSON object: {path.name}')
    return value


def audit(spec):
    """Collect all field mismatches where possible; never infer content quality."""
    capture, original, folder, extraction_version, reviewed_length = spec
    ticker, timestamp = capture.split('_')
    raw_path = ROOT / 'part1_stated_values/data/raw/html' / (capture + '.html')
    text_path = ROOT / 'part1_stated_values/data/processed' / folder / (capture + '.txt')
    paths = dict(raw_html=raw_path, download_metadata=raw_path.with_suffix('.json'),
                 clean_text=text_path, extraction_metadata=text_path.with_suffix('.json'))
    errors, warnings = [], []
    result = dict(capture_id=capture, ticker=ticker, year=int(timestamp[:4]),
                  paths={k: p.relative_to(ROOT).as_posix() for k, p in paths.items()},
                  errors=errors, warnings=warnings, manual_review_status='not_assessed_by_script')

    def require(condition, message):
        if not condition:
            errors.append(message)

    try:
        for name, path in paths.items():
            require(path.is_file(), f'Missing {name}: {path.relative_to(ROOT)}')
        if errors:
            result['technical_status'] = 'fail'
            return result
        raw = raw_path.read_bytes()
        source = read_object(paths['download_metadata'])
        meta = read_object(paths['extraction_metadata'])
        # read_text normalizes Windows CRLF for character comparisons.
        text = text_path.read_text(encoding='utf-8').rstrip('\r\n')
        raw_hash = sha(raw)
        text_bytes_hash = sha(text_path.read_bytes())
        snapshot = f'https://web.archive.org/web/{timestamp}/{original}'
        expected = dict(ticker=ticker, requested_capture_timestamp=timestamp,
                        target_year=int(timestamp[:4]), original_url=original,
                        requested_snapshot_url=snapshot, final_response_url=snapshot,
                        replay_http_status=200, byte_count=len(raw), sha256=raw_hash,
                        annual_selection_final=False)
        for field, value in expected.items():
            require(type(source.get(field)) is type(value) and source.get(field) == value,
                    f'Download metadata mismatch: {field}')
        require(bool(raw), 'Empty raw HTML')
        require('text/html' in str(source.get('content_type', '')).lower(), 'Unexpected source MIME type')
        memento = source.get('memento_datetime')
        if memento:
            date = datetime.strptime(timestamp, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
            require(parsedate_to_datetime(memento) == date, 'Memento timestamp mismatch')
        else:
            warnings.append('Memento-Datetime is missing; requested/final URLs alone are weaker date evidence.')
        for field, value in dict(capture_id=capture, extraction_version=extraction_version,
                                 source_sha256=raw_hash, source_snapshot_url=snapshot,
                                 source_html=raw_path.relative_to(ROOT).as_posix(),
                                 character_count=len(text)).items():
            require(type(meta.get(field)) is type(value) and meta.get(field) == value,
                    f'Extraction metadata mismatch: {field}')
        require(bool(text.strip()), 'Empty extracted text')
        require(len(text) == reviewed_length, 'Length differs from reviewed pilot output; inspect changes')
        if meta.get('output_sha256'):
            require(meta['output_sha256'] == text_bytes_hash, 'Clean-text byte checksum mismatch')
        else:
            warnings.append('Extraction metadata lacks output_sha256. Current hash is recorded, but prior text integrity is not established by length alone.')
        if capture.startswith('AAPL_2024'):
            require(meta.get('environment_spot_check_found') is True, 'Environment diagnostic was not true')
        else:
            require(meta.get('only_planned_text_changes') is True, 'Recorded preservation check was not true')
        result.update(character_count=len(text), source_sha256=raw_hash,
                      clean_file_sha256=text_bytes_hash,
                      normalized_newline_text_sha256=sha(text.encode('utf-8')),
                      extraction_version=extraction_version,
                      recorded_quality_status=meta.get('quality_status'),
                      source_snapshot_url=snapshot)
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        errors.append(f'{type(exc).__name__}: {exc}')
    result['technical_status'] = 'fail' if errors else ('pass_with_warnings' if warnings else 'pass')
    return result


def main():
    """Write JSON/Markdown reports and create a review worksheet only if absent."""
    keys = [(spec[0].split('_')[0], spec[0].split('_')[1][:4]) for spec in CAPTURES]
    if len(keys) != 6 or len(set(keys)) != 6:
        raise ValueError('Pilot must contain six unique company-year entries.')
    records = [audit(spec) for spec in CAPTURES]
    failed = sum(r['technical_status'] == 'fail' for r in records)
    warned = sum(r['technical_status'] == 'pass_with_warnings' for r in records)
    report = dict(validation_version=VERSION, run_at_utc=datetime.now(timezone.utc).isoformat(),
                  scope='Six engineering pilot captures only; not 450-observation coverage.',
                  records=records, counts=dict(total=6, failed=failed, warnings=warned, passed=6-failed-warned),
                  step_2_7_status='pending_manual_and_methodological_signoff',
                  limitations=['Technical consistency does not demonstrate complete extraction or complete archives.',
                               'Cleanup was tailored after inspecting the same pilot pages; this is not held-out validation.',
                               'Apple uses recruitment pages; Microsoft uses corporate overview pages.',
                               'URL families and extraction scopes differ across years.',
                               'No adjacent-year change detection has been validated with this 2016/2020/2024 sample.',
                               'Annual snapshot selection and a scalable extraction policy remain unresolved.'])
    output = ROOT / 'part1_stated_values/outputs'
    output.mkdir(parents=True, exist_ok=True)
    (output / 'pilot_validation.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    lines = ['# Pilot validation', '', 'Technical checks only. Manual and methodological sign-off remains pending.', '',
             '| Capture | Technical status | Characters |', '|---|---|---:|']
    for r in records:
        lines.append(f"| {r['capture_id']} | {r['technical_status']} | {r.get('character_count', 'NA')} |")
        print(f"{r['capture_id']} | {r['technical_status']} | characters={r.get('character_count', 'NA')}")
    for r in records:
        if r['errors'] or r['warnings']:
            lines.extend(['', f"## {r['capture_id']}", ''])
            lines.extend('- ERROR: '+e for e in r['errors'])
            lines.extend('- WARNING: '+w for w in r['warnings'])
    lines.extend(['', '## Limits and outstanding decisions', ''])
    lines.extend('- '+item for item in report['limitations'])
    (output / 'pilot_validation.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    review = ROOT / 'docs/pilot_validation_review.md'
    review.parent.mkdir(parents=True, exist_ok=True)
    if not review.exists():
        sections = ['# Pilot content review', '', 'Reviewer: ', 'Review date: ', '',
                    'Complete only after comparing source HTML and current cleaned text. Keep these notes on reruns.',
                    'Record the clean-file hash from pilot_validation.json so the review identifies exact bytes.', '']
        for r in records:
            sections += [f"## {r['capture_id']}", '', 'Reviewed clean-file SHA-256: ',
                         '- [ ] Source region and cleaned text compared.',
                         '- [ ] Substantive statements, headings, attributions, and qualifying notes checked.',
                         '- [ ] Recorded removals inspected; remaining irrelevant text noted.',
                         '- [ ] Missing/truncated/dynamic content concerns recorded.',
                         'Outcome (acceptable for pilot / needs revision / unusable): ', 'Notes: ', '']
        sections += ['## Pilot-wide decisions', '',
                     '- [ ] Document differences in page purpose and cleanup scope before temporal/sector comparisons.',
                     '- [ ] Describe manual review as source inspection assisted by code, not independent blind validation.',
                     '- [ ] Decide what needs refinement before scaling; these capture-specific scripts are prototypes.',
                     'Decision and next actions: ', '']
        review.write_text('\n'.join(sections), encoding='utf-8')
    print(f'Summary: total=6 | passed={6-failed-warned} | warnings={warned} | failed={failed}')
    print(f'Reports: {output}')
    print(f'Manual review worksheet (existing notes preserved): {review}')
    print('Step 2.7 remains pending manual and methodological sign-off.')
    return 1 if failed else 0


if __name__ == '__main__':
    raise SystemExit(main())
