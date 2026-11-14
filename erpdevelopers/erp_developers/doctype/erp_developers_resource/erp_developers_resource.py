"""Moderated knowledge pointers to native Frappe Web Pages or external sites."""
import frappe
from frappe import _
from frappe.model.document import Document

from erpdevelopers.catalog_rules import external_https_url


class ERPDevelopersResource(Document):
    def validate(self):
        if self.source_kind == "External Source":
            try:
                self.external_url = external_https_url(self.external_url)
            except ValueError:
                frappe.throw(_("External sources must use a valid HTTPS domain."))
            if not (self.source_name or "").strip():
                frappe.throw(_("Credit the original source."))
            self.web_page = None
        elif self.source_kind == "Original Article":
            if not self.web_page:
                frappe.throw(_("Select a Frappe Web Page."))
            self.external_url = None
            self.source_name = None
            if self.published and not frappe.db.get_value("Web Page", self.web_page, "published"):
                frappe.throw(_("Publish the linked Web Page before publishing the resource."))
        else:
            frappe.throw(_("Select a supported content type."))

        if self.published and (
            not (self.summary or "").strip()
            or not (self.editorial_note or "").strip()
        ):
            frappe.throw(_("Published resources need a summary and editorial advice."))
