import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from part2_disclosed_priorities.src import proxy_review as p
class ProxyTests(unittest.TestCase):
 def lex(self):return {'themes':{'people':['employee training'],'innovation':['innovation']},'language_markers':{'uncertainty':['may']}}
 def test_word_boundaries(self):
  m,_=p.metrics('Innovation is useful; innovative is different. Maybe may.',self.lex());self.assertEqual(m['themes']['innovation']['count'],1);self.assertEqual(m['language']['uncertainty']['count'],1)
 def test_phrase_whitespace(self):
  m,_=p.metrics('Employee\n training matters.',self.lex());self.assertEqual(m['themes']['people']['count'],1)
 def test_empty_not_zero_rate(self):
  m,_=p.metrics('',self.lex());self.assertIsNone(m['themes']['people']['per_1000_words'])
 def test_hidden_and_div_text(self):
  s=p.clean_html(b'<html><head>noise</head><body><div>Meaningful values</div><div style="display:none">hidden</div><ix:header>bad</ix:header><table><tr><td>Keep</td><td>words</td></tr></table></body></html>');self.assertIn('Meaningful values',s);self.assertNotIn('hidden',s);self.assertNotIn('noise',s);self.assertNotIn('bad',s);self.assertIn('Keep\nwords',s)
 def test_column_length(self):
  with self.assertRaises(ValueError):p.filing_rows({'accessionNumber':['a'],'filingDate':[],'form':[],'primaryDocument':[]})
 def test_history_old_files_dedup_form(self):
  def table(forms,dates):return {'accessionNumber':[str(i) for i in range(len(forms))],'filingDate':dates,'form':forms,'primaryDocument':['a.htm']*len(forms)}
  old=table(['DEF 14A','DEFA14A'],['2019-03-01','2019-03-02']);recent=table(['DEF 14A'],['2019-03-01'])
  class Fake:
   def get(self,url,*args):return old if 'submissions-001' in url else {'filings':{'recent':recent,'files':[{'name':'CIK0000000001-submissions-001.json','filingFrom':'2016-01-01','filingTo':'2020-01-01'}]}}
  _,r=p.history(1,Fake());self.assertEqual(len(r),1);self.assertEqual(r[0]['form'],'DEF 14A')
 def test_no_contact_blocks_network(self):
  with patch.dict(p.os.environ,{'SEC_USER_AGENT':''}):
   with self.assertRaises(p.Stop):p.Client(1)
 def test_budget_stops_before_network(self):
  with patch.dict(p.os.environ,{'SEC_USER_AGENT':'Test tests@example.invalid'}),tempfile.TemporaryDirectory() as d,patch.object(p,'BASE',Path(d)):
   with self.assertRaises(p.Stop):p.Client(0).get('https://www.sec.gov/no-request')
 def test_unexpected_host(self):
  with patch.dict(p.os.environ,{'SEC_USER_AGENT':'Test tests@example.invalid'}):
   with self.assertRaises(ValueError):p.Client(1).get('https://unrelated.invalid/')
 def test_no_gap_bridging(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);out=root/'out';out.mkdir();lex=root/'lex.json';lex.write_text(json.dumps(self.lex()))
   text='Innovation and employee training. '*100;(root/'text.txt').write_text(text)
   rows=[{'ticker':'X','company_name':'X','sector':'S','year':y,'status':'downloaded','text_file':'text.txt','text_sha256':p.sha(text.encode()),'source_url':'synthetic'} for y in [2018,2020]]
   p.save(out/'inventory.json',rows)
   with patch.object(p,'ROOT',root),patch.object(p,'OUT',out),patch.object(p,'LEXPATH',lex):p.analyze()
   self.assertEqual(p.read(out/'within_company_changes.json'),[])
