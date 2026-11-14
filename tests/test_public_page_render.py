"""Public page guards for partially migrated Frappe 16 sites.

Test results do not replace a site-specific database migration and HTTP UAT.
"""
import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from erpdevelopers.branding import EXPECTED_SITE
from erpdevelopers import catalog
from erpdevelopers.www import lets_talk


class FakeCatalogDatabase:
    def __init__(self, exists=True, missing=()):
        self.exists = exists
        self.missing = set(missing)
        self.calls = []

    def table_exists(self, doctype, cached=True):
        self.calls.append(("table_exists", doctype, cached))
        return self.exists

    def get_table_columns(self, doctype):
        self.calls.append(("get_table_columns", doctype))
        return [
            *[f for f in (*catalog.PLAYLIST_FIELDS, *catalog.RESOURCE_FIELDS)
              if f not in self.missing],
            *[f for f in ("published", "sort_order", "modified")
              if f not in self.missing],
        ]


class TestPublicCatalogRendering(unittest.TestCase):
    def fake_frappe(self, *, exists=True, missing=(), data=None):
        fake = ModuleType("frappe")
        fake.db = FakeCatalogDatabase(exists=exists, missing=missing)
        fake.queries = []

        def get_all(doctype, **kwargs):
            fake.queries.append((doctype, kwargs))
            return list((data or {}).get(doctype, []))
        fake.get_all = get_all
        return fake

    def test_insights_shows_empty_when_resource_table_not_migrated(self):
        fake = self.fake_frappe(exists=False)
        with patch.dict(sys.modules, {"frappe": fake}):
            self.assertEqual(catalog.public_resources(), [])
            self.assertEqual(catalog.public_playlists(), [])
            status = catalog.catalog_health()
        self.assertEqual(fake.queries, [])
        self.assertFalse(status[catalog.RESOURCE_DOCTYPE]["table_present"])

    def test_insights_shows_empty_when_required_columns_are_missing(self):
        fake = self.fake_frappe(missing={"source_kind"})
        with patch.dict(sys.modules, {"frappe": fake}):
            self.assertEqual(catalog.public_resources(), [])
        self.assertEqual(fake.queries, [])

    def test_published_resource_is_returned_and_not_a_guest_query(self):
        entry = SimpleNamespace(
            source_kind="External Source",
            web_page=None,
            external_url="https://docs.frappe.io/framework",
        )
        record = type("FrappeRow", (dict,), {
            "__getattr__": lambda self, key: self[key],
        })({
            "title": "Framework notes", "title_ar": None,
            "topic": "Developer Practices", "summary": "Reviewed link",
            "editorial_note": "Read the security guidance", "language": "English",
            "source_kind": entry.source_kind, "web_page": None,
            "external_url": entry.external_url,
            "source_name": "Frappe Documentation",
        })
        fake = self.fake_frappe(data={catalog.RESOURCE_DOCTYPE: [record]})
        with patch.dict(sys.modules, {"frappe": fake}):
            result = catalog.public_resources()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["href"], entry.external_url)
        self.assertTrue(result[0]["external"])
        self.assertEqual(fake.queries[0][1]["filters"], {"published": 1})
        self.assertEqual(fake.queries[0][1]["limit_page_length"], 60)


class TestPublicCatalogTopicContext(unittest.TestCase):
    """Published content must never turn a valid catalog into HTTP 500."""

    def test_topics_from_plain_dicts_with_missing_or_blank_topics(self):
        data = [
            {"topic": "Solution Architecture"},
            {"topic": "Frappe & ERPNext"},
            {"topic": "Frappe & ERPNext"},
            {"topic": None},
            {"topic": "  "},
        ]
        self.assertEqual(
            catalog.public_catalog_topics(data),
            ["Frappe & ERPNext", "Solution Architecture"],
        )
        self.assertEqual(catalog.public_catalog_topics([]), [])

    def test_training_context_handles_real_published_dicts(self):
        from erpdevelopers.www import training

        ctx = SimpleNamespace()
        rows = [
            {"topic": "Frappe & ERPNext", "title": "Basics",
             "description": "Reviewed playlist", "level": "Beginner",
             "language": "English", "watch_url": "https://www.youtube.com/playlist?list=PLexample"},
            {"topic": "Cloud & DevOps", "title": "Cloud",
             "description": "Reviewed", "level": "Intermediate",
             "language": "Arabic", "watch_url": "https://www.youtube.com/playlist?list=PLother"},
        ]
        # Do not let unittest.mock introspect an unbound Frappe LocalProxy.
        # A complete isolated module works both on Bench and without Frappe in CI.
        fake_frappe = ModuleType("frappe")
        fake_frappe.session = SimpleNamespace(user="Guest")
        with patch.dict(sys.modules, {"frappe": fake_frappe}), patch.object(
            training, "public_playlists", return_value=rows
        ), patch.object(training, "authorized_private_playlists", return_value=[]), patch.object(
            training, "set_public_context", side_effect=lambda context, **_kwargs: None
        ):
            training.get_context(ctx)
        self.assertFalse(ctx.is_authenticated)
        self.assertEqual(ctx.playlists, rows)
        self.assertEqual(ctx.topics, ["Cloud & DevOps", "Frappe & ERPNext"])

    def test_training_context_combines_only_the_authorized_private_result(self):
        from erpdevelopers.www import training

        fake_frappe = ModuleType("frappe")
        fake_frappe.session = SimpleNamespace(user="member@example.com")
        private = [{"topic": "Cybersecurity", "title": "Authorized collection"}]
        ctx = SimpleNamespace()
        with patch.dict(sys.modules, {"frappe": fake_frappe}), patch.object(
            training, "public_playlists", return_value=[]
        ), patch.object(training, "authorized_private_playlists", return_value=private), patch.object(
            training, "set_public_context", side_effect=lambda context, **_kwargs: None
        ):
            training.get_context(ctx)
        self.assertTrue(ctx.is_authenticated)
        self.assertEqual(ctx.playlists, private)
        self.assertEqual(ctx.topics, ["Cybersecurity"])

    def test_insights_context_handles_real_published_dicts(self):
        from erpdevelopers.www import insights

        ctx = SimpleNamespace()
        rows = [
            {"topic": "Cybersecurity", "source_kind": "External Source"},
            {"topic": "AI & Data", "source_kind": "Original Article"},
        ]
        with patch.object(insights, "public_resources", return_value=rows), patch.object(
            insights, "set_public_context", side_effect=lambda context, **_kwargs: None
        ):
            insights.get_context(ctx)
        self.assertEqual(ctx.resources, rows)
        self.assertEqual(ctx.topics, ["AI & Data", "Cybersecurity"])


class TestBookingPageContext(unittest.TestCase):
    def test_public_get_does_not_import_native_post_handler(self):
        source = __import__("pathlib").Path(lets_talk.__file__).read_text()
        self.assertNotIn("from erpdevelopers.meeting_booking import", source)
        self.assertIn("from erpdevelopers.meeting_status import booking_ready", source)

    def test_disabled_by_default_and_site_isolation(self):
        from erpdevelopers.meeting_status import booking_ready
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=EXPECTED_SITE)
        frappe.conf = {}
        utils = ModuleType("frappe.utils")
        utils.cint = lambda value: int(value or 0)
        with patch.dict(sys.modules, {"frappe": frappe, "frappe.utils": utils}):
            self.assertFalse(booking_ready())
            frappe.local.site = "another-site.example"
            frappe.conf["erpdev_meeting_booking_enabled"] = 1
            self.assertFalse(booking_ready())

    def test_lets_talk_page_context_is_safe_when_booking_offline(self):
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=EXPECTED_SITE)
        frappe.conf = {}
        utils = ModuleType("frappe.utils")
        utils.cint = lambda value: int(value or 0)
        ctx = SimpleNamespace()
        with patch.dict(sys.modules, {"frappe": frappe, "frappe.utils": utils}):
            lets_talk.get_context(ctx)
        self.assertFalse(ctx.booking_enabled)
        self.assertEqual(ctx.title, "ERP Developers | Let's Talk")
        self.assertTrue(ctx.topic_options)
        self.assertIn("meeting.css?v=", ctx.meeting_css_url)
        self.assertIn("meeting.js?v=", ctx.meeting_js_url)


if __name__ == "__main__":
    unittest.main()
