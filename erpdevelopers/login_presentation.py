"""Site-scoped login header context; native controller and forms are untouched."""
from erpdevelopers.branding import EXPECTED_SITE, LOGO_URL, versioned_public_asset
from erpdevelopers.language_navigation import language_queries


def update_login_context(context):
    """Called by Frappe after its native page controller, before Jinja rendering.

    No user/session writes, database calls, authentication overrides or new routes.
    Only the existing login page on the configured site gets this header shell.
    """
    import frappe

    if frappe.local.site != EXPECTED_SITE or context.get("path") not in ("login", "/login"):
        return
    context.base_template_path = "templates/erpdevelopers_login_base.html"
    context.brand_logo_url = LOGO_URL
    context.language_queries = language_queries(getattr(frappe.local, "form_dict", {}), login=True)
    context.language_js_url = versioned_public_asset("js/language.js")
    # Native login.html renders its navbar block only when this context flag is on.
    # Our base suppresses only the Guest AJAX picker flag before core JS loads.
    context.show_language_picker = 1
