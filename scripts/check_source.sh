#!/usr/bin/env bash
# Source-only checks. No Bench commands, network, database or service mutation.
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python}"
cd "$ROOT"
"$PYTHON" -m compileall -q erpdevelopers tests scripts
while IFS= read -r -d '' script; do bash -n "$script"; done < <(find scripts -name '*.sh' -print0)
"$PYTHON" -m unittest discover -s tests -v
while IFS= read -r -d '' script; do node --check "$script"; done < <(find erpdevelopers -name '*.js' -print0)
node --test tests/test_catalog_player.mjs
"$PYTHON" - <<'CHECK'
from io import BytesIO
from pathlib import Path
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
with Path("erpdevelopers/locale/ar.po").open("rb") as stream:
    catalog = read_po(stream, locale="ar")
errors = list(catalog.check())
if errors:
    raise SystemExit(f"Invalid Arabic catalog: {errors}")
write_mo(BytesIO(), catalog)
print("PASS: native Arabic catalog compiles")
CHECK
