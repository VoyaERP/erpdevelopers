"""Regression tests for the ERPNext tile in Apps and Desktop Icons fallback."""

import sys
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from erpdevelopers.branding import EXPECTED_SITE, FAVICON_URL
from erpdevelopers.desk_branding import brand_erpnext_on_boot


class TestERPNextDeskBranding(unittest.TestCase):
    def _run(self, site, payload):
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=site)
        with patch.dict(sys.modules, {"frappe": frappe}):
            brand_erpnext_on_boot(payload)

    def test_site_scoped_hook_and_no_global_core_override(self):
        from pathlib import Path

        hooks = (Path(__file__).resolve().parents[1] / "erpdevelopers/hooks.py").read_text()
        self.assertIn(
            'boot_session = "erpdevelopers.desk_branding.brand_erpnext_on_boot"', hooks
        )
        self.assertNotIn("override_whitelisted_methods", hooks)

    def test_only_logo_changes_and_permissions_routes_titles_remain_intact(self):
        erpnext = {
            "app_name": "erpnext",
            "app_title": "ERPNext",
            "app_logo_url": "/assets/erpnext/images/erpnext-logo.svg",
            "on_apps_screen": True,
            "app_route": "/desk/home",
            "sequence_id": 1,
            "dock": [{"module": "Accounting"}],
        }
        other = {"app_name": "hrms", "app_logo_url": "/assets/hrms/logo.svg"}
        payload = {"app_data": [erpnext, other]}
        self._run(EXPECTED_SITE, payload)
        self.assertEqual(payload["app_data"][0]["app_logo_url"], FAVICON_URL)
        self.assertEqual(payload["app_data"][0]["app_title"], "ERPNext")
        self.assertEqual(payload["app_data"][0]["app_route"], "/desk/home")
        self.assertEqual(payload["app_data"][0]["dock"], erpnext["dock"])
        self.assertTrue(payload["app_data"][0]["on_apps_screen"])
        self.assertIs(payload["app_data"][1], other)
        self.assertEqual(erpnext["app_logo_url"], "/assets/erpnext/images/erpnext-logo.svg")

    def test_desktop_icons_fallback_changes_only_erpnext_app(self):
        icons = [
            {"app": "erpnext", "icon_type": "App", "logo_url": "/old.png"},
            {"app": "erpnext", "icon_type": "Link", "logo_url": "/keep.png"},
            {"app": "frappe", "icon_type": "App", "logo_url": "/frappe.png"},
        ]
        payload = {"desktop_icons": icons}
        self._run(EXPECTED_SITE, payload)
        self.assertEqual(payload["desktop_icons"][0]["logo_url"], FAVICON_URL)
        self.assertEqual(payload["desktop_icons"][1]["logo_url"], "/keep.png")
        self.assertEqual(payload["desktop_icons"][2]["logo_url"], "/frappe.png")
        self.assertEqual(icons[0]["logo_url"], "/old.png")

    def test_other_sites_are_untouched_on_shared_bench(self):
        payload = {"app_data": [{"app_name": "erpnext", "app_logo_url": "/old"}]}
        original = payload["app_data"]
        self._run("another-site.example", payload)
        self.assertIs(payload["app_data"], original)
        self.assertEqual(payload["app_data"][0]["app_logo_url"], "/old")

    def test_missing_erpnext_and_repeat_runs_are_safe(self):
        payload = {"app_data": [{"app_name": "frappe", "app_logo_url": "/frappe.svg"}]}
        self._run(EXPECTED_SITE, payload)
        self._run(EXPECTED_SITE, payload)
        self.assertEqual(payload["app_data"][0]["app_logo_url"], "/frappe.svg")
        self.assertEqual(payload["app_data"][0]["app_name"], "frappe")

    def test_no_mutation_of_unrecognized_data_shapes(self):
        payload = {"app_data": None, "desktop_icons": {"unexpected": "shape"}}
        self._run(EXPECTED_SITE, payload)
        self.assertIsNone(payload["app_data"])
        self.assertEqual(payload["desktop_icons"], {"unexpected": "shape"})


if __name__ == "__main__":
    unittest.main()
