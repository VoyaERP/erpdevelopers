#!/usr/bin/env bash
# Deploy the ERP Developers Frappe v16 app to an EXISTING, dedicated site.
# Never create/drop sites, change existing core apps, reconfigure Nginx or restart services.
(
  set -Eeuo pipefail
  trap 'echo "INSTALL STOPPED at line $LINENO; inspect the partial state. Never auto-delete the site or DB." >&2' ERR

  export PATH="$HOME/.local/bin:$PATH"
  export GIT_TERMINAL_PROMPT=0

  SITE="erp-developers.com"
  BENCH="/data/frappe/frappe-bench"
  if [ -n "${ERPDEV_BENCH:-}" ]; then BENCH="$ERPDEV_BENCH"; fi
  APP="$BENCH/apps/erpdevelopers"
  REPO="https://github.com/VoyaERP/erpdevelopers.git"
  REF="version-16"

  echo "=== Host / identity / site safety ==="
  case "$(uname -n)" in
    erptest-lightnode|erptest-lightnode.*) ;;
    *) echo "STOP: wrong server (expected erptest-lightnode)"; exit 2 ;;
  esac
  test "$(id -u)" -ne 0 || { echo "STOP: never run as root"; exit 2; }
  command -v bench >/dev/null || { echo "STOP: bench CLI unavailable"; exit 2; }
  command -v git >/dev/null || { echo "STOP: git unavailable"; exit 2; }
  test -d "$BENCH/apps/frappe" && test -d "$BENCH/sites" || {
    echo "STOP: expected Frappe Bench not found at $BENCH"; exit 2;
  }
  test -f "$BENCH/sites/$SITE/site_config.json" || {
    echo "STOP: target site's site_config.json missing. This is for an EXISTING site only."; exit 2;
  }

  cd "$BENCH"
  bench version
  bench version | grep -Eq '^frappe[[:space:]]+16\.' || {
    echo "STOP: Frappe version 16 required"; exit 2;
  }

  echo "=== Installed apps (before) ==="
  installed_apps="$(bench --site "$SITE" list-apps)"
  printf '%s\n' "$installed_apps"
  if printf '%s\n' "$installed_apps" | grep -Eq '^erpdevelopers([[:space:]]|$)'; then
    echo "STOP: erpdevelopers already installed; use update_erptest_lightnode.sh instead."
    exit 2
  fi

  free_kib="$(df -Pk "$BENCH" | awk 'NR==2 {print $4}')"
  test -n "$free_kib" && test "$free_kib" -ge $((4 * 1024 * 1024)) || {
    echo "STOP: less than 4 GiB disk free before backup/app install"; exit 2;
  }

  echo "=== Verify anonymous public GitHub access ==="
  remote_sha="$(git ls-remote --exit-code "$REPO" "refs/heads/$REF" | awk 'NR==1 {print $1}')"
  test -n "$remote_sha" || { echo "STOP: public version-16 branch unavailable"; exit 2; }
  echo "Desired source commit: $remote_sha"

  if [ -e "$APP" ]; then
    test -d "$APP/.git" || { echo "STOP: app directory exists but is not Git"; exit 2; }
    test -z "$(git -C "$APP" status --porcelain)" || {
      echo "STOP: app checkout is dirty. Preserve local changes."; exit 2;
    }
    test "$(git -C "$APP" branch --show-current)" = "$REF" || {
      echo "STOP: existing app checkout is not on version-16"; exit 2;
    }
    # Bench default clone uses 'upstream'; manual clones usually use 'origin'.
    # Verify either without rewriting remote settings.
    source_remote=""
    for name in upstream origin; do
      if [ "$(git -C "$APP" remote get-url "$name" 2>/dev/null || true)" = "$REPO" ]; then
        source_remote="$name"
        break
      fi
    done
    test -n "$source_remote" || {
      echo "STOP: no approved public HTTPS remote found on the app checkout"; exit 2;
    }
    test "$(git -C "$APP" rev-parse HEAD)" = "$remote_sha" || {
      echo "STOP: existing app checkout is not at public branch HEAD; inspect before changing"; exit 2;
    }
  fi

  echo "=== Back up existing site's database + public/private files ==="
  bench --site "$SITE" backup --with-files
  test -d "$BENCH/sites/$SITE/private/backups" || {
    echo "STOP: backup directory not found"; exit 3;
  }
  find "$BENCH/sites/$SITE/private/backups" -maxdepth 1 -type f -name '*.sql.gz' -print -quit | grep -q . || {
    echo "STOP: database backup file not found"; exit 3;
  }
  echo "Backup available under sites/$SITE/private/backups"
  free_kib="$(df -Pk "$BENCH" | awk 'NR==2 {print $4}')"
  test -n "$free_kib" && test "$free_kib" -ge $((2 * 1024 * 1024)) || {
    echo "STOP: less than 2 GiB remaining after backup; abort app install"; exit 3;
  }

  echo "=== Install public app checkout if absent ==="
  if [ ! -e "$APP" ]; then
    bench get-app --branch "$REF" "$REPO"
  fi
  test -d "$APP/.git" || { echo "STOP: app checkout missing after get-app"; exit 3; }
  test "$(git -C "$APP" rev-parse HEAD)" = "$remote_sha" || {
    echo "STOP: checkout SHA differs from verified remote branch"; exit 3;
  }

  echo "=== Source-only regression checks ==="
  "$BENCH/env/bin/python" -m unittest discover -s "$APP/tests" -v
  if command -v node >/dev/null 2>&1; then
    node --check "$APP/erpdevelopers/public/js/login_chrome.js"
  fi

  echo "=== Install ERP Developers on existing site ==="
  bench --site "$SITE" install-app erpdevelopers
  bench --site "$SITE" migrate

  echo "=== Apply requested ERP Developers website/home branding ==="
  # WARNING: intentional site-specific edit to Website Settings (home_page, logo, favicon).
  bench --site "$SITE" execute erpdevelopers.site_setup.configure_website
  bench build --app erpdevelopers
  bench --site "$SITE" clear-cache
  bench --site "$SITE" clear-website-cache

  echo "=== Installed apps (after) ==="
  bench --site "$SITE" list-apps
  echo "Source commit: $(git -C "$APP" rev-parse HEAD)"
  echo "Installed on existing site: $SITE"
  echo "Nginx, HTTPS, DNS and shared service reloads are NOT handled here."
)
