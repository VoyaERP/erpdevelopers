"""Shared catalog mechanics, not authorization or business publication rules.

Callers own fixed DocType/field lists and mandatory audience filters. This module
must never become an unrestricted public query endpoint.
"""
from collections.abc import Iterable


def schema_status(doctype: str, fields: Iterable[str]) -> dict:
    """Avoid querying missing columns during an interrupted site migration.

    Do not cache schema state across a migration and do not swallow database
    failures: only an absent table/column becomes an empty public directory.
    """
    import frappe

    fields = tuple(fields)
    if not frappe.db.table_exists(doctype, cached=False):
        return {"table_present": False, "missing_columns": list(fields)}
    required = set(fields) | {"published", "sort_order", "modified"}
    existing = set(frappe.db.get_table_columns(doctype))
    return {
        "table_present": True,
        "missing_columns": sorted(required - existing),
    }


def page_number(value, *, maximum: int = 1000) -> int:
    """Normalize an untrusted page value; callers retain their existing caps."""
    if maximum < 1:
        raise ValueError("Page maximum must be positive")
    try:
        return max(1, min(maximum, int(str(value or "1"))))
    except (TypeError, ValueError):
        return 1
