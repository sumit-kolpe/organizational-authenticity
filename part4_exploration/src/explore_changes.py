"""Offline exploratory comparisons using reviewed source inventory and index results."""
import argparse,csv,hashlib,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
VERSION='exploration_v1.0'
ALLOWED={'identical_extracted_blocks','llm_compared_human_reviewed','llm_repaired_human_reviewed'}
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2,allow_nan=False),encoding='utf-8')
def write_csv(p,rows):
 if not rows:p.write_text('',encoding='utf-8');return
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()})
def index(rows):
 result={}
 for r in rows:
  key=(r['ticker'],r['year'])
  if key in result:raise ValueError('Duplicate key: '+str(key))
  result[key]=r
 return result
def cosine(a,b):
 if len(a)!=len(b) or any(not math.isfinite(x) or x<0 for x in a+b):raise ValueError('Invalid vectors')
 n=math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
 if not n:raise ValueError('Zero vector in scored observation')
 return min(1.,max(0.,sum(x*y for x,y in zip(a,b))/n))
def decompose(s0,d0,s1,d1):
 f00=cosine(s0,d0);f10=cosine(s1,d0);f01=cosine(s0,d1);f11=cosine(s1,d1)
 stated=((f10-f00)+(f11-f01))/2
 disclosure=((f01-f00)+(f11-f10))/2
 return stated,disclosure
def stats(vals):
 v=list(vals)
 return {'n':len(v),'mean':statistics.mean(v) if v else None,'median':statistics.median(v) if v else None,'min':min(v) if v else None,'max':max(v) if v else None}
def contrast(rows,label='recorded_text_changed'):
 groups={b:[r for r in rows if r.get(label) is b] for b in (False,True)}
 out={}
 for b,rs in groups.items():
  out['changed' if b else 'unchanged']={'n_companies':len({r['ticker'] for r in rs}),'absolute_change':stats(r['absolute_score_change'] for r in rs),'signed_change':stats(r['score_change'] for r in rs)}
 m=[out[k]['absolute_change']['mean'] for k in ('changed','unchanged')]
 out['changed_minus_unchanged_absolute_mean']=m[0]-m[1] if None not in m else None
 return out
def build_pairs(values,alignment):
 a=index(values);b=index(alignment)
 if set(a)!=set(b) or len(a)!=450:raise ValueError('Expected matching 450-row panels')
 pairs=[]
 for (ticker,y),cur in sorted(b.items()):
  prev=b.get((ticker,y-1))
  if not prev or cur.get('score') is None or prev.get('score') is None:continue
  for row in (prev,cur):
   if not math.isclose(cosine(row['stated_vector'],row['disclosure_rates']),row['score'],abs_tol=1e-10):raise ValueError('Stored score/vector mismatch')
  v=a[ticker,y];old=a[ticker,y-1]
  for vr,ar in ((v,cur),(old,prev)):
   if vr.get('eligible_for_provisional_analysis') is not True:raise ValueError('Ineligible Part 1 row has score')
  status=v['analyst_notes'].get('comparison_status');decision=v.get('changed_from_prior')
  label=decision if type(decision) is bool and status in ALLOWED else None
  ds,dd=decompose(prev['stated_vector'],prev['disclosure_rates'],cur['stated_vector'],cur['disclosure_rates'])
  delta=cur['score']-prev['score']
  if not math.isclose(ds+dd,delta,abs_tol=1e-10):raise ValueError('Decomposition mismatch')
  pairs.append(dict(ticker=ticker,sector=cur['sector'],year=y,previous_year=y-1,previous_score=prev['score'],score=cur['score'],score_change=delta,absolute_score_change=abs(delta),recorded_text_changed=label,comparison_status=status,theme_set_changed=cur['stated_vector']!=prev['stated_vector'],stated_profile_component=ds,proxy_profile_component=dd,scope_sensitivity_retained=cur.get('scope_sensitivity_retained') is True and prev.get('scope_sensitivity_retained') is True,previous_values_url=old.get('snapshot_url'),values_url=v.get('snapshot_url'),previous_proxy_url=prev.get('proxy_url'),proxy_url=cur.get('proxy_url')))
 return pairs
def analyze(p1,p3,out):
 provenance=p3.parent/'run_policy.json'
 if not provenance.exists() or read(provenance)['part1_sha256']!=sha(p1):raise ValueError('Part 1 input does not match Part 3 provenance')
 policy={'version':VERSION,'part1_sha256':sha(p1),'alignment_sha256':sha(p3),'alignment_policy_sha256':sha(provenance),'question':'Is absolute alignment change larger when Part 1 records a text change?','design':'exploratory descriptive association; no causal identification','label_statuses':sorted(ALLOWED)}
 out.mkdir(parents=True,exist_ok=True)
 if (out/'run_policy.json').exists() and read(out/'run_policy.json')!=policy:raise ValueError('Changed inputs: choose a new --output directory')
 pairs=build_pairs(read(p1),read(p3));known=[r for r in pairs if r['recorded_text_changed'] is not None]
 company=[]
 for t in sorted({r['ticker'] for r in known}):
  rs=[r for r in known if r['ticker']==t];c=contrast(rs)
  company.append({'ticker':t,'n_changed':c['changed']['absolute_change']['n'],'n_unchanged':c['unchanged']['absolute_change']['n'],'changed_mean':c['changed']['absolute_change']['mean'],'unchanged_mean':c['unchanged']['absolute_change']['mean'],'within_company_difference':c['changed_minus_unchanged_absolute_mean']})
 both=[r for r in company if r['within_company_difference'] is not None]
 loo=[{'omitted_ticker':t,'difference':contrast([r for r in known if r['ticker']!=t])['changed_minus_unchanged_absolute_mean']} for t in sorted({r['ticker'] for r in known})]
 stable=[r for r in pairs if not r['theme_set_changed']]
 summary={'adjacent_scored_pairs':len(pairs),'known_text_comparison_pairs':len(known),'unknown_text_comparison_pairs':len(pairs)-len(known),'companies_with_known_pairs':len(company),'primary':contrast(known),'theme_set_sensitivity_all_adjacent_pairs':contrast(pairs,'theme_set_changed'),'scope_sensitivity':contrast([r for r in known if r['scope_sensitivity_retained']]),'company_balanced_within_company_difference':stats(r['within_company_difference'] for r in both),'leave_one_company_out_difference':stats(r['difference'] for r in loo if r['difference'] is not None),'largest_company_pair_count':max(Counter(r['ticker'] for r in known).values(),default=0),'unchanged_theme_pairs':len(stable),'unchanged_theme_absolute_alignment_change':stats(r['absolute_score_change'] for r in stable),'max_decomposition_residual':max((abs(r['score_change']-r['stated_profile_component']-r['proxy_profile_component']) for r in pairs),default=0),'interpretation':'Association and exact algebraic attribution, not causal effects. Both sources are communications; historical source differences still limit interpretation.','independent_human_validation':all(r.get('independent_human_validation') is True for r in read(p3)),'review_basis':'project_owner_confirmation_2026-10-19','network_requests':0}
 disagreements=[r for r in known if r['recorded_text_changed'] is False and r['theme_set_changed']]
 summary['unchanged_text_but_changed_themes']=len(disagreements)
 summary['excluding_label_theme_disagreements']=contrast([r for r in known if not (r['recorded_text_changed'] is False and r['theme_set_changed'])])
 save(out/'label_theme_review_queue.json',[{**r,'review_status':'reviewed_no_changes_owner_confirmed','issue':'Recorded unchanged text with changed coded theme set; inspect source/coding scope before correction.'} for r in disagreements])
 for name,obj in [('pairs',pairs),('company_comparisons',company),('leave_one_company_out',loo),('summary',summary),('run_policy',policy)]:
  save(out/(name+'.json'),obj)
  if isinstance(obj,list):write_csv(out/(name+'.csv'),obj)
 return summary
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--part1',type=Path,default=ROOT/'part1_stated_values/outputs/review_v2/part1_values_reviewed.json')
 p.add_argument('--alignment',type=Path,default=ROOT/'part3_alignment/outputs/alignment_v1/alignment.json')
 p.add_argument('--output',type=Path,default=ROOT/'part4_exploration/outputs/exploration_v1')
 a=p.parse_args();print(json.dumps(analyze(a.part1,a.alignment,a.output),indent=2))
if __name__=='__main__':main()
