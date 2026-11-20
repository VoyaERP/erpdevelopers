"""Curator-managed YouTube playlists. Published catalog is read-only for guests."""
import frappe
from frappe import _
from frappe.model.document import Document

from erpdevelopers.catalog_rules import youtube_playlist_id


class ERPDevelopersPlaylist(Document):
    def validate(self):
        try:
            playlist = youtube_playlist_id(self.playlist_url)
        except ValueError:
            frappe.throw(_("Enter a valid HTTPS YouTube playlist URL."))
        # Visibility controls the audience; publication controls availability
        # within that audience. Guest queries always filter visibility=Public.
        if not self.visibility:
            self.visibility = "Public"  # legacy records before this field
        if self.visibility not in ("Public", "Private"):
            frappe.throw(_("Choose Public or Private playlist visibility."))
        self.playlist_id = playlist
        self.playlist_url = f"https://www.youtube.com/playlist?list={playlist}"
        if not (self.description or "").strip():
            frappe.throw(_("A description is required."))
