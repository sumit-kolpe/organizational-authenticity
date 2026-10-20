"""Record the project owner's completed source review with no new data corrections.

This updates review *decisions* only: it does not manufacture missing source text,
revise themes, or change the original research results. Re-run Parts 3 and 4
and the report renderers after applying this step.
"""
from __future__ import annotations
import csv, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P1=ROOT/'part1_stated_values/outputs/review_v2'
P2=ROOT/'part2_disclosed_priorities/outputs/proxy_v2'
ATTESTATION_DATE='2026-10-19' # date of confirmation, not invented per-source review date
CHANGE_STATUS={'llm_compared_pending_review':'llm_compared_human_reviewed',
               'llm_repaired_pending_review':'llm_repaired_human_reviewed'}
NEW_SOURCE_STATUS={'coded_pending_review':'coded_human_reviewed',
                   'ai_reviewed_provisional':'coded_human_reviewed',
                   'excluded_link_hub_pending_replacement':'excluded_link_hub'}

def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
def write_csv(p,rows):
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()})

def apply():
 rows=load(P1/'part1_values_reviewed.json')
 assert len(rows)==450 and sum(r['eligible_for_provisional_analysis'] is True for r in rows)==140
 for r in rows:
  r.setdefault('original_processing_status',r['status'])
  r['status']=NEW_SOURCE_STATUS.get(r['status'],r['status'])
  r['independent_human_review']='completed_no_changes_owner_confirmed'
  r['human_review_attestation_date']=ATTESTATION_DATE
  r['human_review_disposition']='accepted_existing_source' if r['eligible_for_provisional_analysis'] is True else ('no_usable_source' if r['status']=='unavailable' else 'original_exclusion_retained')
  r['annual_selection_final']=r['eligible_for_provisional_analysis'] is True
  notes=r.get('analyst_notes')
  if isinstance(notes,dict):
   notes['comparison_status']=CHANGE_STATUS.get(notes.get('comparison_status'),notes.get('comparison_status'))
 save(P1/'part1_values_reviewed.json',rows);write_csv(P1/'part1_values_reviewed.csv',rows)
 comp=load(P1/'comparison_details.json')
 for r in comp:r['comparison_status']=CHANGE_STATUS.get(r.get('comparison_status'),r.get('comparison_status'))
 save(P1/'comparison_details.json',comp)
 s=load(P1/'review_summary.json')
 s.update(independent_human_validation=True,human_review_completion='completed_no_changes_owner_confirmed',human_review_confirmation_date=ATTESTATION_DATE,human_reviewed_inventory_rows=450,final_accepted_annual_selections=140,statuses=dict(Counter(r['status'] for r in rows)))
 save(P1/'review_summary.json',s)

 metrics=load(P2/'disclosure_metrics.json')
 assert len(metrics)==450 and sum(r['status']=='downloaded' for r in metrics)==443
 for r in metrics:
  usable=r['status']=='downloaded'
  r['human_review_status']='completed_no_changes_owner_confirmed'
  r['human_review_attestation_date']=ATTESTATION_DATE
  r['human_review_disposition']='accepted_existing_proxy' if usable else 'original_missingness_retained'
  if usable:r['analysis_status']='lexically_analyzed_human_reviewed'
 save(P2/'disclosure_metrics.json',metrics);write_csv(P2/'disclosure_metrics.csv',metrics)
 inventory=load(P2/'inventory.json')
 for r in inventory:
  r['manual_review_status']='completed_no_changes_owner_confirmed'
  r['human_review_attestation_date']=ATTESTATION_DATE
  r['human_review_disposition']='accepted_existing_proxy' if r['status']=='downloaded' else 'original_missingness_retained'
  r['annual_selection_final']=r['status']=='downloaded'
 save(P2/'inventory.json',inventory)
 cov=load(P2/'coverage_summary.json')
 cov.update(independent_human_validation=True,human_review_completion='completed_no_changes_owner_confirmed',human_reviewed_inventory_rows=450,reviewed_existing_disclosure_documents=443)
 save(P2/'coverage_summary.json',cov)
 policy=load(P2/'run_policy.json')
 policy['human_source_review']='completed_no_changes_owner_confirmed_2026-10-19'
 save(P2/'run_policy.json',policy)

 status={'item':'independent_human_source_validation','status':'completed_no_changes_owner_confirmed',
  'owner_confirmation_date':ATTESTATION_DATE,
  'scope':'Owner confirmed completing human review of the project; no additional corrections identified.',
  'basis':'Project-owner statement. Historical source documents were not rechecked independently in this packaging pass.',
  'part1_inventory_rows_review_disposition_recorded':450,
  'part1_accepted_existing_sources':140,
  'part1_unavailable_or_excluded_rows_retained':310,
  'part2_inventory_rows_review_disposition_recorded':450,
  'part2_accepted_existing_proxy_documents':443,
  'part2_missing_documents_retained':7,
  'underlying_text_themes_and_metrics_modified':False,
  'downstream_outputs_to_regenerate':True}
 save(ROOT/'docs/human_source_validation_status.json',status)
 print('Human-review completion recorded: 450 Part 1 dispositions (140 accepted), 450 Part 2 dispositions (443 accepted).')

if __name__=='__main__':apply()
