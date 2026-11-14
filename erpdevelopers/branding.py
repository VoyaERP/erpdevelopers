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

# The original customer-selected PNG is deliberately not regenerated or re-encoded.
LOGO_URL = "/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
FAVICON_URL = "/assets/erpdevelopers/images/erpdevelopers-selected-favicon.png"
HOME_STYLESHEET_URL = "/assets/erpdevelopers/css/brand.css"
HOME_STYLESHEET_FILE = Path(__file__).resolve().parent / "public" / "css" / "brand.css"


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
        "favicon": FAVICON_URL,
        "title_prefix": APP_NAME,
        "show_language_picker": 1,
    }
