"""Canonical public event links and search-engine structured metadata.

No DocType is exposed to Guest; callers supply allowlisted, published records.
"""
import json
import re
from datetime import datetime, timezone
from urllib.parse import quote

from erpdevelopers.public_pages import PUBLIC_BASE

_SLUG = re.compile(r"[^a-z0-9]+")
_NAME = re.compile(r"^[a-zA-Z0-9]{6,64}$")


def event_path(item):
    """Use the immutable document ID as the lookup key; title is decorative."""
    title = str(item.get("title") or "event").lower()
    short = _SLUG.sub("-", title).strip("-")[:75].strip("-") or "event"
    return "/events/{}-{}".format(short, quote(str(item["name"]), safe=""))


def event_name_from_path(segment):
    # Match the final ID suffix, never accept raw paths or filters as IDs.
    name = str(segment or "").rsplit("-", 1)[-1]
    return name if _NAME.fullmatch(name) else None


def event_jsonld(item, *, language="en"):
    """Return safely embeddable JSON-LD for a real, published event."""
    title = item.get("title_ar") if language.startswith("ar") and item.get("title_ar") else item["title"]
    description = item.get("description_ar") if language.startswith("ar") and item.get("description_ar") else item.get("description", "")
    status = {"Cancelled": "EventCancelled", "Postponed": "EventPostponed"}
    schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": title,
        "description": description,
        "url": PUBLIC_BASE + event_path(item),
        "eventStatus": "https://schema.org/" + status.get(item.get("event_status"), "EventScheduled"),
        "eventAttendanceMode": "https://schema.org/" + {
            "Online": "OnlineEventAttendanceMode",
            "Hybrid": "MixedEventAttendanceMode",
        }.get(item.get("event_format"), "OfflineEventAttendanceMode"),
        "organizer": {"@type": "Organization", "name": item["organizer"]},
    }
    if item.get("date_only"):
        schema["startDate"] = str(item["start_date"])
        schema["endDate"] = str(item["end_date"])
    else:
        # UTC from the existing validated event-time normalization, not server timezone.
        for name in ("start", "end"):
            stamp = item.get(name + "_utc")
            if stamp:
                if not isinstance(stamp, datetime):
                    stamp = datetime.fromisoformat(str(stamp))
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=timezone.utc)
                schema[name + "Date"] = stamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if item.get("event_format") in ("Online", "Hybrid"):
        schema["location"] = {"@type": "VirtualLocation", "url": item["event_url"]}
    if item.get("event_format") in ("In person", "Hybrid"):
        physical = {"@type": "Place", "name": item.get("venue") or item.get("city") or title,
                    "address": {"@type": "PostalAddress",
                                "addressLocality": item.get("city") or "",
                                "addressCountry": item.get("country") or ""}}
        if item.get("event_format") == "Hybrid":
            schema["location"] = [schema["location"], physical]
        else:
            schema["location"] = physical
    if item.get("media", {}).get("cover"):
        schema["image"] = [PUBLIC_BASE + item["media"]["cover"]["url"]]
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
