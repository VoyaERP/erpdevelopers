"""Private consultation requests; confirmation requires a real calendar Event."""
import frappe
from frappe import _
from frappe.model.document import Document


class ERPDevelopersConsultation(Document):
    def validate(self):
        if self.status == "Confirmed":
            if not self.event or not frappe.db.exists("Event", self.event):
                frappe.throw(_("Link a Calendar Event before confirming this meeting."))
