"""Public website locale links; native Frappe still resolves the _lang request.

No User/Desk preference, session permission or database setting is modified.
"""
from collections.abc import Mapping
from urllib.parse import unquote, urlencode, urlsplit

from erpdevelopers.branding import versioned_public_asset

# Only existing public-directory filters are copied into the no-JavaScript link.
FILTER_KEYS = ("topic", "country", "event_format", "period", "page")


def language_queries(query=None, *, login=False):
    """Build same-path links without reflecting arbitrary parameters or origins."""
    query = query if isinstance(query, Mapping) else {}
    filters = {key: value for key in FILTER_KEYS
               if isinstance(value := query.get(key), str) and 0 < len(value) <= 256}
    if login:
        filters = {}
        redirect = query.get("redirect-to")
        if isinstance(redirect, str) and 0 < len(redirect) <= 2048:
            decoded = redirect
            for _ in range(3):
                decoded = unquote(decoded)
            try:
                parts = urlsplit(decoded)
            except ValueError:
                parts = None
            if (parts is not None and decoded.startswith("/")
                    and not decoded.startswith("//") and not parts.scheme and not parts.netloc
                    and not any(ord(c) < 32 or ord(c) == 127 or c == "\\" for c in decoded)):
                filters["redirect-to"] = redirect
    return {lang: "?" + urlencode({**filters, "_lang": lang}) for lang in ("en", "ar")}


def set_public_language_context(context):
    """Keep the custom header visible for guests and signed-in website visitors.

    The native login uses a separate site/route-scoped context and this URL builder.
    Source-only tests can invoke page context without an active Frappe request.
    """
    try:
        import frappe
    except ModuleNotFoundError:
        query = {}
    else:
        query = getattr(getattr(frappe, "local", None), "form_dict", {})
    context.language_queries = language_queries(query)
    context.language_js_url = versioned_public_asset("js/language.js")
    # Disable only the native Guest-only picker on pages using this custom header.
    # Do not update Website Settings or native authentication templates.
    context.show_language_picker = 0
