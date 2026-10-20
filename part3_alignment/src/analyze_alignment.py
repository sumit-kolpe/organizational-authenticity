"""Offline research analysis of reviewed historical source and disclosure text."""
import argparse,csv,hashlib,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
THEMES=['innovation','integrity','people','inclusion','customer','environment','community','security_privacy','performance']
VERSION='alignment_v1.0'

def read(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(v,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def csvout(p,rows):
 if not rows:p.write_text('',encoding='utf-8');return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()})
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cosine(a,b):
 if len(a)!=len(b):raise ValueError('Unequal vector lengths')
 if any(not math.isfinite(x) or x<0 for x in a+b):raise ValueError('Invalid vector value')
 den=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
 return min(1.,max(0.,sum(x*y for x,y in zip(a,b))/den)) if den else None
def overlap(a,b):
 union=sum(bool(x) or bool(y) for x,y in zip(a,b))
 return sum(bool(x) and bool(y) for x,y in zip(a,b))/union if union else None
def describe(values):
 v=sorted(x for x in values if x is not None)
 if not v:return {'n':0,'mean':None,'median':None,'min':None,'max':None,'sd':None}
 return dict(n=len(v),mean=statistics.mean(v),median=statistics.median(v),min=v[0],max=v[-1],sd=statistics.pstdev(v))
def index(rows):
 out={}
 for r in rows:
  k=(r['ticker'],r['year'])
  if k in out:raise ValueError('Duplicate company-year: '+str(k))
  out[k]=r
 return out
def make_row(a,b):
 if a['sector']!=b['sector']:raise ValueError('Sector mismatch')
 r={k:a[k] for k in ('ticker','year','company_name','sector')}
 r.update(part1_status=a['status'],part2_status=b['status'],snapshot_url=a.get('snapshot_url'),snapshot_timestamp=a.get('snapshot_timestamp'),proxy_url=b.get('source_url'),proxy_filing_date=b.get('filing_date'),proxy_text_sha256=b.get('text_sha256'),part1_flags=(a.get('analyst_notes') or {}).get('flags',[]),part1_ai_review_status=a.get('ai_review_status'),independent_human_validation=(a.get('independent_human_review')=='completed_no_changes_owner_confirmed' and b.get('human_review_status')=='completed_no_changes_owner_confirmed'),source_review_basis='project_owner_confirmation_2026-10-19',score=None,score_status='unscored')
 reasons=[]
 if a.get('eligible_for_provisional_analysis') is not True:reasons.append('part1_ineligible')
 if b.get('status')!='downloaded' or 'themes' not in b:reasons.append('part2_unavailable')
 if reasons:r['exclusion_reasons']=reasons;return r
 ts=a.get('theme_categories') or []
 if set(ts)-set(THEMES):raise ValueError('Unknown Part 1 theme')
 if set(b['themes'])!=set(THEMES):raise ValueError('Part 2 theme mismatch')
 av=[int(t in ts) for t in THEMES]
 counts=[b['themes'][t]['count'] for t in THEMES]
 if any(isinstance(x,bool) or not isinstance(x,int) or x<0 for x in counts):raise ValueError('Invalid count')
 words=b.get('word_count',0)
 if words<=0:raise ValueError('Nonpositive word count')
 bv=[1000*x/words for x in counts]
 for t,v in zip(THEMES,bv):
  if not math.isclose(v,b['themes'][t]['per_1000_words'],rel_tol=1e-9,abs_tol=1e-12):raise ValueError('Rate/count mismatch')
 score=cosine(av,bv)
 if score is None:
  r['exclusion_reasons']=['zero_stated_vector' if not any(av) else 'zero_disclosure_vector'];return r
 keep=[i for i,t in enumerate(THEMES) if t not in ('integrity','inclusion')]
 stamp=str(a.get('snapshot_timestamp') or '')[:8];date=str(b.get('filing_date') or '').replace('-','')
 r.update(score=score,score_status='provisional_textual_alignment',exclusion_reasons=[],stated_vector=av,disclosure_rates=bv,stated_theme_count=sum(av),disclosure_hit_count=sum(counts),proxy_word_count=words,jaccard_one_hit=overlap(av,[int(x>=1) for x in counts]),jaccard_three_hits=overlap(av,[int(x>=3) for x in counts]),cosine_log_rates=cosine(av,[math.log1p(x) for x in bv]),cosine_excluding_integrity_inclusion=cosine([av[i] for i in keep],[bv[i] for i in keep]),snapshot_on_or_before_filing=(stamp<=date if len(stamp)==len(date)==8 else None),scope_sensitivity_retained=not any(f!='generic_extraction_requires_review' for f in r['part1_flags']))
 return r

def analyze(p1,p2,out):
 a=index(read(p1));b=index(read(p2))
 if set(a)!=set(b) or len(a)!=450:raise ValueError('Expected matching 450-row input panels')
 tickers={t for t,y in a}
 if len(tickers)!=50 or set(a)!={(t,y) for t in tickers for y in range(2016,2025)}:raise ValueError('Unexpected panel roster/years')
 policy={'version':VERSION,'part1_sha256':digest(p1),'part2_sha256':digest(p2),'themes':THEMES,'primary':'cosine(binary stated themes, disclosure counts per 1000 words)','missing':'null; no imputation','validation':'Numerical checks plus project-owner-confirmed completed source review, no additional source corrections'}
 out.mkdir(parents=True,exist_ok=True)
 if (out/'run_policy.json').exists() and read(out/'run_policy.json')!=policy:raise ValueError('Inputs changed; choose a new --output directory')
 rows=[make_row(a[k],b[k]) for k in sorted(a)]
 valid=[r for r in rows if r['score'] is not None]
 # Negative control: compare each stated vector with every OTHER available
 # disclosure in the same year, also restricting to sector when possible.
 placebo=[]
 for r in valid:
  controls=[v for k,v in b.items() if k[1]==r['year'] and k[0]!=r['ticker'] and 'themes' in v and v['status']=='downloaded']
  for scope in ('same_year','same_sector_year'):
   cs=[v for v in controls if scope=='same_year' or v['sector']==r['sector']]
   scores=[cosine(r['stated_vector'],[v['themes'][t]['per_1000_words'] for t in THEMES]) for v in cs]
   stats=describe(scores);avg=stats['mean']
   placebo.append({'ticker':r['ticker'],'year':r['year'],'control_scope':scope,'own_score':r['score'],'n_other_proxies':stats['n'],'mean_other_score':avg,'own_minus_other_mean':r['score']-avg if avg is not None else None})
 changes=[];vi=index(valid)
 for (t,y),r in vi.items():
  old=vi.get((t,y-1))
  if old:changes.append(dict(ticker=t,year=y,previous_year=y-1,sector=r['sector'],score=r['score'],previous_score=old['score'],score_change=r['score']-old['score']))
 groups=[]
 for kind in ('year','sector','ticker'):
  for value in sorted({r[kind] for r in rows}):
   rs=[r for r in rows if r[kind]==value]
   groups.append({'group_type':kind,'group':value,'expected':len(rs),'n_companies':len({r['ticker'] for r in rs if r['score'] is not None}),**describe(r['score'] for r in rs)})
 sensitivity=[]
 for metric in ('score','cosine_log_rates','jaccard_one_hit','jaccard_three_hits','cosine_excluding_integrity_inclusion'):
  pairs=[r for r in valid if r.get(metric) is not None]
  sensitivity.append({'check':metric,**describe(r[metric] for r in pairs),'mean_absolute_difference_from_primary':statistics.mean(abs(r[metric]-r['score']) for r in pairs) if pairs else None})
 for check,subset in [('remove_scope_flagged',[r for r in valid if r['scope_sensitivity_retained']]),('snapshot_before_proxy',[r for r in valid if r['snapshot_on_or_before_filing'] is True])]:
  sensitivity.append({'check':check,**describe(r['score'] for r in subset)})
 companies=defaultdict(list)
 for r in valid:companies[r['ticker']].append(r['score'])
 cmeans=[statistics.mean(v) for v in companies.values()]
 within=[(x-statistics.mean(v))**2 for v in companies.values() for x in v]
 stats={'total_company_years':len(rows),'scored_company_years':len(valid),'scored_companies':len(companies),'adjacent_scored_pairs':len(changes),'primary':describe(r['score'] for r in valid),'company_equal_weight_mean':statistics.mean(cmeans) if cmeans else None,'variance_of_company_means':statistics.pvariance(cmeans) if cmeans else None,'mean_squared_within_company_deviation':statistics.mean(within) if within else None,'variance_caveat':'Descriptive unbalanced panel; these are not variance components or causal estimates.','exclusion_reasons':dict(Counter(reason for r in rows for reason in r['exclusion_reasons'])),'independent_human_validation':all(r['independent_human_validation'] for r in rows),'review_basis':'project_owner_confirmation_2026-10-19','all_scores_provisional':True,'network_requests':0}
 stats['negative_controls']={scope:describe(r['own_minus_other_mean'] for r in placebo if r['control_scope']==scope) for scope in ('same_year','same_sector_year')}
 for name,data in [('alignment',rows),('summary',stats),('group_summary',groups),('within_company_changes',changes),('sensitivity_checks',sensitivity),('negative_controls',placebo),('run_policy',policy)]:
  save(out/(name+'.json'),data)
  if isinstance(data,list):csvout(out/(name+'.csv'),data)
 # Deterministic audit queue: low, middle, high score with both source URLs.
 ordered=sorted(valid,key=lambda r:(r['score'],r['ticker'],r['year']))
 selected=sorted(set([0,len(ordered)//2,len(ordered)-1])) if ordered else []
 queue=[{**ordered[i],'review_status':'reviewed_no_changes_owner_confirmed','review_prompt':'Read both linked sources. Are these themes supported, whose proxy voice is counted, and does the score reflect meaningful alignment?'} for i in selected]
 save(out/'source_review_queue.json',queue)
 return stats

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--part1',type=Path,default=ROOT/'part1_stated_values/outputs/review_v2/part1_values_reviewed.json')
 p.add_argument('--part2',type=Path,default=ROOT/'part2_disclosed_priorities/outputs/proxy_v2/disclosure_metrics.json')
 p.add_argument('--output',type=Path,default=ROOT/'part3_alignment/outputs/alignment_v1')
 a=p.parse_args();print(json.dumps(analyze(a.part1,a.part2,a.output),indent=2))
if __name__=='__main__':main()
