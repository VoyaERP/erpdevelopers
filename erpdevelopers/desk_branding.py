"""Site-scoped presentation-only ERPNext icon override for Frappe 16.

Frappe v16 builds the Apps screen and dock from bootinfo.app_data. Older
installations can still use the Desktop Icons fallback. Both get the same
approved ERP Developers shield without touching ERPNext hooks, routes,
permissions or shared Bench assets.
"""

from erpdevelopers.branding import EXPECTED_SITE, FAVICON_URL


def _brand_rows(rows, *, app_field, logo_field, app_icons_only=False):
    """Copy only the matching ERPNext entry; leave other app payloads unchanged."""
    if not isinstance(rows, list):
        return rows

    result = []
    for row in rows:
        is_erpnext = isinstance(row, dict) and row.get(app_field) == "erpnext"
        is_icon = not app_icons_only or row.get("icon_type") == "App"
        if is_erpnext and is_icon:
            result.append({**row, logo_field: FAVICON_URL})
        else:
            result.append(row)
    return result


def brand_erpnext_on_boot(bootinfo):
    """Modify only logo URLs in this site's already permission-filtered boot data.

    No database writes, new app records, monkeypatches or browser-side DOM
    manipulation. A shared Bench may host other tenants; the site guard is
    deliberate and must not be removed.
    """
    import frappe

    if frappe.local.site != EXPECTED_SITE:
        return

    if isinstance(bootinfo.get("app_data"), list):
        bootinfo["app_data"] = _brand_rows(
            bootinfo["app_data"], app_field="app_name", logo_field="app_logo_url"
        )

    if isinstance(bootinfo.get("desktop_icons"), list):
        bootinfo["desktop_icons"] = _brand_rows(
            bootinfo["desktop_icons"],
            app_field="app",
            logo_field="logo_url",
            app_icons_only=True,
        )
