"""Published regional event directory. Reads only; no remote requests or imports."""
from datetime import datetime, timezone
from urllib.parse import urlencode
from babel.dates import format_date
from erpdevelopers.catalog_support import schema_status as _schema_status, page_number
from erpdevelopers.catalog_rules import event_https_url
from erpdevelopers.event_rules import FORMATS, TOPICS, _time
from erpdevelopers.event_media import attach_public_event_media

DOCTYPE = "ERP Developers Event"
PAGE_SIZE = 12
PUBLIC_FIELDS = (
    "name", "title", "title_ar", "description", "description_ar", "topic",
    "event_type", "event_format", "event_status", "organizer", "country", "city",
    "venue", "start_date", "end_date", "start_time", "end_time", "date_only", "time_zone",
    "event_url", "source_url", "verified_on", "start_utc", "end_utc", "regional_relevance",
    "cover_image", "cover_caption", "cover_caption_ar", "has_event_images",
)


def _query_options(params):
    def value(key):
        item = params.get(key, "")
        return item.strip() if isinstance(item, str) else ""
    page = page_number(value("page"), maximum=10000)
    return {
        "topic": value("topic") if value("topic") in TOPICS else "",
        "country": value("country")[:140],
        "event_format": value("event_format") if value("event_format") in FORMATS else "",
        "period": "past" if value("period") == "past" else "upcoming", "page": page,
    }


def get_event_directory(params=None, lang="en", now=None):
    import frappe
    selected = _query_options(params or {})
    result = dict(event_rows=[], countries=[], topics=TOPICS, formats=FORMATS,
                  selected=selected, total=0, pages=1, previous_url=None, next_url=None, schema_ready=False)
    status = _schema_status(DOCTYPE, PUBLIC_FIELDS)
    if not status["table_present"] or status["missing_columns"]:
        return result
    result["schema_ready"] = True
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("The directory clock must have a timezone")
    cutoff = now.astimezone(timezone.utc).replace(tzinfo=None)
    base = {"published": 1, "regional_relevance": 1}
    country_rows = frappe.get_all(DOCTYPE, filters=base, fields=["country"],
                                 distinct=True, order_by="country asc", limit_page_length=200)
    result["countries"] = sorted({r.get("country") for r in country_rows if r.get("country")})
    if selected["country"] not in result["countries"]:
        selected["country"] = ""
    filters = {**base, "end_utc": ["<=" if selected["period"] == "past" else ">", cutoff]}
    for key in ("topic", "country", "event_format"):
        if selected[key]:
            filters[key] = selected[key]
    total = frappe.db.count(DOCTYPE, filters=filters)
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    selected["page"] = min(selected["page"], pages)
    result.update(total=total, pages=pages)
    rows = frappe.get_all(DOCTYPE, filters=filters, fields=list(PUBLIC_FIELDS),
        order_by="start_utc " + ("desc" if selected["period"] == "past" else "asc") + ", name asc",
        limit_start=(selected["page"] - 1) * PAGE_SIZE, limit_page_length=PAGE_SIZE)
    locale = "ar" if str(lang).startswith("ar") else "en"
    for row in rows:
        entry = dict(row)
        try:
            entry["event_url"] = event_https_url(entry["event_url"])
            if entry.get("source_url"):
                entry["source_url"] = event_https_url(entry["source_url"])
            for key in ("start_date", "end_date", "verified_on"):
                if entry.get(key):
                    day = datetime.fromisoformat(str(entry[key])).date()
                    entry[key + "_label"] = format_date(day, format="medium", locale=locale)
            for key in ("start_time", "end_time"):
                value = entry.get(key)
                entry[key + "_label"] = _time(value).strftime("%H:%M") if value is not None and value != "" else ""
        except (ValueError, TypeError):
            continue
        result["event_rows"].append(entry)
    attach_public_event_media(result["event_rows"])
    def page_url(page):
        return "/events?" + urlencode({**{k:v for k,v in selected.items() if v}, "page":page, "_lang":locale})
    if selected["page"] > 1:
        result["previous_url"] = page_url(selected["page"] - 1)
    if selected["page"] < pages:
        result["next_url"] = page_url(selected["page"] + 1)
    return result
