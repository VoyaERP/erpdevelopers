#!/usr/bin/env bash
# Install on a new erptest-lightnode Frappe v16 site only; no shared upgrades.
(
  set -Eeuo pipefail
  trap 'echo "STOP at line $LINENO. Inspect partial site; no automatic deletion." >&2' ERR

  export PATH="$HOME/.local/bin:$PATH"
  SITE="erp-developers.com"
  BENCH="${BENCH:-/data/frappe/frappe-bench}"
  APP="$BENCH/apps/erpdevelopers"
  REPO="https://github.com/VoyaERP/erpdevelopers.git"

  case "$(uname -n)" in
    erptest-lightnode|erptest-lightnode.*) ;;
    *) echo "STOP: run only on erptest-lightnode"; exit 2 ;;
  esac
  test "$(id -u)" != "0" || { echo "STOP: do not use root"; exit 2; }
  command -v bench >/dev/null
  test -d "$BENCH/apps/frappe" && test -d "$BENCH/sites" || {
    echo "STOP: existing Frappe Bench not found"; exit 2;
  }
  test ! -e "$BENCH/sites/$SITE" || {
    echo "STOP: target site exists. Use update flow; never overwrite."; exit 2;
  }

  cd "$BENCH"
  bench version
  bench version | grep -Eq '^frappe[[:space:]]+16\.' || {
    echo "STOP: Frappe 16 required"; exit 2;
  }
  df -h .
  free_kib="$(df -Pk . | awk 'NR==2 {print $4}')"
  test -n "$free_kib" && test "$free_kib" -ge $((3 * 1024 * 1024)) || {
    echo "STOP: less than 3GiB free disk"; exit 2;
  }
  # No SSH deploy keys or stored HTTPS tokens. The app issues a short-lived
  # installation token for this one repository only.
  source "$(dirname "${BASH_SOURCE[0]}")/github_app_auth.sh"
  erpdev_enable_github_app_git
  git ls-remote --exit-code "$REPO" refs/heads/version-16 >/dev/null || {
    echo "STOP: GitHub App cannot read VoyaERP/erpdevelopers." >&2
    echo "Verify app installation, Contents:read, app ID and PEM ownership." >&2
    exit 3
  }

  if [ -e "$APP" ]; then
    test -d "$APP/.git" || { echo "STOP: app path is not a checkout"; exit 2; }
    test -z "$(git -C "$APP" status --porcelain)" || { echo "STOP: app is dirty"; exit 2; }
    test "$(git -C "$APP" branch --show-current)" = version-16 || {
      echo "STOP: unexpected app branch"; exit 2;
    }
    # Existing SSH remotes are NOT rewritten automatically.
    if ! git -C "$APP" remote -v | grep -Fq "$REPO"; then
      echo "STOP: existing app must use its HTTPS GitHub remote (no SSH URL)." >&2
      exit 2
    fi
  else
    bench get-app --branch version-16 "$REPO"
  fi

  # Interactive prompts keep DB and Administrator credentials out of Git.
  bench new-site "$SITE" --db-type mariadb
  bench --site "$SITE" install-app erpdevelopers
  bench --site "$SITE" migrate
  bench --site "$SITE" execute erpdevelopers.site_setup.configure_website
  bench build --app erpdevelopers
  "$BENCH/env/bin/python" -m unittest discover -s "$APP/tests" -v
  bench --site "$SITE" clear-cache
  bench --site "$SITE" clear-website-cache
  bench --site "$SITE" list-apps
  echo "Site prepared: $SITE"
  echo "DNS, TLS, nginx and Bench service restarts require separate review."
)
