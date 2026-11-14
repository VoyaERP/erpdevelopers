"""Pure editorial validation, independent of Frappe, files and page rendering."""
from erpdevelopers.taxonomy import TOPICS

KINDS = {"projects": "Project", "team-advice": "Team Advice"}
TEXT_LIMITS = {
    "title": 200, "title_ar": 200, "summary": 600, "summary_ar": 600,
    "content": 12000, "content_ar": 12000, "industry": 120, "technologies": 240,
    "author_name": 120, "author_name_ar": 120, "cover_caption": 240, "cover_caption_ar": 240,
}


def normalize_publication(data):
    """Pure validation; content stays plain text and is escaped in the template."""
    kind = data.get("publication_type")
    if kind not in KINDS.values() or data.get("topic") not in TOPICS:
        raise ValueError("Select a valid publication type and topic.")
    result = {}
    for field, limit in TEXT_LIMITS.items():
        value = str(data.get(field) or "").strip()
        if len(value) > limit or any(ord(c) < 32 and c not in "\n\r\t" for c in value):
            raise ValueError("Keep publication text within the field limits and remove control characters.")
        if field not in {"summary", "summary_ar", "content", "content_ar"} and any(c in value for c in "\n\r\t"):
            raise ValueError("Keep publication text within the field limits and remove control characters.")
        result[field] = value
    if not all(result[k] for k in ("title", "summary", "content")):
        raise ValueError("Enter the publication title, summary and content.")
    # Native Check fields may arrive as JSON booleans, integers or form strings.
    if data.get("published") in (1, "1"):
        if data.get("public_reviewed") not in (1, "1"):
            raise ValueError("Review the content and confirm public sharing before publishing.")
        if kind == "Team Advice" and not result["author_name"]:
            raise ValueError("Enter a public author name before publishing team advice.")
    return result


