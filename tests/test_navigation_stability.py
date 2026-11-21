"""First-paint contracts for the existing single public navigation."""
from pathlib import Path
from unittest import TestCase

APP = Path(__file__).resolve().parents[1] / "erpdevelopers"


class TestNavigationStability(TestCase):
    def test_language_control_visible_in_a_fixed_slot(self):
        css = (APP / "public/css/brand.css").read_text()
        self.assertIn('.ed-nav .ed-language-switcher{display:inline-flex', css)
        self.assertIn('padding:6px 2px;border:0;border-radius:0;background:transparent', css)
        self.assertIn('.ed-nav-tools{display:flex', css)
        self.assertIn('grid-template-columns:190px minmax(0,1fr) max-content', css)
        self.assertNotIn('.ed-language-switcher.hide', css)
        self.assertNotIn('visibility:hidden', css)
        self.assertNotIn('grid-template-columns:112px 120px', css)

    def test_navigation_links_use_compact_spacing_instead_of_distribution(self):
        css = (APP / "public/css/brand.css").read_text()
        self.assertIn(
            ".ed-nav nav{display:flex;align-items:center;justify-content:center;gap:clamp(8px,.75vw,14px)",
            css,
        )
        self.assertIn(
            "justify-content:flex-start;gap:clamp(8px,1vw,14px);overflow-x:auto",
            css,
        )
        self.assertNotIn(
            ".ed-nav nav{display:flex;align-items:center;justify-content:space-between",
            css,
        )

    def test_one_header_and_server_rendered_link_no_inline_script(self):
        nav = (APP / "templates/includes/erpdevelopers_nav.html").read_text()
        self.assertEqual(nav.count('<header '), 1)
        self.assertEqual(nav.count('id="language-switcher"'), 1)
        self.assertEqual(nav.count('data-language-switch='), 1)
        self.assertNotIn('<select ', nav)
        self.assertIn('language_queries[other_language]', nav)
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
        self.assertIn('height:63px;max-width:100%;object-fit:contain', css)

    def test_short_labels_stay_whole_without_forcing_body_text_to_nowrap(self):
        css = (APP / "public/css/brand.css").read_text()
        self.assertIn('white-space:nowrap;word-break:normal;overflow-wrap:normal', css)
        self.assertIn('.ed-footer-links a{flex:none;white-space:nowrap', css)
        self.assertIn('grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))', css)
        self.assertNotIn('.ed-site *{white-space:nowrap', css)
        self.assertNotIn('text-overflow:ellipsis', css)
