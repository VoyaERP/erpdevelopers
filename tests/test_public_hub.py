"""Pure-source and contract checks for v16 website/ERPNext integration.

These checks do not replace live migrations, role-based UAT or browser testing.
"""
import json
import sys
import unittest
from datetime import date, timedelta
from hashlib import sha256
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

from erpdevelopers.branding import versioned_public_asset
from erpdevelopers.catalog_rules import youtube_playlist_id, external_https_url
from erpdevelopers.intake_rules import TOPICS, WINDOWS, clean_text, validate_date, validate_timezone

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"
DT = APP / "erp_developers/doctype"


class TestCuratedURLs(unittest.TestCase):
    def test_youtube_playlist_canonicalization(self):
        code = "PLabcdefghijklmnopqrst0123456"
        self.assertEqual(
            youtube_playlist_id(f"https://www.youtube.com/playlist?list={code}&si=example"),
            code,
        )
        for source in (
            "https://www.youtube.com/watch?v=abcdef&list=PLabcdefghijklmnopqrst0123456",
            "https://www.youtubeevil.com/playlist?list=PLabcdefghijklmnopqrst0123456",
            "https://youtube.com@evil.example/playlist?list=PLabcdefghijklmnopqrst0123456",
            "http://youtube.com/playlist?list=PLabcdefghijklmnopqrst0123456",
            "https://youtube.com:8080/playlist?list=PLabcdefghijklmnopqrst0123456",
            "https://youtube.com/playlist?list=a",
            "https://www.youtube.com/playlist?list=abc&list=PLabcdefghijklmnopqrst0123456",
        ):
            with self.subTest(url=source), self.assertRaises(ValueError):
                youtube_playlist_id(source)

    def test_external_links_require_https_public_hostname(self):
        self.assertEqual(external_https_url("https://www.microsoft.com/en-us/docs"),
                         "https://www.microsoft.com/en-us/docs")
        for url in (
            "javascript:alert(1)", "data:text/plain,evil", "https://localhost/a",
            "https://127.0.0.1/a", "https://192.168.1.2/a", "https://[::1]/",
            "https://intranet.local/file", "https://erp-developers.com/desk",
            "http://example.com/", "https://user:secret@example.com",
            "https://example.com:8443/a", "//example.com", "https://intranet/",
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                external_https_url(url)


class TestIntakeValidation(unittest.TestCase):
    def test_booking_date_window_and_timezone(self):
        today = date(2026, 11, 14)
        self.assertEqual(validate_date("2026-11-14", today=today), "2026-11-14")
        self.assertEqual(validate_date((today + timedelta(days=90)).isoformat(), today=today),
                         (today + timedelta(days=90)).isoformat())
        for value in ("2026-11-13", "2027-03-01", "14/11/2026", "", "bad"):
            with self.subTest(date=value), self.assertRaises(ValueError):
                validate_date(value, today=today)
        self.assertEqual(validate_timezone("Africa/Cairo"), "Africa/Cairo")
        with self.assertRaises(ValueError):
            validate_timezone("../etc/passwd")

    def test_guest_text_limits_and_topic_allowlist(self):
        self.assertEqual(clean_text("  Solution Architecture  ", limit=120), "Solution Architecture")
        for value in ("", "x"*121, "text\x00hidden"):
            with self.assertRaises(ValueError):
                clean_text(value, limit=120)
        self.assertIn("Solution Architecture", TOPICS)
        self.assertIn("Flexible", WINDOWS)


class TestERPNextPublicHubContracts(unittest.TestCase):
    def test_doctypes_are_native_and_never_guest_readable(self):
        specs = [
            "erp_developers_playlist",
            "erp_developers_resource",
            "erp_developers_consultation",
        ]
        for item in specs:
            with self.subTest(doctype=item):
                path = DT / item / (item + ".json")
                definition = json.loads(path.read_text())
                self.assertEqual(definition["module"], "ERP Developers")
                self.assertTrue(definition["track_changes"])
                self.assertEqual(
                    definition["field_order"],
                    [field["fieldname"] for field in definition["fields"]]
                )
                self.assertNotIn("Guest", {p["role"] for p in definition["permissions"]})
                self.assertTrue((DT / item / (item + ".py")).is_file())
                self.assertTrue((DT / item / "__init__.py").is_file())
        crm = json.loads((DT / "erp_developers_consultation/erp_developers_consultation.json").read_text())
        self.assertIn("Lead", [f.get("options") for f in crm["fields"]])
        self.assertIn("Event", [f.get("options") for f in crm["fields"]])
        self.assertEqual(next(x for x in crm["fields"] if x["fieldname"]=="status")["read_only"], 0)

    def test_guest_submission_is_opt_in_and_crm_conversion_is_staff_only(self):
        code = (APP / "appointments.py").read_text()
        flags = (APP / "consultation_flags.py").read_text()
        self.assertIn('frappe.conf.get("erpdev_consultation_open", 0)', flags)
        self.assertIn('frappe.local.site == EXPECTED_SITE', flags)
        self.assertIn('from erpdevelopers.consultation_flags import booking_open', code)
        self.assertIn('@frappe.whitelist(allow_guest=True, methods=["POST"])', code)
        self.assertIn('@rate_limit(limit=5, seconds=3600, methods="POST")', code)
        self.assertIn('frappe.get_doc("ERP Developers Consultation"', code)
        self.assertIn('consultation.check_permission("write")', code)
        self.assertIn('frappe.has_permission("Lead"', code)
        self.assertIn('if consultation.lead:', code)
        self.assertNotIn('ignore_permissions=True', code.split("def create_or_link_lead")[1])
        client = (APP / "public/js/consultation.js").read_text()
        self.assertIn("frappe.call", client)
        self.assertIn('if not frappe.has_permission("Lead", ptype="read", doc=consultation.lead)', code)
        self.assertNotIn("localStorage", client)
        self.assertNotIn("fetch(", client)

    def test_shared_site_chrome_and_read_only_guide(self):
        pages = ("training", "insights", "lets-talk", "privacy")
        for page in pages:
            html = (APP / f"www/{page}.html").read_text()
            self.assertIn('extends "templates/includes/erpdevelopers_page_base.html"', html)
            self.assertNotIn('<form action="https://', html)
        base = (APP / "templates/includes/erpdevelopers_page_base.html").read_text()
        self.assertEqual(base.count('erpdevelopers_nav.html'), 1)
        self.assertEqual(base.count('erpdevelopers_footer.html'), 1)
        self.assertIn('rel="canonical"', base)
        self.assertIn("erpdevelopers_assistant.html", base)
        guide = (APP / "public/js/assistant.js").read_text()
        self.assertIn("textContent", guide)
        self.assertNotIn("fetch(", guide)
        self.assertNotIn("frappe.call", guide)

    def test_fingerprinted_asset_url_fails_closed(self):
        for name in ("css/portal.css", "js/consultation.js", "js/catalog.js", "js/assistant.js", "css/meeting.css", "js/meeting.js"):
            expected = sha256((APP / "public" / name).read_bytes()).hexdigest()[:16]
            self.assertEqual(versioned_public_asset(name),
                             f"/assets/erpdevelopers/{name}?v={expected}")
        with self.assertRaises(ValueError):
            versioned_public_asset("../sites/site_config.json")


if __name__ == "__main__":
    unittest.main()
