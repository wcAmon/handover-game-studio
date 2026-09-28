import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('delivery',ROOT/'harness/delivery.py')
delivery=importlib.util.module_from_spec(spec);spec.loader.exec_module(delivery)

class DeliveryTests(unittest.TestCase):
    def test_stagnation_replans_then_pauses_and_progress_resets(self):
        p={'stagnation_shifts':2,'replan_shifts':1}
        first=delivery.advance({},'a','a',p)
        self.assertEqual(first['action'],'continue')
        second=delivery.advance(first,'a','a',p)
        self.assertEqual(second['action'],'replan')
        self.assertEqual(delivery.advance(second,'a','a',p)['action'],'pause')
        reset=delivery.advance(second,'a','b',p)
        self.assertEqual(reset['stagnant_shifts'],0)
        self.assertEqual(reset['action'],'continue')
    def test_content_only_and_new_files(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'src').mkdir();(root/'src/a').write_text('one')
            p={'watch':['src']}
            initial=delivery.fingerprint(root,p)
            (root/'doc.md').write_text('not product')
            self.assertEqual(initial,delivery.fingerprint(root,p))
            (root/'src/b').write_text('two')
            self.assertNotEqual(initial,delivery.fingerprint(root,p))
    def test_escape_symlink_and_bad_policy(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);(root/'src').symlink_to('/tmp',target_is_directory=True)
            with self.assertRaises(ValueError):delivery.fingerprint(root,{'watch':['src']})
            with self.assertRaises(ValueError):delivery.fingerprint(root,{'watch':['../other']})
            (root/'delivery.json').write_text('{"version":1,"watch":[],"stagnation_shifts":0}')
            with self.assertRaises(ValueError):delivery.load(root)
