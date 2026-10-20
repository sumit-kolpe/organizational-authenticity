import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]/'part2_disclosed_priorities/src/proxy_review.py'
s=importlib.util.spec_from_file_location('review',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class RepairTests(unittest.TestCase):
 def test_preserve_baseline_resume_and_detect_changes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);old=root/'old';out=root/'new';lex=root/'lex.json'
   (root/'config').mkdir();(root/'config/companies.csv').write_text('fixed roster');lex.write_text('{}')
   tickers=['BLK','XOM','TSLA']+[f'T{i}' for i in range(47)]
   rows=[dict(ticker=t,year=y,status='downloaded',text_file='original.txt') for t in tickers for y in range(2016,2025)]
   m.save(old/'inventory.json',rows);m.save(old/'run_policy.json',{'roster_sha256':m.sha((root/'config/companies.csv').read_bytes()),'lexicon_sha256':m.sha(lex.read_bytes())})
   before=(old/'inventory.json').read_bytes()
   with patch.multiple(m,ROOT=root,OLD_OUT=old,OUT=out,LEXPATH=lex),patch.object(m,'roster',return_value=[]):
    _,result=m.initialize()
    self.assertEqual(sum(r['status']=='not_attempted' for r in result),19)
    self.assertEqual([r for r in result if not m.repair_target(r)],[r for r in rows if not m.repair_target(r)])
    self.assertEqual((old/'inventory.json').read_bytes(),before)
    result[0]['status']='downloaded';m.save(out/'inventory.json',result)
    self.assertEqual(m.initialize()[1][0]['status'],'downloaded')
    lex.write_text('{"changed":true}')
    with self.assertRaises(ValueError):m.initialize()
 def test_annual_target(self):
  self.assertTrue(m.repair_target({'ticker':'TSLA','year':2018}))
  self.assertFalse(m.repair_target({'ticker':'TSLA','year':2019}))
if __name__=='__main__':unittest.main()
