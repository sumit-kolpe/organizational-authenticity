"""Resumable archive discovery and candidate extraction. Never approves research text.

Run from the project root with ``python -m part1_stated_values.src.batch_web --plan``.
Uses a separate batch_v1 directory; existing pilot data and registry are untouched.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, unquote_plus
from urllib.request import Request, build_opener, HTTPRedirectHandler

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'part1_stated_values/data/batch_v1'
OUT = ROOT / 'part1_stated_values/outputs/batch_v1'
FIELDS = ['timestamp', 'original', 'statuscode', 'mimetype', 'digest']
VERSION = 'batch_v1.0'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save_json(path, value):
    """Replace a checkpoint atomically; an interruption cannot leave half a JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    temp.replace(path)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def now():
    return datetime.now(timezone.utc).isoformat()


class StopRun(Exception):
    """Rate limiting, access restriction or request budget: checkpoint and stop."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, budget, delay=3):
        self.budget, self.delay, self.used, self.last = budget, delay, 0, 0.0
        self.opener = build_opener(NoRedirect())

    def get(self, url):
        """Never follow redirects or bypass restrictions. Retry transient failures only."""
        if urlsplit(url).hostname != 'web.archive.org':
            raise ValueError('Network requests restricted to web.archive.org')
        for attempt in range(3):
            if self.used >= self.budget:
                raise StopRun('Request budget reached; rerun to resume.')
            time.sleep(max(0, self.delay - (time.monotonic() - self.last)))
            self.used += 1
            self.last = time.monotonic()
            try:
                req = Request(url, headers={'User-Agent': 'OrganizationalAuthenticityResearch/0.2',
                                           'Accept-Encoding': 'identity'})
                with self.opener.open(req, timeout=45) as response:
                    body = response.read(12 * 1024 * 1024 + 1)
                    if len(body) > 12 * 1024 * 1024:
                        raise ValueError('Response exceeds 12 MiB limit')
                    return body, dict(response.headers), response.geturl()
            except HTTPError as exc:
                if exc.code in (403, 429):
                    raise StopRun(f'HTTP {exc.code}; stopped. Wait or investigate access before resuming.') from exc
                if exc.code not in (500, 502, 503, 504) or attempt == 2:
                    raise ValueError(f'HTTP {exc.code}; Location={exc.headers.get("Location", "")}') from exc
            except (URLError, TimeoutError, ConnectionError):
                if attempt == 2:
                    raise
            time.sleep(5 * 2 ** attempt)
        raise RuntimeError('Retry loop ended unexpectedly')


def parse_cdx(body):
    """Decode CDX JSON, including the empty row + resume-key trailer.

    An empty HTTP body is unresolved, never equivalent to an empty JSON list.
    """
    if not body.strip():
        raise ValueError('Empty CDX body; absence of captures is NOT established')
    value = json.loads(body)
    if not isinstance(value, list):
        raise ValueError('CDX response is not a list')
    if not value:
        return [], None
    if value[0] != FIELDS:
        raise ValueError(f'Unexpected CDX header: {value[0]!r}')
    records, resume = [], None
    trailer = False
    for row in value[1:]:
        if row == []:
            trailer = True
            continue
        if trailer:
            if resume is not None or not isinstance(row, list) or len(row) != 1 or not isinstance(row[0], str):
                raise ValueError('Malformed CDX continuation trailer')
            resume = row[0]
            continue
        if not isinstance(row, list) or len(row) != len(FIELDS) or not all(isinstance(v, str) for v in row):
            raise ValueError('Malformed CDX capture row')
        record = dict(zip(FIELDS, row))
        datetime.strptime(record['timestamp'], '%Y%m%d%H%M%S')
        if not 2016 <= int(record['timestamp'][:4]) <= 2024:
            raise ValueError('CDX returned out-of-scope capture')
        records.append(record)
    if trailer and not resume:
        raise ValueError('Empty continuation trailer')
    return records, resume


def discover(url, client, max_pages, retry_failed=False):
    """Paginate a URL's full study window. Persist each successful page."""
    folder = BASE / 'cdx' / digest(url.encode())[:24]
    checkpoint = folder / 'inventory.json'
    state = read_json(checkpoint) if checkpoint.exists() else {
        'url': url, 'records': [], 'resume_key': None, 'pages': [], 'complete': False}
    if state['url'] != url:
        raise ValueError('Cache identity mismatch')
    for page in state['pages']:
        cached_page = ROOT / page['response_file']
        if not cached_page.exists() or digest(cached_page.read_bytes()) != page['sha256']:
            raise ValueError('CDX cache integrity mismatch; preserve and investigate the affected cache')
    if state['complete'] or (state.get('error') and not retry_failed):
        return state
    state.pop('error', None)
    seen = {p['requested_resume_key'] for p in state['pages']}
    try:
        while len(state['pages']) < max_pages:
            key = state['resume_key']
            if key in seen:
                raise ValueError('Repeated continuation key; inventory incomplete')
            params = dict(url=url, matchType='exact', **{'from':'2016','to':'2024'},
                          output='json', fl=','.join(FIELDS), limit='1000', showResumeKey='true')
            if key:
                # Server supplies an already encoded token; avoid double encoding it.
                params['resumeKey'] = unquote_plus(key)
            request_url = 'https://web.archive.org/cdx/search/cdx?' + urlencode(params)
            body, headers, final = client.get(request_url)
            page = folder / f'page_{len(state["pages"])+1:04d}.json'
            folder.mkdir(parents=True, exist_ok=True)
            page.write_bytes(body)  # Preserve even a malformed response for diagnosis.
            records, next_key = parse_cdx(body)
            state['records'].extend(records)
            state['pages'].append({'request_url':request_url, 'requested_resume_key':key,
                                   'response_file':str(page.relative_to(ROOT)), 'sha256':digest(body),
                                   'retrieved_at':now(), 'headers':headers})
            state['resume_key'], state['complete'] = next_key, next_key is None
            seen.add(key)
            save_json(checkpoint, state)
            if state['complete']:
                break
        if not state['complete']:
            state['error'] = 'page_cap_reached: increase --max-pages to continue'
    except StopRun:
        save_json(checkpoint, state)
        raise
    except Exception as exc:
        state['error'] = f'{type(exc).__name__}: {exc}'
    save_json(checkpoint, state)
    return state


def ordered_candidates(records, year, exclusions, ticker):
    """Eligible direct HTML first; revisit records retained for replay attempts."""
    target = datetime(year, 7, 1, 12)
    unique = {}
    for record in records:
        stamp = record['timestamp']
        if int(stamp[:4]) != year or (ticker, stamp) in exclusions:
            continue
        eligible = ((record['statuscode'] == '200' and record['mimetype'] in ('text/html','application/xhtml+xml'))
                    or record['mimetype'] == 'warc/revisit')
        if eligible:
            unique[(stamp, record['original'])] = record
    return sorted(unique.values(), key=lambda r: (
        abs((datetime.strptime(r['timestamp'], '%Y%m%d%H%M%S')-target).total_seconds()),
        r['timestamp'], r['original']))


def extract(body):
    """Conservative generic extraction. Output always requires relevance review."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(body, 'html.parser')
    title = soup.title.get_text(' ', strip=True) if soup.title else ''
    if soup.select_one('iframe#playback'):
        return '', ['archive_playback_wrapper'], title
    for element in soup.select('script, style, noscript, footer, form, #wm-ipp, #wm-ipp-base'):
        element.decompose()
    # Some corporate templates put actual culture paragraphs inside <nav>.
    # Remove navigation/header containers only when they lack substantive paragraphs.
    for element in list(soup.select('nav, header')):
        if element.name and not any(len(p.get_text(' ', strip=True)) >= 80 for p in element.find_all('p')):
            element.decompose()
    region = soup.find('main') or soup.find(attrs={'role':'main'}) or soup.body or soup
    blocks = []
    for el in region.find_all(['h1','h2','h3','h4','p','li','blockquote']):
        if el.find(['h1','h2','h3','h4','p','li','blockquote']):
            continue  # Nested block is emitted separately; avoid duplicate text.
        text = ' '.join(el.get_text(' ', strip=True).split())
        if text:
            blocks.append(text)
    text = '\n\n'.join(blocks)
    flags = []
    lower = (title + '\n' + text).lower()
    for marker in ('brand config page', 'access denied', 'request rejected', 'verify you are human',
                   'wayback machine has not archived', 'page not found', 'captcha'):
        if marker in lower:
            flags.append('error_or_irrelevant_marker:' + marker)
    if len(text) < 250:
        flags.append('too_little_text')
    if len(text) > 60000:
        flags.append('unusually_long_text')
    # No language/topic classifier here: English and organizational relevance are review fields.
    return text, flags, title


def replay(record, ticker, client):
    stamp, original = record['timestamp'], record['original']
    ident = f'{ticker}_{stamp}_{digest(original.encode())[:12]}'
    folder = BASE / 'captures'
    meta_path, html_path = folder / (ident+'.json'), folder / (ident+'.html')
    if meta_path.exists() and html_path.exists():
        meta = read_json(meta_path)
        body = html_path.read_bytes()
        if meta['original_url'] != original or meta['sha256'] != digest(body):
            raise ValueError('Replay cache integrity mismatch')
    else:
        # if_ requests the archived page frame, avoiding the outer playback wrapper.
        url = f'https://web.archive.org/web/{stamp}if_/{original}'
        body, headers, final = client.get(url)
        h = {k.lower():v for k,v in headers.items()}
        if 'html' not in h.get('content-type','').lower():
            raise ValueError('Replay response is not HTML')
        match = re.search(r'/web/(\d{14})(?:[a-z]+_)?/', final)
        if not match or match.group(1) != stamp:
            raise ValueError('Replay changed capture timestamp')
        memento = h.get('memento-datetime')
        if memento and parsedate_to_datetime(memento).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S') != stamp:
            raise ValueError('Memento timestamp differs from requested capture')
        folder.mkdir(parents=True, exist_ok=True)
        html_path.write_bytes(body)
        meta = {'original_url':original,'timestamp':stamp,'requested_url':url,'final_url':final,
                'headers':headers,'memento_datetime':memento,'sha256':digest(body),'retrieved_at':now()}
        save_json(meta_path, meta)
    text, flags, title = extract(body)
    if not meta.get('memento_datetime'):
        flags.append('memento_header_missing')
    text_path = folder / (ident+'.txt')
    text_path.write_text(text+'\n', encoding='utf-8')
    return {'snapshot_timestamp':stamp,'original_url':original,'snapshot_url':meta['requested_url'],
            'html_file':str(html_path.relative_to(ROOT)), 'text_file':str(text_path.relative_to(ROOT)),
            'text_sha256':digest(text.encode()),'characters':len(text),'title':title,
            'quality_flags':'; '.join(flags),'extraction_status':'screened_candidate' if not flags else 'flagged_candidate',
            'manual_review_status':'pending','annual_selection_final':False,'analysis_version':VERSION}


def write_outputs(rows):
    OUT.mkdir(parents=True, exist_ok=True)
    save_json(OUT/'company_year_inventory.json', rows)
    columns = ['ticker','company_name','sector','year','status','discovery_complete','page_family',
               'original_url','snapshot_timestamp','snapshot_url','characters','quality_flags',
               'text_file','html_file','text_sha256','manual_review_status','annual_selection_final',
               'notes']
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)
    path = OUT/'company_year_inventory.csv'
    temp = path.with_suffix('.tmp')
    temp.write_text(buffer.getvalue(),encoding='utf-8-sig')
    temp.replace(path)
    save_json(OUT/'coverage_summary.json', {'updated_at':now(),'total_company_years':len(rows),
                  'statuses':dict(Counter(r['status'] for r in rows)),
                  'warning':'Candidate extraction only. No LLM analysis or final annual selection.'})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--plan', action='store_true', help='Validate inputs and print plan; no network')
    mode.add_argument('--run', action='store_true')
    p.add_argument('--tickers', nargs='+')
    p.add_argument('--years', nargs='+', type=int, default=list(range(2016,2025)))
    p.add_argument('--max-pages', type=int, default=20, help='Maximum CDX pages per candidate URL')
    p.add_argument('--max-requests', type=int, default=1500)
    p.add_argument('--attempts-per-year', type=int, default=3)
    p.add_argument('--retry-failed', action='store_true', help='Revisit previous errors/incomplete discovery; retains successful caches')
    args = p.parse_args()
    if min(args.max_pages,args.max_requests,args.attempts_per_year) < 1 or not set(args.years) <= set(range(2016,2025)):
        p.error('Positive limits and years 2016–2024 required')
    with (ROOT/'config/companies.csv').open(encoding='utf-8-sig',newline='') as stream:
        companies = list(csv.DictReader(stream))
    if len(companies)!=50 or len({c['ticker'] for c in companies})!=50:
        p.error('Expected 50 unique assignment companies')
    manifest = read_json(ROOT/'config/batch_page_candidates.json')
    known = {c['ticker'] for c in companies}
    if args.tickers and not set(args.tickers)<=known:
        p.error('Unknown ticker')
    if not {c['ticker'] for c in manifest['candidates']}<=known:
        p.error('Manifest has unknown ticker')
    print(f'Plan: 50 companies x 9 years = 450 rows. Enabled URL leads: {sum(c["enabled"] for c in manifest["candidates"])}')
    print('Berkshire source suitability remains unresolved. All new sources need historical review.')
    if args.plan:
        print('Plan passed; no network requests or output data changes.')
        return 0
    config_path = OUT/'run_config.json'
    signature = {'manifest_sha256':digest((ROOT/'config/batch_page_candidates.json').read_bytes()),
                 'companies_sha256':digest((ROOT/'config/companies.csv').read_bytes()),
                 'analysis_version':VERSION}
    if config_path.exists() and read_json(config_path) != signature:
        p.error('Run inputs changed. Back up this run and create a new version; do not mix source policies.')
    save_json(config_path, signature)
    inventory_path = OUT/'company_year_inventory.json'
    prior = {(r['ticker'],r['year']):r for r in read_json(inventory_path)} if inventory_path.exists() else {}
    rows = [prior.get((c['ticker'],year), {**c,'year':year,'status':'not_attempted',
            'manual_review_status':'pending','annual_selection_final':False})
            for c in companies for year in range(2016,2025)]
    write_outputs(rows)
    client = Client(args.max_requests)
    exclusions = {(x['ticker'],x['timestamp']) for x in manifest['excluded_captures']}
    try:
        for company in companies:
            ticker = company['ticker']
            if args.tickers and ticker not in args.tickers:
                continue
            candidates = sorted((c for c in manifest['candidates'] if c['ticker']==ticker and c['enabled']),key=lambda c:c['priority'])
            selected = [r for r in rows if r['ticker']==ticker and r['year'] in args.years]
            if not candidates:
                for row in selected:
                    row.update(status='source_selection_pending',notes='No enabled suitable source; not evidence of absence.')
                write_outputs(rows)
                continue
            if all(r['status'] in ('candidate_ready','candidate_flagged') for r in selected):
                continue
            states = [(candidate,discover(candidate['url'],client,args.max_pages,args.retry_failed)) for candidate in candidates]
            complete = all(s['complete'] for _,s in states)
            for row in selected:
                if row['status'] in ('candidate_ready','candidate_flagged'):
                    continue
                if row['status']!='not_attempted' and not args.retry_failed:
                    continue
                row.update(discovery_complete=complete,attempts=[])
                attempts, chosen = 0, None
                # Respect page priority; do not merge unrelated pages or splice their text.
                for candidate,state in states:
                    for capture in ordered_candidates(state['records'],row['year'],exclusions,ticker):
                        if attempts>=args.attempts_per_year:
                            break
                        attempts+=1
                        try:
                            result = replay(capture,ticker,client)
                            result['page_family']=candidate['page_family']
                            row['attempts'].append(result)
                            if chosen is None:
                                chosen=result
                            if result['extraction_status']=='screened_candidate':
                                chosen=result
                                break
                        except StopRun:
                            raise
                        except Exception as exc:
                            row['attempts'].append({'timestamp':capture['timestamp'],'original_url':capture['original'],
                                                    'error':f'{type(exc).__name__}: {exc}'})
                    if chosen and chosen['extraction_status']=='screened_candidate':
                        break
                if chosen:
                    row.update(chosen)
                    row['status']='candidate_ready' if chosen['extraction_status']=='screened_candidate' else 'candidate_flagged'
                else:
                    count=sum(sum(int(r['timestamp'][:4])==row['year'] for r in s['records']) for _,s in states)
                    row['status']=('replay_failed' if attempts else 'no_eligible_capture_returned' if count
                                   else 'no_records_for_queried_urls' if complete else 'discovery_unresolved')
                row['notes']='; '.join(filter(None,[s.get('error','') for _,s in states])) or 'Provisional URL family; content review and final annual selection pending.'
                write_outputs(rows)
                print(f'{ticker} {row["year"]}: {row["status"]} | full_inventory={complete}',flush=True)
    except (StopRun,KeyboardInterrupt) as exc:
        write_outputs(rows)
        print(f'Stopped safely: {exc or "keyboard interruption"}. Checkpoints retained.')
        return 2
    print(f'Output: {OUT / "company_year_inventory.csv"}')
    print('No final Part 1 dataset: LLM coding and manual/source-family review remain pending.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
