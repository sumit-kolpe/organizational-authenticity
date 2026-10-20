"""Collect one consistent disclosure type and analyze it with a transparent lexical baseline.
No LLM API needed. All observations are provisional; prose cannot establish actual conduct.
"""
import argparse,csv,hashlib,json,os,re,statistics,time
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
from urllib.parse import quote,urlsplit
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'part2_disclosed_priorities/data/proxy_v1'
OUT=ROOT/'part2_disclosed_priorities/outputs/proxy_v2'
OLD_OUT=ROOT/'part2_disclosed_priorities/outputs/proxy_v1'
CIK_OVERRIDES={'BLK':1364742,'XOM':34088}
ANNUAL_ACCESSION='0001564590-18-009339'
LEXPATH=ROOT/'part2_disclosed_priorities/config/lexicon.json'
VERSION='proxy_review_v2.0'
FIELDS=['accessionNumber','filingDate','reportDate','form','primaryDocument']

def sha(b):return hashlib.sha256(b).hexdigest()
def save(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8');tmp.replace(path)
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def write_csv(path,rows):
 path.parent.mkdir(parents=True,exist_ok=True)
 if not rows:path.write_text('',encoding='utf-8');return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v for k,v in r.items()})
class Stop(Exception):pass
class Client:
 def __init__(self,budget):
  self.ua=os.getenv('SEC_USER_AGENT','');self.budget=budget;self.used=0;self.last=0
  if not re.search(r'[^\s@]+@[^\s@]+\.[^\s@]+',self.ua) or any(x in self.ua.lower() for x in ('your_email','example.com','your@email')):
   raise Stop('Set SEC_USER_AGENT to your real name and contact email; do not use a placeholder.')
 def get(self,url,json_expected=False):
  if urlsplit(url).hostname not in ('www.sec.gov','data.sec.gov'):raise ValueError('Unexpected SEC host')
  key=sha(url.encode());path=BASE/'http'/f'{key}.bin';meta=path.with_suffix('.json')
  if path.exists() and meta.exists():
   b=path.read_bytes();m=read(meta)
   if m['sha256']!=sha(b) or m['url']!=url:raise ValueError('Cache integrity mismatch')
   return json.loads(b) if json_expected else b
  for attempt in range(3):
   if self.used>=self.budget:raise Stop('Request budget reached; rerun same command to resume.')
   time.sleep(max(0,1-(time.monotonic()-self.last)));self.last=time.monotonic();self.used+=1
   try:
    with urlopen(Request(url,headers={'User-Agent':self.ua,'Accept-Encoding':'identity'}),timeout=60) as response:
     if urlsplit(response.geturl()).hostname not in ('www.sec.gov','data.sec.gov'):raise ValueError('Unexpected redirect host')
     b=response.read(30*1024*1024+1)
     if len(b)>30*1024*1024:raise ValueError('Document exceeds 30 MiB limit')
     if not b.strip():raise ValueError('Empty response')
     if json_expected:json.loads(b)
     low=b[:10000].lower()
     if any(x in low for x in (b'your request originates from an undeclared automated tool',b'request rate threshold exceeded',b'access denied')):raise Stop('SEC access restriction returned; stop and report.')
     path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix('.tmp');tmp.write_bytes(b);tmp.replace(path)
     save(meta,{'url':url,'sha256':sha(b),'bytes':len(b),'retrieved_at':datetime.now(timezone.utc).isoformat(),'content_type':response.headers.get('Content-Type'),'final_url':response.geturl()})
     return json.loads(b) if json_expected else b
   except HTTPError as e:
    if e.code in (403,429):raise Stop(f'SEC HTTP {e.code}; stop, do not repeatedly retry or bypass access controls.') from None
    if e.code not in (500,502,503,504) or attempt==2:raise ValueError(f'SEC HTTP {e.code}: {url}') from None
   except (URLError,TimeoutError,ConnectionError):
    if attempt==2:raise ValueError('Network request failed: '+url) from None
   time.sleep(5*(attempt+1))

def filing_rows(table):
 if not isinstance(table,dict) or 'accessionNumber' not in table:raise ValueError('Invalid submissions structure')
 n=len(table['accessionNumber'])
 for k in ('filingDate','form','primaryDocument'):
  if len(table.get(k,[]))!=n:raise ValueError('Unequal submissions arrays')
 return [{k:table.get(k,['']*n)[i] for k in FIELDS} for i in range(n)]

def history(cik,client):
 v=client.get(f'https://data.sec.gov/submissions/CIK{int(cik):010d}.json',True)
 rows=filing_rows(v['filings']['recent'])
 for f in v['filings'].get('files',[]):
  if f.get('filingTo','9999')<'2016-01-01' or f.get('filingFrom','0000')>'2024-12-31':continue
  name=f['name']
  if not re.fullmatch(r'CIK\d+-submissions-\d+\.json',name):raise ValueError('Unexpected historical submissions filename')
  rows.extend(filing_rows(client.get('https://data.sec.gov/submissions/'+name,True)))
 dedup={r['accessionNumber']:r for r in rows if r['form']=='DEF 14A' and '2016-01-01'<=r['filingDate']<='2024-12-31'}
 return v,sorted(dedup.values(),key=lambda r:(r['filingDate'],r['accessionNumber']))

def clean_html(body):
 from bs4 import BeautifulSoup
 soup=BeautifulSoup(body,'html.parser')
 for e in list(soup.find_all()):
  if not e.name:continue
  name=e.name.lower();style=(e.get('style','') or '').replace(' ','').lower()
  if name in ('script','style','noscript','head') or name in ('ix:header','ix:hidden','xbrli:context','xbrli:unit') or 'display:none' in style or 'visibility:hidden' in style:e.decompose()
 # Boundary before block/cell text avoids merging words; retain numeric tables transparently.
 for br in soup.find_all('br'):br.replace_with('\n')
 chunks=[]
 for s in soup.stripped_strings:
  text=' '.join(s.split())
  if text:chunks.append(text)
 return '\n'.join(chunks)

def patterns(words):
 return re.compile(r'(?<!\w)(?:'+'|'.join(re.escape(w) for w in sorted(words,key=len,reverse=True))+r')(?!\w)',re.I)
def metrics(text,lex):
 normalized=' '.join(text.lower().split());words=re.findall(r"[a-z]+(?:'[a-z]+)?",normalized);n=len(words)
 result={'word_count':n,'character_count':len(text),'themes':{},'language':{}};evidence=[]
 for section in ('themes','language_markers'):
  for cat,terms in lex[section].items():
   hits=list(patterns(terms).finditer(normalized));v={'count':len(hits),'per_1000_words':1000*len(hits)/n if n else None}
   result['themes' if section=='themes' else 'language'][cat]=v
   if section=='themes':
    for m in hits[:5]:evidence.append({'theme':cat,'matched_term':m.group(),'normalized_character_offset':m.start(),'excerpt':normalized[max(0,m.start()-160):m.end()+160]})
 total=sum(x['count'] for x in result['themes'].values())
 for x in result['themes'].values():x['share_of_theme_hits']=x['count']/total if total else None
 result['total_theme_hits']=total
 result['extraction_warning']='Full document incl. tables, compensation, proposals and management language; lexical mentions are not endorsement.'
 return result,evidence

def roster():
 with (ROOT/'config/companies.csv').open(encoding='utf-8-sig') as f:cs=list(csv.DictReader(f))
 if len(cs)!=50 or len({c['ticker'] for c in cs})!=50:raise ValueError('Expected fixed 50-company roster')
 return cs

def repair_target(r):
 return r['ticker'] in CIK_OVERRIDES or (r['ticker']=='TSLA' and r['year']==2018)

def initialize():
 cs=roster()
 original=read(OLD_OUT/'inventory.json')
 if len(original)!=450 or len({(r['ticker'],r['year']) for r in original})!=450:
  raise ValueError('Expected complete original inventory with 450 unique keys')
 old_policy=read(OLD_OUT/'run_policy.json')
 if old_policy['roster_sha256']!=sha((ROOT/'config/companies.csv').read_bytes()) or old_policy['lexicon_sha256']!=sha(LEXPATH.read_bytes()):
  raise ValueError('Roster or lexicon changed since baseline')
 policy={'version':VERSION,'baseline_inventory_sha256':sha((OLD_OUT/'inventory.json').read_bytes()),'roster_sha256':old_policy['roster_sha256'],'lexicon_sha256':old_policy['lexicon_sha256'],'cik_overrides':CIK_OVERRIDES,'annual_proxy_override':ANNUAL_ACCESSION,'selection':'Filing calendar year; earliest DEF 14A except verified TSLA 2018 annual proxy; historical CIK overrides BLK/XOM.'}
 path=OUT/'run_policy.json'
 if path.exists() and read(path)!=policy:raise ValueError('Repair inputs changed; stop to preserve reproducibility')
 save(path,policy)
 dest=OUT/'inventory.json'
 if dest.exists():return cs,read(dest)
 rows=[];audit=[]
 for old in original:
  if repair_target(old):
   audit.append(old)
   r={k:old[k] for k in ('ticker','company_name','sector','year','form') if k in old}
   r.update(status='not_attempted',manual_review_status='pending',repair_reason='Historical entity mapping' if old['ticker'] in CIK_OVERRIDES else 'Replace special-meeting proxy with annual proxy')
   rows.append(r)
  else:rows.append(old)
 save(OUT/'replaced_baseline_rows.json',audit);save(dest,rows)
 return cs,rows

def collect(args):
 cs,rows=initialize();client=Client(args.max_requests)
 try:
  mapping=client.get('https://www.sec.gov/files/company_tickers.json',True)
  matches=defaultdict(list)
  for v in mapping.values():matches[v['ticker'].replace('.','-').upper()].append(v)
  for c in cs:
   if args.tickers and c['ticker'] not in args.tickers:continue
   selected=[r for r in rows if r['ticker']==c['ticker']]
   if all(r['status'] in ('downloaded','no_DEF14A_for_current_CIK','mapping_unresolved','unsupported_document_format') for r in selected):continue
   found=([{'cik_str':CIK_OVERRIDES[c['ticker']]}] if c['ticker'] in CIK_OVERRIDES else matches[c['ticker'].replace('.','-').upper()])
   if len(found)!=1:
    for r in selected:r.update(status='mapping_unresolved',notes='Current SEC ticker mapping not unique; manual entity history needed.')
    save(OUT/'inventory.json',rows);continue
   cik=int(found[0]['cik_str'])
   try:company,filings=history(cik,client)
   except ValueError as e:
    for r in selected:
     if r['status']!='downloaded':r.update(status='discovery_failed',error=str(e))
    save(OUT/'inventory.json',rows);continue
   save(OUT/'discovery'/f'{c["ticker"]}.json',{'cik':cik,'sec_name':company.get('name'),'former_names':company.get('formerNames',[]),'filings':filings})
   for r in selected:
    if r['status']=='downloaded':continue
    candidates=[f for f in filings if int(f['filingDate'][:4])==r['year']]
    r.update(cik=cik,sec_entity_name=company.get('name'),candidate_count=len(candidates),candidates=candidates,entity_scope_warning=('Historical CIK override for 2016-2024; broader entity continuity not asserted.' if c['ticker'] in CIK_OVERRIDES else 'Current CIK only; predecessor/successor coverage not asserted.'))
    if not candidates:r.update(status='no_DEF14A_for_current_CIK');save(OUT/'inventory.json',rows);continue
    f=candidates[0]
    if c['ticker']=='TSLA' and r['year']==2018:
     annual=[v for v in candidates if v['accessionNumber']==ANNUAL_ACCESSION]
     if len(annual)!=1:raise ValueError('Verified Tesla annual proxy absent from submissions; stop for review')
     f=annual[0]
    doc=f['primaryDocument'];acc=f['accessionNumber']
    if not re.fullmatch(r'\d{10}-\d{2}-\d{6}',acc) or '..' in doc or '/' in doc:raise ValueError('Unexpected archive identifier')
    url=f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-","")}/{quote(doc)}'
    r.update(filing_date=f['filingDate'],report_date=f.get('reportDate'),accession=acc,source_url=url,selection_warning='Earliest definitive proxy in filing year; may be special meeting. Multiple candidates retained for review.' if len(candidates)>1 else 'Definitive proxy; annual-meeting status not independently verified.')
    if c['ticker']=='TSLA' and r['year']==2018:r['selection_warning']='Explicit verified annual proxy override; baseline special meeting preserved in audit.'
    if not doc.lower().endswith(('.htm','.html','.txt')):r.update(status='unsupported_document_format');save(OUT/'inventory.json',rows);continue
    try:
     body=client.get(url);text=clean_html(body) if doc.lower().endswith(('.htm','.html')) else body.decode('utf-8',errors='replace')
     if len(re.findall(r'\w+',text))<1000:raise ValueError('Too little proxy text; source/error response needs review')
     stem=f'{c["ticker"]}_{r["year"]}_{acc}';folder=BASE/'documents';folder.mkdir(parents=True,exist_ok=True)
     hp=folder/(stem+('.html' if not doc.endswith('.txt') else '.raw.txt'));tp=folder/(stem+'.txt');hp.write_bytes(body);tp.write_text(text,encoding='utf-8')
     r.update(status='downloaded',raw_file=str(hp.relative_to(ROOT)),text_file=str(tp.relative_to(ROOT)),raw_sha256=sha(body),text_sha256=sha(text.encode()),characters=len(text),annual_meeting_marker=bool(re.search(r'annual\s+meeting',text,re.I)))
    except ValueError as e:r.update(status='download_failed',error=str(e))
    save(OUT/'inventory.json',rows);print(c['ticker'],r['year'],r['status'],flush=True)
 except (Stop,KeyboardInterrupt) as e:
  save(OUT/'inventory.json',rows);print('Stopped safely:',e);return False
 return True

def analyze():
 rows=read(OUT/'inventory.json');lex=read(LEXPATH);metrics_rows=[];evidence=[];by_company=defaultdict(list)
 for r in rows:
  out={k:r.get(k) for k in ('ticker','company_name','sector','year','status','filing_date','report_date','accession','source_url','cik','candidate_count','annual_meeting_marker','selection_warning','entity_scope_warning')}
  if r['status']=='downloaded':
   p=ROOT/Path(r['text_file'].replace('\\','/'));text=p.read_text(encoding='utf-8')
   if sha(text.encode())!=r['text_sha256']:raise ValueError('Text integrity mismatch')
   m,ev=metrics(text,lex);out.update(m);out['text_sha256']=r['text_sha256'];out['analysis_status']='lexically_analyzed_pending_review'
   for e in ev:evidence.append({'ticker':r['ticker'],'year':r['year'],'source_url':r['source_url'],**e})
   by_company[r['ticker']].append(out)
  else:out['analysis_status']='unavailable'
  metrics_rows.append(out)
 save(OUT/'disclosure_metrics.json',metrics_rows);write_csv(OUT/'disclosure_metrics.csv',metrics_rows);write_csv(OUT/'theme_evidence.csv',evidence)
 changes=[]
 for ticker,rs in by_company.items():
  idx={r['year']:r for r in rs}
  for y,r in sorted(idx.items()):
   if y-1 not in idx:continue
   old=idx[y-1]
   changes.append({'ticker':ticker,'sector':r['sector'],'year':y,'previous_year':y-1,'theme_rate_changes':{t:r['themes'][t]['per_1000_words']-old['themes'][t]['per_1000_words'] for t in lex['themes']},'language_rate_changes':{t:r['language'][t]['per_1000_words']-old['language'][t]['per_1000_words'] for t in lex['language_markers']},'interpretation':'Descriptive lexical change; not causal or endorsement.'})
 write_csv(OUT/'within_company_changes.csv',changes);save(OUT/'within_company_changes.json',changes)
 sectors=[]
 for sector in sorted({r['sector'] for r in metrics_rows}):
  for y in range(2016,2025):
   rs=[r for r in metrics_rows if r['sector']==sector and r['year']==y and 'themes' in r]
   for t in lex['themes']:sectors.append({'sector':sector,'year':y,'theme':t,'n_documents':len(rs),'mean_per_1000_words':statistics.mean(r['themes'][t]['per_1000_words'] for r in rs) if rs else None})
 write_csv(OUT/'sector_year_themes.csv',sectors)
 events=[]
 # Paired company means reduce changing-composition confounding; 2020 transition excluded.
 for ticker,rs in by_company.items():
  pre=[r for r in rs if r['year'] in (2018,2019)];post=[r for r in rs if r['year'] in (2021,2022)]
  if len(pre)!=2 or len(post)!=2:continue
  vals={}
  for t in lex['themes']:vals[t]=statistics.mean(r['themes'][t]['per_1000_words'] for r in post)-statistics.mean(r['themes'][t]['per_1000_words'] for r in pre)
  events.append({'ticker':ticker,'sector':rs[0]['sector'],'pre_years':'2018,2019','post_years':'2021,2022','theme_rate_changes':vals,'covid_marker_change':statistics.mean(r['language']['covid']['per_1000_words'] for r in post)-statistics.mean(r['language']['covid']['per_1000_words'] for r in pre),'caveat':'Coincidence with pandemic period, not a causal estimate; filing-year timing and other changes confound.'})
 write_csv(OUT/'pandemic_paired_comparison.csv',events);save(OUT/'pandemic_paired_comparison.json',events)
 summary={'total_company_years':len(rows),'statuses':dict(Counter(r['status'] for r in rows)),'analyzed_documents':sum('themes' in r for r in metrics_rows),'analyzed_companies':len(by_company),'adjacent_year_pairs':len(changes),'pandemic_complete_company_pairs':len(events),'multiple_proxy_candidate_years':sum(r.get('candidate_count',0)>1 for r in rows),'missing_is_not_zero':True,'method':'transparent lexical baseline; no LLM classification and no independent human validation'}
 save(OUT/'coverage_summary.json',summary);print(json.dumps(summary,indent=2))
 # Report generated from observed outputs, never placeholder findings.
 text=f'''# Part 2 run report\n\nDisclosure type: DEF 14A definitive proxy statements.\nAnalyzed documents: {summary['analyzed_documents']} / 450 across {len(by_company)} companies.\nAdjacent-year pairs: {len(changes)}. Complete pandemic-window companies: {len(events)}.\n\nThis is a dictionary-based lexical baseline, not a measure of actual behavior.\nProxy statements mix management claims, shareholder proposals, legal requirements\nand compensation language. Counts measure disclosed attention, not endorsement.\nLanguage markers quantify commitment, uncertainty and obligation, not validated sentiment.\nThe event comparison is descriptive and does not establish pandemic causation.\nTargeted model-supported source review corrected BLK/XOM historical CIKs and TSLA 2018 selection.\nOther source and extraction checks remain pending; no independent human validation.\n'''
 (OUT/'run_report.md').write_text(text,encoding='utf-8')

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['plan','collect','analyze','all']);p.add_argument('--max-requests',type=int,default=1000);p.add_argument('--tickers',nargs='+');a=p.parse_args()
 if a.max_requests<1:p.error('Positive request budget required')
 if a.tickers and not set(a.tickers)<={c['ticker'] for c in roster()}:p.error('Unknown ticker')
 if a.action=='plan':print('50 companies x 9 filing years; DEF 14A only; lexical baseline; no Gemini calls.');return
 if a.action in ('collect','all'):
  try:
   if not collect(a):return
  except Stop as e:print('Stopped:',e);return
 if a.action in ('analyze','all'):analyze()
if __name__=='__main__':main()
