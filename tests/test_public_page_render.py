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
        # Frappe _dict provides both attribute and mapping access.
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


class TestBookingPageContext(unittest.TestCase):
    def test_public_get_does_not_import_crm_post_api(self):
        source = __import__("pathlib").Path(lets_talk.__file__).read_text()
        self.assertNotIn("from erpdevelopers.appointments import", source)
        self.assertIn("from erpdevelopers.consultation_flags import booking_open", source)

    def test_disabled_by_default_and_site_isolation(self):
        from erpdevelopers.consultation_flags import booking_open
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=EXPECTED_SITE)
        frappe.conf = {}
        utils = ModuleType("frappe.utils")
        utils.cint = lambda value: int(value or 0)
        with patch.dict(sys.modules, {"frappe": frappe, "frappe.utils": utils}):
            self.assertFalse(booking_open())
            frappe.conf["erpdev_consultation_open"] = 1
            self.assertTrue(booking_open())
            frappe.local.site = "another-site.example"
            self.assertFalse(booking_open())

    def test_lets_talk_page_context_does_not_touch_crm(self):
        from erpdevelopers.public_pages import set_public_context
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
        self.assertTrue(ctx.time_windows)


if __name__ == "__main__":
    unittest.main()
