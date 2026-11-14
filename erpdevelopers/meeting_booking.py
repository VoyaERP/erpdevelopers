"""Greenbox-style meeting booking using *native ERPNext v16* Appointment.

Native ERPNext owns live slots, holiday/capacity validation, verification
emails, Lead/Customer linking, agent assignment and Frappe Calendar Events.
No separate meeting series, Lead, Event or third-party calendar is created.
"""
import json
from urllib.parse import urlsplit

import frappe
from frappe import _
from frappe.rate_limiter import rate_limit
from frappe.utils import validate_email_address

from erpdevelopers.meeting_rules import (
    available_slot_matches,
    validate_booking_date,
    validate_meeting_contact,
    validate_slot_time,
)
from erpdevelopers.meeting_status import booking_state
from erpdevelopers.branding import EXPECTED_SITE


def _enabled_state():
    state = booking_state()
    if not state["enabled"]:
        frappe.throw(_("Online meeting booking is currently unavailable."), frappe.PermissionError)
    return state


@frappe.whitelist(allow_guest=True, methods=["GET"])
@rate_limit(limit=60, seconds=3600)
def get_meeting_settings():
    """Only public-facing fields; never return staff, calendar or mail details."""
    return booking_state()


@frappe.whitelist(allow_guest=True, methods=["GET"])
@rate_limit(limit=120, seconds=3600)
def get_meeting_slots(date, timezone):
    state = _enabled_state()
    try:
        day = validate_booking_date(date, timezone, state["advance_booking_days"])
    except (ValueError, TypeError):
        frappe.throw(_("Choose a date in the available booking window."))
    from erpnext.www.book_appointment.index import get_appointment_slots
    slots = get_appointment_slots(day, timezone)
    # The browser sees dates, times, and available flags only.
    return [
        {"time": item["time"].isoformat() if hasattr(item["time"], "isoformat") else str(item["time"]),
         "availability": bool(item["availability"])}
        for item in slots
    ]


@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=300, methods="POST")
def book_meeting(date, time, timezone, contact):
    """Submit to ERPNext's email-verification portal; never confirm on POST."""
    state = _enabled_state()
    # Frappe provides CSRF enforcement; reject explicitly foreign origins as
    # an additional, site-specific safeguard against cross-origin booking.
    request = getattr(frappe.local, "request", None)
    origin = request.headers.get("Origin") if request is not None else None
    if origin:
        parsed = urlsplit(origin)
        if parsed.scheme != "https" or parsed.hostname != EXPECTED_SITE or parsed.port not in (None, 443):
            frappe.throw(_("Meeting requests must originate from this website."), frappe.PermissionError)
    try:
        day = validate_booking_date(date, timezone, state["advance_booking_days"])
        slot_time = validate_slot_time(time)
        payload = json.loads(contact) if isinstance(contact, str) else contact
        details = validate_meeting_contact(payload)
        validated_email = validate_email_address(details["email"], throw=True)
        # Frappe's mail validator also accepts comma-separated addresses;
        # native appointment confirmation must have exactly one recipient.
        if not validated_email or "," in validated_email or validated_email != details["email"]:
            raise ValueError("Use one individual email address")
        details["email"] = validated_email
    except (TypeError, ValueError):
        frappe.throw(_("Review the selected meeting slot and contact details."))

    from erpnext.www.book_appointment.index import create_appointment, get_appointment_slots

    current_slots = get_appointment_slots(day, timezone)
    if not available_slot_matches(current_slots, day, slot_time):
        frappe.throw(_("That meeting time is no longer available. Choose another slot."))

    note = "\n".join(filter(None, (
        "ERP Developers meeting request",
        "Contact consent: visitor requested this meeting",
        f"Topic: {details['topic']}",
        f"Company: {details['company']}" if details["company"] else "",
        f"Requirements: {details['message']}" if details["message"] else "",
    )))
    native_contact = {
        "name": details["name"],
        "email": details["email"],
        "number": details["phone"],
        "skype": "",
        "notes": note,
    }
    # ERPNext creates Unverified; verification then links Lead/Customer and
    # builds an Event. Never create a second CRM record or expose the doc ID.
    create_appointment(day, slot_time, timezone, frappe.as_json(native_contact))
    return {"accepted": True, "email_confirmation_required": True}
