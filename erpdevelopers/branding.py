"""Stable ERP Developers brand identity and website asset configuration.

Pure Python module: safe to import in static CI, Frappe commands and page controllers.
Only the explicitly configured site may receive Website Settings updates.
"""

from functools import lru_cache
from hashlib import sha256
from pathlib import Path

APP_NAME = "ERP Developers"
TAGLINE = "Engage. Reason. Progress."
EXPECTED_SITE = "erp-developers.com"
HOME_ROUTE = "erp-developers-home"
# Native Frappe v16 honors the sanitized redirect-to parameter after login.
# This URL is for authorized Desk/System Users, not future website members.
DESK_SIGNIN_URL = "/login?redirect-to=/desk"

# The original customer-selected PNG is deliberately not regenerated or re-encoded.
LOGO_URL = "/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
FAVICON_URL = "/assets/erpdevelopers/images/erpdevelopers-selected-favicon.png"
# Frappe Standard Navbar trusts this administrator-controlled HTML setting.
# Its image and Frappe's native login-logo resolve to the SAME approved PNG.
NAVBAR_BRAND_HTML = (
    f'<img src="{LOGO_URL}" alt="{APP_NAME} — {TAGLINE}" '
    'width="210" height="70">'
)
LOGIN_STYLESHEET_URL = "/assets/erpdevelopers/css/login.css"
LOGIN_STYLESHEET_FILE = Path(__file__).resolve().parent / "public" / "css" / "login.css"
HOME_STYLESHEET_URL = "/assets/erpdevelopers/css/brand.css"
HOME_STYLESHEET_FILE = Path(__file__).resolve().parent / "public" / "css" / "brand.css"


@lru_cache(maxsize=1)
def login_stylesheet_url():
    """Version the render-blocking, CSS-only native login theme by file bytes.

    Gunicorn web reload is required after updating hooks, like all Frappe hooks.
    """
    digest = sha256(LOGIN_STYLESHEET_FILE.read_bytes()).hexdigest()[:16]
    return f"{LOGIN_STYLESHEET_URL}?v={digest}"


@lru_cache(maxsize=1)
def homepage_stylesheet_url():
    """Use a content hash, not a manually maintained cache-busting timestamp.

    This value is computed once per Python web process. Reload the web process
    after deployment so both the template and its stylesheet version advance.
    """
    digest = sha256(HOME_STYLESHEET_FILE.read_bytes()).hexdigest()[:16]
    return f"{HOME_STYLESHEET_URL}?v={digest}"


def website_settings_values():
    """Return a new mapping so callers cannot modify global brand configuration."""
    return {
        "home_page": HOME_ROUTE,
        "app_name": APP_NAME,
        "app_logo": LOGO_URL,
        "brand_html": NAVBAR_BRAND_HTML,
        "banner_image": LOGO_URL,
        "favicon": FAVICON_URL,
        "title_prefix": APP_NAME,
        "show_language_picker": 1,
    }


def desk_navbar_settings_values():
    """Use the original uploaded PNG for the Frappe Desk navbar, too.

    Navbar Settings is a site-specific Single DocType. The Frappe v16 boot
    path obtains app_logo_url from Website Settings or Navbar Settings,
    then falls back to app_logo_url hooks.
    """
    return {"app_logo": LOGO_URL}


@lru_cache(maxsize=8)
def versioned_public_asset(relative_path):
    """Hash site-specific CSS/JS to avoid stale assets after deployment."""
    allowed = {
        "css/portal.css", "js/catalog.js", "js/assistant.js",
        "js/consultation.js", "css/meeting.css", "js/meeting.js",
    }
    if relative_path not in allowed:
        raise ValueError("Unexpected public asset")
    asset = Path(__file__).resolve().parent / "public" / relative_path
    digest = sha256(asset.read_bytes()).hexdigest()[:16]
    return f"/assets/erpdevelopers/{relative_path}?v={digest}"
