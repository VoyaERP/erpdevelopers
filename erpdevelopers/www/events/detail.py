"""Published event details. Never use get_doc on a Guest-controlled identifier."""
from erpdevelopers.branding import versioned_public_asset
from erpdevelopers.events_catalog import DOCTYPE, PUBLIC_FIELDS
from erpdevelopers.event_media import attach_public_event_media
from erpdevelopers.event_seo import event_name_from_path, event_path, event_jsonld
from erpdevelopers.public_pages import PUBLIC_BASE, set_public_context


def get_context(context):
    import frappe
    name = event_name_from_path(frappe.form_dict.get("event_key"))
    if not name:
        frappe.throw("Event not found", frappe.DoesNotExistError)
    rows = frappe.get_all(
        DOCTYPE,
        filters={"name": name, "published": 1, "regional_relevance": 1},
        fields=list(PUBLIC_FIELDS),
        limit_page_length=1,
    )
    if not rows:
        frappe.throw("Event not found", frappe.DoesNotExistError)
    item = dict(rows[0])
    from erpdevelopers.catalog_rules import event_https_url
    try:
        item["event_url"] = event_https_url(item["event_url"])
        if item.get("source_url"):
            item["source_url"] = event_https_url(item["source_url"])
    except ValueError:
        frappe.throw("Event not found", frappe.DoesNotExistError)
    attach_public_event_media([item])
    lang = str(frappe.local.lang or "en")
    title = item.get("title_ar") if lang.startswith("ar") and item.get("title_ar") else item["title"]
    description = item.get("description_ar") if lang.startswith("ar") and item.get("description_ar") else item.get("description", "")
    path = event_path(item)
    set_public_context(context, slug=path, title=title, description=description[:160])
    context.metatags["og:type"] = "website"
    context.metatags["og:title"] = title
    context.metatags["og:description"] = description[:200]
    if item.get("media", {}).get("cover"):
        context.image = PUBLIC_BASE + item["media"]["cover"]["url"]
    context.event = item
    context.event_jsonld = event_jsonld(item, language=lang)
    context.events_css_url = versioned_public_asset("css/events.css")
    context.no_cache = 1
