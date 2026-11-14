"""Reusable Frappe website context for public ERP Developers pages."""
from erpdevelopers.branding import (
    APP_NAME, DESK_SIGNIN_URL, FAVICON_URL, LOGO_URL, EXPECTED_SITE,
    homepage_stylesheet_url,
)

PUBLIC_BASE = f"https://{EXPECTED_SITE}"
PORTAL_CSS = "/assets/erpdevelopers/css/portal.css"
CATALOG_JS = "/assets/erpdevelopers/js/catalog.js"
ASSISTANT_JS = "/assets/erpdevelopers/js/assistant.js"


def set_public_context(context, *, slug, title, description):
    """Use Frappe's native metatags and one brand/nav/footer on every page."""
    canonical = f"{PUBLIC_BASE}/{slug.lstrip('/')}"
    context.title = f"{APP_NAME} | {title}"
    context.description = description
    context.image = f"{PUBLIC_BASE}{LOGO_URL}"
    context.metatags = {
        "og:type": "website",
        "og:url": canonical,
        "og:site_name": APP_NAME,
    }
    context.canonical_url = canonical
    context.brand_logo_url = LOGO_URL
    context.brand_icon_url = FAVICON_URL
    context.desk_signin_url = DESK_SIGNIN_URL
    context.homepage_css_url = homepage_stylesheet_url()
    context.portal_css_url = PORTAL_CSS
    context.catalog_js_url = CATALOG_JS
    context.assistant_js_url = ASSISTANT_JS
    context.no_cache = 1
