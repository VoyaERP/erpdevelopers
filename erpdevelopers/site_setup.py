"""Explicit, idempotent branding for the existing ERP Developers site only.

This file is intentionally not an after-install hook or a whitelisted API.
Run via bench --site erp-developers.com execute erpdevelopers.site_setup.configure_website.
"""

import frappe

from erpdevelopers.branding import EXPECTED_SITE, HOME_ROUTE, website_settings_values


def configure_website():
    """Synchronize approved branding without changing any other Frappe site."""
    if frappe.local.site != EXPECTED_SITE:
        raise RuntimeError("Refusing to change Website Settings on an unexpected site.")

    settings = frappe.get_single("Website Settings")
    changed = []
    for fieldname, value in website_settings_values().items():
        if settings.get(fieldname) != value:
            settings.set(fieldname, value)
            changed.append(fieldname)

    if changed:
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()

    return {
        "site": EXPECTED_SITE,
        "changed_fields": changed,
        "home_page": HOME_ROUTE,
    }
