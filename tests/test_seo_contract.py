"""Public SEO and crawl-safety contracts. Runs without a Frappe runtime."""

import json
import unittest
from pathlib import Path

from erpdevelopers.branding import LOGO_URL, EXPECTED_SITE
from erpdevelopers.seo import (
    CANONICAL_HOME_URL,
    ROBOTS_TXT,
    SEO_DESCRIPTION,
    SEO_DESCRIPTION_AR,
    SEO_TITLE,
    SEO_TITLE_AR,
    SOCIAL_IMAGE_URL,
    homepage_seo_context,
)


ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "erpdevelopers/www/erp-developers-home.html"
CONTROLLER = ROOT / "erpdevelopers/www/erp_developers_home.py"


class TestHomepageSEO(unittest.TestCase):
    def test_canonical_and_search_snippet(self):
        meta = homepage_seo_context()
        self.assertEqual(meta["title"], SEO_TITLE)
        self.assertEqual(meta["description"], SEO_DESCRIPTION)
        self.assertEqual(meta["canonical_home_url"], f"https://{EXPECTED_SITE}/")
        self.assertLessEqual(len(SEO_TITLE), 65)
        self.assertTrue(120 <= len(SEO_DESCRIPTION) <= 165)
        self.assertEqual(SOCIAL_IMAGE_URL, f"https://{EXPECTED_SITE}{LOGO_URL}")
        self.assertEqual(meta["image"], SOCIAL_IMAGE_URL)

    def test_bilingual_homepage_metadata_and_language_alternates(self):
        english = homepage_seo_context("en")
        arabic = homepage_seo_context("ar")
        self.assertEqual(english["title"], SEO_TITLE)
        self.assertEqual(arabic["title"], SEO_TITLE_AR)
        self.assertEqual(arabic["description"], SEO_DESCRIPTION_AR)
        self.assertEqual(english["canonical_home_url"], CANONICAL_HOME_URL)
        self.assertEqual(arabic["canonical_home_url"], CANONICAL_HOME_URL + "?_lang=ar")
        self.assertEqual(arabic["metatags"]["og:url"], arabic["canonical_home_url"])
        self.assertEqual(
            english["language_alternates"], arabic["language_alternates"]
        )
        self.assertEqual(
            {v["lang"] for v in english["language_alternates"]}, {"en", "ar"}
        )
        html = HOME.read_text(encoding="utf-8")
        self.assertIn('hreflang="{{ alternate.lang | e }}"', html)
        self.assertEqual(html.count('rel="canonical"'), 1)
        self.assertIn("ERP Developers: ERP consulting,", html)
        self.assertIn("software and technology solutions.", html)

    def test_organization_schema_has_expertise_without_fabricated_credentials(self):
        nodes = json.loads(homepage_seo_context()["structured_data_json"])["@graph"]
        organization = nodes[0]
        self.assertEqual(organization["name"], "ERP Developers")
        self.assertIn("ERPNext", organization["knowsAbout"])
        self.assertIn("System integration", organization["knowsAbout"])
        self.assertNotIn("sameAs", organization)
        self.assertNotIn("aggregateRating", organization)

    def test_social_metadata_use_native_frappe_metatags(self):
        meta = homepage_seo_context()
        self.assertEqual(meta["metatags"]["og:type"], "website")
        self.assertEqual(meta["metatags"]["og:url"], CANONICAL_HOME_URL)
        self.assertEqual(meta["metatags"]["twitter:card"], "summary_large_image")
        html = HOME.read_text(encoding="utf-8")
        self.assertIn('rel="canonical"', html)
        self.assertIn("{{ canonical_home_url | e }}", html)
        self.assertNotIn('name="description"', html, "Frappe already renders description")
        self.assertNotIn('property="og:title"', html, "Frappe already renders OG meta")
        self.assertIn("{{ structured_data_json | safe }}", html)
        controller = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn("homepage_seo_context()", controller)

    def test_structured_data_is_valid_and_does_not_claim_future_products(self):
        schema = json.loads(homepage_seo_context()["structured_data_json"])
        self.assertEqual(schema["@context"], "https://schema.org")
        nodes = schema["@graph"]
        self.assertEqual({x["@type"] for x in nodes}, {"Organization", "WebSite"})
        self.assertEqual(nodes[1]["url"], CANONICAL_HOME_URL)
        self.assertEqual(nodes[1]["inLanguage"], ["en", "ar"])
        self.assertNotIn("JobPosting", json.dumps(schema))
        self.assertNotIn("Course", json.dumps(schema))
        self.assertNotIn("SoftwareApplication", json.dumps(schema))

    def test_robots_txt_is_public_and_respects_private_paths(self):
        self.assertIn("User-agent: *", ROBOTS_TXT)
        self.assertIn("Allow: /", ROBOTS_TXT)
        for path in ("/api/", "/app", "/desk", "/login", "/me"):
            self.assertIn(f"Disallow: {path}", ROBOTS_TXT)
        self.assertIn(f"Sitemap: {CANONICAL_HOME_URL}sitemap.xml", ROBOTS_TXT)

    def test_no_public_login_or_desk_schema(self):
        html = HOME.read_text(encoding="utf-8")
        self.assertNotIn('href="/app"', html)
        self.assertNotIn('type="application/ld+json"', (ROOT / "erpdevelopers/public/css/login.css").read_text())


if __name__ == "__main__":
    unittest.main()
