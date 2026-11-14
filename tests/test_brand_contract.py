from pathlib import Path
import hashlib
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"
LOGO = "erpdevelopers-selected-logo.png"
ICON = "erpdevelopers-selected-favicon.png"


class TestBrandContract(unittest.TestCase):
    def test_exact_user_selected_logo_bytes(self):
        images = APP / "public" / "images"
        logo = (images / LOGO).read_bytes()
        self.assertEqual(len(logo), 419610)
        self.assertTrue(logo.startswith(bytes((137, 80, 78, 71, 13, 10, 26, 10))))
        self.assertEqual(hashlib.sha256(logo).hexdigest(), "250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d")
        self.assertEqual(hashlib.sha256((images / ICON).read_bytes()).hexdigest(), "f329dde3a9af289c82a03601e15a30fe46809cd2a717457cdf62823aecc4524c")

    def test_logo_is_consistent_and_no_generated_logo_used(self):
        home = (APP / "www" / "erp-developers-home.html").read_text(encoding="utf-8")
        js = (APP / "public" / "js" / "login_chrome.js").read_text(encoding="utf-8")
        setup = (APP / "site_setup.py").read_text(encoding="utf-8")
        self.assertGreaterEqual(home.count(LOGO), 2)
        self.assertIn(LOGO, js)
        self.assertIn(LOGO, setup)
        self.assertIn(ICON, setup)
        self.assertNotIn("erp-developers-logo.svg", home + js + setup)
        self.assertNotIn("erp-mark.svg", home + js + setup)
        self.assertIn('"app_logo": BRAND_LOGO', setup)
        self.assertIn('"favicon": ICON', setup)

    def test_brand_words(self):
        home = (APP / "www" / "erp-developers-home.html").read_text(encoding="utf-8")
        for word in ("Engage.", "Reason.", "Progress.", "Developers", "AI"):
            self.assertIn(word, home)

    def test_no_active_integrations_claimed(self):
        home = (APP / "www" / "erp-developers-home.html").read_text(encoding="utf-8")
        self.assertIn("Planned module", home)
        self.assertIn("not active on this preview site", home)

    def test_version_boundary(self):
        config = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('frappe = ">=16.0.0,<17.0.0"', config)


if __name__ == "__main__":
    unittest.main()
