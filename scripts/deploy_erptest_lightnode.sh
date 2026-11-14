#!/usr/bin/env bash
# Complete release runner. Reuse the backup/test/migration updater; do not duplicate it.
# Run a saved copy outside the checkout with an exact EXPECTED_SHA.
set -Eeuo pipefail
export PATH="$HOME/.local/bin:$PATH"
SITE="erp-developers.com"
BENCH="${BENCH:-/data/frappe/frappe-bench}"
APP="$BENCH/apps/erpdevelopers"
WEB="frappe-bench-web:frappe-bench-frappe-web"
EXPECTED_SHA="${EXPECTED_SHA:-}"
TMP=""
STAGE="preflight"
cleanup() { if [ -n "$TMP" ]; then rm -rf "$TMP"; fi; }
failed() {
  echo "STOP at stage: $STAGE, line $1. No automatic rollback or repeated restart was attempted." >&2
  if [ "$STAGE" = "readiness" ] || [ "$STAGE" = "frontend verification" ]; then
    sudo supervisorctl status "$WEB" || true
    sudo supervisorctl tail "$WEB" stderr || true
  fi
}
trap cleanup EXIT
trap 'failed "$LINENO"' ERR
case "$(uname -n)" in erptest-lightnode|erptest-lightnode.*) ;; *) echo "STOP: wrong host" >&2; exit 2;; esac
test "$(id -u)" -ne 0 || { echo "STOP: run as the Bench owner, not root" >&2; exit 2; }
[[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]] || { echo "STOP: supply a full EXPECTED_SHA" >&2; exit 2; }
test -f "$BENCH/sites/$SITE/site_config.json"
test -d "$APP/.git"
test -x "$BENCH/env/bin/python"
for command in git curl bash sudo; do command -v "$command" >/dev/null; done
cd "$BENCH"
test "$(git -C "$APP" branch --show-current)" = "version-16"
test -z "$(git -C "$APP" status --porcelain)"
REMOTE=""
for candidate in upstream origin; do
  if [ "$(git -C "$APP" remote get-url "$candidate" 2>/dev/null || true)" = "https://github.com/VoyaERP/erpdevelopers.git" ]; then
    REMOTE="$candidate"; break
  fi
done
test -n "$REMOTE"
export GIT_TERMINAL_PROMPT=0
git -C "$APP" fetch "$REMOTE" version-16
test "$(git -C "$APP" rev-parse FETCH_HEAD)" = "$EXPECTED_SHA"
git -C "$APP" merge-base --is-ancestor HEAD "$EXPECTED_SHA"
sudo supervisorctl status "$WEB"
TMP="$(mktemp -d)"
git -C "$APP" show "${EXPECTED_SHA}:scripts/update_erptest_lightnode.sh" > "$TMP/update.sh"
bash -n "$TMP/update.sh"
STAGE="backup, tests and application update"
BENCH="$BENCH" EXPECTED_SHA="$EXPECTED_SHA" bash "$TMP/update.sh"
test "$(git -C "$APP" rev-parse HEAD)" = "$EXPECTED_SHA"
STAGE="web restart"
sudo supervisorctl restart "$WEB"
STAGE="readiness"
echo "=== Check Frappe readiness before frontend verification ==="
# TLS bypass is exclusively for the loopback origin; public checks verify TLS.
curl -q -kfsS --noproxy '*' \
  --resolve "$SITE:443:127.0.0.1" \
  --connect-timeout 3 --max-time 8 \
  --retry 12 --retry-delay 2 --retry-max-time 60 --retry-connrefused \
  "https://$SITE/api/method/ping" -o "$TMP/ping.json"
"$BENCH/env/bin/python" - "$TMP/ping.json" <<'PY'
import json
import sys
from pathlib import Path
try:
    value = json.loads(Path(sys.argv[1]).read_text())
except (OSError, ValueError):
    raise SystemExit("STOP: readiness response is not valid JSON") from None
if not isinstance(value, dict) or value.get("message") != "pong":
    raise SystemExit("STOP: readiness response is not Frappe pong")
PY
STAGE="frontend verification"
BENCH="$BENCH" bash "$APP/scripts/verify_frontend.sh"
curl -q -kfsS --noproxy '*' --resolve "$SITE:443:127.0.0.1" \
  --connect-timeout 3 --max-time 20 "https://$SITE/login?_lang=ar" -o "$TMP/login-ar.html"
"$BENCH/env/bin/python" "$APP/scripts/inspect_arabic_login.py" "$TMP/login-ar.html"
echo "=== Projects, Team Advice and the minimal footer: origin and public HTML ==="
PUBLICATION_DIGEST="$(sha256sum "$APP/erpdevelopers/public/css/publications.css" | cut -c1-16)"
PUBLICATION_CSS="/assets/erpdevelopers/css/publications.css?v=$PUBLICATION_DIGEST"
for route in projects team-advice; do
  for language in en ar; do
    for source in origin public; do
      CURL_EXTRA=()
      if [ "$source" = "origin" ]; then
        CURL_EXTRA=(-k --noproxy '*' --resolve "$SITE:443:127.0.0.1")
      fi
      curl -q -fsS "${CURL_EXTRA[@]}" --connect-timeout 3 --max-time 20 \
        "https://$SITE/$route?_lang=$language" -o "$TMP/publication.html"
      "$BENCH/env/bin/python" "$APP/scripts/inspect_publications.py" "$TMP/publication.html" \
        --route "$route" --language "$language" --stylesheet "$PUBLICATION_CSS"
    done
  done
done
curl -q -fsS --connect-timeout 3 --max-time 20 "https://$SITE$PUBLICATION_CSS" -o "$TMP/publications.css"
cmp -s "$APP/erpdevelopers/public/css/publications.css" "$TMP/publications.css"
echo "PASS: deployed $EXPECTED_SHA, Frappe ready, frontend and Arabic login verified."
echo "PASS: Projects, Team Advice, three footer links and publication asset bytes verified."
