import importlib.util,tempfile,unittest,zipfile
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'shared/final_audit.py'
spec=importlib.util.spec_from_file_location('final_audit',P);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class AuditTests(unittest.TestCase):
 def test_duplicate_detection(self):
  with self.assertRaises(ValueError):m.index([{'ticker':'A','year':2020}]*2)
 def test_numerical_mismatch(self):
  with self.assertRaises(ValueError):m.near(.5,.6)
 def test_tolerance(self):m.near(.5,.5+1e-13)
 def test_archive_selection(self):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)
   for n in ['docs/note.md','part3_alignment/src/main.py','part3_alignment/outputs/alignment_v1/results.json','part3_alignment/outputs/old/results.json','part3_alignment/data/raw.txt','part3_alignment/.env']:
    p=r/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
   archive=m.package(r,{'part3_alignment':'alignment_v1'})
   with zipfile.ZipFile(archive) as z:
    names=z.namelist();self.assertIn('part3_alignment/outputs/alignment_v1/results.json',names);self.assertIn('submission_manifest.json',names)
    self.assertNotIn('part3_alignment/outputs/old/results.json',names);self.assertNotIn('part3_alignment/data/raw.txt',names);self.assertNotIn('part3_alignment/.env',names)
if __name__=='__main__':unittest.main()
