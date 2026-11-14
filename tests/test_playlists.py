"""Frappe 16 playlist privacy, publication and in-page-only player contracts."""
from html.parser import HTMLParser
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
        access = next(f for f in schema["fields"] if f["fieldname"] == "visibility")
        self.assertEqual(access["fieldtype"], "Select")
        self.assertEqual(access["options"], "Public\nPrivate")
        self.assertEqual(access["default"], "Public")
        self.assertNotIn("Guest", {p["role"] for p in schema["permissions"]})
        self.assertIn("visibility", schema["field_order"])
        self.assertIn("visibility", catalog.PLAYLIST_FIELDS)
    @staticmethod
    def _controller():
        fake = ModuleType("frappe")
        fake._ = lambda value: value
        def fail(message):
            raise ValueError(message)
        fake.throw = fail
        model, document = ModuleType("frappe.model"), ModuleType("frappe.model.document")
        document.Document = type("Document", (), {})
        spec = util.spec_from_file_location("_playlist_validator_under_test", PLAYLIST / "erp_developers_playlist.py")
        module = util.module_from_spec(spec)
        with patch.dict(sys.modules, {"frappe": fake, "frappe.model": model, "frappe.model.document": document}):
            spec.loader.exec_module(module)
        return module.ERPDevelopersPlaylist
    def _new_playlist(self, visibility):
        item = self._controller()()
        item.visibility, item.published = visibility, 1
        item.description = "Reviewed playlist metadata"
        item.playlist_url = "https://www.youtube.com/playlist?list=PLabcdefghijklmnopqrst0123456"
        return item
    def test_private_published_remains_private_by_visibility_filter(self):
        item = self._new_playlist("Private"); item.validate()
        self.assertEqual(item.published, 1)
        self.assertEqual(item.visibility, "Private")
        self.assertEqual(item.playlist_id, "PLabcdefghijklmnopqrst0123456")
    def test_public_save_preserves_approved_published_status(self):
        item = self._new_playlist("Public"); item.validate()
        self.assertEqual(item.published, 1)
    def test_old_rows_get_public_default_and_unknown_value_rejected(self):
        item = self._new_playlist(None); item.validate()
        self.assertEqual(item.visibility, "Public")
        with self.assertRaisesRegex(ValueError, "Choose Public or Private"):
            self._new_playlist("Anyone").validate()
    def test_guest_catalog_filters_private_records_at_database(self):
        fake, received = ModuleType("frappe"), {}
        fake.db = type("DB", (), {"table_exists": lambda self, doctype, cached=False: True,
            "get_table_columns": lambda self, doctype: [*catalog.PLAYLIST_FIELDS, "published", "sort_order", "modified"]})()
        def query(doctype, **kwargs):
            received.update(kwargs)
            return [{"title":"Learning", "title_ar":None, "topic":"Solution Architecture", "level":"Beginner", "language":"English", "description":"Curated", "playlist_url":"https://www.youtube.com/playlist?list=PLabcdefghijklmnopqrst0123456", "playlist_id":"", "visibility":"Public"}]
        fake.get_all = query
        with patch.dict(sys.modules, {"frappe": fake}):
            results = catalog.public_playlists()
        self.assertEqual(received["filters"], {"published":1,"visibility":"Public"})
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["watch_url"].startswith("https://www.youtube.com/playlist?list="))
        self.assertEqual(results[0]["visibility"], "Public")
        self.assertEqual(results[0]["playlist_id"], "PLabcdefghijklmnopqrst0123456")
    def test_desk_does_not_silently_unpublish_private_collections(self):
        client = (PLAYLIST / "erp_developers_playlist.js").read_text()
        self.assertNotIn('set_value("published", 0)', client)
        self.assertNotIn('set_df_property("published", "read_only"', client)


class Tags(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.tags=[]; self.feed(source)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class TestProtectedPlaylistDialog(TestCase):
    def test_embed_is_user_initiated_privacy_enhanced_and_compatible(self):
        html=(ROOT / "www/training.html").read_text()
        js=(ROOT / "public/js/catalog.js").read_text()
        css=(ROOT / "public/css/portal.css").read_text()
        frame=next(a for t,a in Tags(html).tags if t=="iframe" and "data-player-frame" in a)
        self.assertNotIn("src",frame)
        self.assertNotIn("sandbox",frame)
        self.assertEqual(frame["referrerpolicy"],"strict-origin-when-cross-origin")
        self.assertIn("encrypted-media",frame["allow"])
        self.assertIn("data-player-status",html)
        for required in ("youtube-nocookie.com/embed/videoseries", "event.preventDefault()", "!idPattern.test(id)", 'typeof dialog.showModal === "function"', "frame.src = embed.toString()", 'removeAttribute("src")', "dialog.showModal()", 'dialog.addEventListener("close", stopPlayback)', 'const idPattern = /^[A-Za-z0-9_-]{12,64}$/'):
            self.assertIn(required,js)
        for forbidden in ("innerHTML","localStorage","window.open","location.href","fetch(","data-player-external"):
            self.assertNotIn(forbidden,js)
        self.assertIn(".ed-playlist-dialog::backdrop",css)
    def test_watch_is_a_button_and_no_app_owned_youtube_links_exist(self):
        html=(ROOT / "www/training.html").read_text()
        tags=Tags(html).tags
        triggers=[(t,a) for t,a in tags if "data-playlist-open" in a]
        self.assertEqual(len(triggers),1)
        tag,attrs=triggers[0]
        self.assertEqual(tag,"button")
        self.assertEqual(attrs["type"],"button")
        self.assertEqual(attrs["aria-controls"],"ed-playlist-dialog")
        self.assertIn("disabled",attrs)
        self.assertNotIn("href",attrs); self.assertNotIn("target",attrs)
        self.assertEqual(attrs["data-playlist-id"],"{{ item.playlist_id | e }}")
        self.assertNotIn("Open on YouTube",html)
        self.assertNotIn("data-player-external",html)
        self.assertNotIn("item.watch_url",html)
        for tag,attrs in tags:
            if tag=="a":
                self.assertNotIn("youtube",attrs.get("href","").lower())
        head=html.split("{% block ed_head %}",1)[1].split("{% endblock %}",1)[0]
        scripts=[a for t,a in Tags(head).tags if t=="script"]
        self.assertEqual(len(scripts),1)
        self.assertEqual(scripts[0]["src"],"{{ catalog_js_url | e }}")
        self.assertEqual(scripts[0]["data-cfasync"],"false")
        self.assertIn("defer",scripts[0])
        self.assertEqual(html.count("{{ catalog_js_url | e }}"),1)
    def test_training_remains_published_only(self):
        source=(ROOT / "catalog.py").read_text()
        self.assertIn('"visibility": "Public"',source)
        self.assertNotIn('ignore_permissions=True',source)


if __name__ == "__main__":
    import unittest
    unittest.main()
