"""Site-specific, rate-limited public requests and permission-checked CRM handoff.

Guests cannot read consultation records. Creating a Lead is a separate action
by an authorized ERPNext Sales User after review; never by a guest.
"""
from datetime import date
import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import cint, strip_html, validate_email_address

from erpdevelopers.branding import EXPECTED_SITE
from erpdevelopers.intake_rules import TOPICS, WINDOWS, clean_text, validate_date, validate_timezone


def booking_open():
    return (frappe.local.site == EXPECTED_SITE
            and cint(frappe.conf.get("erpdev_consultation_open", 0)) == 1)


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=3600, methods="POST")
def request_consultation(
    contact_name: str, email: str, topic: str, preferred_date: str,
    preferred_window: str, time_zone: str, message: str,
    contact_consent: int = 0, company: str = "", website: str = "",
):
    if not booking_open():
        frappe.throw(_("Appointment requests are not enabled."), frappe.PermissionError)
    # Hidden bot field; do not create a record and do not leak other records.
    if website:
        return {"accepted": True}

    try:
        name = clean_text(strip_html(contact_name), limit=120)
        email = clean_text(email, limit=200)
        company = clean_text(strip_html(company or ""), limit=140, required=False)
        message = clean_text(strip_html(message), limit=1800)
        day = validate_date(preferred_date, today=date.today())
        zone = validate_timezone(time_zone)
        if topic not in TOPICS or preferred_window not in WINDOWS or not cint(contact_consent):
            raise ValueError("Invalid request fields or missing consent")
        email = validate_email_address(email, throw=True)
    except (ValueError, TypeError):
        frappe.throw(_("Review your details, preferred date and contact consent."))

    frappe.get_doc({
        "doctype": "ERP Developers Consultation",
        "contact_name": name, "email": email, "company": company,
        "topic": topic, "preferred_date": day, "preferred_window": preferred_window,
        "time_zone": zone, "message": message, "contact_consent": 1,
        "status": "Requested",
    }).insert(ignore_permissions=True)
    return {"accepted": True}


@frappe.whitelist(methods=["POST"])
def create_or_link_lead(consultation_name: str):
    """Staff-only CRM conversion with no duplicate Lead for the same email."""
    if frappe.local.site != EXPECTED_SITE:
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    consultation = frappe.get_doc("ERP Developers Consultation", consultation_name)
    consultation.check_permission("write")
    if not frappe.has_permission("Lead", ptype="create"):
        frappe.throw(_("Lead creation permission is required."), frappe.PermissionError)
    if consultation.lead:
        if not frappe.has_permission("Lead", ptype="read", doc=consultation.lead):
            frappe.throw(_("CRM Lead access is required."), frappe.PermissionError)
        return {"lead": consultation.lead, "existing": True}

    existing = frappe.db.get_value("Lead", {"email_id": consultation.email}, "name")
    if existing:
        if not frappe.has_permission("Lead", ptype="read", doc=existing):
            frappe.throw(_("An existing Lead requires CRM access."), frappe.PermissionError)
        lead_name = existing
    else:
        lead = frappe.get_doc({
            "doctype": "Lead", "lead_name": consultation.contact_name,
            "email_id": consultation.email,
            "company_name": consultation.company or "",
            "status": "Lead",
        })
        lead.insert()
        lead_name = lead.name
    consultation.lead = lead_name
    if consultation.status == "Requested":
        consultation.status = "Contacted"
    consultation.save()
    return {"lead": lead_name, "existing": bool(existing)}
