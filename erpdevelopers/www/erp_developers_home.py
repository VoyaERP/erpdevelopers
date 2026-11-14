"""Page controller for /erp-developers-home (hyphens are scrubbed by Frappe)."""

from erpdevelopers.branding import DESK_SIGNIN_URL, FAVICON_URL, LOGO_URL, homepage_stylesheet_url
from erpdevelopers.content import AI_FLOW, ECOSYSTEM, ROADMAP, VALUES
from erpdevelopers.seo import homepage_seo_context


def get_context(context):
    # Frappe MetaTags renders search, OpenGraph and Twitter tags once.
    for field, value in homepage_seo_context().items():
        setattr(context, field, value)
    context.no_cache = 1
    context.brand_logo_url = LOGO_URL
    context.desk_signin_url = DESK_SIGNIN_URL
    context.brand_icon_url = FAVICON_URL
    context.homepage_css_url = homepage_stylesheet_url()
    context.values_items = VALUES
    context.ecosystem_items = ECOSYSTEM
    context.ai_flow_items = AI_FLOW
    context.roadmap_items = ROADMAP
