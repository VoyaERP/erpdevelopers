"""Vision and editorial SEO contracts, isolated from Frappe and site data."""
import importlib
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

from erpdevelopers.branding import EXPECTED_SITE, versioned_public_asset
from erpdevelopers.guide_content import GUIDES, guide_links, set_guide_context

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


class TestEditorialGuides(TestCase):
    def test_each_guide_has_distinct_substantive_bilingual_content(self):
        self.assertEqual(set(GUIDES), {"erp-development", "erpnext-development"})
        for slug, page in GUIDES.items():
            for language in ("en", "ar"):
                with self.subTest(slug=slug, language=language):
                    content = page[language]
                    self.assertTrue(all(content[key] for key in ("title", "heading", "description", "lead")))
                    self.assertEqual(len(content["sections"]), 5)
                    self.assertGreater(sum(len(body.split()) for _, body in content["sections"]), 200)
                    self.assertTrue((APP / "www" / (slug + ".html")).is_file())
                    self.assertTrue((APP / "www" / (slug.replace("-", "_") + ".py")).is_file())
            self.assertNotEqual(page["en"]["heading"], page["ar"]["heading"])

    def test_metadata_and_language_alternates_match_visible_content(self):
        for slug in GUIDES:
            for lang in ("en", "ar"):
                ctx = SimpleNamespace()
                set_guide_context(ctx, slug, lang)
                expected = f"https://{EXPECTED_SITE}/{slug}?_lang={lang}"
                self.assertEqual(ctx.canonical_url, expected)
                self.assertEqual(ctx.metatags["og:url"], expected)
                self.assertIn(ctx.guide["title"], ctx.title)
                self.assertEqual(ctx.description, ctx.guide["description"])
                self.assertEqual({a["lang"] for a in ctx.language_alternates}, {"en", "ar"})
                self.assertIn(expected, [a["href"] for a in ctx.language_alternates])
                schema = json.loads(ctx.guide_schema_json)
                self.assertEqual(schema["@graph"][0]["name"], ctx.guide["heading"])
                self.assertEqual(schema["@graph"][0]["inLanguage"], lang)
                self.assertEqual({x["@type"] for x in schema["@graph"]}, {"WebPage", "BreadcrumbList"})
                self.assertNotIn("AggregateRating", ctx.guide_schema_json)
                self.assertNotIn("Product", ctx.guide_schema_json)
                self.assertEqual(ctx.no_cache, 1)

    def test_unknown_route_rejected_before_url_construction(self):
        with self.assertRaises(ValueError):
            set_guide_context(SimpleNamespace(), "https://evil.example/", "en")

    def test_fresh_content_and_json_script_escaping(self):
        first = SimpleNamespace()
        set_guide_context(first, "erp-development", "en")
        first.guide["sections"].clear()
        second = SimpleNamespace()
        set_guide_context(second, "erp-development", "en")
        self.assertEqual(len(second.guide["sections"]), 5)
        with patch.dict(GUIDES["erp-development"]["en"], {"heading": "</script><script>unsafe()</script>"}):
            set_guide_context(second, "erp-development", "en")
        self.assertNotIn("</script>", second.guide_schema_json)
        self.assertIn("\\u003c", second.guide_schema_json)

    def test_controllers_use_native_request_language_and_are_sitemap_enabled(self):
        fake = ModuleType("frappe")
        fake.local = SimpleNamespace(lang="ar")
        for slug in GUIDES:
            module = importlib.import_module("erpdevelopers.www." + slug.replace("-", "_"))
            ctx = SimpleNamespace()
            with patch.dict(sys.modules, {"frappe": fake}):
                module.get_context(ctx)
            self.assertEqual(ctx.guide_language, "ar")
            self.assertEqual(module.sitemap, 1)

    def test_guides_share_one_template_and_link_from_homepage(self):
        template = (APP / "templates/includes/erpdevelopers_guide.html").read_text()
        for slug in GUIDES:
            wrapper = (APP / "www" / (slug + ".html")).read_text()
            self.assertIn("erpdevelopers_guide.html", wrapper)
        self.assertIn('hreflang="{{ alternate.lang | e }}"', template)
        self.assertIn("{{ guide_schema_json | safe }}", template)
        self.assertIn("{{ heading | e }}", template)
        self.assertIn("{{ body | e }}", template)
        home = (APP / "www/erp-developers-home.html").read_text()
        self.assertIn("for item in guide_links", home)
        self.assertEqual({item["slug"] for item in guide_links()}, set(GUIDES))


class TestVisionSection(TestCase):
    def test_local_existing_image_not_remote_or_generated_duplicate(self):
        home = (APP / "www/erp-developers-home.html").read_text()
        self.assertEqual(home.count('id="vision"'), 1)
        self.assertIn('class="ed-vision-image"', home)
        self.assertIn('src="/assets/erpdevelopers/images/login-network.svg"', home)
        self.assertTrue((APP / "public/images/login-network.svg").is_file())
        self.assertIn('loading="lazy" decoding="async"', home)
        self.assertNotIn("requestFullscreen", home)
        self.assertIn('href="/#vision"', (APP / "templates/includes/erpdevelopers_nav.html").read_text())

    def test_full_height_does_not_fix_or_clip_text_height(self):
        css = (APP / "public/css/discovery.css").read_text()
        self.assertIn("min-height:calc(100svh", css)
        self.assertIn("--ed-header-anchor-offset", css)
        self.assertIn("@media(max-width:760px)", css)
        self.assertIn("html[lang^=\"ar\"]", css)
        self.assertNotIn("position:fixed", css)
        self.assertIn("object-fit:cover", css)
        self.assertIn("?v=", versioned_public_asset("css/discovery.css"))
