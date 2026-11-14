"""First-paint contracts for the existing single public navigation."""
from pathlib import Path
from unittest import TestCase

APP = Path(__file__).resolve().parents[1] / "erpdevelopers"


class TestNavigationStability(TestCase):
    def test_language_picker_keeps_its_space_during_native_loading(self):
        css = (APP / "public/css/brand.css").read_text()
        self.assertIn('.ed-nav .ed-language-switcher{display:block!important', css)
        self.assertIn('.ed-nav .ed-language-switcher.hide{visibility:hidden;pointer-events:none}', css)
        self.assertNotIn('.ed-language-switcher.hide{display:none', css)
        self.assertIn('grid-template-columns:112px 120px', css)
        self.assertIn('grid-template-columns:70px 108px', css)

    def test_one_header_and_native_picker_no_new_navigation_script(self):
        nav = (APP / "templates/includes/erpdevelopers_nav.html").read_text()
        self.assertEqual(nav.count('<header '), 1)
        self.assertEqual(nav.count('id="language-switcher"'), 1)
        self.assertEqual(nav.count('<select '), 1)
        self.assertNotIn('<script', nav)
        self.assertNotIn('onclick=', nav)
        self.assertNotIn('onchange=', nav)
        self.assertIn('class="ed-nav-links"', nav)
        self.assertIn('lang="{{ boot.lang | e }}"', nav)
        self.assertIn("boot.lang.startswith('ar')", nav)

    def test_header_styles_are_not_a_second_override_file(self):
        css = (APP / "public/css/brand.css").read_text()
        self.assertEqual(css.count('.ed-nav{'), 1)
        self.assertFalse((APP / "public/css/navigation.css").exists())
        self.assertFalse((APP / "public/js/navigation.js").exists())
        self.assertIn('height:69px;max-width:100%;object-fit:contain', css)

    def test_short_labels_stay_whole_without_forcing_body_text_to_nowrap(self):
        css = (APP / "public/css/brand.css").read_text()
        self.assertIn('white-space:nowrap;word-break:normal;overflow-wrap:normal', css)
        self.assertIn('.ed-footer-links a{flex:none;white-space:nowrap', css)
        self.assertIn('grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))', css)
        self.assertNotIn('.ed-site *{white-space:nowrap', css)
        self.assertNotIn('text-overflow:ellipsis', css)
