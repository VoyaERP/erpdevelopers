"""Canonical, non-deceptive public SEO data for the ERP Developers landing page.

Only published content is described. Planned LMS, jobs and AI modules must not
be advertised as live services or marked up as active products.
"""
from json import dumps
from erpdevelopers.branding import APP_NAME, EXPECTED_SITE, LOGO_URL, TAGLINE

PUBLIC_BASE_URL = f"https://{EXPECTED_SITE}"
CANONICAL_HOME_URL = f"{PUBLIC_BASE_URL}/"
SOCIAL_IMAGE_URL = f"{PUBLIC_BASE_URL}{LOGO_URL}"
SEO_TITLE = "ERP Developers | ERP Consulting & Technology Solutions"
SEO_DESCRIPTION = (
    "ERP Developers provides ERP consulting, ERPNext and Frappe development, "
    "system integration, solution architecture and technology guidance for businesses."
)
SEO_TITLE_AR = "ERP Developers | استشارات ERP وحلول التقنية"
SEO_DESCRIPTION_AR = (
    "ERP Developers للاستشارات في أنظمة ERP وتطوير ERPNext وFrappe "
    "وتكامل الأنظمة وهندسة الحلول والتقنيات الحديثة لدعم أعمال المؤسسات."
)
ROBOTS_TXT = (
    "User-agent: *\nAllow: /\nDisallow: /app\nDisallow: /desk\n"
    "Disallow: /api/\nDisallow: /login\nDisallow: /me\n"
    f"Sitemap: {PUBLIC_BASE_URL}/sitemap.xml\n"
)


def homepage_seo_context(language="en"):
    """Shared bilingual homepage metadata through native Frappe MetaTags."""
    language = "ar" if str(language).lower().startswith("ar") else "en"
    title = SEO_TITLE_AR if language == "ar" else SEO_TITLE
    description = SEO_DESCRIPTION_AR if language == "ar" else SEO_DESCRIPTION
    canonical = CANONICAL_HOME_URL + ("?_lang=ar" if language == "ar" else "")
    organization_id = f"{CANONICAL_HOME_URL}#organization"
    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "Organization", "@id": organization_id, "name": APP_NAME,
         "url": CANONICAL_HOME_URL, "logo": SOCIAL_IMAGE_URL, "slogan": TAGLINE,
         "description": SEO_DESCRIPTION,
         "knowsAbout": ["ERP consulting", "ERPNext", "Frappe Framework",
                        "Microsoft Dynamics 365 Business Central",
                        "System integration", "Solution architecture",
                        "Cloud technology", "Digital transformation"]},
        {"@type": "WebSite", "@id": f"{CANONICAL_HOME_URL}#website", "name": APP_NAME,
         "url": CANONICAL_HOME_URL, "description": SEO_DESCRIPTION,
         "publisher": {"@id": organization_id}, "inLanguage": ["en", "ar"]},
    ]}
    return {
        "title": title, "description": description, "image": SOCIAL_IMAGE_URL,
        "canonical_home_url": canonical, "seo_language": language,
        "language_alternates": [
            {"lang": "en", "href": CANONICAL_HOME_URL},
            {"lang": "ar", "href": CANONICAL_HOME_URL + "?_lang=ar"},
        ],
        "metatags": {"og:type": "website", "og:url": canonical,
                     "og:site_name": APP_NAME, "twitter:card": "summary_large_image",
                     "robots": "index, follow, max-image-preview:large"},
        "structured_data_json": dumps(schema, ensure_ascii=False, separators=(",", ":"), sort_keys=True).replace("<", "\\u003c"),
    }
