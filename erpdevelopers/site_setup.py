"""Explicit per-site branding for erp-developers.com.

CLI-only setup. This is deliberately NOT a whitelisted API method or an
after-install hook: no existing Frappe site is changed by installing the app.
"""

import frappe

EXPECTED_SITE = "erp-developers.com"
HOME_ROUTE = "erp-developers-home"
ICON = "/assets/erpdevelopers/images/erp-mark.svg"


def configure_website():
    """Run only with: bench --site erp-developers.com execute erpdevelopers.site_setup.configure_website."""
    if frappe.local.site != EXPECTED_SITE:
        raise RuntimeError("Refusing to change Website Settings on an unexpected site.")

    settings = frappe.get_single("Website Settings")
    desired = {
        "home_page": HOME_ROUTE,
        "app_name": "ERP Developers",
        "app_logo": ICON,
        "favicon": ICON,
        "title_prefix": "ERP Developers",
        "show_language_picker": 1,
    }
    changed = []
    for fieldname, value in desired.items():
        if settings.get(fieldname) != value:
            settings.set(fieldname, value)
            changed.append(fieldname)

    if changed:
        settings.save(ignore_permissions=True)
        frappe.db.commit()
        frappe.clear_cache()
    return {"site": EXPECTED_SITE, "changed_fields": changed, "home_page": HOME_ROUTE}
