from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TestBrandContract(unittest.TestCase):
    def test_brand_words(self):
        template = (ROOT / "erpdevelopers/www/erp-developers-home.html").read_text(encoding="utf-8")
        for word in ("Engage.", "Reason.", "Progress.", "Developers", "AI"):
            self.assertIn(word, template)

    def test_approved_neural_logo_is_exact_and_not_placeholder(self):
        import hashlib

        images = ROOT / "erpdevelopers/public/images"
        original = (images / "erp-developers-neural-intelligence.svg").read_bytes()
        self.assertEqual(
            hashlib.sha256(original).hexdigest(),
            "9ff7a4b8409a3bbf1f5cf438e5d73fc3d3fd28f564576c720c572d55f6d93293",
        )
        canonical = original.decode("utf-8")
        viewport = 'width="1400" height="360" viewBox="0 0 1400 360"'
        cropped = canonical.replace(
            viewport, 'width="780" height="310" viewBox="42 20 780 310"'
        )
        self.assertEqual((images / "erp-developers-logo.svg").read_text(encoding="utf-8"), cropped)
        icon = canonical.replace(
            viewport, 'width="268" height="268" viewBox="64 37 268 268"'
        )
        import re
        icon = re.sub(r'\n<g font-family="Inter,Arial,sans-serif">[\s\S]*?</g>', "", icon)
        self.assertEqual((images / "erp-mark.svg").read_text(encoding="utf-8"), icon)

    def test_logo_appears_on_home_and_login_and_site_branding(self):
        homepage = (ROOT / "erpdevelopers/www/erp-developers-home.html").read_text(encoding="utf-8")
        login_js = (ROOT / "erpdevelopers/public/js/login_chrome.js").read_text(encoding="utf-8")
        site_setup = (ROOT / "erpdevelopers/site_setup.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(homepage.count("erp-developers-logo.svg"), 2)
        self.assertIn("erp-mark.svg", homepage)
        self.assertIn("erp-developers-logo.svg", login_js)
        self.assertIn('"app_logo": BRAND_LOGO', site_setup)
        self.assertIn('"favicon": ICON', site_setup)
        self.assertNotIn("wordmark()", login_js)

    def test_compact_responsive_layout_and_native_login_remain(self):
        homepage = (ROOT / "erpdevelopers/www/erp-developers-home.html").read_text(encoding="utf-8")
        home_css = (ROOT / "erpdevelopers/public/css/brand.css").read_text(encoding="utf-8")
        login_css = (ROOT / "erpdevelopers/public/css/login.css").read_text(encoding="utf-8")
        self.assertIn("ed-hero-inner", homepage)
        self.assertIn("ed-visual", homepage)
        self.assertIn("ed-grid", homepage)
        self.assertIn("@media(max-width:540px)", home_css)
        self.assertIn("padding-top:52px;padding-bottom:57px", home_css)
        self.assertIn("min-height:426px", login_css)
        self.assertIn("url(\"/assets/erpdevelopers/images/login-network.svg\")", login_css)

    def test_no_active_integrations_claimed(self):
        template = (ROOT / "erpdevelopers/www/erp-developers-home.html").read_text(encoding="utf-8")
        self.assertIn("Planned module", template)
        self.assertIn("not active on this preview site", template)

    def test_version_boundary(self):
        config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('frappe = ">=16.0.0,<17.0.0"', config)


if __name__ == "__main__":
    unittest.main()
