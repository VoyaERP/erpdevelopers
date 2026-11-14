"""Regression checks for the website's bilingual responsive layout.

These tests inspect shipped styles and templates. They cannot replace visual
browser UAT on the deployed Frappe/ERPNext site.
"""
from pathlib import Path
from unittest import TestCase

APP = Path(__file__).resolve().parents[1] / "erpdevelopers"
BRAND = (APP / "public/css/brand.css").read_text(encoding="utf-8")
PORTAL = (APP / "public/css/portal.css").read_text(encoding="utf-8")
MEETING = (APP / "public/css/meeting.css").read_text(encoding="utf-8")


class TestResponsiveWebsite(TestCase):
    def test_arabic_heading_leading_and_direction(self):
        self.assertIn('html[lang^="ar"] .ed-site{', BRAND)
        self.assertIn('direction:rtl;line-height:1.85', BRAND)
        self.assertIn('html[lang^="ar"] .ed-site :is(h1,h2,h3){line-height:1.5', BRAND)
        self.assertIn('font-size:clamp(35px,9vw,44px)', BRAND)
        self.assertIn("overflow-wrap:break-word", BRAND)
        self.assertIn("text-wrap:balance", BRAND)

    def test_mobile_navigation_has_separate_rows(self):
        self.assertIn("@media(max-width:1100px){", BRAND)
        self.assertIn("overflow-x:auto;scrollbar-width:thin", BRAND)
        self.assertIn("@media(max-width:480px){", BRAND)
        for phrase in (
            ".ed-nav-tools{display:contents}",
            ".ed-nav-cta{grid-column:2;grid-row:2",
            ".ed-nav nav{grid-column:1;grid-row:2",
        ):
            self.assertIn(phrase, BRAND)

    def test_decorative_labels_never_force_text_overlap(self):
        self.assertNotIn("min-width:max-content", BRAND)
        self.assertIn(".ed-art-float-a,.ed-art-float-b,.ed-art-float-c{position:static", BRAND)
        self.assertIn(".ed-link-grid{display:grid;grid-template-columns:minmax(0,1.14fr)", BRAND)
        self.assertIn(".ed-section-head>p{flex:0 1 385px;min-width:0", BRAND)
        self.assertIn("max-width:43%", BRAND)
        self.assertIn("overflow-x:clip;overflow-y:visible", BRAND)

    def test_booking_form_adapts_and_preserves_accessible_fields(self):
        html = (APP / "www/lets-talk.html").read_text(encoding="utf-8")
        self.assertIn(".ed-meet-booking-layout{display:grid;grid-template-columns:minmax(0,1.47fr)", MEETING)
        self.assertIn(".ed-booking-head{display:flex;align-items:start;justify-content:space-between;flex-wrap:wrap", MEETING)
        self.assertIn(".ed-meeting-picker{grid-template-columns:1fr}", MEETING)
        self.assertIn(".ed-booking-pane :is(input,select,textarea){font-size:16px}", MEETING)
        self.assertIn(".ed-meeting-selection>span:last-child{min-width:0;flex:1", MEETING)
        self.assertIn(".ed-booking-pane[hidden]{display:none!important}", MEETING)
        self.assertIn("@media(max-width:900px){", MEETING)
        self.assertIn("@media(max-width:700px){", MEETING)
        self.assertIn('id="ed-meeting-form"', html)
        self.assertEqual(html.count('<form id="ed-meeting-form"'), 1)
        self.assertIn('id="ed-meeting-consent"', html)
        self.assertIn('id="ed-meeting-month"', html)
        self.assertIn('id="ed-meeting-slots"', html)
        self.assertIn('id="ed-meet-aside-selection"', html)
        self.assertIn('id="meeting-start"', html)
        self.assertIn('data-booking-ready=', html)
        self.assertIn('{% if not booking_enabled %}', html)
        self.assertIn('class="ed-meet-fields" {% if not booking_enabled %}disabled{% endif %}', html)
        self.assertIn('data-meeting-stage="details"', html)
        self.assertIn('data-meeting-stage="contact"', html)
        self.assertNotIn('ed-meeting-progress', html)
        self.assertNotIn('ed-meeting-next', html)

    def test_training_and_insights_support_long_translations(self):
        self.assertIn(".ed-card-bottom{display:flex;flex-wrap:wrap", PORTAL)
        self.assertIn(".ed-page-hero h1{", PORTAL)
        self.assertIn("line-height:1.25;", PORTAL)
        self.assertIn("@media(max-width:960px){.ed-page-hero-inner{grid-template-columns:minmax(0,1fr)", PORTAL)
        self.assertIn(".ed-learning-lanes{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))", PORTAL)

    def test_styles_are_site_only_and_do_not_override_desk(self):
        hook = (APP / "hooks.py").read_text(encoding="utf-8")
        for css in (BRAND, PORTAL, MEETING):
            self.assertNotIn("!important;transform:scaleX(-1);transform:scaleX(-1)", css)
            self.assertNotIn("body[data-path=\"app\"]", css)
        self.assertNotIn('web_include_css = ["css/brand.css"]', hook)


if __name__ == "__main__":
    import unittest
    unittest.main()
