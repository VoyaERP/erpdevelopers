"""Bilingual responsive contracts; browser tests also measure real layout."""
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
        self.assertIn("grid-row:2;grid-column:1/-1", BRAND)
        self.assertIn(".ed-nav-tools{grid-row:1;grid-column:2", BRAND)
        self.assertIn("flex-wrap:nowrap", BRAND)
        self.assertNotIn(".ed-nav-tools{display:contents}", BRAND)
        self.assertNotIn(".ed-nav-cta{grid-column:2;grid-row:2", BRAND)

    def test_decorative_labels_never_force_text_overlap(self):
        self.assertNotIn("min-width:max-content", BRAND)
        self.assertIn(".ed-art-float-a,.ed-art-float-b,.ed-art-float-c{position:static", BRAND)
        self.assertIn(".ed-link-grid{display:grid;grid-template-columns:minmax(0,1.14fr)", BRAND)
        self.assertIn(".ed-section-head>p{flex:0 1 385px;min-width:0", BRAND)
        self.assertIn("max-width:43%", BRAND)
        self.assertIn("overflow-x:clip;overflow-y:visible", BRAND)

    def test_header_is_sticky_and_in_page_links_clear_it(self):
        self.assertIn(".ed-nav{position:sticky;top:0;z-index:110", BRAND)
        self.assertIn(".ed-skip{position:fixed;top:-100px;inset-inline-start:12px;z-index:300", BRAND)
        self.assertIn("--ed-header-anchor-offset:95px", BRAND)
        self.assertIn("scroll-margin-top:var(--ed-header-anchor-offset)", BRAND)
        self.assertIn("--ed-header-anchor-offset:145px", BRAND)
        nav = (APP / "templates/includes/erpdevelopers_nav.html").read_text()
        self.assertIn('<header class="ed-nav" lang="{{ boot.lang | e }}"', nav)
        self.assertIn('href="/lets-talk#meeting-start"', nav)
        self.assertIn('dir="{{', nav)

    def test_guide_does_not_cover_footer_and_remains_keyboard_accessible(self):
        assistant = (APP / "templates/includes/erpdevelopers_assistant.html").read_text()
        guide_js = (APP / "public/js/assistant.js").read_text()
        self.assertIn("bottom:calc(19px + var(--ed-guide-footer-visible,0px))", PORTAL)
        self.assertIn("bottom:calc(10px + var(--ed-guide-footer-visible,0px))", PORTAL)
        self.assertIn("--ed-guide-footer-visible", guide_js)
        self.assertIn('footer.getBoundingClientRect()', guide_js)
        self.assertIn('window.addEventListener("scroll", scheduleFooterSync, { passive: true })', guide_js)
        self.assertIn('window.addEventListener("resize", scheduleFooterSync, { passive: true })', guide_js)
        self.assertIn('new ResizeObserver(scheduleFooterSync).observe(footer)', guide_js)
        self.assertIn('aria-expanded="false"', assistant)
        self.assertIn('Escape', guide_js)
        self.assertNotIn("A team member confirms the slot", assistant)
        self.assertIn("verify the appointment through the email link", assistant)
        self.assertNotIn("frappe.call", guide_js)
        self.assertNotIn("fetch(", guide_js)

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
        for marker in ("ed-meeting-form", "ed-meeting-consent", "ed-meeting-month", "ed-meeting-slots", "ed-meet-aside-selection", "meeting-start"):
            self.assertIn(f'id="{marker}"', html)
        self.assertEqual(html.count('<form id="ed-meeting-form"'), 1)
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
            self.assertNotIn('body[data-path="app"]', css)
        self.assertNotIn('web_include_css = ["css/brand.css"]', hook)


if __name__ == "__main__":
    import unittest
    unittest.main()
