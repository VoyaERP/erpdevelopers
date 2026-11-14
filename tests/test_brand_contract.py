"""Behavioral contracts for branding, Frappe route context and safe website setup."""

from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase, mock
from importlib import util
import sys

from erpdevelopers import branding

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"
LOGO = "erpdevelopers-selected-logo.png"
ICON = "erpdevelopers-selected-favicon.png"


class TestBrandContract(TestCase):
    def test_customer_logo_is_byte_exact(self):
        images = APP / "public" / "images"
        logo = (images / LOGO).read_bytes()
        self.assertEqual(len(logo), 419610)
        self.assertTrue(logo.startswith(bytes((137, 80, 78, 71, 13, 10, 26, 10))))
        self.assertEqual(
            sha256(logo).hexdigest(),
            "250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d",
        )
        self.assertEqual(
            sha256((images / ICON).read_bytes()).hexdigest(),
            "f329dde3a9af289c82a03601e15a30fe46809cd2a717457cdf62823aecc4524c",
        )
        self.assertEqual(branding.LOGO_URL.rsplit("/", 1)[-1], LOGO)
        self.assertEqual(branding.FAVICON_URL.rsplit("/", 1)[-1], ICON)

    def test_content_hashed_css_url_and_no_duplicate_global_include(self):
        css = (APP / "public" / "css" / "brand.css").read_bytes()
        url = branding.homepage_stylesheet_url()
        expected = sha256(css).hexdigest()[:16]
        self.assertEqual(url, f"/assets/erpdevelopers/css/brand.css?v={expected}")

        home = (APP / "www" / "erp-developers-home.html").read_text(encoding="utf-8")
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn('{% block head_include %}', home)
        self.assertIn('{{ super() }}', home)
        self.assertEqual(home.count('{{ homepage_css_url | e }}'), 1)
        self.assertIn('rel="stylesheet"', home)
        self.assertNotIn('/assets/erpdevelopers/css/brand.css', home)
        self.assertNotIn('/assets/erpdevelopers/css/brand.css', hooks)
        self.assertIn('login.css', hooks)
        self.assertIn('login_chrome.js', hooks)

    def test_page_controller_binds_frappe_hyphenated_route(self):
        self.assertTrue((APP / "www" / (branding.HOME_ROUTE + ".html")).is_file())
        self.assertTrue(
            (APP / "www" / (branding.HOME_ROUTE.replace("-", "_") + ".py")).is_file()
        )
        from erpdevelopers.www.erp_developers_home import get_context
        context = SimpleNamespace()
        get_context(context)
        self.assertEqual(context.brand_logo_url, branding.LOGO_URL)
        self.assertEqual(context.homepage_css_url, branding.homepage_stylesheet_url())
        self.assertEqual(context.title, branding.APP_NAME + " | " + branding.TAGLINE)
        self.assertEqual(context.no_cache, 1)

    def test_brand_assets_have_one_authoritative_source(self):
        home = (APP / "www" / "erp-developers-home.html").read_text(encoding="utf-8")
        js = (APP / "public" / "js" / "login_chrome.js").read_text(encoding="utf-8")
        setup = (APP / "site_setup.py").read_text(encoding="utf-8")
        self.assertEqual(home.count('{{ brand_logo_url | e }}'), 3)
        self.assertIn(branding.LOGO_URL, js)  # fallback for native login chrome
        self.assertIn('website_settings_values()', setup)
        self.assertNotIn("erp-mark.svg", home + js + setup)
        self.assertNotIn("erp-developers-logo.svg", home + js + setup)
        self.assertNotIn("erpdevelopers-selected-logo.png", home)

    def test_html_copy_does_not_claim_roadmap_features_are_running(self):
        home = (APP / "www" / "erp-developers-home.html").read_text(encoding="utf-8")
        for word in ("Engage.", "Reason.", "Progress.", "Developers", "AI"):
            self.assertIn(word, home)
        self.assertIn("Planned module", home)
        self.assertIn("not active on this preview site", home)

    def test_css_rules_scoped_and_responsive(self):
        css = (APP / "public" / "css" / "brand.css").read_text(encoding="utf-8")
        login = (APP / "public" / "css" / "login.css").read_text(encoding="utf-8")
        self.assertIn(".ed-site {", css)
        self.assertNotIn(":root {", css)
        self.assertIn(".ed-hero-inner {", css)
        self.assertIn(".ed-skip {", css)
        self.assertIn("@media(max-width:540px)", css)
        self.assertIn('body[data-path="login"]', login)
        self.assertIn('url("/assets/erpdevelopers/images/login-network.svg")', login)

    def test_version_boundary(self):
        config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('frappe = ">=16.0.0,<17.0.0"', config)


class TestSiteScopedBranding(TestCase):
    def _fixture(self, site):
        calls = {"get_single": 0, "save": 0, "commit": 0, "clear_cache": 0}
        values = {}

        class Settings:
            def get(self, key):
                return values.get(key)

            def set(self, key, value):
                values[key] = value

            def save(self, ignore_permissions=False):
                self_is_correct = ignore_permissions is True
                if not self_is_correct:
                    raise AssertionError("Expected explicit administrator-only setup")
                calls["save"] += 1

        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=site)
        frappe.get_single = lambda doctype: (
            calls.__setitem__("get_single", calls["get_single"] + 1) or Settings()
        ) if doctype == "Website Settings" else None
        frappe.db = SimpleNamespace(
            commit=lambda: calls.__setitem__("commit", calls["commit"] + 1)
        )
        frappe.clear_cache = lambda: calls.__setitem__(
            "clear_cache", calls["clear_cache"] + 1
        )

        # The real site_setup imports frappe; simulate it without a bench/DB.
        spec = util.spec_from_file_location(
            "erpdevelopers_site_setup_under_test", APP / "site_setup.py"
        )
        module = util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {"frappe": frappe}):
            spec.loader.exec_module(module)
        return module, calls, values

    def test_rejects_other_site_before_reading_or_writing_db(self):
        module, calls, values = self._fixture("other-site.example")
        with self.assertRaisesRegex(RuntimeError, "unexpected site"):
            module.configure_website()
        self.assertEqual(calls, {"get_single": 0, "save": 0, "commit": 0, "clear_cache": 0})
        self.assertEqual(values, {})

    def test_updates_only_changed_settings_and_is_idempotent(self):
        module, calls, values = self._fixture(branding.EXPECTED_SITE)
        first = module.configure_website()
        self.assertEqual(first["site"], branding.EXPECTED_SITE)
        self.assertEqual(set(first["changed_fields"]), set(branding.website_settings_values()))
        self.assertEqual(values, branding.website_settings_values())
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["commit"], 1)

        again = module.configure_website()
        self.assertEqual(again["changed_fields"], [])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["commit"], 1)
        self.assertEqual(calls["clear_cache"], 1)

    def test_settings_mapping_is_not_shared_mutable_state(self):
        first = branding.website_settings_values()
        first["app_logo"] = "/wrong-logo.png"
        self.assertEqual(branding.website_settings_values()["app_logo"], branding.LOGO_URL)
