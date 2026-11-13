#!/usr/bin/env bash
# Fast-forward ERP Developers only; does not run bench update or restart.
(
  set -Eeuo pipefail
  trap 'echo "UPDATE STOPPED at line $LINENO. Review partial state." >&2' ERR
  export PATH="$HOME/.local/bin:$PATH"
  SITE="erp-developers.com"
  BENCH="${BENCH:-/data/frappe/frappe-bench}"
  APP="$BENCH/apps/erpdevelopers"

  case "$(uname -n)" in erptest-lightnode|erptest-lightnode.*) ;; *) echo "Wrong host"; exit 2;; esac
  test "$(id -u)" != "0" || { echo "Do not use root"; exit 2; }
  test -d "$BENCH/sites/$SITE" && test -d "$APP/.git" || {
    echo "Site/app missing; use fresh install flow"; exit 2;
  }
  cd "$BENCH"
  bench --site "$SITE" list-apps | grep -q '^erpdevelopers ' || {
    echo "App not installed on target site"; exit 2;
  }
  test -z "$(git -C "$APP" status --porcelain)" || { echo "Dirty app"; exit 2; }
  test "$(git -C "$APP" branch --show-current)" = "version-16" || {
    echo "Wrong app branch"; exit 2;
  }
  REMOTE=""
  for name in origin upstream; do
    if git -C "$APP" remote get-url "$name" 2>/dev/null | grep -Fq 'VoyaERP/erpdevelopers'; then
      REMOTE="$name"
      break
    fi
  done
  test -n "$REMOTE" || { echo "Unexpected Git remote"; exit 2; }
  REPO="https://github.com/VoyaERP/erpdevelopers.git"
  test "$(git -C "$APP" remote get-url "$REMOTE")" = "$REPO" || {
    echo "STOP: HTTPS public origin required. Inspect origin rather than rewriting it automatically." >&2
    exit 2
  }
  echo "=== Verify anonymous public GitHub branch ==="
  export GIT_TERMINAL_PROMPT=0
  git ls-remote --exit-code "$REPO" refs/heads/version-16 >/dev/null || {
    echo "STOP: Cannot read public version-16 branch" >&2
    exit 3
  }
  bench --site "$SITE" backup --with-files
  git -C "$APP" fetch "$REMOTE" version-16
  git -C "$APP" merge --ff-only "$REMOTE/version-16"
  bench --site "$SITE" migrate
  bench --site "$SITE" execute erpdevelopers.site_setup.configure_website
  bench build --app erpdevelopers
  "$BENCH/env/bin/python" -m unittest discover -s "$APP/tests" -v
  bench --site "$SITE" clear-cache
  bench --site "$SITE" clear-website-cache
  echo "Verified app HEAD: $(git -C "$APP" rev-parse HEAD)"
  echo "Review shared service restart separately."
)
