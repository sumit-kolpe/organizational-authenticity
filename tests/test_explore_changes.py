import unittest
from part4_exploration.src import explore_changes as e
class ExplorationTests(unittest.TestCase):
 def test_decomposition_adds(self):
  a,b=e.decompose([1,0],[2,1],[1,1],[1,3])
  self.assertAlmostEqual(a+b,e.cosine([1,1],[1,3])-e.cosine([1,0],[2,1]))
 def test_fixed_values_zero_component(self):
  a,b=e.decompose([1,0],[2,1],[1,0],[1,3]);self.assertEqual(a,0)
 def test_fixed_proxy_zero_component(self):
  a,b=e.decompose([1,0],[2,1],[1,1],[2,1]);self.assertEqual(b,0)
 def test_identical_zero(self):self.assertEqual(e.decompose([1,0],[2,1],[1,0],[2,1]),(0,0))
 def test_unknown_not_unchanged(self):
  r=[{'ticker':'A','recorded_text_changed':None,'absolute_score_change':1,'score_change':1}]
  s=e.contrast(r);self.assertEqual(s['unchanged']['absolute_change']['n'],0);self.assertIsNone(s['changed_minus_unchanged_absolute_mean'])
 def test_contrast(self):
  r=[dict(ticker='A',recorded_text_changed=True,absolute_score_change=.3,score_change=-.3),dict(ticker='A',recorded_text_changed=False,absolute_score_change=.1,score_change=.1)]
  self.assertAlmostEqual(e.contrast(r)['changed_minus_unchanged_absolute_mean'],.2)
 def test_duplicate_fails(self):
  with self.assertRaises(ValueError):e.index([{'ticker':'A','year':2020}]*2)
 def test_zero_vector_fails(self):
  with self.assertRaises(ValueError):e.cosine([0,0],[1,0])
if __name__=='__main__':unittest.main()
