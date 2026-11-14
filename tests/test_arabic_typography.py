"""Greenbox-family Arabic typography without a global Desk/theme override."""
from pathlib import Path
from unittest import TestCase

from erpdevelopers.branding import versioned_public_asset
from erpdevelopers.hooks import web_include_css

APP = Path(__file__).resolve().parents[1] / "erpdevelopers"


class TestArabicTypography(TestCase):
    def test_greenbox_tajawal_is_loaded_and_not_just_named(self):
        css = (APP / "public/css/arabic_typography.css").read_text()
        self.assertIn("family=Tajawal:wght@400;500;700;800&display=swap", css)
        self.assertIn('font-family:"Tajawal",Arial,sans-serif', css)
        self.assertNotIn("Noto Sans Arabic", css)

    def test_public_and_native_login_styles_are_arabic_scoped(self):
        css = (APP / "public/css/arabic_typography.css").read_text()
        self.assertIn('html[lang^="ar"] .ed-site', css)
        self.assertIn('body[data-path="login"]', css)
        self.assertNotIn(":root", css)
        self.assertNotIn(".desk", css)
        self.assertIn("letter-spacing:0", css)
        self.assertIn("line-height:1.9", css)

    def test_shared_stylesheet_is_fingerprinted_once(self):
        expected = versioned_public_asset("css/arabic_typography.css")
        self.assertEqual(web_include_css.count(expected), 1)
        self.assertIn("?v=", expected)
