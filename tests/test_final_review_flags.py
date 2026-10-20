"""Regression checks for the owner-confirmed review-status postprocessing."""
import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
class FinalReviewTests(unittest.TestCase):
 def test_part1_decisions_and_exclusions(self):
  a=read('part1_stated_values/outputs/review_v2/part1_values_reviewed.json')
  self.assertEqual(len(a),450)
  self.assertTrue(all(r['independent_human_review']=='completed_no_changes_owner_confirmed' for r in a))
  self.assertEqual(sum(r['annual_selection_final'] for r in a),140)
  self.assertTrue(all(r['annual_selection_final'] is (r['eligible_for_provisional_analysis'] is True) for r in a))
 def test_part2_review_and_missing(self):
  b=read('part2_disclosed_priorities/outputs/proxy_v2/disclosure_metrics.json')
  self.assertEqual(len(b),450)
  self.assertTrue(all(r['human_review_status']=='completed_no_changes_owner_confirmed' for r in b))
  self.assertEqual(sum(r['status']=='downloaded' for r in b),443)
  self.assertTrue(all(r['analysis_status']=='lexically_analyzed_human_reviewed' for r in b if r['status']=='downloaded'))
 def test_no_false_unreviewed_downstream(self):
  a=read('part3_alignment/outputs/alignment_v1/alignment.json')
  self.assertEqual(len(a),450)
  self.assertTrue(all(r['independent_human_validation'] for r in a))
  self.assertTrue(read('part4_exploration/outputs/exploration_v2/summary.json')['independent_human_validation'])
 def test_source_review_queues_closed_no_edits(self):
  x=read('part3_alignment/outputs/alignment_v1/source_review_queue.json')
  y=read('part4_exploration/outputs/exploration_v2/label_theme_review_queue.json')
  self.assertEqual((len(x),len(y)),(3,4))
  self.assertTrue(all(r['review_status']=='reviewed_no_changes_owner_confirmed' for r in x+y))
 def test_owner_attestation_is_explicit(self):
  r=read('docs/human_source_validation_status.json')
  self.assertEqual(r['status'],'completed_no_changes_owner_confirmed')
  self.assertFalse(r['underlying_text_themes_and_metrics_modified'])
if __name__=='__main__':unittest.main()
