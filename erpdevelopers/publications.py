"""Explicitly reviewed public stories; never read ERPNext Project or User data.

One native publication editor supplies two directories. No public write API,
background importer, automatic project exposure, or fabricated portfolio data.
"""
from urllib.parse import quote, urlencode

from erpdevelopers.catalog_support import schema_status as _schema_status, page_number
from erpdevelopers.taxonomy import TOPICS
from erpdevelopers.public_media import (
    image_path, public_files as _public_files, verify_public_image as _verify_file,
)
from erpdevelopers.publication_rules import KINDS, TEXT_LIMITS, normalize_publication
from erpdevelopers.public_pages import set_public_context
from erpdevelopers.branding import versioned_public_asset

DOCTYPE = "ERP Developers Publication"
PAGE_SIZE = 12
FIELDS = (
    "name", "publication_type", "title", "title_ar", "topic", "summary", "summary_ar",
    "content", "content_ar", "industry", "technologies", "author_name", "author_name_ar",
    "cover_image", "cover_caption", "cover_caption_ar", "public_reviewed",
)


def validate_publication_cover(doc):
    """Reuse the shared public-image security checks, without any gallery or privacy mutation."""
    import frappe
    value = doc.get("cover_image")
    if not value:
        return
    path = image_path(value)
    record = _public_files([path]).get(path)
    if not record:
        raise ValueError("Choose an existing public image up to 5 MB; private or missing files cannot be displayed.")
    _verify_file(frappe.get_doc("File", record["name"]))


def _page_number(value):
    """Compatibility entrypoint; the shared helper owns normalization."""
    return page_number(value, maximum=1000)


def public_publications(slug, args=None, lang="en"):
    """Bounded, constant-DocType projection with mandatory publication/review filters.

    get_all is intentional for this curated public projection only. No Guest
    read permission is granted on the underlying editorial DocType.
    """
    import frappe
    if slug not in KINDS:
        raise ValueError("Unknown publication directory")
    args = args or {}
    page = _page_number(args.get("page"))
    topic = args.get("topic") if args.get("topic") in TOPICS else ""
    filters = {"published": 1, "public_reviewed": 1, "publication_type": KINDS[slug]}
    if topic:
        filters["topic"] = topic
    result = {"items": [], "page": page, "topic": topic, "has_next": False}
    schema = _schema_status(DOCTYPE, FIELDS)
    if not schema["table_present"] or schema["missing_columns"]:
        return result
    rows = frappe.get_all(DOCTYPE, fields=list(FIELDS), filters=filters,
        order_by="sort_order asc, modified desc, name asc",
        limit_start=(page - 1) * PAGE_SIZE, limit_page_length=PAGE_SIZE + 1)
    result["has_next"] = len(rows) > PAGE_SIZE
    rows = rows[:PAGE_SIZE]
    paths = {}
    for row in rows:
        try:
            if row.get("cover_image"):
                paths[row["name"]] = image_path(row["cover_image"])
        except ValueError:
            continue
    files = _public_files(paths.values())
    for row in rows:
        arabic = lang.startswith("ar") and all(row.get(f"{key}_ar") for key in ("title", "summary", "content"))
        suffix = "_ar" if arabic else ""
        entry = {key: str(row.get(key + suffix) or "")[:TEXT_LIMITS[key]]
                 for key in ("title", "summary", "content")}
        entry.update({"name": row["name"], "topic": row.get("topic") or "",
                      "lang": "ar" if arabic else "en", "cover": None})
        entry["industry"] = str(row.get("industry") or "")[:120] if slug == "projects" else ""
        entry["technologies"] = str(row.get("technologies") or "")[:240] if slug == "projects" else ""
        entry["author"] = str(row.get("author_name_ar" if arabic else "author_name") or row.get("author_name") or "")[:120] if slug == "team-advice" else ""
        path = paths.get(row["name"])
        if path in files:
            entry["cover"] = {"url": quote(path, safe="/-_.~"),
                "alt": str(row.get("cover_caption_ar" if arabic else "cover_caption") or entry["title"])[:240]}
        result["items"].append(entry)
    return result


def set_publication_context(context, slug):
    import frappe
    from frappe import _
    if slug not in KINDS:
        raise ValueError("Unknown publication directory")
    lang = "ar" if str(frappe.local.lang or "en").startswith("ar") else "en"
    is_projects = slug == "projects"
    title = _("Projects") if is_projects else _("Team Advice")
    description = (_("Explore published project stories, technologies and lessons from delivery.")
                   if is_projects else _("Practical recommendations from our team on ERP, development and technology decisions."))
    set_public_context(context, slug=slug, title=title, description=description)
    context.directory_title = title
    context.directory_slug = slug
    context.is_projects = is_projects
    context.publications_css_url = versioned_public_asset("css/publications.css")
    context.directory = public_publications(slug, frappe.form_dict, lang)
    context.topics = TOPICS
    context.directory_language = lang
    context.can_manage_publications = (frappe.session.user != "Guest" and frappe.has_permission(DOCTYPE, "read"))
    context.manage_publications_url = "/desk/erp-developers-publication?" + urlencode({"publication_type": KINDS[slug]})
    context.canonical_url += "?" + urlencode({"_lang": lang})
    context.metatags["og:url"] = context.canonical_url
    def page_url(page):
        values = {"_lang": lang, "page": page}
        if context.directory["topic"]:
            values["topic"] = context.directory["topic"]
        return f"/{slug}?" + urlencode(values) + "#publications"
    context.previous_page_url = page_url(context.directory["page"] - 1) if context.directory["page"] > 1 else None
    context.next_page_url = page_url(context.directory["page"] + 1) if context.directory["has_next"] and context.directory["page"] < 1000 else None
