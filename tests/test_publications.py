"""Publication boundaries: explicit review, safe projection, no private ERP reads."""
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

from erpdevelopers import publications as p

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


def record(**changes):
    value = {"name": "demo1", "publication_type": "Project", "title": "Reviewed project",
             "title_ar": "", "summary": "Public summary", "summary_ar": "",
             "content": "Public story\n\nSecond paragraph", "content_ar": "",
             "topic": p.TOPICS[0], "published": 1, "public_reviewed": 1,
             "internal_notes": "NEVER PUBLIC", "industry": "Manufacturing",
             "technologies": "ERPNext", "author_name": "", "cover_image": ""}
    value.update(changes)
    return value


class TestPublicationRules(TestCase):
    def test_publication_requires_content_and_explicit_review(self):
        for updates in ({"public_reviewed": 0}, {"content": ""}, {"title": " "}, {"summary": ""}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                p.normalize_publication(record(**updates))
        self.assertTrue(p.normalize_publication(record()))
        self.assertTrue(p.normalize_publication(record(published=0, public_reviewed=0)))

    def test_advice_requires_public_byline_not_private_user_lookup(self):
        with self.assertRaisesRegex(ValueError, "author"):
            p.normalize_publication(record(publication_type="Team Advice"))
        result = p.normalize_publication(record(publication_type="Team Advice", author_name="Editorial team"))
        self.assertEqual(result["author_name"], "Editorial team")

    def test_type_topic_and_text_boundaries(self):
        for updates in ({"publication_type": "User"}, {"topic": "Unknown"}, {"title": "x" * 201},
                        {"summary": "x" * 601}, {"content": "x" * 12001}, {"title": "x\nother"},
                        {"content": "x\x00"}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                p.normalize_publication(record(**updates))
        self.assertEqual(len(p.normalize_publication(record(content="x" * 12000))["content"]), 12000)

    def test_normalization_does_not_publish_or_change_privacy(self):
        data = record(published=0, public_reviewed=0, cover_image="/private/files/secret.png")
        result = p.normalize_publication(data)
        self.assertNotIn("published", result)
        self.assertNotIn("public_reviewed", result)
        self.assertNotIn("cover_image", result)
        self.assertEqual(data["published"], 0)

    def test_cover_reuses_file_validation_and_never_converts_private_files(self):
        fake = ModuleType("frappe")
        fake.get_doc = Mock()
        with patch.dict(sys.modules, {"frappe": fake}), self.assertRaises(ValueError):
            p.validate_publication_cover(record(cover_image="/private/files/secret.png"))
        fake.get_doc.assert_not_called()
        with patch.dict(sys.modules, {"frappe": fake}), patch.object(p, "_public_files", return_value={}), self.assertRaises(ValueError):
            p.validate_publication_cover(record(cover_image="/files/missing.png"))
        file_doc = object()
        fake.get_doc.return_value = file_doc
        with patch.dict(sys.modules, {"frappe": fake}), patch.object(p, "_public_files", return_value={"/files/photo.png": {"name": "FILE-1"}}), patch.object(p, "_verify_file") as verify:
            p.validate_publication_cover(record(cover_image="/files/photo.png"))
        verify.assert_called_once_with(file_doc)


class TestPublicPublicationProjection(TestCase):
    def run_query(self, rows, slug="projects", args=None, lang="en", schema=None):
        fake = ModuleType("frappe")
        fake.get_all = Mock(return_value=rows)
        with patch.dict(sys.modules, {"frappe": fake}), patch.object(p, "_schema_status", return_value=schema or {"table_present": True, "missing_columns": []}), patch.object(p, "_public_files", return_value={}):
            result = p.public_publications(slug, args, lang)
        return result, fake.get_all

    def test_each_directory_has_mandatory_review_and_publish_filters(self):
        for slug, kind in p.KINDS.items():
            result, query = self.run_query([record(publication_type=kind)], slug, {"published": 0, "doctype": "Project"})
            self.assertEqual(query.call_args.args, (p.DOCTYPE,))
            self.assertEqual(query.call_args.kwargs["filters"], {"published": 1, "public_reviewed": 1, "publication_type": kind})
            self.assertNotIn("internal_notes", query.call_args.kwargs["fields"])
            self.assertNotIn("internal_notes", result["items"][0])
            self.assertNotIn("NEVER PUBLIC", str(result))

    def test_schema_absent_never_queries_an_unmigrated_table(self):
        result, query = self.run_query([], schema={"table_present": False, "missing_columns": ["title"]})
        self.assertEqual(result["items"], [])
        query.assert_not_called()

    def test_pagination_and_topic_are_bounded(self):
        rows = [record(name=f"story{i}") for i in range(13)]
        result, query = self.run_query(rows, args={"page": "2", "topic": p.TOPICS[2]})
        self.assertEqual(len(result["items"]), 12)
        self.assertTrue(result["has_next"])
        self.assertEqual(query.call_args.kwargs["limit_start"], 12)
        self.assertEqual(query.call_args.kwargs["limit_page_length"], 13)
        self.assertEqual(query.call_args.kwargs["filters"]["topic"], p.TOPICS[2])
        result, query = self.run_query([], args={"page": "bad", "topic": "<script>"})
        self.assertEqual(result["page"], 1)
        self.assertNotIn("topic", query.call_args.kwargs["filters"])
        self.assertEqual(p._page_number("999999999"), 1000)
        self.assertEqual(p._page_number(-5), 1)

    def test_complete_arabic_translation_or_whole_entry_fallback(self):
        result, _ = self.run_query([record(title_ar="عنوان", summary_ar="ملخص", content_ar="محتوى")], lang="ar")
        self.assertEqual(result["items"][0]["lang"], "ar")
        self.assertEqual(result["items"][0]["title"], "عنوان")
        result, _ = self.run_query([record(title_ar="عنوان")], lang="ar")
        self.assertEqual(result["items"][0]["lang"], "en")
        self.assertEqual(result["items"][0]["title"], "Reviewed project")

    def test_unsafe_and_now_private_covers_are_omitted(self):
        rows = [record(name="one", cover_image="https://evil.example/a.png"), record(name="two", cover_image="/private/files/a.png"), record(name="three", cover_image="/files/a.png")]
        result, _ = self.run_query(rows)
        self.assertTrue(all(item["cover"] is None for item in result["items"]))

    def test_unknown_directory_is_rejected(self):
        fake = ModuleType("frappe")
        with patch.dict(sys.modules, {"frappe": fake}), self.assertRaises(ValueError):
            p.public_publications("users")


class TestPublicationSchemaAndChrome(TestCase):
    def test_one_editor_scoped_roles_and_native_save_actions(self):
        folder = APP / "erp_developers/doctype/erp_developers_publication"
        schema = json.loads((folder / "erp_developers_publication.json").read_text())
        fields = {field["fieldname"]: field for field in schema["fields"]}
        self.assertEqual(fields["publication_type"]["options"], "Project\nTeam Advice")
        self.assertEqual(fields["published"]["default"], "0")
        self.assertEqual(fields["public_reviewed"]["default"], "0")
        self.assertEqual({row["role"] for row in schema["permissions"]}, {"Website Manager", "System Manager"})
        self.assertGreaterEqual(sum(f["fieldtype"] == "Column Break" for f in fields.values()), 4)
        js = (folder / "erp_developers_publication.js").read_text()
        self.assertIn("frm.save()", js)
        self.assertNotIn("frappe.call", js)
        self.assertEqual(fields["content"]["fieldtype"], "Long Text")

    def test_footer_has_only_requested_navigation_links_and_local_top(self):
        source = (APP / "templates/includes/erpdevelopers_footer.html").read_text()
        links = source.split('class="ed-footer-links"', 1)[1]
        self.assertEqual(links.count("<a "), 3)
        for required in ('href="/lets-talk#meeting-start"', 'href="{{ desk_signin_url | e }}"', 'href="#top"'):
            self.assertIn(required, links)
        for unwanted in ("/training", "/events", "/insights", "/projects", "/team-advice"):
            self.assertNotIn(unwanted, links)

    def test_publication_routes_share_template_and_have_header_links(self):
        nav = (APP / "templates/includes/erpdevelopers_nav.html").read_text()
        for route in p.KINDS:
            self.assertIn(f'href="/{route}"', nav)
            self.assertIn("erpdevelopers_publications.html", (APP / f"www/{route}.html").read_text())
            controller = (APP / f"www/{route.replace('-', '_')}.py").read_text()
            self.assertIn("set_publication_context", controller)
            self.assertIn("sitemap = 1", controller)
        template = (APP / "templates/includes/erpdevelopers_publications.html").read_text()
        self.assertNotIn("directory.items", template)
        self.assertNotIn("| safe", template)
        self.assertIn("item.content | e", template)
        self.assertIn("<details", template)
        self.assertIn('method="get"', template)
        self.assertNotIn("<script", template)
