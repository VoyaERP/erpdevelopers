"""Pure validation shared by the native ERPNext meeting scheduler.

ERPNext remains the authority for appointment capacity, assigned agents,
holiday calendars, email verification and CRM/Event creation.
"""
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
import re

from erpdevelopers.intake_rules import TOPICS, clean_text, validate_timezone


def validate_booking_date(value, timezone, advance_days, *, now=None):
    """Compare in the visitor's IANA time zone, not the web worker time zone."""
    zone = validate_timezone(timezone)
    try:
        day = date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError("Use an ISO date") from None
    today = (now or datetime.now(ZoneInfo(zone))).astimezone(ZoneInfo(zone)).date()
    window = min(max(int(advance_days or 7), 1), 90)
    if not today <= day <= today + timedelta(days=window):
        raise ValueError("Meeting date is outside the booking window")
    return day.isoformat()


def validate_slot_time(value):
    if not isinstance(value, str) or not re.fullmatch(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]", value):
        raise ValueError("Invalid slot time")
    return value


def validate_meeting_contact(details):
    """Return safe, size-bounded fields; no caller-controlled record identifiers."""
    if not isinstance(details, dict):
        raise ValueError("Invalid meeting contact")
    if details.get("website"):
        raise ValueError("Invalid meeting request")
    if details.get("consent") not in (1, "1", True):
        raise ValueError("Contact permission required")
    data = {
        "name": clean_text(details.get("name"), limit=120),
        "email": clean_text(details.get("email"), limit=200),
        "phone": clean_text(details.get("phone") or "", limit=45, required=False),
        "company": clean_text(details.get("company") or "", limit=140, required=False),
        "topic": details.get("topic"),
        "message": clean_text(details.get("message") or "", limit=1500, required=False),
    }
    if data["topic"] not in TOPICS:
        raise ValueError("Unsupported meeting topic")
    # Avoid storing active HTML in native CRM display names or appointment notes.
    if any("<" in str(value) or ">" in str(value) for value in data.values()):
        raise ValueError("HTML markup is not accepted")
    return data


def available_slot_matches(slots, requested_date, requested_time):
    """Confirm a slot from *current* native ERPNext availability, not client state."""
    for slot in slots:
        when = slot.get("time")
        if hasattr(when, "strftime"):
            day, time = when.strftime("%Y-%m-%d"), when.strftime("%H:%M:%S")
        elif isinstance(when, str):
            match = re.search(r"^(\\d{4}-\\d{2}-\\d{2})[ T](\\d{2}:\\d{2}:\\d{2})", when)
            day, time = (match.group(1), match.group(2)) if match else ("", "")
        else:
            continue
        if day == requested_date and time == requested_time and bool(slot.get("availability")):
            return True
    return False
