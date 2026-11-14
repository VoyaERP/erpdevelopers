"""Event photo permission, upload, gallery and public projection regression tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import json
import sys

from erpdevelopers import event_media as media

ROOT = Path(__file__).resolve().parents[1]


class Row(dict):
    def set(self, key, value):
        self[key] = value


class TestEventImagePaths(TestCase):
    def test_native_public_upload_paths(self):
        self.assertEqual(media.image_path("/files/event%20poster.png"), "/files/event poster.png")
        self.assertEqual(media.image_path("/files/\u0641\u0639\u0627\u0644\u064a\u0629.jpg"), "/files/\u0641\u0639\u0627\u0644\u064a\u0629.jpg")

    def test_private_remote_active_content_and_traversal_rejected(self):
        for value in ("/private/files/x.png", "https://example.com/x.jpg", "//host/x.png", "data:image/png,AA",
            "/files/../secret.png", "/files/%2e%2e%2fsecret.png", "/files/%252e%252e%252fsecret.png",
            "/files/x.svg", "/files/x.html", "/files/x.png?token=secret", "/files/x.png#hash",
            "/files/a\"onerror=x.png", "/files/\\private.png", "/files/x\n.png", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                media.image_path(value)

    def test_native_schema_and_explicit_public_upload_warning(self):
        root = ROOT / "erpdevelopers/erp_developers/doctype"
        event = json.loads((root / "erp_developers_event/erp_developers_event.json").read_text())
        child = json.loads((root / "erp_developers_event_image/erp_developers_event_image.json").read_text())
        for schema in (event, child):
            self.assertEqual(schema["field_order"], [f["fieldname"] for f in schema["fields"]])
            self.assertNotIn("Guest", [p["role"] for p in schema["permissions"]])
        fields = {f["fieldname"]: f for f in event["fields"]}
        self.assertEqual(fields["cover_image"]["fieldtype"], "Attach Image")
        self.assertEqual(fields["cover_image"]["make_attachment_public"], 1)
        self.assertIn("draft", fields["cover_image"]["description"])
        self.assertEqual(fields["event_images"]["options"], media.IMAGE_DOCTYPE)
        self.assertEqual(child["istable"], 1)
        self.assertTrue(fields["has_event_images"]["read_only"])


class TestEventMediaSave(TestCase):
    def test_gallery_size_duplicates_and_empty_rows_fail(self):
        for rows in ([Row(image="/files/a.png") for _ in range(9)],
                     [Row(image="/files/a.png"), Row(image="/files/a.png")], [Row(image="")]):
            fake = ModuleType("frappe")
            with patch.dict(sys.modules, {"frappe": fake}), self.assertRaises(ValueError):
                media.validate_event_media(Row(event_images=rows))

    def test_missing_or_private_file_is_not_made_public(self):
        with patch.dict(sys.modules, {"frappe": ModuleType("frappe")}), patch.object(media, "_public_files", return_value={}):
            with self.assertRaisesRegex(ValueError, "private or missing"):
                media.validate_event_media(Row(cover_image="/files/no-longer-public.jpg"))

    def test_save_uses_existing_file_permissions_and_sets_gallery_flag(self):
        fake = ModuleType("frappe")
        file = object()
        fake.get_doc = lambda doctype, name: file
        doc = Row(cover_image="/files/cover.png", cover_caption=" Poster ",
                  event_images=[Row(image="/files/detail.png", caption=" Room ")])
        records = {"/files/cover.png": {"name": "C"}, "/files/detail.png": {"name": "D"}}
        with patch.dict(sys.modules, {"frappe": fake}), patch.object(media, "_public_files", return_value=records), patch.object(media, "_verify_file") as verify:
            media.validate_event_media(doc)
        self.assertEqual(verify.call_count, 2)
        self.assertEqual(doc["has_event_images"], 1)
        self.assertEqual(doc["cover_caption"], "Poster")
        self.assertEqual(doc["event_images"][0]["caption"], "Room")

    def test_real_local_image_bytes_and_read_permission(self):
        from PIL import Image
        with TemporaryDirectory() as folder:
            base = Path(folder) / "public/files"
            base.mkdir(parents=True)
            path = base / "poster.png"
            Image.new("RGB", (32, 24)).save(path)
            permissions = []
            doc = SimpleNamespace(is_private=0, is_folder=0, file_url="/files/poster.png",
                get_full_path=lambda: str(path), check_permission=lambda p: permissions.append(p))
            fake = ModuleType("frappe")
            fake.get_site_path = lambda *parts: str(Path(folder).joinpath(*parts))
            with patch.dict(sys.modules, {"frappe": fake}):
                media._verify_file(doc)
                self.assertEqual(permissions, ["read"])
                doc.is_private = 1
                with self.assertRaises(ValueError): media._verify_file(doc)
                doc.is_private = 0
                path.write_text("<script>not an image</script>")
                with self.assertRaises(ValueError): media._verify_file(doc)
                path.write_bytes(b"x" * (media.MAX_BYTES + 1))
                with self.assertRaisesRegex(ValueError, "5 MB"): media._verify_file(doc)
                doc.get_full_path = lambda: str(Path(folder) / "outside.png")
                with self.assertRaises(ValueError): media._verify_file(doc)


class TestPublicEventMedia(TestCase):
    def fake(self, files=None, gallery=None):
        fake = ModuleType("frappe")
        fake.calls = []
        fake.db = SimpleNamespace(table_exists=lambda name: True)
        def query(doctype, **kwargs):
            fake.calls.append((doctype, kwargs))
            return (files or []) if doctype == "File" else (gallery or [])
        fake.get_all = query
        return fake

    def test_no_photos_means_no_extra_database_queries(self):
        fake = self.fake()
        entry = {"name": "E"}
        with patch.dict(sys.modules, {"frappe": fake}): media.attach_public_event_media([entry])
        self.assertEqual(fake.calls, [])
        self.assertEqual(entry["media"], {"cover": None, "gallery": []})

    def test_batched_parent_scoped_gallery_and_current_public_files(self):
        files = [{"name": "F1", "file_url": "/files/cover.png", "file_size": 50},
                 {"name": "F2", "file_url": "/files/room.png", "file_size": 60}]
        gallery = [{"parent": "E", "image": "/files/room.png", "caption": "Room"},
                   {"parent": "E", "image": "/private/files/secret.png"},
                   {"parent": "HIDDEN", "image": "/files/cover.png"}]
        fake = self.fake(files, gallery)
        entry = {"name": "E", "cover_image": "/files/cover.png", "has_event_images": 1}
        with patch.dict(sys.modules, {"frappe": fake}): media.attach_public_event_media([entry])
        self.assertEqual(entry["media"]["cover"]["url"], "/files/cover.png")
        self.assertEqual([p["url"] for p in entry["media"]["gallery"]], ["/files/room.png"])
        self.assertEqual(len(fake.calls), 2)
        filters = fake.calls[0][1]["filters"]
        self.assertEqual(filters["parent"], ["in", ["E"]])
        self.assertEqual(filters["parenttype"], media.EVENT_DOCTYPE)
        self.assertEqual(filters["parentfield"], "event_images")
        self.assertEqual(fake.calls[1][1]["filters"]["is_private"], 0)

    def test_file_deleted_or_made_private_after_publication_is_omitted(self):
        fake = self.fake()
        entry = {"name": "E", "cover_image": "/files/old-public.png"}
        with patch.dict(sys.modules, {"frappe": fake}): media.attach_public_event_media([entry])
        self.assertIsNone(entry["media"]["cover"])

    def test_first_gallery_photo_falls_back_as_cover_and_duplicates_removed(self):
        fake = self.fake(files=[{"name": "F", "file_url": "/files/a b.png", "file_size": 50}],
            gallery=[{"parent": "E", "image": "/files/a%20b.png"}, {"parent": "E", "image": "/files/a b.png"}])
        entry = {"name": "E", "has_event_images": 1}
        with patch.dict(sys.modules, {"frappe": fake}): media.attach_public_event_media([entry])
        self.assertEqual(entry["media"]["cover"]["url"], "/files/a%20b.png")
        self.assertEqual(entry["media"]["gallery"], [])
