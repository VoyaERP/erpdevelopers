"""Curator-managed external events, separate from private Frappe calendar events."""
import frappe
from frappe import _
from frappe.model.document import Document

from erpdevelopers.event_rules import normalize_event


class ERPDevelopersEvent(Document):
    def validate(self):
        try:
            values = normalize_event(self.as_dict())
        except ValueError as exc:
            frappe.throw(_(str(exc)))
        for field, value in values.items():
            self.set(field, value)
