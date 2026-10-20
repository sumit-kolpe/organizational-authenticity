import copy,math,unittest
from part3_alignment.src import analyze_alignment as m

class AlignmentTests(unittest.TestCase):
 def pair(self):
  a=dict(ticker='T',year=2020,company_name='Test',sector='Tech',status='coded',eligible_for_provisional_analysis=True,theme_categories=['innovation'],snapshot_timestamp='20200601000000',analyst_notes={'flags':[]})
  b=dict(ticker='T',year=2020,sector='Tech',status='downloaded',filing_date='2020-04-01',word_count=1000,themes={t:{'count':int(t=='innovation'),'per_1000_words':float(t=='innovation')} for t in m.THEMES})
  return a,b
 def test_identical(self):self.assertEqual(m.cosine([1,0],[10,0]),1)
 def test_disjoint(self):self.assertEqual(m.cosine([1,0],[0,1]),0)
 def test_zero_is_missing(self):self.assertIsNone(m.cosine([0,0],[1,0]))
 def test_scale_invariance(self):self.assertAlmostEqual(m.cosine([1,1],[2,5]),m.cosine([1,1],[20,50]))
 def test_missing_does_not_become_zero(self):
  a,b=self.pair();a['eligible_for_provisional_analysis']=False
  r=m.make_row(a,b);self.assertIsNone(r['score']);self.assertIn('part1_ineligible',r['exclusion_reasons'])
 def test_zero_stated(self):
  a,b=self.pair();a['theme_categories']=[];self.assertIsNone(m.make_row(a,b)['score'])
 def test_unknown_theme_fails(self):
  a,b=self.pair();a['theme_categories']=['invented']
  with self.assertRaises(ValueError):m.make_row(a,b)
 def test_duplicate_fails(self):
  a,b=self.pair()
  with self.assertRaises(ValueError):m.index([a,a])
 def test_timing_is_recorded_not_silently_imputed(self):
  a,b=self.pair();r=m.make_row(a,b);self.assertEqual(r['score'],1);self.assertFalse(r['snapshot_on_or_before_filing'])
 def test_bad_rate_fails(self):
  a,b=self.pair();b['themes']['innovation']['per_1000_words']=8
  with self.assertRaises(ValueError):m.make_row(a,b)
 def test_jaccard(self):self.assertAlmostEqual(m.overlap([1,1,0],[0,1,1]),1/3)
 def test_invalid_vector_fails(self):
  with self.assertRaises(ValueError):m.cosine([1],[float('nan')])
if __name__=='__main__':unittest.main()
