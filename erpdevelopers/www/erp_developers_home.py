"""Page controller for /erp-developers-home (hyphens are scrubbed by Frappe)."""

from erpdevelopers.branding import APP_NAME, DESK_SIGNIN_URL, FAVICON_URL, LOGO_URL, TAGLINE, homepage_stylesheet_url
from erpdevelopers.content import AI_FLOW, ECOSYSTEM, ROADMAP, VALUES


def get_context(context):
    context.title = f"{APP_NAME} | {TAGLINE}"
    context.description = (
        "A community for developers, business leaders and technology innovators."
    )
    context.no_cache = 1
    context.brand_logo_url = LOGO_URL
    context.desk_signin_url = DESK_SIGNIN_URL
    context.brand_icon_url = FAVICON_URL
    context.homepage_css_url = homepage_stylesheet_url()
    context.values_items = VALUES
    context.ecosystem_items = ECOSYSTEM
    context.ai_flow_items = AI_FLOW
    context.roadmap_items = ROADMAP
