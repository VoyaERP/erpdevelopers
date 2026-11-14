"""Page controller for /erp-developers-home (hyphens are scrubbed by Frappe)."""

from erpdevelopers.branding import DESK_SIGNIN_URL, FAVICON_URL, LOGO_URL, homepage_stylesheet_url, versioned_public_asset
from erpdevelopers.content import ECOSYSTEM, VALUES
from erpdevelopers.seo import homepage_seo_context
from erpdevelopers.public_pages import PORTAL_CSS, ASSISTANT_JS
from erpdevelopers.guide_content import INTRO, guide_links
from erpdevelopers.language_navigation import set_public_language_context


def get_context(context):
    # Frappe MetaTags renders search, OpenGraph and Twitter tags once.
    for field, value in homepage_seo_context().items():
        setattr(context, field, value)
    context.no_cache = 1
    set_public_language_context(context)
    context.brand_logo_url = LOGO_URL
    context.desk_signin_url = DESK_SIGNIN_URL
    context.brand_icon_url = FAVICON_URL
    context.homepage_css_url = homepage_stylesheet_url()
    context.portal_css_url = PORTAL_CSS
    context.assistant_js_url = ASSISTANT_JS
    context.discovery_css_url = versioned_public_asset("css/discovery.css")
    context.guide_links = guide_links()
    context.guide_intro = dict(INTRO)
    context.values_items = VALUES
    context.ecosystem_items = ECOSYSTEM
