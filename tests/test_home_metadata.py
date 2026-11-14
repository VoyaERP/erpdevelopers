from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("inspect_home_metadata", ROOT / "scripts/inspect_home_metadata.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class TestHomepageMetadata(TestCase):
    def test_frappe_double_space_and_equivalent_markup_pass(self):
        for tag in ('<meta property="og:type"  content="website">', "<meta content='website' property='og:type'>", '<meta\n content="website"\n property="og:type" />'):
            with self.subTest(tag=tag):
                self.assertEqual(MODULE.inspect_markup('<html><head>'+tag+'</head><body></body></html>'), [])
    def test_missing_wrong_and_conflicting_values_fail(self):
        for tags in ('', '<meta property="og:type" content="article">', '<meta property="og:type" content="website"><meta property="og:type" content="article">'):
            self.assertTrue(MODULE.inspect_markup('<head>'+tags+'</head>'))
    def test_body_text_cannot_satisfy_the_head_check(self):
        self.assertTrue(MODULE.inspect_markup('<head></head><body><meta property="og:type" content="website"></body>'))
