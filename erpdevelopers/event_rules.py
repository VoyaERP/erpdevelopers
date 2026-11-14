"""Pure event rules. No provider calls, scheduler, credentials or DB access."""
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from erpdevelopers.catalog_rules import external_https_url

TOPICS = (
    "ERP & Business Applications", "Solution Architecture", "Developer Practices",
    "Cloud & DevOps", "AI & Data", "Cybersecurity", "Digital Transformation", "General Technology",
)
FORMATS = ("In person", "Online", "Hybrid")
EVENT_TYPES = ("Conference", "Exhibition", "Workshop", "Webinar", "Meetup")
STATUSES = ("Scheduled", "Postponed", "Cancelled")


def _text(value, maximum, required=False):
    value = str(value or "").strip()
    if len(value) > maximum or (required and not value):
        raise ValueError("Complete the required event details within the field limits.")
    return value


def _date(value):
    try:
        return date.fromisoformat(str(value))
    except (ValueError, TypeError):
        raise ValueError("Enter valid event dates.") from None


def _time(value):
    try:
        if isinstance(value, timedelta):
            seconds = int(value.total_seconds())
            if not 0 <= seconds < 86400:
                raise ValueError()
            return time(seconds // 3600, seconds % 3600 // 60, seconds % 60)
        parsed = time.fromisoformat(str(value))
        if parsed.tzinfo is not None:
            raise ValueError()
        return parsed.replace(microsecond=0)
    except (ValueError, TypeError):
        raise ValueError("Enter valid local start and end times.") from None


def _utc(local, zone):
    aware = local.replace(tzinfo=zone)
    if aware.astimezone(timezone.utc).astimezone(zone).replace(tzinfo=None) != local:
        raise ValueError("This local time does not exist because of a clock change.")
    if aware.utcoffset() != local.replace(tzinfo=zone, fold=1).utcoffset():
        raise ValueError("This local time is ambiguous because of a clock change.")
    return aware.astimezone(timezone.utc).replace(tzinfo=None)


def normalize_event(data):
    """Validate an editorial record and derive UTC query fields from local dates.

    Separate Date/Time fields avoid interpreting venue time as the user's or
    server's timezone. Date-only end dates are inclusive; UTC end is exclusive.
    """
    result = {
        "title": _text(data.get("title"), 140, True),
        "title_ar": _text(data.get("title_ar"), 140),
        "description": _text(data.get("description"), 1600, True),
        "description_ar": _text(data.get("description_ar"), 1600),
        "organizer": _text(data.get("organizer"), 140, True),
        "city": _text(data.get("city"), 140),
        "venue": _text(data.get("venue"), 240),
        "country": _text(data.get("country"), 140),
    }
    for field, choices in (("topic", TOPICS), ("event_type", EVENT_TYPES),
                           ("event_format", FORMATS), ("event_status", STATUSES)):
        value = data.get(field)
        if value not in choices:
            raise ValueError("Select a valid topic, type, format and event status.")
        result[field] = value
    if result["event_format"] != "Online" and not all(result[f] for f in ("country", "city", "venue")):
        raise ValueError("Country, city and venue are required for in-person and hybrid events.")
    key = _text(data.get("time_zone"), 80, True)
    try:
        zone = ZoneInfo(key)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("Enter a valid IANA time zone, such as Asia/Riyadh or Africa/Cairo.") from None
    start, end = _date(data.get("start_date")), _date(data.get("end_date"))
    if end < start:
        raise ValueError("The event end must be after its start.")
    date_only = str(data.get("date_only", 1)) in ("1", "True", "true")
    if date_only:
        beginning = datetime.combine(start, time.min)
        finish = datetime.combine(end + timedelta(days=1), time.min)
        result.update(start_time=None, end_time=None)
    else:
        start_time, end_time = _time(data.get("start_time")), _time(data.get("end_time"))
        beginning, finish = datetime.combine(start, start_time), datetime.combine(end, end_time)
        result.update(start_time=start_time.isoformat(), end_time=end_time.isoformat())
    beginning, finish = _utc(beginning, zone), _utc(finish, zone)
    if finish <= beginning:
        raise ValueError("The event end must be after its start.")
    result.update(time_zone=key, start_date=start.isoformat(), end_date=end.isoformat(),
                  date_only=int(date_only), start_utc=beginning, end_utc=finish)
    result["event_url"] = external_https_url(data.get("event_url"))
    source_url = _text(data.get("source_url"), 1500)
    result["source_url"] = external_https_url(source_url) if source_url else None
    provider = _text(data.get("source_provider") or "Manual", 80, True)
    external_id = _text(data.get("source_event_id"), 200)
    result.update(source_provider=provider, source_event_id=external_id or None)
    result["source_key"] = sha256(f"{provider.casefold()}\0{external_id}".encode()).hexdigest() if external_id else None
    checked = data.get("verified_on")
    if checked:
        if _date(checked) > datetime.now(zone).date():
            raise ValueError("The source verification date cannot be in the future.")
    if str(data.get("published", 0)) in ("1", "True", "true") and not checked:
        raise ValueError("Verify the source and enter its verification date before publishing.")
    return result
