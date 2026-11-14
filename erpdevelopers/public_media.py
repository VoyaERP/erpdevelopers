"""Shared native public-image validation and bounded File projection.

No remote fetch, public/private conversion, file deletion or permission override.
Existing validation message keys are retained to preserve translated errors.
"""
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import warnings

MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 24_000_000
EXTENSIONS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP", ".gif": "GIF"}


def image_path(value):
    """Return one decoded /files filename, never an external/private/arbitrary path."""
    # urlsplit strips some raw control characters; reject them before parsing.
    if (not isinstance(value, str) or not value or len(value) > 1200 or
        value != value.strip() or "\\" in value or any(ord(c) < 32 or ord(c) == 127 for c in value)):
        raise ValueError("Upload a public JPG, PNG, WebP or GIF using Attach Image.")
    try:
        parts = urlsplit(value)
        decoded = unquote(parts.path, errors="strict")
    except (ValueError, UnicodeError):
        raise ValueError("The event image path is invalid.") from None
    if parts.scheme or parts.netloc or parts.query or parts.fragment or not decoded.startswith("/files/"):
        raise ValueError("Event images must be public uploads under /files/, not private files or external URLs.")
    name = decoded[len("/files/"):]
    if (not name or name in {".", ".."} or any(c in name for c in '/\\%<>\"\'`?#:') or
        any(ord(c) < 32 or ord(c) == 127 for c in name) or Path(name).suffix.lower() not in EXTENSIONS):
        raise ValueError("Upload a public JPG, PNG, WebP or GIF using Attach Image.")
    return decoded


def validate_caption(value):
    value = str(value or "").strip()
    if len(value) > 240 or any(ord(c) < 32 for c in value):
        raise ValueError("Image captions must be plain text of at most 240 characters.")
    return value


def public_files(paths):
    """One bounded lookup, always re-checking current File privacy at render time."""
    import frappe
    paths = set(paths)
    if not paths:
        return {}
    candidates = sorted(paths | {quote(p, safe="/-_.~") for p in paths})
    rows = frappe.get_all("File", filters={
        "file_url": ["in", candidates], "is_private": 0, "is_folder": 0,
    }, fields=["name", "file_url", "file_size"], limit_page_length=len(candidates) * 4)
    found = {}
    for row in rows:
        try:
            key = image_path(row.get("file_url"))
            size = int(row.get("file_size") or 0)
        except (ValueError, TypeError):
            continue
        if key in paths and 0 < size <= MAX_BYTES:
            found.setdefault(key, row)
    return found


def verify_public_image(file_doc):
    """Verify local image bytes on save, not on every public directory request."""
    import frappe
    from PIL import Image, UnidentifiedImageError
    file_doc.check_permission("read")
    if file_doc.is_private or file_doc.is_folder:
        raise ValueError("Choose a public image upload; private files are never made public automatically.")
    # Validate URL before get_full_path; do not use get_content, which may fetch URLs.
    relative = image_path(file_doc.file_url)
    base = Path(frappe.get_site_path("public", "files")).resolve()
    path = Path(file_doc.get_full_path()).resolve()
    if not path.is_relative_to(base) or not path.is_file():
        raise ValueError("The uploaded image file is missing or outside the public files folder.")
    if not 0 < path.stat().st_size <= MAX_BYTES:
        raise ValueError("Each event image must be no larger than 5 MB.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                if image.format != EXTENSIONS[Path(relative).suffix.lower()]:
                    raise ValueError("The file contents do not match a supported image format.")
                if image.width * image.height > MAX_PIXELS:
                    raise ValueError("Resize the event image to no more than 24 megapixels.")
                image.verify()
    except (OSError, UnidentifiedImageError, Image.DecompressionBombWarning, Image.DecompressionBombError):
        raise ValueError("The uploaded file is not a valid supported image.") from None


