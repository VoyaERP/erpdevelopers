from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


class TestNativeLogin(unittest.TestCase):
    def test_assets_not_auth_overrides(self):
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("web_include_js", hooks)
        self.assertIn("login_chrome.js", hooks)
        self.assertIn("login.css", hooks)
        self.assertNotIn("override_whitelisted_methods", hooks)

    def test_login_script_never_creates_form_or_intercepts_login(self):
        js = (APP / "public/js/login_chrome.js").read_text(encoding="utf-8")
        self.assertIn('document.getElementById("page-login")', js)
        self.assertIn('!== "/login"', js)
        for forbidden in ('innerHTML', 'createElement("form")', 'frappe.call(', 'fetch(',
                          'document.documentElement.lang ='):
            self.assertNotIn(forbidden, js)

    def test_css_is_route_scoped(self):
        css = (APP / "public/css/login.css").read_text(encoding="utf-8")
        self.assertIn('body[data-path="login"]', css)
        self.assertIn(".ed-login-website", css)

    def test_site_setup_is_explicit_and_site_scoped(self):
        setup = (APP / "site_setup.py").read_text(encoding="utf-8")
        self.assertIn('EXPECTED_SITE = "erp-developers.com"', setup)
        self.assertIn("frappe.local.site != EXPECTED_SITE", setup)
        self.assertNotIn("@frappe.whitelist", setup)

    def test_homepage_single_chrome(self):
        home = (APP / "www/erp-developers-home.html").read_text(encoding="utf-8")
        self.assertIn("{% block navbar %}{% endblock %}", home)
        self.assertIn("{% block footer %}{% endblock %}", home)
        self.assertIn("{% block page_container %}", home)
        self.assertIn('href="/login"', home)
        self.assertFalse((APP / "www/index.html").exists())

    def test_install_is_site_guarded(self):
        script = (ROOT / "scripts/install_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn('test ! -e "$BENCH/sites/$SITE"', script)
        self.assertIn("bench new-site", script)
        self.assertNotIn("bench update", script)
        self.assertNotIn("drop-site", script)


if __name__ == "__main__":
    unittest.main()
