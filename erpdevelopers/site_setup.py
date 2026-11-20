"""Explicit, idempotent, site-scoped website and Desk logo configuration.

CLI-only: bench --site erp-developers.com execute erpdevelopers.site_setup.configure_website
No installation hooks, login overrides, global Desk CSS or public write APIs.
"""

import frappe

from erpdevelopers.branding import (
    EXPECTED_SITE,
    HOME_ROUTE,
    desk_navbar_settings_values,
    website_settings_values,
)
from erpdevelopers.seo import ROBOTS_TXT


def _apply_values(document, values):
    """Set only changed Single DocType fields; return the names changed."""
    changed = []
    for fieldname, value in values.items():
        if document.get(fieldname) != value:
            document.set(fieldname, value)
            changed.append(fieldname)

    if changed:
        document.save(ignore_permissions=True)
    return changed


def configure_website():
    """Apply approved branding to the one authorized Frappe site only.

    The public website/login uses Website Settings. Frappe's Desk navbar
    also supports Navbar Settings.app_logo, so configure both consistently.
    One transaction, no duplicate logo copies or changes to Frappe core.
    """
    if frappe.local.site != EXPECTED_SITE:
        raise RuntimeError("Refusing to change Website Settings on an unexpected site.")

    website = frappe.get_single("Website Settings")
    desk_navbar = frappe.get_single("Navbar Settings")

    website_values = website_settings_values()
    # Preserve any administrator-managed robots.txt policy; populate only
    # when blank. The rule is crawl guidance, not an authorization control.
    if not (website.get("robots_txt") or "").strip():
        website_values["robots_txt"] = ROBOTS_TXT

    changed_website = _apply_values(website, website_values)
    changed_desk = _apply_values(desk_navbar, desk_navbar_settings_values())

    if changed_website or changed_desk:
        frappe.db.commit()
        frappe.clear_cache()

    return {
        "site": EXPECTED_SITE,
        "changed_fields": changed_website,
        "desk_changed_fields": changed_desk,
        "home_page": HOME_ROUTE,
    }
