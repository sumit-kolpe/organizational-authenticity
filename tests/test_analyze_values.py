import unittest
from part1_stated_values.src.analyze_values import clean,validate_code,validate_change
class AnalysisTests(unittest.TestCase):
 def test_testimonial_separate(self):
  b,_=clean(b'<main><blockquote>A sufficiently long employee testimonial for testing.</blockquote><p>We protect our environment and invest in communities.</p></main>','TEST')
  self.assertEqual(b[0]['kind'],'quotation_or_testimonial');self.assertEqual(b[1]['kind'],'body')
 def coding(self):return {'suitability':'usable','source_scope':'values','concerns':[],'language':{'tone':'assertive','emphasis':'environment'},'themes':[{'category':'environment','evidence_ids':['b0000'],'rationale':'commitment'}]}
 def test_copy_exact(self):
  text='We protect nature .';v=validate_code(self.coding(),[{'id':'b0000','kind':'body','text':text}]);self.assertEqual(v['themes'][0]['evidence'][0]['text'],text)
 def test_invented_id(self):
  with self.assertRaises(ValueError):validate_code(self.coding(),[])
 def test_heading_rejected(self):
  with self.assertRaises(ValueError):validate_code(self.coding(),[{'id':'b0000','kind':'heading','text':'Environment'}])
 def test_incomparable_requires_null(self):
  with self.assertRaises(ValueError):validate_change({'comparable':False,'changed_from_prior':False},[],[])
 def test_changed_requires_evidence(self):
  with self.assertRaises(ValueError):validate_change({'comparable':True,'changed_from_prior':True,'summary':'changed','linguistic_shift':'new','evidence':[]},[],[])
 def test_wrapper(self):self.assertEqual(clean(b'<iframe id="playback"></iframe>','X')[1],['archive_wrapper'])
 def test_link_hub(self):
  b,_=clean(b'<main><p><a href="/">A long article headline which should never be body evidence</a></p></main>','X');self.assertEqual(b,[])
