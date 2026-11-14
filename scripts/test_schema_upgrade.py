"""CI-only native Frappe schema validation and real MariaDB URL conversion.

Not a full bench migrate test. Executes Git-blob-pinned native validation/type
functions with a minimal metadata facade, then tests their SQL types in an
isolated database. Never run against a Bench or production database.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATABASE = "erpdevelopers_schema_test"
TABLE = "tabERP Developers Event"
NATIVE = {
    "frappe/database/schema.py": "f4da30150424f4afe9031518880fb18c16720180",
    "frappe/database/mariadb/mysqlclient.py": "bfb95d7c2fdbc83ca3cd8db8297e86ecfe12c310",
}


class AttrDict(dict):
    __getattr__ = dict.get


def native_source(path):
    url = "https://raw.githubusercontent.com/frappe/frappe/v16.56.0/" + path
    with urlopen(url, timeout=30) as response:
        data = response.read(2_000_001)
    if len(data) > 2_000_000:
        raise RuntimeError("Unexpected native source size")
    digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if digest != NATIVE[path]:
        raise RuntimeError("Native source pin mismatch: " + path)
    return ast.parse(data.decode("utf-8"), filename=path)


def select_method(tree, cls, method):
    parent = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == cls)
    return next(node for node in parent.body if isinstance(node, ast.FunctionDef) and node.name == method)


def load_native(db):
    schema = native_source("frappe/database/schema.py")
    mysql = native_source("frappe/database/mariadb/mysqlclient.py")
    definition = next(node for node in schema.body if isinstance(node, ast.FunctionDef) and node.name == "get_definition")
    methods = [select_method(schema, "DBTable", "validate"), definition,
               select_method(mysql, "MariaDBDatabase", "setup_type_map")]

    def throw(message):
        raise ValueError(message)

    shim = SimpleNamespace(db=db, _dict=AttrDict, throw=throw, bold=str,
                           msgprint=lambda message: (_ for _ in ()).throw(AssertionError(message)))
    namespace = {
        "frappe": shim, "_": lambda value: value, "cint": lambda value: int(value or 0),
        "VARCHAR_CAST_PATTERN": re.compile(r"varchar\(([\d]+)\)"),
        "CONFIGURABLE_DECIMAL_TYPES": ("Currency", "Float", "Percent"),
        "DEFAULT_DECIMAL_LENGTH": 21, "DEFAULT_DECIMAL_PRECISION": 9,
    }
    module = ast.Module(body=methods, type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), "<pinned native schema methods>", "exec"), namespace)
    namespace["setup_type_map"](db)
    return namespace


def validate(native, fields, current=None, *, is_new=False, istable=False):
    columns = {field["fieldname"]: AttrDict(field) for field in fields}
    table = SimpleNamespace(doctype="ERP Developers Event", columns=columns,
                            current_columns=current or {}, meta={"istable": istable},
                            is_new=lambda: is_new, setup_table_columns=lambda: None)
    native["validate"](table)


def main():
    if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("ERPDEV_SCHEMA_TEST") != "1":
        raise SystemExit("STOP: isolated GitHub Actions database test only")
    import pymysql
    from erpdevelopers.catalog_rules import event_https_url

    connection = pymysql.connect(host="127.0.0.1", port=3307, user="root",
        password=os.environ["SCHEMA_TEST_PASSWORD"], database=DATABASE,
        charset="utf8mb4", autocommit=True, connect_timeout=10, read_timeout=20, write_timeout=20)
    try:
        def sql(query):
            with connection.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        db = SimpleNamespace(VARCHAR_LEN=140, STANDARD_VARCHAR_COLUMNS=(), CHILD_TABLE_COLUMNS=(), sql=sql)
        native = load_native(db)
        definitions = []
        for path in sorted((ROOT / "erpdevelopers").glob("**/doctype/*/*.json")):
            item = json.loads(path.read_text(encoding="utf-8"))
            if item.get("doctype") == "DocType":
                definitions.append(item)
        assert definitions
        event = next(item for item in definitions if item["name"] == "ERP Developers Event")
        url_fields = [field for field in event["fields"] if field["fieldname"] in ("event_url", "source_url")]
        assert len(url_fields) == 2

        with connection.cursor() as cursor:
            cursor.execute("SELECT DATABASE()")
            assert cursor.fetchone()[0] == DATABASE
            cursor.execute("DROP TABLE IF EXISTS `tabERP Developers Event`")
            cursor.execute("CREATE TABLE `tabERP Developers Event` (`name` varchar(140) PRIMARY KEY, "
                           "`event_url` varchar(1500), `source_url` varchar(1500)) "
                           "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
            prefix = "https://events.example.org/?reference="
            samples = [("short", "https://events.example.org/forum", None),
                       ("empty-source", "https://events.example.org/forum", ""),
                       ("unicode-legacy", "https://events.example.org/\u0639\u0631\u0636", None)]
            for size in (1000, 1001, 1499, 1500):
                value = event_https_url(prefix + "a" * (size - len(prefix)))
                samples.append(("url-" + str(size), value, value))
            cursor.executemany("INSERT INTO `tabERP Developers Event` (`name`,`event_url`,`source_url`) VALUES (%s,%s,%s)", samples)

        def columns():
            with connection.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM `tabERP Developers Event`")
                return {row[0]: {"type": row[1]} for row in cursor.fetchall()}

        def snapshot():
            with connection.cursor() as cursor:
                # HEX proves byte-for-byte equality, not collation-dependent equality.
                cursor.execute("SELECT name, HEX(event_url), HEX(source_url) FROM `tabERP Developers Event` ORDER BY name")
                return cursor.fetchall()

        before = snapshot()
        for field in ("event_url", "source_url"):
            old = [{"fieldname": field, "fieldtype": "Data", "length": 1500}]
            validate(native, old, columns(), is_new=True)
            try:
                validate(native, old, columns())
            except ValueError as exc:
                assert str(exc) == f"Length of {field} should be between 1 and 1000", str(exc)
                print("PASS: native existing-table validator reproduces " + field + " failure", flush=True)
            else:
                raise AssertionError("Old invalid metadata unexpectedly passed native validation")
        for item in definitions:
            validate(native, item.get("fields", []), istable=bool(item.get("istable")))
        print(f"PASS: all {len(definitions)} app DocTypes pass native existing-table metadata validation", flush=True)

        for attempt in (1, 2):
            validate(native, url_fields, columns())
            types = {field["fieldname"]: native["get_definition"](field["fieldtype"], length=field.get("length")) for field in url_fields}
            assert types == {"event_url": "text", "source_url": "text"}, types
            with connection.cursor() as cursor:
                cursor.execute("ALTER TABLE `tabERP Developers Event` MODIFY `event_url` text, MODIFY `source_url` text")
            assert snapshot() == before, "Conversion changed stored URL bytes or NULLs"
            assert all(columns()[field]["type"] == "text" for field in types)
            print(f"PASS: MariaDB conversion pass {attempt} preserves all {len(samples)} rows, long URLs and NULLs", flush=True)
        print("PASS: focused schema upgrade regression; full site migration remains a deployment check", flush=True)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
