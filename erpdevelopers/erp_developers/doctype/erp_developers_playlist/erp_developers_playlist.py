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
        self.playlist_id = playlist
        self.playlist_url = f"https://www.youtube.com/playlist?list={playlist}"
        if not (self.description or "").strip():
            frappe.throw(_("A description is required."))
