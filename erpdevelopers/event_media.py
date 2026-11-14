"""Public event images, using native File records. No remote fetch or privacy changes."""
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
import warnings

EVENT_DOCTYPE = "ERP Developers Event"
IMAGE_DOCTYPE = "ERP Developers Event Image"
MAX_GALLERY = 8
MAX_BYTES = 5 * 1024 * 1024
MAX_PIXELS = 24_000_000
EXTENSIONS = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP", ".gif": "GIF"}


def image_path(value):
    """Return one decoded /files filename, never an external/private/arbitrary path."""
    if not isinstance(value, str) or not value or len(value) > 1200:
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


def _caption(value):
    value = str(value or "").strip()
    if len(value) > 240 or any(ord(c) < 32 for c in value):
        raise ValueError("Image captions must be plain text of at most 240 characters.")
    return value


def _public_files(paths):
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


def _verify_file(file_doc):
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


def validate_event_media(doc):
    """Run within native Document.validate; does not publish, upload or delete files."""
    import frappe
    rows = doc.get("event_images") or []
    if len(rows) > MAX_GALLERY:
        raise ValueError("Add no more than 8 gallery images per event.")
    refs = []
    if doc.get("cover_image"):
        refs.append(image_path(doc.get("cover_image")))
    for key in ("cover_caption", "cover_caption_ar"):
        doc.set(key, _caption(doc.get(key)))
    gallery = set()
    for row in rows:
        path = image_path(row.get("image"))
        if path in gallery:
            raise ValueError("The event gallery contains the same image more than once.")
        gallery.add(path)
        refs.append(path)
        for key in ("caption", "caption_ar"):
            row.set(key, _caption(row.get(key)))
    records = _public_files(refs)
    for path in set(refs):
        record = records.get(path)
        if not record:
            raise ValueError("Choose an existing public image up to 5 MB; private or missing files cannot be displayed.")
        _verify_file(frappe.get_doc("File", record["name"]))
    doc.set("has_event_images", int(bool(rows)))


def attach_public_event_media(entries):
    """Add a safe cover/gallery to the already filtered published event page.

    Only the supplied page's parent IDs are queried. Private File references are
    omitted even if a record was made private after its event was published.
    """
    import frappe
    if not entries:
        return
    candidates = {entry["name"]: [] for entry in entries}
    for entry in entries:
        entry["media"] = {"cover": None, "gallery": []}
        if entry.get("cover_image"):
            candidates[entry["name"]].append({"image": entry["cover_image"],
                "caption": entry.get("cover_caption"), "caption_ar": entry.get("cover_caption_ar")})
    parents = [e["name"] for e in entries if e.get("has_event_images")]
    if parents and frappe.db.table_exists(IMAGE_DOCTYPE):
        rows = frappe.get_all(IMAGE_DOCTYPE, filters={"parent": ["in", parents],
            "parenttype": EVENT_DOCTYPE, "parentfield": "event_images"},
            fields=["parent", "image", "caption", "caption_ar", "idx"],
            order_by="parent asc, idx asc", limit_page_length=len(parents) * MAX_GALLERY)
        for row in rows:
            if row["parent"] in candidates and len(candidates[row["parent"]]) < MAX_GALLERY + 1:
                candidates[row["parent"]].append(row)
    paths = set()
    for photos in candidates.values():
        for photo in photos:
            try:
                photo["path"] = image_path(photo.get("image"))
                paths.add(photo["path"])
            except ValueError:
                continue
    records = _public_files(paths)
    for entry in entries:
        photos, seen = [], set()
        for photo in candidates[entry["name"]]:
            path = photo.get("path")
            if path not in records or path in seen:
                continue
            seen.add(path)
            photos.append({"url": quote(path, safe="/-_.~"),
                "caption": str(photo.get("caption") or "")[:240],
                "caption_ar": str(photo.get("caption_ar") or "")[:240]})
        if photos:
            entry["media"] = {"cover": photos[0], "gallery": photos[1:MAX_GALLERY + 1]}
