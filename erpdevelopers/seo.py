"""Canonical, non-deceptive public SEO data for the ERP Developers landing page.

Only published content is described. Planned LMS, jobs and AI modules must not
be advertised as live services or marked up as active products.
"""
from json import dumps
from erpdevelopers.branding import APP_NAME, EXPECTED_SITE, LOGO_URL, TAGLINE

PUBLIC_BASE_URL = f"https://{EXPECTED_SITE}"
CANONICAL_HOME_URL = f"{PUBLIC_BASE_URL}/"
SOCIAL_IMAGE_URL = f"{PUBLIC_BASE_URL}{LOGO_URL}"
SEO_TITLE = "ERP Developers | Developer Community & Technology"
SEO_DESCRIPTION = (
    "Practical ERP development and ERPNext guides, curated training, and Middle East "
    "technology events from ERP Developers. Learn across business platforms."
)
ROBOTS_TXT = (
    "User-agent: *\nAllow: /\nDisallow: /app\nDisallow: /desk\n"
    "Disallow: /api/\nDisallow: /login\nDisallow: /me\n"
    f"Sitemap: {PUBLIC_BASE_URL}/sitemap.xml\n"
)


def homepage_seo_context():
    """Return fresh values using Frappe's existing MetaTags pipeline."""
    organization_id = f"{CANONICAL_HOME_URL}#organization"
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": organization_id, "name": APP_NAME,
         "url": CANONICAL_HOME_URL, "logo": SOCIAL_IMAGE_URL, "slogan": TAGLINE},
        {"@type": "WebSite", "@id": f"{CANONICAL_HOME_URL}#website", "name": APP_NAME,
         "url": CANONICAL_HOME_URL, "description": SEO_DESCRIPTION,
         "publisher": {"@id": organization_id}, "inLanguage": ["en", "ar"]},
    ]}
    return {
        "title": SEO_TITLE, "description": SEO_DESCRIPTION, "image": SOCIAL_IMAGE_URL,
        "canonical_home_url": CANONICAL_HOME_URL,
        "metatags": {"og:type": "website", "og:url": CANONICAL_HOME_URL,
                     "og:site_name": APP_NAME, "twitter:card": "summary_large_image",
                     "robots": "index, follow, max-image-preview:large"},
        "structured_data_json": dumps(schema, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("<", "\\u003c"),
    }
