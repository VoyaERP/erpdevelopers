"""Actual-page inspector rejects stale footer, English Arabic heading and assets."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("inspect_publications", ROOT / "scripts/inspect_publications.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
CSS = "/assets/erpdevelopers/css/publications.css?v=123"
SOURCE = '''<html><head><link rel="stylesheet" href="''' + CSS + '''"></head>
<body><main id="top"><h1 id="ed-publications-title">Projects</h1><section id="publications"></section>
<footer><a href="/">Logo</a><div class="ed-footer-links"><a href="/lets-talk#meeting-start">Let's Talk</a><a href="/login?redirect-to=/desk">Team Login</a><a href="#top">Back to top</a></div></footer></main></body></html>'''


class TestPublicationVerifier(TestCase):
    def test_accepts_correct_directory_in_both_languages(self):
        self.assertEqual(MODULE.inspect(SOURCE, "projects", "en", CSS), [])
        self.assertEqual(MODULE.inspect(SOURCE.replace("Projects", "المشاريع"), "projects", "ar", CSS), [])
        self.assertEqual(MODULE.inspect(SOURCE.replace("Projects", "Team Advice"), "team-advice", "en", CSS), [])
        self.assertEqual(MODULE.inspect(SOURCE.replace("Projects", "نصائح الفريق"), "team-advice", "ar", CSS), [])

    def test_rejects_stale_footer_and_heading_and_css(self):
        self.assertTrue(MODULE.inspect(SOURCE.replace('<a href="#top">', '<a href="/training">'), "projects", "en", CSS))
        self.assertTrue(MODULE.inspect(SOURCE, "projects", "ar", CSS))
        self.assertTrue(MODULE.inspect(SOURCE, "projects", "en", CSS + "bad"))
        self.assertTrue(MODULE.inspect(SOURCE.replace('id="top"', 'id="other"'), "projects", "en", CSS))
