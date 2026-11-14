"""Read-only public views of explicitly published ERP Developers Desk content."""
from erpdevelopers.catalog_rules import external_https_url


def public_playlists():
    import frappe

    items = frappe.get_all(
        "ERP Developers Playlist",
        filters={"published": 1},
        fields=["title", "title_ar", "topic", "level", "language",
                "description", "playlist_url", "playlist_id"],
        order_by="sort_order asc, modified desc",
        limit_page_length=60,
    )
    # Treat record URLs as untrusted even after saving: defense in depth.
    from erpdevelopers.catalog_rules import youtube_playlist_id

    result = []
    for item in items:
        try:
            list_id = youtube_playlist_id(item.playlist_url)
        except ValueError:
            continue
        entry = dict(item)
        entry["watch_url"] = f"https://www.youtube.com/playlist?list={list_id}"
        result.append(entry)
    return result


def public_resources():
    import frappe

    rows = frappe.get_all(
        "ERP Developers Resource",
        filters={"published": 1},
        fields=["title", "title_ar", "topic", "summary", "editorial_note",
                "language", "source_kind", "external_url", "source_name", "web_page"],
        order_by="sort_order asc, modified desc",
        limit_page_length=60,
    )
    internal = {r.web_page for r in rows if r.source_kind == "Original Article" and r.web_page}
    published_pages = {}
    if internal:
        pages = frappe.get_all(
            "Web Page",
            filters={"name": ["in", sorted(internal)], "published": 1},
            fields=["name", "route"],
        )
        published_pages = {p.name: p.route for p in pages if p.route}

    result = []
    for row in rows:
        item = dict(row)
        if item["source_kind"] == "Original Article":
            route = published_pages.get(item["web_page"])
            if not route or route.lstrip("/").startswith(("desk/", "app/", "login", "api/")):
                continue
            item["href"] = "/" + route.strip("/")
            item["external"] = False
        else:
            try:
                item["href"] = external_https_url(item["external_url"])
            except ValueError:
                continue
            item["external"] = True
        result.append(item)
    return result
