"""Behavioral contracts for branding, Frappe route context and safe website setup."""
from hashlib import sha256
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase, mock
from importlib import util
import sys

from erpdevelopers import branding
from erpdevelopers.seo import ROBOTS_TXT

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
        self.assertEqual(sha256(logo).hexdigest(), "250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d")
        self.assertEqual(sha256((images / ICON).read_bytes()).hexdigest(), "f329dde3a9af289c82a03601e15a30fe46809cd2a717457cdf62823aecc4524c")
        self.assertEqual(branding.LOGO_URL.rsplit("/", 1)[-1], LOGO)
        self.assertEqual(branding.FAVICON_URL.rsplit("/", 1)[-1], ICON)

    def test_content_hashed_css_url_and_no_duplicate_global_include(self):
        css = (APP / "public" / "css" / "brand.css").read_bytes()
        expected = sha256(css).hexdigest()[:16]
        self.assertEqual(branding.homepage_stylesheet_url(), f"/assets/erpdevelopers/css/brand.css?v={expected}")
        home = (APP / "www/erp-developers-home.html").read_text(encoding="utf-8")
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn('{% block head_include %}', home)
        self.assertIn('{{ super() }}', home)
        self.assertEqual(home.count('{{ homepage_css_url | e }}'), 1)
        self.assertIn('rel="stylesheet"', home)
        self.assertNotIn('/assets/erpdevelopers/css/brand.css', home)
        self.assertNotIn('/assets/erpdevelopers/css/brand.css', hooks)
        self.assertIn('login_stylesheet_url()', hooks)
        self.assertNotIn('web_include_js', hooks)
        self.assertNotIn('login_chrome.js', hooks)
        self.assertEqual(branding.login_stylesheet_url(), "/assets/erpdevelopers/css/login.css?v=" + sha256((APP / "public/css/login.css").read_bytes()).hexdigest()[:16])

    def test_page_controller_binds_frappe_hyphenated_route(self):
        self.assertTrue((APP / "www" / (branding.HOME_ROUTE + ".html")).is_file())
        self.assertTrue((APP / "www" / (branding.HOME_ROUTE.replace("-", "_") + ".py")).is_file())
        from erpdevelopers.www.erp_developers_home import get_context
        context = SimpleNamespace()
        get_context(context)
        self.assertEqual(context.brand_logo_url, branding.LOGO_URL)
        self.assertEqual(context.desk_signin_url, branding.DESK_SIGNIN_URL)
        self.assertEqual(branding.DESK_SIGNIN_URL, "/login?redirect-to=/desk")
        self.assertEqual(context.brand_icon_url, branding.FAVICON_URL)
        self.assertEqual(context.homepage_css_url, branding.homepage_stylesheet_url())
        self.assertEqual(context.title, "ERP Developers | Developer Community & Technology")
        self.assertEqual(context.no_cache, 1)

    def test_brand_assets_have_one_authoritative_source(self):
        home = (APP / "www/erp-developers-home.html").read_text()
        nav = (APP / "templates/includes/erpdevelopers_nav.html").read_text()
        footer = (APP / "templates/includes/erpdevelopers_footer.html").read_text()
        setup = (APP / "site_setup.py").read_text()
        self.assertEqual(nav.count("{{ brand_logo_url | e }}"), 1)
        self.assertEqual(footer.count("{{ brand_logo_url | e }}"), 1)
        self.assertNotIn("Building a smarter, more connected technology community.", footer)
        for section in (home, nav, footer):
            self.assertNotIn('Book a Meeting', section)
            self.assertNotIn('Book a meeting', section)
            self.assertIn('{{ _("Let\'s Talk") }}', section)
        self.assertIn('href="/lets-talk#meeting-start"', nav)
        self.assertIn('href="/lets-talk#meeting-start"', footer)
        self.assertEqual(home.count("{{ brand_icon_url | e }}"), 1)
        self.assertIn('include "templates/includes/erpdevelopers_nav.html"', home)
        self.assertIn('include "templates/includes/erpdevelopers_footer.html"', home)
        self.assertIn(branding.LOGO_URL, branding.NAVBAR_BRAND_HTML)
        self.assertIn("website_settings_values()", setup)
        self.assertNotIn("erp-mark.svg", home + nav + footer + setup)
        self.assertNotIn("erp-developers-logo.svg", home + nav + footer + setup)
        self.assertNotIn("erpdevelopers-selected-logo.png", home + nav + footer)

    def test_static_content_is_typed_and_declared_once(self):
        from erpdevelopers import content
        home = (APP / "www/erp-developers-home.html").read_text(encoding="utf-8")
        self.assertEqual(len(content.VALUES), 3)
        self.assertEqual(len(content.ECOSYSTEM), 6)
        for collection in (content.VALUES, content.ECOSYSTEM):
            self.assertEqual(len({entry.index for entry in collection}), len(collection))
            self.assertTrue(all(entry.title.strip() and entry.description.strip() for entry in collection))
        self.assertIn("{% for item in ecosystem_items %}", home)
        self.assertIn("{% for value in values_items %}", home)
        self.assertNotIn("{{ item.index", home, "Card numbering must not be visible")
        self.assertNotIn("{{ value.index", home, "Brand pills must not have numbering")
        self.assertNotIn("{{ step.index", home, "Presentation-style roadmap removed")
        self.assertNotIn("ed-steps", home)
        self.assertIn("Planned module", home)
        self.assertIn('href="/lets-talk#meeting-start"', home)
        self.assertIn("ed-link-grid", home)

    def test_html_copy_does_not_claim_roadmap_features_are_running(self):
        from erpdevelopers import content
        home = (APP / "www/erp-developers-home.html").read_text()
        nav = (APP / "templates/includes/erpdevelopers_nav.html").read_text()
        self.assertEqual([v.title for v in content.VALUES], ["Engage.", "Reason.", "Progress."])
        self.assertIn("ERP Developers", nav)
        self.assertIn("Planned module", home)
        self.assertIn("AI advisory features are planned, not active today.", home)
        self.assertNotIn("AI capabilities are live", home)

    def test_native_frappe_bilingual_selector_and_translation_coverage(self):
        import csv
        import re
        from babel.messages.pofile import read_po
        from erpdevelopers import content
        from erpdevelopers.intake_rules import TOPICS, WINDOWS
        from erpdevelopers.event_rules import TOPICS as EVENT_TOPICS, FORMATS, EVENT_TYPES, STATUSES
        home = (APP / "www/erp-developers-home.html").read_text(encoding="utf-8")
        files = [
            "templates/includes/erpdevelopers_nav.html", "templates/includes/erpdevelopers_footer.html",
            "templates/includes/erpdevelopers_assistant.html", "www/training.html", "www/insights.html",
            "www/lets-talk.html", "www/privacy.html", "www/events.html",
        ]
        sources = [home] + [(APP / f).read_text(encoding="utf-8") for f in files]
        with (APP / "translations/ar.csv").open(encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream))
        self.assertTrue(all(len(row) == 2 and row[0] and row[1] for row in rows))
        translations = {en: ar for en, ar in rows}
        self.assertEqual(len(translations), len(rows), "Arabic CSV keys must be unique")
        # Frappe v16 merges CSV and compiled gettext; validate both native sources.
        with (APP / "locale/ar.po").open("rb") as stream:
            messages = read_po(stream, locale="ar", abort_invalid=True)
        self.assertFalse(list(messages.check()))
        translations.update({m.id: m.string for m in messages if m.id and isinstance(m.id, str) and m.string})
        literals = set()
        for html in sources:
            literals.update(m.group(2) for m in re.finditer(r"""_\((["'])(.*?)\1\)""", html))
        dynamic = set(TOPICS) | set(WINDOWS) | set(EVENT_TOPICS) | set(FORMATS) | set(EVENT_TYPES) | set(STATUSES)
        for items in (content.ECOSYSTEM, content.AI_FLOW, content.ROADMAP):
            dynamic.update(x.title for x in items)
            dynamic.update(x.description for x in items)
        missing = (literals | dynamic) - set(translations)
        self.assertFalse(missing, f"Missing Arabic translations: {sorted(missing)}")
        nav = sources[1]
        self.assertIn('id="language-switcher"', nav)
        self.assertIn('id="ed-language-select"', nav)
        self.assertIn('class="form-control"', nav)
        self.assertIn("{{ _(item.title) | e }}", home)
        self.assertIn("{{ _(value.title) | e }}", home)
        self.assertNotIn("{{ step.index", home)

    def test_css_rules_scoped_and_responsive(self):
        css = (APP / "public/css/brand.css").read_text(encoding="utf-8")
        login = (APP / "public/css/login.css").read_text(encoding="utf-8")
        self.assertIn(".ed-site {", css)
        self.assertNotIn(":root {", css)
        self.assertIn(".ed-hero-inner{", css)
        self.assertIn(".ed-skip{", css)
        self.assertIn("@media(max-width:540px)", css)
        self.assertIn('body[data-path="login"]', login)
        self.assertIn('url("/assets/erpdevelopers/images/login-network.svg")', login)

    def test_version_boundary(self):
        config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('frappe = ">=16.0.0,<17.0.0"', config)
        self.assertIn('erpnext = ">=16.0.0,<17.0.0"', config)


class TestSiteScopedBranding(TestCase):
    def _fixture(self, site):
        calls = {"get_single": 0, "save": 0, "commit": 0, "clear_cache": 0}
        website_fields, desk_fields = {}, {}
        class Settings:
            def __init__(self, fields):
                self.fields = fields
            def get(self, key):
                return self.fields.get(key)
            def set(self, key, value):
                self.fields[key] = value
            def save(self, ignore_permissions=False):
                if ignore_permissions is not True:
                    raise AssertionError("Expected explicit admin-only site setup")
                calls["save"] += 1
        def get_single(doctype):
            calls["get_single"] += 1
            if doctype == "Website Settings":
                return Settings(website_fields)
            if doctype == "Navbar Settings":
                return Settings(desk_fields)
            raise AssertionError("Unexpected single doctype read: " + doctype)
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=site)
        frappe.get_single = get_single
        frappe.db = SimpleNamespace(commit=lambda: calls.__setitem__("commit", calls["commit"] + 1))
        frappe.clear_cache = lambda: calls.__setitem__("clear_cache", calls["clear_cache"] + 1)
        spec = util.spec_from_file_location("erpdevelopers_site_setup_under_test", APP / "site_setup.py")
        module = util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {"frappe": frappe}):
            spec.loader.exec_module(module)
        return module, calls, website_fields, desk_fields

    def test_rejects_other_site_before_reading_or_writing_db(self):
        module, calls, website, desk = self._fixture("other-site.example")
        with self.assertRaisesRegex(RuntimeError, "unexpected site"):
            module.configure_website()
        self.assertEqual(calls, {"get_single": 0, "save": 0, "commit": 0, "clear_cache": 0})
        self.assertEqual(website, {})
        self.assertEqual(desk, {})

    def test_updates_both_branding_surfaces_in_one_transaction(self):
        module, calls, website, desk = self._fixture(branding.EXPECTED_SITE)
        first = module.configure_website()
        self.assertEqual(first["site"], branding.EXPECTED_SITE)
        self.assertEqual(set(first["changed_fields"]), set(branding.website_settings_values()) | {"robots_txt"})
        self.assertEqual(first["desk_changed_fields"], ["app_logo"])
        self.assertEqual(website, {**branding.website_settings_values(), "robots_txt": ROBOTS_TXT})
        self.assertEqual(desk, branding.desk_navbar_settings_values())
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["commit"], 1)
        self.assertEqual(calls["clear_cache"], 1)
        again = module.configure_website()
        self.assertEqual(again["changed_fields"], [])
        self.assertEqual(again["desk_changed_fields"], [])
        self.assertEqual(calls["save"], 2)
        self.assertEqual(calls["commit"], 1)
        self.assertEqual(calls["clear_cache"], 1)

    def test_existing_website_branding_unchanged_when_only_desk_logo_is_missing(self):
        module, calls, website, desk = self._fixture(branding.EXPECTED_SITE)
        website.update(branding.website_settings_values())
        website["robots_txt"] = ROBOTS_TXT
        result = module.configure_website()
        self.assertEqual(result["changed_fields"], [])
        self.assertEqual(result["desk_changed_fields"], ["app_logo"])
        self.assertEqual(calls["save"], 1)
        self.assertEqual(calls["commit"], 1)
        self.assertEqual(website, {**branding.website_settings_values(), "robots_txt": ROBOTS_TXT})
        self.assertEqual(desk, branding.desk_navbar_settings_values())

    def test_existing_custom_robots_policy_is_preserved(self):
        module, calls, website, desk = self._fixture(branding.EXPECTED_SITE)
        website.update(branding.website_settings_values())
        website["robots_txt"] = "User-agent: *\\nDisallow: /\\n"
        desk.update(branding.desk_navbar_settings_values())
        result = module.configure_website()
        self.assertEqual(result["changed_fields"], [])
        self.assertEqual(result["desk_changed_fields"], [])
        self.assertEqual(website["robots_txt"], "User-agent: *\\nDisallow: /\\n")
        self.assertEqual(calls["save"], 0)
        self.assertEqual(calls["commit"], 0)

    def test_settings_mapping_is_not_shared_mutable_state(self):
        first = branding.website_settings_values()
        first["app_logo"] = "/wrong-logo.png"
        desk = branding.desk_navbar_settings_values()
        desk["app_logo"] = "/wrong-desk-logo.png"
        self.assertEqual(branding.website_settings_values()["app_logo"], branding.LOGO_URL)
        self.assertEqual(branding.desk_navbar_settings_values()["app_logo"], branding.LOGO_URL)
