"""Lightweight public status gate; GET pages never import the booking POST handler."""
from erpdevelopers.branding import EXPECTED_SITE


def booking_state():
    import frappe
    from frappe.utils import cint

    if frappe.local.site != EXPECTED_SITE or not cint(frappe.conf.get("erpdev_meeting_booking_enabled", 0)):
        return {"enabled": False}

    required = ("Appointment", "Appointment Booking Settings", "Event", "Lead")
    if not all(frappe.db.exists("DocType", name) for name in required):
        return {"enabled": False}
    settings = frappe.get_single("Appointment Booking Settings")
    if not all((
        cint(settings.enable_scheduling),
        cint(settings.enable_appointment_portal),
        settings.holiday_list,
        settings.availability_of_slots,
        cint(settings.number_of_agents) > 0,
        settings.agent_list,
    )):
        return {"enabled": False}
    # The native portal creates Unverified records and emails a verification
    # link. Do not offer bookings if the confirmation email cannot be sent.
    if not frappe.db.exists("Email Account", {"enable_outgoing": 1, "default_outgoing": 1}):
        return {"enabled": False}

    return {
        "enabled": True,
        "advance_booking_days": min(max(cint(settings.advance_booking_days) or 7, 1), 90),
        "appointment_duration": cint(settings.appointment_duration),
        "email_confirmation_required": True,
    }


def booking_ready():
    return booking_state()["enabled"]


def diagnose_meeting_booking():
    """Read-only, operator-only Bench diagnostic. No guest whitelist."""
    import frappe

    if frappe.session.user != "Administrator" and "System Manager" not in frappe.get_roles():
        frappe.throw("System Manager role required", frappe.PermissionError)
    result = {"site": frappe.local.site, "ready": booking_ready()}
    result["feature_enabled"] = bool(frappe.conf.get("erpdev_meeting_booking_enabled", 0))
    result["native_appointment_available"] = bool(frappe.db.exists("DocType", "Appointment"))
    if frappe.db.exists("DocType", "Appointment Booking Settings"):
        s = frappe.get_single("Appointment Booking Settings")
        result.update({
            "scheduling_enabled": bool(s.enable_scheduling),
            "portal_enabled": bool(s.enable_appointment_portal),
            "holiday_list_configured": bool(s.holiday_list),
            "availability_configured": bool(s.availability_of_slots),
            "agent_count": len(s.agent_list or []),
            "duration_minutes": s.appointment_duration,
        })
    result["outgoing_email_available"] = bool(
        frappe.db.exists("Email Account", {"enable_outgoing": 1, "default_outgoing": 1})
    )
    return result
