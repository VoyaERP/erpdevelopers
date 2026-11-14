"""Frappe 16 playlist privacy, editorial publication and embedded player contracts.

These source and isolated controller checks must be followed by live site UAT.
"""
from importlib import util
import json
from pathlib import Path
import sys
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch

from erpdevelopers import catalog

ROOT = Path(__file__).resolve().parents[1] / "erpdevelopers"
PLAYLIST = ROOT / "erp_developers/doctype/erp_developers_playlist"


class TestPlaylistBackend(TestCase):
    def test_private_field_does_not_grant_guest_access(self):
        schema = json.loads((PLAYLIST / "erp_developers_playlist.json").read_text())
        access = next(field for field in schema["fields"] if field["fieldname"] == "visibility")
        self.assertEqual(access["fieldtype"], "Select")
        self.assertEqual(access["options"], "Public\nPrivate")
        self.assertEqual(access["default"], "Public")
        self.assertNotIn("Guest", {p["role"] for p in schema["permissions"]})
        self.assertIn("visibility", schema["field_order"])
        self.assertIn("visibility", catalog.PLAYLIST_FIELDS)

    @staticmethod
    def _controller():
        """Isolate the Frappe Document base; use the real playlist validator."""
        fake_frappe = ModuleType("frappe")
        fake_frappe._ = lambda value: value

        def fail(message):
            raise ValueError(message)
        fake_frappe.throw = fail
        model = ModuleType("frappe.model")
        document = ModuleType("frappe.model.document")
        document.Document = type("Document", (), {})
        spec = util.spec_from_file_location(
            "_playlist_validator_under_test",
            PLAYLIST / "erp_developers_playlist.py",
        )
        module = util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            "frappe": fake_frappe, "frappe.model": model,
            "frappe.model.document": document,
        }):
            spec.loader.exec_module(module)
        return module.ERPDevelopersPlaylist

    def _new_playlist(self, visibility):
        item = self._controller()()
        item.visibility = visibility
        item.published = 1
        item.description = "Reviewed playlist metadata"
        item.playlist_url = "https://www.youtube.com/playlist?list=PLabcdefghijklmnopqrst0123456"
        return item

    def test_private_published_remains_private_by_visibility_filter(self):
        item = self._new_playlist("Private")
        item.validate()
        self.assertEqual(item.published, 1)
        self.assertEqual(item.visibility, "Private")
        self.assertEqual(item.playlist_id, "PLabcdefghijklmnopqrst0123456")

    def test_public_save_preserves_approved_published_status(self):
        item = self._new_playlist("Public")
        item.validate()
        self.assertEqual(item.published, 1)

    def test_old_rows_get_public_default_and_unknown_value_rejected(self):
        legacy = self._new_playlist(None)
        legacy.validate()
        self.assertEqual(legacy.visibility, "Public")
        invalid = self._new_playlist("Anyone")
        with self.assertRaisesRegex(ValueError, "Choose Public or Private"):
            invalid.validate()

    def test_guest_catalog_filters_private_records_at_database(self):
        mock_frappe = ModuleType("frappe")
        received = {}
        mock_frappe.db = type("DB", (), {
            "table_exists": lambda self, doctype, cached=False: True,
            "get_table_columns": lambda self, doctype: [
                *catalog.PLAYLIST_FIELDS, "published", "sort_order", "modified",
            ],
        })()

        def query(doctype, **kwargs):
            received.update(kwargs)
            return [{
                "title": "Learning", "title_ar": None,
                "topic": "Solution Architecture", "level": "Beginner",
                "language": "English", "description": "Curated",
                "playlist_url": "https://www.youtube.com/playlist?list=PLabcdefghijklmnopqrst0123456",
                "playlist_id": "",  # legacy row: validated URL is source of truth
                "visibility": "Public",
            }]
        mock_frappe.get_all = query
        with patch.dict(sys.modules, {"frappe": mock_frappe}):
            results = catalog.public_playlists()
        self.assertEqual(received["filters"], {"published": 1, "visibility": "Public"})
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["watch_url"].startswith("https://www.youtube.com/playlist?list="))
        self.assertEqual(results[0]["visibility"], "Public")
        self.assertEqual(results[0]["playlist_id"], "PLabcdefghijklmnopqrst0123456")
        client = (PLAYLIST / "erp_developers_playlist.js").read_text()
        self.assertIn('frm.set_df_property("published", "read_only"', client)
        self.assertIn('frm.set_value("published", 0)', client)
        self.assertIn('frm.doc.visibility === "Private"', client)



class TestProtectedPlaylistDialog(TestCase):
    def test_embed_is_user_initiated_privacy_enhanced_and_compatible(self):
        html = (ROOT / "www/training.html").read_text()
        js = (ROOT / "public/js/catalog.js").read_text()
        css = (ROOT / "public/css/portal.css").read_text()
        self.assertIn('id="ed-playlist-dialog"', html)
        self.assertIn('data-playlist-id="{{ item.playlist_id | e }}"', html)
        self.assertIn('data-player-frame', html)
        self.assertNotIn('sandbox=', html)
        self.assertIn('allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture; web-share"', html)
        self.assertIn("data-player-status", html)
        self.assertIn('referrerpolicy="strict-origin-when-cross-origin"', html)
        self.assertNotIn('src="https://www.youtube', html, "Do not embed on page load")
        self.assertIn("youtube-nocookie.com/embed/videoseries", js)
        self.assertNotIn('embed.searchParams.set("listType"', js)
        self.assertIn('event.preventDefault(); // only intercept', js)
        self.assertIn('if (!idPattern.test(id)) return', js)
        self.assertIn('typeof dialog.showModal !== "function"', js)
        self.assertIn('href="{{ item.watch_url | e }}" target="_blank" rel="noopener noreferrer"', html)
        self.assertIn('class="ed-playlist-play-icon"', html)
        self.assertIn('a.ed-playlist-watch{color:#fff!important}', css)
        self.assertIn('frame.src = embed.toString()', js)
        self.assertIn('frame.removeAttribute("src")', js)
        self.assertIn('dialog.showModal()', js)
        self.assertIn('dialog.addEventListener("close", stopPlayback)', js)
        self.assertIn('const idPattern = /^[A-Za-z0-9_-]{12,64}$/', js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("localStorage", js)
        self.assertNotIn("fetch(", js)
        self.assertIn(".ed-playlist-dialog::backdrop", css)

    def test_training_remains_published_only(self):
        source = (ROOT / "catalog.py").read_text()
        self.assertIn('"visibility": "Public"', source)
        self.assertNotIn('ignore_permissions=True', source)
        self.assertIn('target="_blank" rel="noopener noreferrer"', (ROOT / "www/training.html").read_text())


if __name__ == "__main__":
    import unittest
    unittest.main()
