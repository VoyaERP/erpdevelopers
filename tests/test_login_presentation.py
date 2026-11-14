"""Login header is presentation-only, route/site-scoped and always accessible."""
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from urllib.parse import parse_qs
import sys

from erpdevelopers.branding import EXPECTED_SITE, LOGO_URL
from erpdevelopers.language_navigation import language_queries
from erpdevelopers.login_presentation import update_login_context

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


class Context(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__


class TestLoginPresentation(TestCase):
    def invoke(self, context, site=EXPECTED_SITE, query=None):
        fake = ModuleType("frappe")
        fake.local = SimpleNamespace(site=site, form_dict=query or {})
        fake.session = SimpleNamespace(user="Guest")
        with patch.dict(sys.modules, {"frappe": fake}):
            update_login_context(context)
        self.assertEqual(fake.session.user, "Guest")

    def test_other_sites_and_routes_are_untouched(self):
        for path, site in (("login", "another.invalid"), ("training", EXPECTED_SITE),
                           ("desk", EXPECTED_SITE), ("update-password", EXPECTED_SITE)):
            context = Context(path=path, show_language_picker=0, base_template_path="custom.html")
            before = dict(context)
            self.invoke(context, site)
            self.assertEqual(context, before)

    def test_repeated_login_hook_keeps_auth_and_redirect_context(self):
        for path in ("login", "/login"):
            context = Context(path=path, disable_signup=True, disable_user_pass_login=True,
                              provider_logins=[{"name": "SSO"}], redirect_to="/desk")
            self.invoke(context, query={"redirect-to": "/desk"})
            self.assertTrue(context.disable_signup)
            self.assertTrue(context.disable_user_pass_login)
            self.assertEqual(context.provider_logins, [{"name": "SSO"}])
            self.assertEqual(context.redirect_to, "/desk")
            self.assertEqual(context.brand_logo_url, LOGO_URL)
            self.assertEqual(context.show_language_picker, 1)
            self.assertEqual(context.base_template_path, "templates/erpdevelopers_login_base.html")
            self.assertIn("js/language.js?v=", context.language_js_url)
            previous = dict(context)
            self.invoke(context, query={"redirect-to": "/desk"})
            self.assertEqual(context, previous)

    def test_safe_local_redirect_preserved_without_sensitive_values(self):
        for redirect in ("/desk", "/desk/project/PROJ-001", "/projects?page=2", "/desk#task"):
            urls = language_queries({"redirect-to": redirect, "password": "secret", "token": "secret"}, login=True)
            self.assertEqual(parse_qs(urls["ar"][1:]), {"redirect-to": [redirect], "_lang": ["ar"]})

    def test_unsafe_redirects_are_not_reflected_by_server_fallback(self):
        for redirect in ("https://evil.invalid", "//evil.invalid", "/%2fevil.invalid",
                         "/%252fevil.invalid", "/\\evil.invalid", "/%0aevil", "x", ["/desk"], "x" * 2049):
            with self.subTest(redirect=redirect):
                self.assertEqual(language_queries({"redirect-to": redirect}, login=True),
                                 {"en": "?_lang=en", "ar": "?_lang=ar"})

    def test_login_shares_control_and_script_without_auth_template_copy(self):
        base = (APP / "templates/erpdevelopers_login_base.html").read_text()
        self.assertIn('{% extends "templates/base.html" %}', base)
        self.assertEqual(base.count('import language_control with context'), 1)
        self.assertEqual(base.count('{{ language_control() }}'), 1)
        self.assertEqual(base.count('{{ language_js_url | e }}'), 1)
        self.assertEqual(base.count('<nav '), 1)
        self.assertNotIn('<form', base)
        self.assertNotIn('page_content', base)
        self.assertIn('window.show_language_picker = false;', base)
        self.assertIn('block base_scripts', base)
        self.assertFalse((APP / "www/login.html").exists())
        self.assertFalse((APP / "www/login.py").exists())
        script = (APP / "public/js/language.js").read_text()
        self.assertIn('header.closest(".ed-site") || header', script)
        self.assertIn('!scope.contains(anchor)', script)
        for forbidden in ('password', 'form-login', 'sessionStorage', 'localStorage', 'frappe.call'):
            self.assertNotIn(forbidden, script)

    def test_logo_sizes_are_proportional_and_control_is_never_hidden(self):
        css = (APP / "public/css/login.css").read_text()
        self.assertIn('flex:0 1 260px', css)
        self.assertIn('flex-basis:200px', css)
        self.assertIn('aspect-ratio:2048/682', css)
        self.assertIn('min-height:46px', css)
        self.assertNotIn('#language-switcher.hide', css)
        self.assertNotIn('max-width:145px', css)


class TestLoginHeaderInspection(TestCase):
    def test_server_markup_and_stale_picker(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location("login_header_check", ROOT / "scripts/inspect_login_brand.py")
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        html = '<nav class="navbar ed-login-nav"><a id="language-switcher" href="?_lang=ar" data-language-switch="ar" hreflang="ar">Arabic</a></nav><script defer src="/assets/erpdevelopers/js/language.js?v=abc"></script>'
        self.assertTrue(module.inspect_language_control(html)[0])
        self.assertFalse(module.inspect_language_control(html.replace('<a id=', '<select id='))[0])
        self.assertFalse(module.inspect_language_control(html.replace('hreflang="ar"', 'hreflang="ar" hidden'))[0])
        self.assertFalse(module.inspect_language_control(html + html)[0])
        self.assertFalse(module.inspect_language_control(html.replace('?_lang=ar', 'https://bad.invalid/?_lang=ar'))[0])
