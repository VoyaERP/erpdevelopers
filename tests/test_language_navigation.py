"""A public locale control must not depend on Guest status or an AJAX response."""
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs
import sys

from erpdevelopers.language_navigation import language_queries, set_public_language_context

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


class TestLanguageNavigation(TestCase):
    def test_same_path_queries_use_native_lang_and_preserve_directory_filters(self):
        urls = language_queries({"topic": "Cloud & DevOps", "country": "Saudi Arabia",
                                 "event_format": "In person", "period": "past", "page": "2", "_lang": "en"})
        for lang, url in urls.items():
            self.assertTrue(url.startswith("?"))
            query = parse_qs(url[1:])
            self.assertEqual(query["_lang"], [lang])
            self.assertEqual(query["topic"], ["Cloud & DevOps"])
            self.assertEqual(query["page"], ["2"])
            self.assertEqual(query["period"], ["past"])

    def test_unrecognized_sensitive_or_nonscalar_parameters_are_not_reflected(self):
        urls = language_queries({"redirect-to": "https://evil.invalid", "password": "secret",
                                 "token": "secret", "topic": ["x"], "country": "x" * 257})
        self.assertEqual(urls, {"en": "?_lang=en", "ar": "?_lang=ar"})
        self.assertEqual(language_queries(None), urls)
        self.assertEqual(language_queries("invalid"), urls)

    def test_context_is_available_without_a_frappe_request(self):
        fake = ModuleType("frappe")
        with patch.dict(sys.modules, {"frappe": fake}):
            context = SimpleNamespace()
            set_public_language_context(context)
        self.assertEqual(context.language_queries["ar"], "?_lang=ar")
        self.assertEqual(context.show_language_picker, 0)
        self.assertIn("/js/language.js?v=", context.language_js_url)

    def test_guest_and_logged_in_context_have_the_same_visible_locale_contract(self):
        for user in ("Guest", "member@example.invalid", "Administrator"):
            fake = ModuleType("frappe")
            fake.session = SimpleNamespace(user=user)
            fake.local = SimpleNamespace(form_dict={"topic": "ERP", "_lang": "en"})
            with patch.dict(sys.modules, {"frappe": fake}):
                context = SimpleNamespace()
                set_public_language_context(context)
            self.assertEqual(parse_qs(context.language_queries["ar"][1:]),
                             {"topic": ["ERP"], "_lang": ["ar"]})
            self.assertEqual(fake.session.user, user)

    def test_enhancement_is_loaded_once_per_page_without_global_injection(self):
        for template in ("www/erp-developers-home.html", "templates/includes/erpdevelopers_page_base.html"):
            source = (APP / template).read_text()
            self.assertEqual(source.count("{{ language_js_url | e }}"), 1)
            self.assertIn('data-cfasync="false" defer', source)
        hooks = (APP / "hooks.py").read_text()
        self.assertNotIn("language.js", hooks)
        self.assertNotIn("web_include_js", hooks)
        self.assertFalse((APP / "www/login.html").exists())

    def test_no_ajax_native_override_auth_write_or_private_navigation(self):
        script = (APP / "public/js/language.js").read_text()
        for forbidden in ("frappe.call", "fetch(", "innerHTML", "frappe.show_language_picker",
                          "localStorage", "window.location.reload", "check_permission"):
            self.assertNotIn(forbidden, script)
        self.assertIn('header.dataset.languageBound === "1"', script)
        self.assertIn('url.origin !== window.location.origin', script)
        self.assertIn('!publicPaths.has(url.pathname)', script)
        self.assertIn('href.startsWith("#")', script)
        self.assertIn('form[method="get" i]', script)
        self.assertIn('preferred_language=${target}; Path=/; SameSite=Lax', script)
