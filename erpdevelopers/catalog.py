"""Curator-reviewed public catalogue; no Guest DocType permissions are granted.

During a partial/stale migration, a public index remains renderable as empty.
Operators can diagnose missing schemas with catalog_health via bench execute.
Other database failures still raise normally, rather than being silently hidden.
"""
from erpdevelopers.catalog_rules import external_https_url, youtube_playlist_id

PLAYLIST_DOCTYPE = "ERP Developers Playlist"
RESOURCE_DOCTYPE = "ERP Developers Resource"
PLAYLIST_FIELDS = (
    "title", "title_ar", "topic", "level", "language",
    "description", "playlist_url", "playlist_id", "visibility",
)
RESOURCE_FIELDS = (
    "title", "title_ar", "topic", "summary", "editorial_note",
    "language", "source_kind", "external_url", "source_name", "web_page",
)


def _schema_status(doctype, fields):
    """One DB metadata lookup: do not query a table missing after partial migrate."""
    import frappe

    if not frappe.db.table_exists(doctype, cached=False):
        return {"table_present": False, "missing_columns": list(fields)}

    required = set(fields) | {"published", "sort_order", "modified"}
    existing = set(frappe.db.get_table_columns(doctype))
    return {
        "table_present": True,
        "missing_columns": sorted(required - existing),
    }


def catalog_health():
    """Read-only diagnostic for Bench operators, not a public API endpoint."""
    return {
        PLAYLIST_DOCTYPE: _schema_status(PLAYLIST_DOCTYPE, PLAYLIST_FIELDS),
        RESOURCE_DOCTYPE: _schema_status(RESOURCE_DOCTYPE, RESOURCE_FIELDS),
    }


def _published_rows(doctype, fields):
    import frappe

    status = _schema_status(doctype, fields)
    if not status["table_present"] or status["missing_columns"]:
        return []
    return frappe.get_all(
        doctype,
        filters=(
            {"published": 1, "visibility": "Public"}
            if doctype == PLAYLIST_DOCTYPE else {"published": 1}
        ),
        fields=list(fields),
        order_by="sort_order asc, modified desc",
        limit_page_length=60,
    )


def public_playlists():
    rows = _published_rows(PLAYLIST_DOCTYPE, PLAYLIST_FIELDS)
    result = []
    for item in rows:
        try:
            list_id = youtube_playlist_id(item["playlist_url"])
        except ValueError:
            continue
        entry = dict(item)
        # Always take the validated ID from the canonical URL. Older imported
        # records can have a blank/stale read-only playlist_id field.
        entry["playlist_id"] = list_id
        entry["watch_url"] = f"https://www.youtube.com/playlist?list={list_id}"
        result.append(entry)
    return result


def authorized_private_playlists():
    """Return private playlists only with an authenticated, permission-filtered read.

    A Frappe session does not override YouTube's own video privacy rules.
    """
    import frappe

    if frappe.session.user == "Guest":
        return []
    status = _schema_status(PLAYLIST_DOCTYPE, PLAYLIST_FIELDS)
    if not status["table_present"] or status["missing_columns"]:
        return []
    rows = frappe.get_list(
        PLAYLIST_DOCTYPE,
        filters={"published": 1, "visibility": "Private"},
        fields=["name", *PLAYLIST_FIELDS],
        order_by="sort_order asc, modified desc",
        limit_page_length=60,
    )
    result = []
    for item in rows:
        try:
            list_id = youtube_playlist_id(item["playlist_url"])
        except ValueError:
            continue
        entry = dict(item)
        entry["playlist_id"] = list_id
        entry["watch_url"] = f"https://www.youtube.com/playlist?list={list_id}"
        result.append(entry)
    return result


def public_resources():
    import frappe

    rows = _published_rows(RESOURCE_DOCTYPE, RESOURCE_FIELDS)
    internal = {r.web_page for r in rows if r.source_kind == "Original Article" and r.web_page}
    published_pages = {}
    if internal:
        # If Frappe's own Web Page table is undergoing migration, do not expose
        # a draft article and do not render its link.
        if frappe.db.table_exists("Web Page", cached=False):
            pages = frappe.get_all(
                "Web Page",
                filters={"name": ["in", sorted(internal)], "published": 1},
                fields=["name", "route"],
            )
            published_pages = {p.name: p.route for p in pages if p.route}

    result = []
    for row in rows:
        item = dict(row)
        if item["source_kind"] == "Original Article":
            route = published_pages.get(item["web_page"])
            if not route or route.lstrip("/").startswith(("desk/", "app/", "login", "api/")):
                continue
            item["href"] = "/" + route.strip("/")
            item["external"] = False
        else:
            try:
                item["href"] = external_https_url(item["external_url"])
            except ValueError:
                continue
            item["external"] = True
        result.append(item)
    return result

def public_catalog_topics(rows):
    """Get distinct topics from published catalog dictionaries.

    `public_playlists` and `public_resources` intentionally convert Frappe
    rows to plain dicts before returning them; controllers must use key access
    rather than Python attribute access. Ignore malformed/blank topics while
    preserving the published-only row filter and stable case-insensitive sort.
    """
    return sorted(
        {row["topic"].strip() for row in rows
         if isinstance(row.get("topic"), str) and row["topic"].strip()},
        key=str.casefold,
    )
