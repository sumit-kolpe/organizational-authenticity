"""Small synthetic tests: these fixtures are NOT research observations."""
import importlib.util
import json
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('batch_web',Path(__file__).resolve().parents[1]/'part1_stated_values/src/batch_web.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class BatchTests(unittest.TestCase):
    def record(self, stamp='20200701000000', status='200', mime='text/html'):
        return dict(zip(b.FIELDS,[stamp,'https://example.org/about',status,mime,'synthetic']))

    def test_empty_json_is_empty_inventory(self):
        self.assertEqual(b.parse_cdx(b'[]'),([],None))

    def test_empty_body_is_not_absence(self):
        with self.assertRaises(ValueError): b.parse_cdx(b'')

    def test_html_error_is_not_json(self):
        with self.assertRaises(ValueError): b.parse_cdx(b'<html>Error</html>')

    def test_continuation_token(self):
        body=json.dumps([b.FIELDS,list(self.record().values()),[],['org%2Cexample%29+20200701%21']]).encode()
        records,key=b.parse_cdx(body)
        self.assertEqual(len(records),1)
        self.assertEqual(key,'org%2Cexample%29+20200701%21')

    def test_bad_trailer_rejected(self):
        with self.assertRaises(ValueError): b.parse_cdx(json.dumps([b.FIELDS,[]]).encode())

    def test_wrong_header_rejected(self):
        with self.assertRaises(ValueError): b.parse_cdx(b'[["wrong"]]')

    def test_out_of_window_rejected(self):
        with self.assertRaises(ValueError): b.parse_cdx(json.dumps([b.FIELDS,list(self.record('20250101000000').values())]).encode())

    def test_rank_and_year_filter(self):
        records=[self.record('20200101000000'),self.record(),self.record('20210701000000')]
        actual=b.ordered_candidates(records,2020,set(),'TEST')
        self.assertEqual([r['timestamp'] for r in actual],['20200701000000','20200101000000'])

    def test_exclusion_and_redirect(self):
        records=[self.record(),self.record('20200601000000','301')]
        self.assertEqual(b.ordered_candidates(records,2020,{('TEST','20200701000000')},'TEST'),[])

    def test_revisit_retained(self):
        self.assertEqual(len(b.ordered_candidates([self.record(status='-',mime='warc/revisit')],2020,set(),'TEST')),1)

    def test_wrapper_rejected(self):
        text,flags,_=b.extract(b'<html><iframe id="playback" src="archive"></iframe></html>')
        self.assertEqual(text,'')
        self.assertIn('archive_playback_wrapper',flags)

    def test_text_preservation_and_boilerplate(self):
        paragraph='We value integrity, safety and respect. '*10
        text,flags,_=b.extract(('<nav>REMOVE</nav><main><h1>Our values</h1><p>'+paragraph+'</p></main><footer>REMOVE</footer>').encode())
        self.assertIn('Our values',text)
        self.assertIn('integrity, safety',text)
        self.assertNotIn('REMOVE',text)
        self.assertEqual(flags,[])

    def test_substantive_paragraph_inside_navigation_preserved(self):
        paragraph="A culture of collaboration and creativity supports our employees. " * 3
        text,_,_=b.extract(("<main><nav><p>"+paragraph+"</p></nav></main>").encode())
        self.assertIn("collaboration and creativity",text)

    def test_configuration_page_rejected(self):
        _,flags,_=b.extract(b'<main><h1>Brand Config Page</h1><p>Not corporate values.</p></main>')
        self.assertTrue(any('brand config' in f for f in flags))

if __name__=='__main__': unittest.main()
