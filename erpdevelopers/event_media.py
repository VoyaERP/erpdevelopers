"""Event-specific gallery assembly using the shared public-image boundary."""
from urllib.parse import quote

# Compatibility aliases preserve existing event callers and test patch points.
from erpdevelopers.public_media import (
    EXTENSIONS, MAX_BYTES, MAX_PIXELS, image_path,
    public_files as _public_files,
    validate_caption as _caption,
    verify_public_image as _verify_file,
)

EVENT_DOCTYPE = "ERP Developers Event"
IMAGE_DOCTYPE = "ERP Developers Event Image"
MAX_GALLERY = 8


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
