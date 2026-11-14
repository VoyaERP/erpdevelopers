"""The deployed-HTML verifier must reject stale external Watch links."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest import TestCase

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("inspect_training_player", ROOT / "scripts/inspect_training_player.py")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
HTML = '''<html><head>
<script defer data-cfasync="false" src="/assets/erpdevelopers/js/catalog.js?v=abc"></script>
</head><body><article class="ed-resource-card">
<button aria-controls="ed-playlist-dialog" data-playlist-open type="button">Watch here</button>
</article><dialog id="ed-playlist-dialog"><iframe data-player-frame
referrerpolicy="strict-origin-when-cross-origin"></iframe></dialog></body></html>'''


class TestDeployedTrainingMarkup(TestCase):
    def test_accepts_local_button_without_attribute_order_dependency(self):
        self.assertEqual(MODULE.inspect_markup(HTML), [])
        self.assertEqual(MODULE.inspect_markup(HTML.replace('"', "'")), [])

    def test_rejects_old_external_watch_anchor(self):
        legacy = HTML.replace('<button ', '<a href="https://www.youtube.com/" ').replace('</button>', '</a>')
        self.assertTrue(MODULE.inspect_markup(legacy))

    def test_rejects_eager_external_frame(self):
        self.assertTrue(MODULE.inspect_markup(HTML.replace('<iframe ', '<iframe src="https://www.youtube.com/embed/videoseries" ')))

    def test_rejects_body_only_or_missing_catalog_script(self):
        stale = HTML.replace('<head>', '<section>').replace('</head>', '</section>')
        self.assertTrue(MODULE.inspect_markup(stale))

    def test_empty_catalog_can_still_have_a_ready_dialog(self):
        empty = HTML[:HTML.index('<article')] + HTML[HTML.index('<dialog'):]
        self.assertEqual(MODULE.inspect_markup(empty), [])
