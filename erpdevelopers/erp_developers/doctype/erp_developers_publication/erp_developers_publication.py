import frappe
from frappe import _
from frappe.model.document import Document
from erpdevelopers.publications import normalize_publication, validate_publication_cover


class ERPDevelopersPublication(Document):
    def validate(self):
        try:
            for field, value in normalize_publication(self.as_dict()).items():
                self.set(field, value)
            validate_publication_cover(self)
        except ValueError as exc:
            frappe.throw(_(str(exc)))
