"""Curator-managed public events, separate from private calendar records."""
import frappe
from frappe import _
from frappe.model.document import Document

from erpdevelopers.catalog_rules import EventLinkError
from erpdevelopers.event_rules import normalize_event
from erpdevelopers.event_media import validate_event_media


class ERPDevelopersEvent(Document):
    def validate(self):
        try:
            values = normalize_event(self.as_dict())
            validate_event_media(self)
        except EventLinkError as exc:
            labels = {"event_url": _("Official event URL"), "source_url": _("Source URL")}
            frappe.throw(_("{0}: {1}").format(labels[exc.fieldname], _(str(exc))))
        except ValueError as exc:
            frappe.throw(_(str(exc)))
        for field, value in values.items():
            self.set(field, value)
