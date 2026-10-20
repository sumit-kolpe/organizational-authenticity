"""List files mentioning assistance/model use without changing their contents.
PDFs need text extraction/manual inspection; the report lists them separately.
"""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assistance_reference_inventory.json'
PATTERN=re.compile(r'AI[- ]assisted|ChatGPT|OpenAI assistant|Gemini|independent[- _]human|human validation',re.I)
def main():
 results=[];pdfs=[]
 for directory in ['docs','shared','config','part1_stated_values','part2_disclosed_priorities','part3_alignment','part4_exploration']:
  base=ROOT/directory
  if not base.exists():continue
  for f in base.rglob('*'):
   if not f.is_file() or f==OUT or any(p in ('data','cache','__pycache__','.venv') for p in f.parts):continue
   if f.suffix.lower()=='.pdf':pdfs.append(str(f.relative_to(ROOT)));continue
   if f.suffix.lower() not in ('.py','.md','.txt','.csv','.json','.yaml','.yml'):continue
   text=f.read_text(encoding='utf-8-sig',errors='replace');hits=list(PATTERN.finditer(text))
   if hits:results.append({'project_path':str(f.relative_to(ROOT)),'references':sorted({m.group() for m in hits}),'occurrences':len(hits)})
 for f in ROOT.glob('*.md'):
  hits=list(PATTERN.finditer(f.read_text(encoding='utf-8',errors='replace')))
  if hits:results.append({'project_path':f.name,'references':sorted({m.group() for m in hits}),'occurrences':len(hits)})
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps({'text_files':results,'pdfs_requiring_text_review':pdfs,'scope':'Authored project text outside raw data/cache; no contents modified.'},indent=2),encoding='utf-8')
 print('Saved',OUT)
if __name__=='__main__':main()
