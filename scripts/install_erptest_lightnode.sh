#!/usr/bin/env bash
# Install on a new erptest-lightnode Frappe v16 site only; no shared upgrades.
(
  set -Eeuo pipefail
  trap 'echo "STOP at line $LINENO. Inspect partial site; no automatic deletion." >&2' ERR

  export PATH="$HOME/.local/bin:$PATH"
  SITE="erp-developers.com"
  BENCH="$HOME/frappe-bench"
  APP="$BENCH/apps/erpdevelopers"
  REPO="git@github.com:VoyaERP/erpdevelopers.git"

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
  git ls-remote --exit-code "$REPO" refs/heads/version-16 >/dev/null || {
    echo "STOP: private GitHub repository access not configured"; exit 3;
  }

  if [ -e "$APP" ]; then
    test -d "$APP/.git" || { echo "STOP: app path is not a checkout"; exit 2; }
    test -z "$(git -C "$APP" status --porcelain)" || { echo "STOP: app is dirty"; exit 2; }
    test "$(git -C "$APP" branch --show-current)" = version-16 || {
      echo "STOP: unexpected app branch"; exit 2;
    }
    git -C "$APP" remote -v | grep -Fq 'VoyaERP/erpdevelopers' || {
      echo "STOP: unexpected app Git remote"; exit 2;
    }
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
