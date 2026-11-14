"""Stable ERP Developers identity and explicit website asset configuration."""
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

APP_NAME = "ERP Developers"
TAGLINE = "Engage. Reason. Progress."
EXPECTED_SITE = "erp-developers.com"
HOME_ROUTE = "erp-developers-home"
DESK_SIGNIN_URL = "/login?redirect-to=/desk"
LOGO_URL = "/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
FAVICON_URL = "/assets/erpdevelopers/images/erpdevelopers-selected-favicon.png"
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
    """Content fingerprint. Reload web processes after deploying new assets."""
    digest = sha256(LOGIN_STYLESHEET_FILE.read_bytes()).hexdigest()[:16]
    return f"{LOGIN_STYLESHEET_URL}?v={digest}"


@lru_cache(maxsize=1)
def homepage_stylesheet_url():
    """Content fingerprint, computed once per Python web process."""
    digest = sha256(HOME_STYLESHEET_FILE.read_bytes()).hexdigest()[:16]
    return f"{HOME_STYLESHEET_URL}?v={digest}"


def website_settings_values():
    return {
        "home_page": HOME_ROUTE, "app_name": APP_NAME, "app_logo": LOGO_URL,
        "banner_image": LOGO_URL, "brand_html": NAVBAR_BRAND_HTML,
        "favicon": FAVICON_URL, "title_prefix": APP_NAME, "show_language_picker": 1,
    }


def desk_navbar_settings_values():
    return {"app_logo": LOGO_URL}


@lru_cache(maxsize=8)
def versioned_public_asset(relative_path):
    """Hash only explicitly permitted site assets, never arbitrary paths."""
    allowed = {
        "css/portal.css", "js/catalog.js", "js/assistant.js",
        "js/consultation.js", "css/meeting.css", "js/meeting.js",
        "css/arabic_typography.css", "css/events.css",
    }
    if relative_path not in allowed:
        raise ValueError("Unexpected public asset")
    asset = Path(__file__).resolve().parent / "public" / relative_path
    digest = sha256(asset.read_bytes()).hexdigest()[:16]
    return f"/assets/erpdevelopers/{relative_path}?v={digest}"
