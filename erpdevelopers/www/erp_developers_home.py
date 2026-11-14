"""Page controller for /erp-developers-home (hyphens are scrubbed by Frappe)."""

from erpdevelopers.branding import APP_NAME, LOGO_URL, TAGLINE, homepage_stylesheet_url


def get_context(context):
    context.title = f"{APP_NAME} | {TAGLINE}"
    context.description = (
        "A community for developers, business leaders and technology innovators."
    )
    context.no_cache = 1
    context.brand_logo_url = LOGO_URL
    context.homepage_css_url = homepage_stylesheet_url()
