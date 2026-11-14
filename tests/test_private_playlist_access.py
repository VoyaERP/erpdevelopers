"""Regression checks: private playlist IDs never reach Guest responses."""
import sys
import types
import unittest
from unittest.mock import patch

from erpdevelopers import catalog


PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLabc1234567890123"


class TestPrivatePlaylistAccess(unittest.TestCase):
    def test_guest_cannot_query_private_records(self):
        frappe = types.SimpleNamespace(
            session=types.SimpleNamespace(user="Guest"),
            get_list=lambda *a, **kw: self.fail("Guest queried private records"),
        )
        with patch.dict(sys.modules, {"frappe": frappe}):
            self.assertEqual(catalog.authorized_private_playlists(), [])

    def test_signed_in_reads_only_private_published_records_with_permissions(self):
        calls = []
        def get_list(doctype, **kwargs):
            calls.append((doctype, kwargs))
            return [{
                "name": "PRIVATE-001",
                "title": "Member training",
                "playlist_url": PLAYLIST_URL,
                "visibility": "Private",
            }]
        frappe = types.SimpleNamespace(
            session=types.SimpleNamespace(user="learner@example.com"),
            get_list=get_list,
        )
        with patch.dict(sys.modules, {"frappe": frappe}), patch.object(
            catalog, "_schema_status", return_value={"table_present": True, "missing_columns": []}
        ):
            result = catalog.authorized_private_playlists()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["playlist_id"], "PLabc1234567890123")
        self.assertEqual(calls[0][0], catalog.PLAYLIST_DOCTYPE)
        self.assertEqual(calls[0][1]["filters"], {"published": 1, "visibility": "Private"})

    def test_rejects_invalid_url_from_private_catalog(self):
        frappe = types.SimpleNamespace(
            session=types.SimpleNamespace(user="learner@example.com"),
            get_list=lambda *args, **kwargs: [
                {"playlist_url": "https://evil.example/playlist?list=PLabc1234567890123"}
            ],
        )
        with patch.dict(sys.modules, {"frappe": frappe}), patch.object(
            catalog, "_schema_status", return_value={"table_present": True, "missing_columns": []}
        ):
            self.assertEqual(catalog.authorized_private_playlists(), [])


if __name__ == "__main__":
    unittest.main()
