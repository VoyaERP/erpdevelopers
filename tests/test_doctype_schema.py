"""Offline schema guard: a new table must also remain valid on later migrations.

Frappe v16.56.0 DBTable.validate checks varchar lengths on EXISTING tables.
A first installation can therefore miss metadata that fails during an upgrade.
The isolated MariaDB CI job additionally exercises pinned native Frappe methods.
"""
import json
from pathlib import Path
from unittest import TestCase

from erpdevelopers.catalog_rules import EventLinkError, event_https_url

APP = Path(__file__).resolve().parents[1] / "erpdevelopers"
# From frappe/database/mariadb/mysqlclient.py, MariaDBDatabase.setup_type_map.
VARCHAR_TYPES = frozenset({
    "Data", "Link", "Dynamic Link", "Select", "Read Only", "Color",
    "Icon", "Phone", "Autocomplete",
})


def schemas():
    for path in sorted(APP.glob("**/doctype/*/*.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if schema.get("doctype") == "DocType":
            yield path, schema


class TestDocTypeUpgradeSchema(TestCase):
    def test_all_doctype_varchar_lengths_are_valid_on_existing_tables(self):
        definitions = list(schemas())
        self.assertTrue(definitions)
        checked = 0
        for path, schema in definitions:
            for field in schema.get("fields", []):
                if field.get("fieldtype") not in VARCHAR_TYPES:
                    continue
                with self.subTest(doctype=schema["name"], field=field["fieldname"]):
                    length = int(field.get("length") or 140)
                    self.assertTrue(1 <= length <= 1000, f"{path}: invalid varchar length {length}")
                    checked += 1
        self.assertGreater(checked, 0)

    def test_all_doctype_field_orders_and_child_table_targets_are_valid(self):
        definitions = {schema["name"]: schema for _, schema in schemas()}
        for name, schema in definitions.items():
            fields = schema.get("fields", [])
            with self.subTest(doctype=name):
                names = [field["fieldname"] for field in fields]
                self.assertEqual(len(set(names)), len(names))
                self.assertEqual(schema["field_order"], names)
            for field in fields:
                if field.get("fieldtype") == "Table":
                    with self.subTest(doctype=name, field=field["fieldname"]):
                        self.assertIn(field["options"], definitions)
                        self.assertEqual(definitions[field["options"]].get("istable"), 1)

    def test_both_event_urls_use_nonindexed_text_storage_without_length(self):
        definition = next(schema for _, schema in schemas() if schema["name"] == "ERP Developers Event")
        fields = {field["fieldname"]: field for field in definition["fields"]}
        for key in ("event_url", "source_url"):
            with self.subTest(field=key):
                self.assertEqual(fields[key]["fieldtype"], "Small Text")
                self.assertNotIn("length", fields[key])
                self.assertFalse(fields[key].get("unique"))
                self.assertFalse(fields[key].get("search_index"))
                self.assertNotIn(key, definition.get("search_fields", "").split(","))
        self.assertEqual(fields["event_url"]["reqd"], 1)
        self.assertFalse(fields["source_url"].get("reqd"))
        self.assertNotIn("Guest", {item["role"] for item in definition["permissions"]})

    def test_links_longer_than_varchar_limit_are_preserved_not_truncated(self):
        prefix = "https://events.example.org/?reference="
        for length in (1000, 1001, 1499, 1500):
            value = prefix + "a" * (length - len(prefix))
            for field in ("event_url", "source_url"):
                with self.subTest(length=length, field=field):
                    self.assertEqual(event_https_url(value, fieldname=field), value)

    def test_normalized_url_limit_is_still_enforced(self):
        prefix = "https://events.example.org/"
        for value in (prefix + "a" * (1501 - len(prefix)), prefix + "\u0639" * 250):
            with self.subTest(value_length=len(value)), self.assertRaises(EventLinkError):
                event_https_url(value, fieldname="event_url")

    def test_storage_fix_does_not_weaken_url_security(self):
        for value in ("https://127.0.0.1/", "https://erp-developers.com/desk", "javascript:alert(1)"):
            with self.subTest(value=value), self.assertRaises(EventLinkError):
                event_https_url(value, fieldname="event_url")
