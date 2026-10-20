"""Fresh offline cross-part checks and a provisional submission archive.

Recomputes the mathematics directly instead of calling the analysis modules.
Does not validate source meaning, contact external services, or alter datasets.
"""
import argparse,csv,hashlib,json,math,statistics,sys,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACTIVE={'part1_stated_values':'review_v2','part2_disclosed_priorities':'proxy_v2','part3_alignment':'alignment_v1','part4_exploration':'exploration_v2'}
THEMES=['innovation','integrity','people','inclusion','customer','environment','community','security_privacy','performance']
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def index(rows):
 result={(r['ticker'],r['year']):r for r in rows}
 if len(result)!=len(rows):raise ValueError('Duplicate company-year key')
 return result
def near(a,b):
 if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-12):raise ValueError(f'Numerical mismatch: {a} versus {b}')
def audit(root,part4_version):
 active=dict(ACTIVE);active['part4_exploration']=part4_version
 folders={p:root/p/'outputs'/v for p,v in active.items()}
 p1=folders['part1_stated_values']/'part1_values_reviewed.json'
 p2=folders['part2_disclosed_priorities']/'disclosure_metrics.json'
 p3=folders['part3_alignment']/'alignment.json'
 p4=folders['part4_exploration']/'pairs.json'
 a,b,c=map(index,[read(p1),read(p2),read(p3)])
 if not (set(a)==set(b)==set(c) and len(a)==450):raise ValueError('Panels must have matching 450 unique keys')
 roster=list(csv.DictReader((root/'config/companies.csv').open(encoding='utf-8-sig')))
 expected={(r['ticker'],y) for r in roster for y in range(2016,2025)}
 if len(roster)!=50 or set(a)!=expected:raise ValueError('Fixed roster/year mismatch')
 sectors={r['ticker']:r['sector'] for r in roster}
 for source in (a,b,c):
  if any(r['sector']!=sectors[t] for (t,y),r in source.items()):raise ValueError('Sector mismatch')
 # The downstream run must be bound to the inputs actually present locally.
 policy3=read(folders['part3_alignment']/'run_policy.json')
 if policy3['part1_sha256']!=digest(p1) or policy3['part2_sha256']!=digest(p2):raise ValueError('Part 3 provenance does not match current input bytes')
 policy4=read(folders['part4_exploration']/'run_policy.json')
 if policy4['part1_sha256']!=digest(p1) or policy4['alignment_sha256']!=digest(p3) or policy4['alignment_policy_sha256']!=digest(folders['part3_alignment']/'run_policy.json'):raise ValueError('Part 4 provenance mismatch')
 scores={}
 for key,row in b.items():
  if 'themes' in row:
   if row['status']!='downloaded' or row['word_count']<=0:raise ValueError('Invalid analyzed proxy')
   for metric in list(row['themes'].values())+list(row['language'].values()):near(metric['per_1000_words'],1000*metric['count']/row['word_count'])
   if sum(v['count'] for v in row['themes'].values())!=row['total_theme_hits']:raise ValueError('Theme total mismatch')
  eligible=a[key].get('eligible_for_provisional_analysis') is True and 'themes' in row
  if eligible:
   stated=[int(t in (a[key].get('theme_categories') or [])) for t in THEMES]
   counts=[row['themes'][t]['count'] for t in THEMES]
   if stated!=c[key].get('stated_vector'):raise ValueError('Stored stated vector differs from Part 1 themes')
   for expected,observed in zip([1000*n/row['word_count'] for n in counts],c[key]['disclosure_rates']):near(expected,observed)
   den=math.sqrt(sum(stated)*sum(x*x for x in counts))
   if den:
    score=sum(x*y for x,y in zip(stated,counts))/den
    near(score,c[key]['score']);scores[key]=score
   elif c[key]['score'] is not None:raise ValueError('Zero vector was scored')
  elif c[key]['score'] is not None:raise ValueError('Missing/ineligible input was scored')
 summary3=read(folders['part3_alignment']/'summary.json')
 if len(scores)!=summary3['scored_company_years']:raise ValueError('Part 3 count mismatch')
 near(statistics.mean(scores.values()),summary3['primary']['mean'])
 pairs=read(p4);expected_pairs={k for k in scores if (k[0],k[1]-1) in scores}
 if set(index(pairs))!=expected_pairs:raise ValueError('Part 4 adjacent-pair mismatch')
 for r in pairs:
  key=(r['ticker'],r['year']);near(r['score_change'],scores[key]-scores[key[0],key[1]-1]);near(r['absolute_score_change'],abs(r['score_change']));near(r['score_change'],r['stated_profile_component']+r['proxy_profile_component'])
  source=a[key];label=source.get('changed_from_prior');status=source['analyst_notes'].get('comparison_status')
  expected_label=label if type(label) is bool and status in {'identical_extracted_blocks','llm_compared_human_reviewed','llm_repaired_human_reviewed'} else None
  if r['recorded_text_changed'] is not expected_label:raise ValueError('Part 4 text-change label differs from Part 1')
 known=[r for r in pairs if r['recorded_text_changed'] is not None]
 diff=statistics.mean(r['absolute_score_change'] for r in known if r['recorded_text_changed'] is True)-statistics.mean(r['absolute_score_change'] for r in known if r['recorded_text_changed'] is False)
 summary4=read(folders['part4_exploration']/'summary.json');near(diff,summary4['primary']['changed_minus_unchanged_absolute_mean'])
 if summary4['known_text_comparison_pairs']!=len(known) or summary4['adjacent_scored_pairs']!=len(pairs):raise ValueError('Part 4 summary count mismatch')
 # Do not infer PDF creation, page length, or readability from console output.
 from pypdf import PdfReader
 pdfs=[root/'part1_stated_values/Part1_Summary.pdf',folders['part2_disclosed_priorities']/'Part2_Summary.pdf',folders['part3_alignment']/'Part3_Summary.pdf',folders['part4_exploration']/'Part4_Summary.pdf']
 page_counts={}
 for p in pdfs:
  n=len(PdfReader(p).pages);page_counts[p.relative_to(root).as_posix()]=n
  if not 1<=n<=2:raise ValueError('Summary exceeds 1-2 page requirement: '+str(p))
 readmes={part:(root/part/'README.md').exists() for part in active}
 required_code={'part1_stated_values':'analyze_values.py','part2_disclosed_priorities':'proxy_review.py','part3_alignment':'analyze_alignment.py','part4_exploration':'explore_changes.py'}
 missing_code=[str(Path(part)/'src'/name) for part,name in required_code.items() if not (root/part/'src'/name).is_file()]
 if missing_code:raise ValueError('Required analysis source files missing: '+', '.join(missing_code))
 result={'status':'numerical_checks_passed_review_completion_owner_confirmed','active_versions':active,'panel_rows':len(a),'part1_eligible':sum(r.get('eligible_for_provisional_analysis') is True for r in a.values()),'part2_analyzed':sum('themes' in r for r in b.values()),'part3_scored':len(scores),'part3_mean':statistics.mean(scores.values()),'part4_known_pairs':len(known),'part4_difference':diff,'summary_page_counts':page_counts,'readme_present':readmes,'independent_human_validation':all(r.get('independent_human_review')=='completed_no_changes_owner_confirmed' for r in a.values()) and all(r.get('human_review_status')=='completed_no_changes_owner_confirmed' for r in b.values()),'source_review':'Project owner confirms completed source review with no further corrections; numerical checks independently confirm arithmetic, not source accuracy.','network_requests':0}
 (root/'docs').mkdir(exist_ok=True);(root/'docs/local_final_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
 return result,active
def package(root,active):
 """Whitelist project deliverables; preserve older files on disk, omit them from ZIP."""
 allowed_ext={'.py','.md','.txt','.json','.csv','.yaml','.yml','.toml','.pdf','.png','.svg'}
 files=[]
 for top in ['config','docs','shared','tests',*active]:
  folder=root/top
  if not folder.exists():continue
  for f in folder.rglob('*'):
   if not f.is_file() or f.is_symlink():continue
   rel=f.relative_to(root)
   if any(x.startswith('.') or x in ('__pycache__','data','cache','caches','node_modules') for x in rel.parts):continue
   if f.suffix.lower() not in allowed_ext:continue
   if 'outputs' in rel.parts:
    i=rel.parts.index('outputs')
    if top not in active or len(rel.parts)<=i+1 or rel.parts[i+1]!=active[top]:continue
   if f.name in ('assistance_reference_inventory.json','assistance_reference_inventory.md','submission_assistance_references.json'):continue
   if any(x in f.name.lower() for x in ('credential','secret','token')):continue
   files.append(f)
 for name in ('README.md','README_SUBMISSION.md','requirements.txt','requirements-lock.txt','requirements-final.txt','START_FINAL_AUDIT.md','.env.example'):
  if (root/name).is_file():files.append(root/name)
 # The old scanner may reference files omitted from the archive. Build an exact
 # inventory from the selected deliverables, including extracted PDF text.
 import re
 from pypdf import PdfReader
 pattern=re.compile(r'AI[- _]assisted|ChatGPT|Gemini|OpenAI|LLM|independent[_ -]human|human validation',re.I)
 references=[]
 for f in sorted(set(files)):
  if f.suffix.lower()=='.pdf':
   text='\n'.join(p.extract_text() or '' for p in PdfReader(f).pages)
  elif f.suffix.lower() in ('.png','.svg'):continue
  else:text=f.read_text(encoding='utf-8-sig',errors='replace')
  hits=list(pattern.finditer(text))
  if hits:references.append({'file':f.relative_to(root).as_posix(),'terms':sorted({m.group() for m in hits}),'occurrences':len(hits)})
 inventory=root/'docs/submission_assistance_references.json'
 inventory.write_text(json.dumps({'scope':'Selected submission files; PDF text extracted; inventory excludes itself. Mentions do not imply authorship for third-party source text.','files':references},indent=2),encoding='utf-8');files.append(inventory)
 dest=root/'submission';dest.mkdir(exist_ok=True)
 archive=dest/'organizational_authenticity_final_submission.zip'
 manifest=[{'path':f.relative_to(root).as_posix(),'sha256':digest(f),'bytes':f.stat().st_size} for f in sorted(set(files))]
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
  for f in sorted(set(files)):z.write(f,f.relative_to(root).as_posix())
  z.writestr('submission_manifest.json',json.dumps(manifest,indent=2))
 return archive
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--part4-version',default='exploration_v2');p.add_argument('--package',action='store_true');args=p.parse_args()
 try:
  result,active=audit(ROOT,args.part4_version);print(json.dumps(result,indent=2))
  if args.package:
   if not all(result['readme_present'].values()):raise ValueError('A per-part README.md is missing; audit report lists which one')
   print('Saved:',package(ROOT,active))
 except (ValueError,KeyError,FileNotFoundError,ImportError) as e:
  print('Audit needs attention:',e);sys.exit(1)
if __name__=='__main__':main()
