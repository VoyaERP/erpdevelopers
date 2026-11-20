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
  RELEASE_BRANCH="${RELEASE_BRANCH:-version-16}"
  ALLOW_BRANCH_SWITCH="${ALLOW_BRANCH_SWITCH:-0}"
  case "$RELEASE_BRANCH" in version-16|production-v16) ;; *) echo "STOP: unsupported release branch"; exit 2;; esac

  case "$(uname -n)" in erptest-lightnode|erptest-lightnode.*) ;; *) echo "STOP: wrong host"; exit 2;; esac
  test "$(id -u)" -ne 0 || { echo "STOP: do not use root"; exit 2; }
  test -f "$BENCH/sites/$SITE/site_config.json" || { echo "STOP: target site missing"; exit 2; }
  test -d "$APP/.git" || { echo "STOP: existing app checkout missing"; exit 2; }
  if ! [[ "$EXPECTED_SHA" =~ ^[0-9a-f]{40}$ ]]; then
    echo "STOP: EXPECTED_SHA must be an exact 40-character commit SHA"; exit 2;
  fi

  cd "$BENCH"
  bench --site "$SITE" list-apps | grep -Eq '^erpdevelopers[[:space:]]' || {
    echo "STOP: app not installed on target site"; exit 2;
  }
  test -z "$(git -C "$APP" status --porcelain)" || { echo "STOP: dirty checkout"; exit 2; }
  CURRENT_BRANCH="$(git -C "$APP" branch --show-current)"

  REMOTE=""
  for name in upstream origin; do
    if [ "$(git -C "$APP" remote get-url "$name" 2>/dev/null || true)" = "$REPO" ]; then
      REMOTE="$name"; break
    fi
  done
  test -n "$REMOTE" || { echo "STOP: unexpected GitHub remote"; exit 2; }

  echo "=== Fetch and validate intended release ==="
  export GIT_TERMINAL_PROMPT=0
  git -C "$APP" fetch "$REMOTE" "$RELEASE_BRANCH"
  TARGET="$(git -C "$APP" rev-parse FETCH_HEAD)"
  CURRENT="$(git -C "$APP" rev-parse HEAD)"
  if [ "$TARGET" != "$EXPECTED_SHA" ]; then
    echo "STOP: fetched $TARGET does not match EXPECTED_SHA $EXPECTED_SHA"; exit 3;
  fi
  git -C "$APP" merge-base --is-ancestor "$CURRENT" "$TARGET" || {
    echo "STOP: non-fast-forward update"; exit 3;
  }
  POLICY_DIR="$(mktemp -d)"
  trap 'rm -rf "$POLICY_DIR"' EXIT
  git -C "$APP" show "${TARGET}:scripts/release_policy.py" > "$POLICY_DIR/policy.py"
  "$BENCH/env/bin/python" "$POLICY_DIR/policy.py" "$CURRENT_BRANCH" "$RELEASE_BRANCH" "$TARGET" --allow-switch "$ALLOW_BRANCH_SWITCH"
  if [ "$CURRENT_BRANCH" != "$RELEASE_BRANCH" ] && git -C "$APP" show-ref --verify --quiet "refs/heads/$RELEASE_BRANCH"; then
    git -C "$APP" merge-base --is-ancestor "$RELEASE_BRANCH" "$TARGET" || {
      echo "STOP: existing production branch diverges from target"; exit 3;
    }
  fi

  echo "=== Back up target site including all files ==="
  bench --site "$SITE" backup --with-files

  if [ "$CURRENT_BRANCH" != "$RELEASE_BRANCH" ]; then
    if git -C "$APP" show-ref --verify --quiet "refs/heads/$RELEASE_BRANCH"; then
      git -C "$APP" switch "$RELEASE_BRANCH"
    else
      git -C "$APP" switch -c "$RELEASE_BRANCH" "$CURRENT"
    fi
  fi
  git -C "$APP" merge --ff-only "$TARGET"
  test "$(git -C "$APP" rev-parse HEAD)" = "$TARGET"
  test "$(git -C "$APP" branch --show-current)" = "$RELEASE_BRANCH"

  echo "=== Static checks BEFORE database migration ==="
  test -f "$APP/erpdevelopers/modules.txt"
  test -f "$APP/erpdevelopers/patches.txt"
  PYTHON="$BENCH/env/bin/python" bash "$APP/scripts/check_source.sh"
  # Native login stays CSS-first; the removed login script must not return.
  test ! -e "$APP/erpdevelopers/public/js/login_chrome.js"
  test ! -e "$APP/tests/login_chrome_dom.test.cjs"
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

  echo "Updated $SITE on $RELEASE_BRANCH to ERP Developers commit $TARGET"
  echo "No shared services restarted; reload the web service separately and verify frontend."
)
