"""Regional public events. External synchronization is deliberately not enabled."""
from erpdevelopers.events_catalog import DOCTYPE, get_event_directory
from erpdevelopers.public_pages import set_public_context
from erpdevelopers.branding import versioned_public_asset

sitemap = 1


def get_context(context):
    import frappe
    set_public_context(context, slug="events", title="Events",
                       description="Reviewed technology, ERP, cloud, AI and cybersecurity events for the Middle East community.")
    for field, value in get_event_directory(frappe.form_dict, frappe.local.lang or "en").items():
        setattr(context, field, value)
    context.events_css_url = versioned_public_asset("css/events.css")
    context.can_manage_events = bool(getattr(context, "schema_ready", False) and
                                    frappe.session.user != "Guest" and frappe.has_permission(DOCTYPE, "write"))
    if any(frappe.form_dict.get(key) for key in ("topic", "country", "event_format", "period", "page")):
        context.metatags["robots"] = "noindex, follow"
