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

    def test_no_custom_form_or_auth_interception(self):
        js = (APP / "public/js/login_chrome.js").read_text(encoding="utf-8")
        self.assertIn('document.getElementById("page-login")', js)
        self.assertIn('!== "/login"', js)
        self.assertIn("document.body.dataset.edLoginEnhanced", js)
        self.assertIn("document.body.prepend(skip, top)", js)
        for forbidden in ('innerHTML', 'create("form")', 'createElement("form")',
                          "frappe.call(", "fetch(", "XMLHttpRequest",
                          "document.documentElement.lang =", "wrapper.insertBefore("):
            self.assertNotIn(forbidden, js)

    def test_native_sections_remain_unmodified(self):
        js = (APP / "public/js/login_chrome.js").read_text(encoding="utf-8")
        self.assertNotIn("page.querySelectorAll(", js)
        self.assertNotIn("MutationObserver", js)
        css = (APP / "public/css/login.css").read_text(encoding="utf-8")
        self.assertIn('body[data-path="login"]', css)
        self.assertIn(".ed-login-website", css)
        self.assertIn('url("/assets/erpdevelopers/images/login-network.svg")', css)
        self.assertTrue((APP / "public/images/login-network.svg").is_file())

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
