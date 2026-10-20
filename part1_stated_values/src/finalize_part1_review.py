"""Offline, conservative Part 1 export. No API calls or silent failure conversion.
Run from project root; preserves values_v2 and all raw responses.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'part1_stated_values/outputs/values_v2'
OUT=ROOT/'part1_stated_values/outputs/review_v1'

def write_json(name,value):
 (OUT/name).write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
def table(name,rows,fields):
 with (OUT/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 rows=json.loads((SOURCE/'analysis_results.json').read_text(encoding='utf-8'))
 assert len(rows)==450 and len({(r['ticker'],r['year']) for r in rows})==450
 index={(r['ticker'],r['year']):r for r in rows}
 exported=[];evidence=[];issues=[];changes=[];audit=[]
 for r in rows:
  usable=r['status']=='coded_pending_review';coding=r.get('coding',{});themes=[];flags=list(r.get('quality_flags',[]))
  if r['ticker']=='GOOGL':flags.append('historical_founding_letter_not_new_annual_commitments')
  if r['ticker'] in ('AAPL','NVDA'):flags.append('recruitment_scope')
  if r['ticker']=='ABT':flags.append('product_and_award_content_requires_semantic_review')
  if usable:
   blocks={b['id']:b for b in r['blocks']}
   for t in coding['themes']:
    # One reviewed false positive: a financial-report link is not a stated performance value.
    if t['category']=='performance' and all(e['text'].strip()=="Learn more about Wells Fargo's financial performance." for e in t['evidence']):
     audit.append({'ticker':r['ticker'],'year':r['year'],'action':'remove_theme','category':'performance','reason':'Financial-report navigation pointer, not a substantive commitment','original':t});continue
    for e in t['evidence']:
     assert e['id'] in blocks and e['text']==blocks[e['id']]['text']
     assert blocks[e['id']]['kind']=='body'
     evidence.append({'ticker':r['ticker'],'year':r['year'],'category':t['category'],'block_id':e['id'],'text':e['text'],'snapshot_url':r['snapshot_url'],'rationale':t['rationale']})
    themes.append(t['category'])
  if 'failed' in r['status'] or 'failed' in r['comparison_status']:
   issues.append({'ticker':r['ticker'],'year':r['year'],'status':r['status'],'error':r.get('error'),'comparison_status':r['comparison_status'],'comparison_error':r.get('comparison_error'),'comparison_repair_error':r.get('comparison_repair_error'),'disposition':'Retain missing; no blanket validation relaxation'})
  change=r.get('changed_from_prior')
  if change is not None:
   previous=index.get((r['ticker'],r['year']-1));assert previous and usable and previous['status']=='coded_pending_review'
  comparison=r.get('comparison',{})
  if r['comparison_status']=='comparison_validation_failed':change=None
  changes.append({'ticker':r['ticker'],'year':r['year'],'changed_from_prior':change,'comparison_status':r['comparison_status'],'summary':comparison.get('summary',''),'linguistic_shift':r.get('linguistic_shift',''),'comparable':comparison.get('comparable'),'evidence':comparison.get('evidence',[])})
  notes={'source_scope':coding.get('source_scope'),'source_suitability':coding.get('suitability'),'flags':flags,'concerns':coding.get('concerns',[]),'language':coding.get('language'),'comparison_status':r['comparison_status'],'linguistic_shift':r.get('linguistic_shift'),'error':r.get('error'),'human_review':'pending'}
  exported.append({'ticker':r['ticker'],'company_name':r.get('company_name'),'sector':r.get('sector'),'year':r['year'],
   'page_text_clean':'\n\n'.join(b['text'] for b in r['blocks'] if b['kind']!='quotation_or_testimonial'),
   'changed_from_prior':change,'theme_categories':themes if usable else None,'analyst_notes':notes,
   'status':r['status'],'snapshot_url':r.get('snapshot_url'),'snapshot_timestamp':r.get('snapshot_timestamp'),
   'eligible_for_provisional_analysis':usable,'independent_human_review':'pending','annual_selection_final':False})
 write_json('part1_values_reviewed.json',exported);write_json('comparison_details.json',changes);write_json('remaining_issues.json',issues);write_json('review_edits.json',audit)
 table('part1_values_reviewed.csv',[{**r,'theme_categories':json.dumps(r['theme_categories']) if r['theme_categories'] is not None else '', 'analyst_notes':json.dumps(r['analyst_notes'],ensure_ascii=False)} for r in exported],list(exported[0]))
 table('theme_evidence.csv',evidence,['ticker','year','category','block_id','text','snapshot_url','rationale'])
 coverage=[]
 for year in range(2016,2025):
  subset=[r for r in exported if r['year']==year];coverage.append({'year':year,'expected':50,'coded':sum(r['eligible_for_provisional_analysis'] for r in subset),'coding_failed':sum(r['status']=='coding_validation_failed' for r in subset),'comparison_known':sum(r['changed_from_prior'] is not None for r in subset)})
 table('coverage_by_year.csv',coverage,list(coverage[0]))
 counts=Counter(t for r in exported if r['eligible_for_provisional_analysis'] for t in r['theme_categories'])
 summary={'total_rows':450,'coded_observations':sum(r['eligible_for_provisional_analysis'] for r in exported),'coded_companies':len({r['ticker'] for r in exported if r['eligible_for_provisional_analysis']}),'statuses':dict(Counter(r['status'] for r in exported)),'comparison_statuses':dict(Counter(r['comparison_status'] for r in rows)),'changed_true':sum(r['changed_from_prior'] is True for r in exported),'changed_false':sum(r['changed_from_prior'] is False for r in exported),'changed_unknown':sum(r['changed_from_prior'] is None for r in exported),'theme_observation_counts':dict(counts),'coverage_by_year':coverage,'explicit_review_edits':len(audit),'source_sha256':hashlib.sha256((SOURCE/'analysis_results.json').read_bytes()).hexdigest(),'independent_human_review_completed':False,'final_annual_selections':0}
 write_json('review_summary.json',summary)
 # Review worksheet is not falsely labelled a completed human evaluation.
 sample=[('AAPL',2024),('ABT',2020),('CVX',2024),('JPM',2024),('MSFT',2024),('GOOGL',2024),('NVDA',2022),('WFC',2024),('TSLA',2024),('COP',2024)]
 table('human_review_worksheet.csv',[{'ticker':t,'year':y,'reviewer':'','source_suitable':'','theme_precision_notes':'','missing_themes':'','cleaning_notes':'','decision':''} for t,y in sample],['ticker','year','reviewer','source_suitable','theme_precision_notes','missing_themes','cleaning_notes','decision'])
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
