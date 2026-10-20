"""Apply documented ten-observation model-supported review, offline and reproducibly."""
import csv,hashlib,json
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'part1_stated_values/outputs/review_v1'
RAW=ROOT/'part1_stated_values/outputs/values_v2'
CAP=ROOT/'part1_stated_values/data/batch_v1/captures'
DECISIONS=ROOT/'part1_stated_values/config/ai_review_decisions.json'
OUT=ROOT/'part1_stated_values/outputs/review_v2'
class Text(HTMLParser):
 def __init__(self):super().__init__();self.parts=[]
 def handle_data(self,d):self.parts.append(d)
def norm(s):return ' '.join(s.split())
def dump(name,v): (OUT/name).write_text(json.dumps(v,indent=2,ensure_ascii=False),encoding='utf-8')
def table(name,rows,fields):
 with (OUT/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(r.get(k),ensure_ascii=False) if isinstance(r.get(k),(dict,list)) else r.get(k) for k in fields})
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=json.loads((BASE/'part1_values_reviewed.json').read_text(encoding='utf-8'))
 raw=json.loads((RAW/'analysis_results.json').read_text(encoding='utf-8'));idx={(r['ticker'],r['year']):r for r in rows};ri={(r['ticker'],r['year']):r for r in raw}
 ds=json.loads(DECISIONS.read_text(encoding='utf-8'));keys={(d['ticker'],d['year']) for d in ds};evidence=list(csv.DictReader((BASE/'theme_evidence.csv').open(encoding='utf-8-sig')))
 evidence=[e for e in evidence if (e['ticker'],int(e['year'])) not in keys];audit=[];worksheet=[]
 for d in ds:
  key=(d['ticker'],d['year']);r=idx[key];src=ri[key];assert d['source_text_sha256']==src['text_sha256']
  files=list(CAP.glob(f"{d['ticker']}_{src['snapshot_timestamp']}_*.html"));assert len(files)==1
  body=files[0].read_bytes();meta=json.loads(files[0].with_suffix('.json').read_text(encoding='utf-8'));assert hashlib.sha256(body).hexdigest()==meta['sha256']
  parser=Text();parser.feed(body.decode('utf-8',errors='replace'));htmltext=norm(' '.join(parser.parts))
  blocks={b['id']:dict(b) for b in src['blocks']}
  for b in d['recovered_blocks']:
   assert norm(b['text']) in htmltext,'Recovered text not in source HTML'
   blocks[b['id']]={**b,'kind':'body_recovered_from_html'}
  for cat,ids in d['themes'].items():
   for i in ids:
    assert i in blocks
    assert norm(blocks[i]['text']) in htmltext,'Evidence not found in HTML'
    evidence.append({'ticker':key[0],'year':key[1],'category':cat,'block_id':i,'text':blocks[i]['text'],'snapshot_url':r['snapshot_url'],'rationale':'model-supported source review; see ai_quality_review.csv','review_type':'model_supported'})
  before={'theme_categories':r['theme_categories'],'status':r['status'],'page_text_clean':r['page_text_clean']}
  r['page_text_clean']='\n\n'.join(blocks[i]['text'] for i in d['keep_ids']+[b['id'] for b in d['recovered_blocks']])
  excluded=d['decision']=='Exclude';r['theme_categories']=None if excluded else list(d['themes']);r['eligible_for_provisional_analysis']=not excluded
  r['status']='excluded_after_ai_review' if excluded else 'ai_reviewed_provisional';r['ai_review_status']='completed';r['independent_human_review']='not_performed';r['annual_selection_final']=False
  r['analyst_notes']['ai_review']={k:d[k] for k in ('decision','source_suitable','theme_precision_notes','missing_themes','cleaning_notes')};r['analyst_notes']['human_review']='not_performed'
  audit.append({'ticker':key[0],'year':key[1],'before':before,'after_themes':r['theme_categories'],'decision':d['decision'],'source_html_sha256':meta['sha256'],'review_type':'model_supported'})
  worksheet.append({**{k:d[k] for k in ('ticker','year','source_suitable','theme_precision_notes','missing_themes','cleaning_notes','decision')},'reviewer':'OpenAI assistant','review_type':'model-supported quality review','independent_human_validation':False})
 # Existing comparisons were computed on the old extraction. Preserve, but do not
 # silently present them as comparisons of the revised observation texts.
 comparisons=json.loads((BASE/'comparison_details.json').read_text(encoding='utf-8'))
 invalidated=[]
 for c in comparisons:
  key=(c['ticker'],c['year']);r=idx[key]
  if key in keys or (key[0],key[1]-1) in keys:
   if r['changed_from_prior'] is not None:
    invalidated.append({'ticker':key[0],'year':key[1],'original_changed_from_prior':r['changed_from_prior']})
    c['pre_review_comparison']=dict(c);c['changed_from_prior']=None;c['comparison_status']='review_changed_source_recomparison_pending'
    r['changed_from_prior']=None;r['analyst_notes']['comparison_status']=c['comparison_status']
 for r in rows:
  r.setdefault('ai_review_status','not_in_ten_observation_sample')
  r.setdefault('independent_human_review','not_performed')
 dump('part1_values_reviewed.json',rows);table('part1_values_reviewed.csv',rows,list(rows[0]))
 table('theme_evidence.csv',evidence,['ticker','year','category','block_id','text','snapshot_url','rationale','review_type'])
 table('ai_quality_review.csv',worksheet,list(worksheet[0]));dump('ai_review_audit.json',audit);dump('comparison_details.json',comparisons)
 dump('invalidated_comparisons.json',invalidated)
 coverage=[{'year':y,'expected':50,'coded':sum(r['year']==y and r['eligible_for_provisional_analysis'] for r in rows),'comparison_known':sum(r['year']==y and r['changed_from_prior'] is not None for r in rows)} for y in range(2016,2025)]
 table('coverage_by_year.csv',coverage,list(coverage[0]))
 summary={'total_rows':len(rows),'eligible_observations':sum(r['eligible_for_provisional_analysis'] for r in rows),'eligible_companies':len({r['ticker'] for r in rows if r['eligible_for_provisional_analysis']}),'reviewed_observations':10,'excluded_by_this_review':1,'known_comparisons':sum(r['changed_from_prior'] is not None for r in rows),'changed_true':sum(r['changed_from_prior'] is True for r in rows),'changed_false':sum(r['changed_from_prior'] is False for r in rows),'comparisons_invalidated':len(invalidated),'independent_human_validation':False,'statuses':dict(Counter(r['status'] for r in rows)),'theme_counts':dict(Counter(t for r in rows for t in (r['theme_categories'] or []))),'coverage_by_year':coverage}
 dump('review_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
