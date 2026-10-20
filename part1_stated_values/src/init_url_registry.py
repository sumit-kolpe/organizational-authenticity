"""Initialize a research URL registry from existing metadata and pilot evidence.
Run: python -m part1_stated_values.src.init_url_registry
No network requests. Existing registry files are never overwritten.
"""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
SECTORS = {
    'Technology': 'MSFT AAPL NVDA GOOGL META AVGO CRM ORCL IBM INTC'.split(),
    'Financials': 'BRK.B JPM BAC WFC GS MS BLK SCHW AXP C'.split(),
    'Healthcare': 'LLY UNH JNJ ABBV MRK TMO ABT PFE MDT BMY'.split(),
    'Consumer Discretionary': 'AMZN TSLA HD MCD NKE SBUX TGT LOW TJX F'.split(),
    'Energy': 'XOM CVX COP EOG SLB MPC PSX VLO OXY HAL'.split(),
}
PILOT_URLS = {
    'MSFT_20160101214549': 'http://www.microsoft.com/en-us/about',
    'MSFT_20200102053409': 'https://www.microsoft.com/en-us/about',
    'MSFT_20240101141329': 'https://www.microsoft.com/en-us/about/',
    'AAPL_20160101124138': 'https://www.apple.com/jobs/us/',
    'AAPL_20200115042328': 'https://www.apple.com/jobs/us/about.html',
    'AAPL_20240319041941': 'https://www.apple.com/careers/us/',
}
POLICY = '''# Page-selection policy — provisional v1

## Scope
Use the assignment's exact 50-company sample and 2016–2024 window.
Assignment sector labels are retained; they are not a newly verified GICS classification.
This registry documents candidate pages and evidence; it does not select annual snapshots.

## Selection procedure
1. Locate official organizational identity pages (values, mission, purpose, or substantive About pages).
2. Prefer organizational coverage over products, investor news, or vacancies. Assess actual content, not URL names alone.
3. Record competing candidates, their purpose, scope, and reasons for preferring or rejecting them.
4. Verify historical captures and their identity/content before claiming historical suitability. A current official page is only a discovery lead for earlier years.
5. Prefer consistent page purpose across years. Record page-family transitions; do not silently substitute a recruitment page for a values page.
6. Use recruitment pages only as explicit provisional alternatives when they contain substantive organizational values; investigate broader identity pages before final selection.
7. Mark a company mapping reviewed only after documenting candidate research, historical evidence, scope limitations, and a selection rationale. A reviewed mapping can still have missing years.

## Evidence rules
Keep HTTP/HTTPS and trailing-slash variants distinct until archive evidence supports equivalence.
An observed timestamp establishes one capture, not continuous availability between dates.
Keep effective_from/effective_to null unless supported by explicit evidence; null means unknown.
Do not use low keyword counts to reject a page: that would select sources based on the outcome being measured.
Do not follow external links or combine several pages into one observation without documenting a revised unit-of-analysis policy.
Retain rejected candidates and their reasons as the registry grows.

## Pilot evidence
The six seed entries come from inspected pilot captures. Microsoft uses corporate-overview pages; Apple uses recruitment pages containing values language.
They remain provisional candidates, with selected_for_annual_collection=false.
An engineering-quality extraction is not a final page-selection decision.

## Completion criteria for Step 3.1
All 50 companies must have documented candidate research and an explicit outcome: reviewed mapping, unresolved case, or unavailable after documented searches.
Record evidence URLs/timestamps and historical-domain/URL transitions where supported.
Unresolved and unavailable cases must remain visible, not be filled with guessed URLs.
Annual CDX discovery, snapshot selection, and collection belong to later steps.

## Registry fields
- companies: one tracking record per assignment company; pilot_evidence_only or pending_research at initialization.
- candidates: one record per exact candidate URL; multiple candidates per company are allowed.
- page_type/page_family: source-purpose labels, not thematic classifications.
- historical_evidence: observed captures, their raw hash, and traceable pilot artifacts.
- effective_from/effective_to: unknown unless evidence establishes an interval.
- selection_status/selection_rationale: explicit provisional or reviewed selection decision.
- alternative_candidates_reviewed: initially false; the seed is not a complete discovery log.
- selected_for_annual_collection: initially false for every candidate.

## Next research batch
Revisit Microsoft and Apple alternatives first to resolve the pilot's source-purpose mismatch. Then research remaining companies in small batches, recording unsuccessful searches too.
'''


def read_companies(path):
    """Validate the exact assignment tickers and sector mapping; preserve names."""
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not {'ticker', 'company_name', 'sector'}.issubset(reader.fieldnames or []):
            raise ValueError('companies.csv requires ticker, company_name, sector headers.')
        rows = [{k: (r.get(k) or '').strip() for k in ('ticker', 'company_name', 'sector')} for r in reader]
    expected = {ticker: sector for sector, tickers in SECTORS.items() for ticker in tickers}
    if len(rows) != 50 or {r['ticker'] for r in rows} != set(expected):
        raise ValueError('Expected exactly the 50 assignment tickers, without duplicates.')
    for row in rows:
        if row['sector'] != expected[row['ticker']] or not row['company_name']:
            raise ValueError(f"Missing company name or assignment-sector mismatch: {row['ticker']}")
    return rows


def initialize():
    """Seed evidence without inventing historical intervals or final selections."""
    destination = ROOT / 'config/page_registry.json'
    if destination.exists():
        print(f'Registry already exists; left unchanged: {destination}')
        print('This initializer does not validate or update an existing registry.')
        return
    rows = read_companies(ROOT / 'config/companies.csv')
    report_path = ROOT / 'part1_stated_values/outputs/pilot_validation.json'
    report = json.loads(report_path.read_text(encoding='utf-8'))
    records = report['records']
    if len(records) != 6 or {r['capture_id'] for r in records} != set(PILOT_URLS):
        raise ValueError('Expected the six inspected pilot records, without duplicates.')
    candidates = []
    for record in records:
        capture = record['capture_id']
        ticker, timestamp = capture.split('_')
        url = PILOT_URLS[capture]
        snapshot = f'https://web.archive.org/web/{timestamp}/{url}'
        if (record['technical_status'] not in ('pass', 'pass_with_warnings')
                or record.get('errors') or record['source_snapshot_url'] != snapshot):
            raise ValueError(f'Pilot validation failed or URL differs: {capture}')
        apple = ticker == 'AAPL'
        candidates.append(dict(
            candidate_id=capture + '_page', ticker=ticker, original_url=url,
            hostname=urlsplit(url).hostname,
            page_type='recruitment_with_values' if apple else 'corporate_overview',
            page_family='apple_careers_identity' if apple else 'microsoft_about',
            verification_status='inspected_pilot_capture_only',
            effective_from=None, effective_to=None,
            selection_status='provisional_candidate', selected_for_annual_collection=False,
            alternative_candidates_reviewed=False,
            selection_rationale='Used for the engineering pilot; broader and historically comparable candidates still need review.',
            scope_notes='Recruitment framing may emphasize employees disproportionately.' if apple else 'Overview mixes identity statements and directory/project descriptions.',
            historical_evidence=[dict(capture_id=capture, timestamp=timestamp, snapshot_url=snapshot,
                                     source_sha256=record['source_sha256'],
                                     raw_html=record['paths']['raw_html'],
                                     technical_status=record['technical_status'],
                                     technical_warnings=record['warnings'],
                                     review_record='docs/pilot_validation_review.md')]))
    companies = [{**r, 'research_status': 'pilot_evidence_only' if r['ticker'] in ('AAPL', 'MSFT') else 'pending_research',
                  'candidate_ids': [c['candidate_id'] for c in candidates if c['ticker'] == r['ticker']],
                  'research_notes': ''} for r in rows]
    registry = dict(schema_version=1, created_at_utc=datetime.now(timezone.utc).isoformat(),
                    scope_years=list(range(2016, 2025)), source_company_file='config/companies.csv',
                    source_pilot_validation=report_path.relative_to(ROOT).as_posix(),
                    sector_basis='assignment-defined groups; not newly verified GICS membership',
                    companies=companies, candidates=candidates)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects an existing edited registry.
    with destination.open('x', encoding='utf-8') as handle:
        json.dump(registry, handle, indent=2, ensure_ascii=False)
        handle.write('\n')
    policy_path = ROOT / 'docs/page_selection_policy.md'
    policy_path.parent.mkdir(parents=True, exist_ok=True)
    if not policy_path.exists():
        policy_path.write_text(POLICY, encoding='utf-8')
    print('Companies registered: 50')
    print('Companies with pilot evidence only: 2')
    print('Companies pending research: 48')
    print('Pilot URL candidates: 6')
    print('Final annual-collection selections: 0')
    print(f'Registry: {destination}')
    print(f'Policy (existing text preserved): {policy_path}')
    print('No network requests made. Step 3.1 remains in progress.')


def main():
    try:
        initialize()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Registry initialization stopped: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
