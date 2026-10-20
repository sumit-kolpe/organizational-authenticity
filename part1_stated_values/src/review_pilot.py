"""Offline, source-specific review of the six v1 pilot responses; no API calls.
Preserves raw model output and records every evidence correction explicitly.
This is an assistant-assisted audit, not an independent human evaluation.
"""
import copy
import hashlib
import json
from pathlib import Path
from . import gemini_pilot as pilot

REPLACEMENTS = {
 'NVDA': {'community': 'Our passion for delivering the best in visual computing technology extends to making a contribution to our communities .'},
 'JPM': {
 'community': 'Leverage our success in order to give back to the communities where we do business',
 'inclusion': 'Excel by embracing an inclusive work environment and diverse teams',
 'innovation': 'Innovate, test and learn — we know some ideas will fail, and that’s okay',
 'integrity': 'At JPMorganChase, acting with integrity is paramount — and it applies to every aspect of our company.',
 'people': 'Respect people’s personal lives and show compassion when an employee is struggling',
 'performance': 'We set the highest standards of performance',
 'security_privacy': 'Build a safety-first culture'}}
NOTES = {
 'MSFT': ['Values-section descriptions are substantive, but navigation contaminates the extraction. Clean body before scaling.', 'A CSR report is not required for Part 1; concise values descriptions can be relevant.'],
 'AAPL': ['Careers-page scope; recruitment emphasis limits comparability.', 'Customer quotation is attributed to Ehsan, Engineering Manager in the archived HTML; removed from corporate-statement coding.'],
 'NVDA': ['Culture/recruitment page with substantive claims and trailing navigation.', 'Community quote corrected only by restoring the source space before the period.'],
 'AMZN': ['Exclude this link-heavy source from thematic analysis; find the archived Leadership Principles destination. The brief Day 1 statement alone is insufficient for broad values coverage.'],
 'GOOGL': ['Historical founding/restructuring letter displayed in 2024. Capture year is not authorship year.', 'Retain only as a documented historical-letter source; do not infer fresh 2024 priorities.', 'No requirement to be a sustainability report for Part 1.'],
 'JPM': ['Business-principles statements have substantive content; news/navigation contamination needs cleaning.', 'Quotes replaced by shorter exact source spans. Original model wording and rationale remain in model_coding.', 'Safety/control quotation concerns internal risk controls; interpretation is narrow, not evidence of a privacy commitment.']}


def review(row, text, raw):
    c=raw['candidates'][0]
    if c.get('finishReason')!='STOP': raise ValueError('Incomplete response')
    coding=json.loads(''.join(p.get('text','') for p in c['content']['parts'] if not p.get('thought')))
    original=copy.deepcopy(coding); edits=[]; invalid=[]
    for item in coding['themes']:
        if not isinstance(item.get('quote'),str) or len(item['quote'])<25 or item['quote'] not in text:
            invalid.append(item['category'])
        replacement=REPLACEMENTS.get(row['ticker'],{}).get(item['category'])
        if replacement:
            if replacement not in text: raise ValueError('Review patch does not match source; stop')
            edits.append({'category':item['category'],'old_quote':item['quote'],'new_quote':replacement,
                          'reason':'Explicit source-specific correction; no fuzzy matching or relaxed validator'})
            item['quote']=replacement
            item['rationale']='Assistant review: exact source passage supports '+item['category']+' under the proposed taxonomy.'
    if row['ticker']=='AAPL':
        removed=[x for x in coding['themes'] if x['category']=='customer']
        coding['themes']=[x for x in coding['themes'] if x['category']!='customer']
        edits.append({'category':'customer','action':'removed','evidence':removed,'reason':NOTES['AAPL'][1]})
    if row['ticker']!='AMZN': coding['suitability']='mixed'
    coding['concerns']=list(dict.fromkeys(coding['concerns']+NOTES[row['ticker']]))
    if row['ticker']=='MSFT': coding['source_scope']='Corporate values section embedded in navigation-heavy extraction.'
    if row['ticker']=='GOOGL': coding['source_scope']='Historical Alphabet founding/restructuring letter still displayed in the 2024 capture.'
    pilot.validate(coding,text)
    return {**{k:row.get(k) for k in ('ticker','year','sector','snapshot_url','text_sha256')},
            'reviewer':'assistant_source_review_v1','independent_human_evaluation':False,
            'manual_review_status':'pending','annual_selection_final':False,
            'original_invalid_categories':invalid,'model_coding':original,'reviewed_coding':coding,
            'review_edits':edits,'status':'excluded_source' if row['ticker']=='AMZN' else 'reviewed_pilot_pending_human_review'}


def main():
    results=[]
    for row,text in pilot.tasks():
        model='gemini-3.1-flash-lite'
        signature=hashlib.sha256((model+'\n'+pilot.PROMPT+'\n'+text).encode()).hexdigest()
        cache=pilot.OUT/'cache'/f'{signature}.json'
        raw=json.loads(cache.read_text(encoding='utf-8'))
        result=review(row,text,raw)
        result.update(model=model,cache_sha256=hashlib.sha256(cache.read_bytes()).hexdigest(),
                      prompt_sha256=hashlib.sha256(pilot.PROMPT.encode()).hexdigest())
        results.append(result)
    dest=pilot.ROOT/'part1_stated_values/outputs/pilot_review_v1'
    pilot.save(dest/'reviewed_pilot_results.json',results)
    summary={'observations':len(results),'raw_responses_with_invalid_quotes':sum(bool(x['original_invalid_categories']) for x in results),
             'invalid_quotes':sum(len(x['original_invalid_categories']) for x in results),
             'excluded_sources':[x['ticker'] for x in results if x['status']=='excluded_source'],
             'network_requests':0,'warning':'Source-specific assistant review, not model accuracy evaluation or final annual selection.'}
    pilot.save(dest/'review_summary.json',summary)
    print(json.dumps(summary,indent=2))
    print('Saved:',dest)

if __name__=='__main__': main()
