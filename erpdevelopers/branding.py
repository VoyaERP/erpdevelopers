"""Stable ERP Developers identity and explicit website asset configuration."""
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


def _fingerprinted_asset_url(file_path: Path, public_url: str) -> str:
    """One content-hash implementation for all ERP Developers website assets.

    Recalculate on use so updated CSS obtains a fresh URL without retaining a
    previous deployment's fingerprint in a long-running web process.
    """
    digest = sha256(file_path.read_bytes()).hexdigest()[:16]
    return f"{public_url}?v={digest}"


def login_stylesheet_url():
    return _fingerprinted_asset_url(LOGIN_STYLESHEET_FILE, LOGIN_STYLESHEET_URL)


def homepage_stylesheet_url():
    return _fingerprinted_asset_url(HOME_STYLESHEET_FILE, HOME_STYLESHEET_URL)


def website_settings_values():
    return {
        "home_page": HOME_ROUTE, "app_name": APP_NAME, "app_logo": LOGO_URL,
        "banner_image": LOGO_URL, "brand_html": NAVBAR_BRAND_HTML,
        "favicon": FAVICON_URL, "title_prefix": APP_NAME, "show_language_picker": 1,
    }


def desk_navbar_settings_values():
    return {"app_logo": LOGO_URL}


def versioned_public_asset(relative_path):
    """Hash only explicitly permitted site assets, never arbitrary paths."""
    allowed = {
        "css/portal.css", "js/catalog.js", "js/assistant.js",
        "js/consultation.js", "css/meeting.css", "js/meeting.js",
        "css/arabic_typography.css", "css/events.css", "css/discovery.css",
        "css/publications.css", "js/language.js",
    }
    if relative_path not in allowed:
        raise ValueError("Unexpected public asset")
    asset = Path(__file__).resolve().parent / "public" / relative_path
    return _fingerprinted_asset_url(asset, f"/assets/erpdevelopers/{relative_path}")
