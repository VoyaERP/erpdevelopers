#!/usr/bin/env bash
# Guarded site-specific update: no core upgrade, new site or service restart.
(
  set -Eeuo pipefail
  trap 'echo "UPDATE STOPPED at line $LINENO; inspect partial state." >&2' ERR
  export PATH="$HOME/.local/bin:$PATH"

  SITE="erp-developers.com"
  BENCH="${BENCH:-/data/frappe/frappe-bench}"
  APP="$BENCH/apps/erpdevelopers"
  REPO="https://github.com/VoyaERP/erpdevelopers.git"
  EXPECTED_SHA="${EXPECTED_SHA:-}"

  case "$(uname -n)" in erptest-lightnode|erptest-lightnode.*) ;; *) echo "STOP: wrong host"; exit 2;; esac
  test "$(id -u)" -ne 0 || { echo "STOP: do not use root"; exit 2; }
  test -f "$BENCH/sites/$SITE/site_config.json" || { echo "STOP: target site missing"; exit 2; }
  test -d "$APP/.git" || { echo "STOP: existing app checkout missing"; exit 2; }
  if [ -n "$EXPECTED_SHA" ] && ! [[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]; then
    echo "STOP: EXPECTED_SHA must be an exact 40-character commit SHA"; exit 2;
  fi

  cd "$BENCH"
  bench --site "$SITE" list-apps | grep -Eq '^erpdevelopers[[:space:]]' || {
    echo "STOP: app not installed on target site"; exit 2;
  }
  test -z "$(git -C "$APP" status --porcelain)" || { echo "STOP: dirty checkout"; exit 2; }
  test "$(git -C "$APP" branch --show-current)" = "version-16" || {
    echo "STOP: wrong app branch"; exit 2;
  }

  REMOTE=""
  for name in upstream origin; do
    if [ "$(git -C "$APP" remote get-url "$name" 2>/dev/null || true)" = "$REPO" ]; then
      REMOTE="$name"; break
    fi
  done
  test -n "$REMOTE" || { echo "STOP: unexpected GitHub remote"; exit 2; }

  echo "=== Back up target site including all files ==="
  bench --site "$SITE" backup --with-files

  echo "=== Fetch and validate intended release ==="
  export GIT_TERMINAL_PROMPT=0
  git -C "$APP" fetch "$REMOTE" version-16
  TARGET="$(git -C "$APP" rev-parse FETCH_HEAD)"
  CURRENT="$(git -C "$APP" rev-parse HEAD)"
  if [ -n "$EXPECTED_SHA" ] && [ "$TARGET" != "$EXPECTED_SHA" ]; then
    echo "STOP: fetched $TARGET does not match EXPECTED_SHA $EXPECTED_SHA"; exit 3;
  fi
  git -C "$APP" merge-base --is-ancestor "$CURRENT" "$TARGET" || {
    echo "STOP: non-fast-forward update"; exit 3;
  }
  git -C "$APP" merge --ff-only "$TARGET"
  test "$(git -C "$APP" rev-parse HEAD)" = "$TARGET"

  echo "=== Static checks BEFORE database migration ==="
  test -f "$APP/erpdevelopers/modules.txt"
  test -f "$APP/erpdevelopers/patches.txt"
  "$BENCH/env/bin/python" -m compileall -q "$APP/erpdevelopers" "$APP/tests"
  "$BENCH/env/bin/python" -m unittest discover -s "$APP/tests" -v
  if command -v node >/dev/null 2>&1; then
    node --check "$APP/erpdevelopers/public/js/login_chrome.js"
  fi
  APPROVED_SHA="250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d"
  LOGO_SHA="$(sha256sum "$APP/erpdevelopers/public/images/erpdevelopers-selected-logo.png" | cut -d' ' -f1)"
  test "$LOGO_SHA" = "$APPROVED_SHA" || {
    echo "STOP: selected logo does not match approved source"; exit 3;
  }

  echo "=== Apply ONLY target-site changes ==="
  bench --site "$SITE" migrate
  bench --site "$SITE" execute erpdevelopers.site_setup.configure_website
  bench build --app erpdevelopers
  bench --site "$SITE" clear-cache
  bench --site "$SITE" clear-website-cache

  echo "Updated $SITE to ERP Developers commit $TARGET"
  echo "No shared services restarted; reload the web service separately and verify frontend."
)
