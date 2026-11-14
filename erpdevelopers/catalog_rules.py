"""Pure URL rules for curated links. Never resolve DNS or fetch remote content."""
import ipaddress
import posixpath
import re
from urllib.parse import parse_qs, quote, unquote, urlsplit, urlunsplit

_PLAYLIST_ID = re.compile(r"^[A-Za-z0-9_-]{12,64}$")
_HOSTS = {"youtube.com", "www.youtube.com", "music.youtube.com"}
_SITE_HOSTS = {"erp-developers.com", "www.erp-developers.com"}
_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.I)
_LOCAL_SUFFIXES = (".local", ".internal", ".localhost", ".lan", ".home", ".corp", ".test", ".invalid")
_PRIVATE_ROUTES = {"app", "desk", "api", "login", "private", "me"}


class EventLinkError(ValueError):
    """Keep the field label separate so native Frappe can translate both parts."""
    def __init__(self, fieldname, message):
        self.fieldname = fieldname
        super().__init__(message)


def youtube_playlist_id(url: str) -> str:
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
            raise ValueError()
        return candidates[0]
    except ValueError:
        raise ValueError("Use a valid HTTPS YouTube playlist link") from None


def _public_https_url(url, *, normalize=False):
    if not isinstance(url, str):
        raise ValueError("Enter a public website URL.")
    value = url.strip()
    if not value or len(value) > 1500 or "\\" in value or any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise ValueError("Enter a valid website URL without control characters or backslashes.")
    if normalize:
        if value.startswith("//"):
            value = "https:" + value
        elif not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", value):
            value = "https://" + value
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        port = parsed.port
    except ValueError:
        raise ValueError("The website hostname or port is invalid.") from None
    if parsed.scheme not in (("http", "https") if normalize else ("https",)):
        raise ValueError("Use HTTPS or paste the public website domain.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Website URLs cannot contain a username or password.")
    if port not in (None, 443) and not (normalize and parsed.scheme == "http" and port == 80):
        raise ValueError("Use the standard HTTPS website port.")
    try:
        host = host.encode("idna").decode("ascii").lower()
    except UnicodeError:
        raise ValueError("The website hostname is invalid.") from None
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("Use a public domain name, not an IP address.")
    labels = host.split(".")
    # Browsers accept shortened/octal/hex IPv4 forms that ipaddress does not.
    numeric_end = re.fullmatch(r"(?:[0-9]+|0x[0-9a-f]+)", labels[-1], re.I)
    if (not host or len(host) > 253 or len(labels) < 2 or numeric_end or
        any(not _LABEL.fullmatch(label) for label in labels) or
        not re.search(r"[a-z]", labels[-1], re.I)):
        raise ValueError("Enter a valid public domain, for example www.example.com.")
    if host.endswith(_LOCAL_SUFFIXES):
        raise ValueError("Local and private-network hostnames are not allowed.")
    if host in _SITE_HOSTS:
        if not normalize:
            raise ValueError("Use an external website for this resource.")
        # Our own public pages are valid event sources; administrative URLs are not.
        decoded = parsed.path
        for _ in range(4):
            next_value = unquote(decoded)
            if next_value == decoded:
                break
            decoded = next_value
        if "\\" in decoded or "%" in decoded or any(ord(c) < 32 for c in decoded):
            raise ValueError("Use a public page, not a private or administrative route.")
        cleaned = posixpath.normpath("/" + decoded.lstrip("/"))
        first = cleaned.lstrip("/").split("/", 1)[0].casefold()
        if first in _PRIVATE_ROUTES:
            raise ValueError("Use a public page, not a private or administrative route.")
    parts = [parsed.path, parsed.query, parsed.fragment]
    if any(re.search(r"%(?![0-9A-Fa-f]{2})", part) for part in parts):
        raise ValueError("The URL contains an invalid percent-encoded character.")
    result = urlunsplit(("https", host,
        quote(parsed.path, safe="/%:@!$&'()*+,;=-._~"),
        quote(parsed.query, safe="/%?:@!$&'()*+,;=-._~"),
        quote(parsed.fragment, safe="/%?:@!$&'()*+,;=-._~")))
    if len(result) > 1500:
        raise ValueError("The website URL is too long.")
    return result


def external_https_url(url: str) -> str:
    """Strict HTTPS links used by the existing resource catalog."""
    return _public_https_url(url)


def event_https_url(url: str, fieldname=None) -> str:
    """Normalize pasted event domains/HTTP links to HTTPS, without fetching them.

    This validates link syntax, not DNS reachability, TLS support or redirects.
    It is not an SSRF guard for future server-side importers.
    """
    try:
        return _public_https_url(url, normalize=True)
    except ValueError as exc:
        if fieldname:
            raise EventLinkError(fieldname, str(exc)) from None
        raise
