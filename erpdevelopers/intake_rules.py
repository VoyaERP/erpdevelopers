"""Pure public-booking validation. A request is NOT a confirmed meeting slot."""
from datetime import date, timedelta
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

TOPICS = (
    "ERP & Digital Transformation",
    "Solution Architecture",
    "Training & Mentorship",
    "Development & Integrations",
    "Partnerships",
    "Other",
)
WINDOWS = ("Flexible", "Morning", "Afternoon")


def clean_text(value, *, limit, required=True):
    if not isinstance(value, str):
        raise ValueError("Invalid text")
    value = value.strip()
    if (len(value) > limit or any(ord(c) < 32 and c not in "\n\t" for c in value)
        or (required and not value)):
        raise ValueError("Invalid text")
    return value


def validate_date(value, *, today: date):
    try:
        day = date.fromisoformat(value)
    except (ValueError, TypeError):
        raise ValueError("Use an ISO date") from None
    if not today <= day <= today + timedelta(days=90):
        raise ValueError("Date must be within the next 90 days")
    return day.isoformat()


def validate_timezone(value):
    value = clean_text(value, limit=64)
    if not re.fullmatch(r"[A-Za-z0-9_+/-]{1,64}", value):
        raise ValueError("Invalid time zone")
    try:
        ZoneInfo(value)
    except (ValueError, ZoneInfoNotFoundError):
        raise ValueError("Use a valid IANA time zone") from None
    return value
