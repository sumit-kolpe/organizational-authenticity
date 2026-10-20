import unittest
from part1_stated_values.src.gemini_pilot import validate
class EvidenceTests(unittest.TestCase):
    def sample(self):
        return {'suitability':'usable','source_scope':'corporate','concerns':[], 'themes':[{'category':'innovation','quote':'We continuously invest in innovation.','rationale':'Explicit commitment.'}]}
    def test_exact_evidence(self):
        self.assertEqual(validate(self.sample(),'We continuously invest in innovation.')['suitability'],'usable')
    def test_hallucinated_quote(self):
        with self.assertRaises(ValueError): validate(self.sample(),'Unrelated source text')
    def test_duplicate_category(self):
        x=self.sample(); x['themes']*=2
        with self.assertRaises(ValueError): validate(x,'We continuously invest in innovation.')
    def test_unsuitable_with_labels(self):
        x=self.sample(); x['suitability']='unsuitable'
        with self.assertRaises(ValueError): validate(x,'We continuously invest in innovation.')
    def test_unknown_category(self):
        x=self.sample(); x['themes'][0]['category']='invented'
        with self.assertRaises(ValueError): validate(x,'We continuously invest in innovation.')
    def test_empty_usable_labels(self):
        x=self.sample(); x['themes']=[]
        self.assertEqual(validate(x,'text')['themes'],[])
