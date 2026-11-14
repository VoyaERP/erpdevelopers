"""Small pure validators shared by Desk models and public catalog rendering.

No external fetches, YouTube scraping or ingestion of external page content.
"""
import ipaddress
import re
from urllib.parse import parse_qs, urlsplit

_PLAYLIST_ID = re.compile(r"^[A-Za-z0-9_-]{12,64}$")
_HOSTS = {"youtube.com", "www.youtube.com", "music.youtube.com"}


def youtube_playlist_id(url: str) -> str:
    """Return one validated YouTube list id, never an embeddable arbitrary URL."""
    value = (url or "").strip()
    if len(value) > 500 or "\\" in value or any(ord(c) < 32 for c in value):
        raise ValueError("Invalid playlist URL")
    try:
        parsed = urlsplit(value)
        query = parse_qs(parsed.query, keep_blank_values=True)
        candidates = query.get("list", [])
        if (parsed.scheme != "https" or parsed.hostname not in _HOSTS
            or parsed.username or parsed.password or parsed.port not in (None, 443)
            or parsed.path != "/playlist" or len(candidates) != 1
            or not _PLAYLIST_ID.fullmatch(candidates[0])):
            raise ValueError("Use a valid HTTPS YouTube playlist link")
        return candidates[0]
    except ValueError:
        raise ValueError("Use a valid HTTPS YouTube playlist link") from None


def external_https_url(url: str) -> str:
    """Validate curated *links* only; never download or parse remote content."""
    value = (url or "").strip()
    if len(value) > 1500 or not value or any(ord(c) < 32 for c in value) or "\\" in value:
        raise ValueError("External link must be a valid HTTPS URL")
    try:
        p = urlsplit(value)
        host = p.hostname or ""
        if (p.scheme != "https" or not host or p.username or p.password
            or p.port not in (None, 443) or host.endswith((".local", ".internal"))
            or host in {"localhost", "erp-developers.com"} or "." not in host
            or host.startswith(".") or host.endswith(".")):
            raise ValueError()
        try:
            ipaddress.ip_address(host)
        except ValueError:
            pass  # DNS hostname rather than an IP literal.
        else:
            raise ValueError()
        return value
    except ValueError:
        raise ValueError("Use an external HTTPS domain; private addresses are not allowed") from None
