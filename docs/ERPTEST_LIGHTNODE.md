# ERP Developers — deployment on erptest-lightnode

- **Public domain:** https://erp-developers.com
- **Host:** erptest-lightnode
- **Repository:** https://github.com/VoyaERP/erpdevelopers (public)
- **Branch:** version-16
- **App:** erpdevelopers
- **Site:** erp-developers.com
- **Expected Bench:** /data/frappe/frappe-bench — observed previously; verify on the server
- **Status:** Existing erp-developers.com Frappe 16 + ERPNext 16 site observed by operator; app absent. Existing-site installer added. No install, DNS/TLS change or live browser UAT confirmed.

## Observed site state — existing Frappe 16 site (2026-11-14)

The operator connected via SSH and confirmed:

- Existing `sites/erp-developers.com` directory: **yes** (new-site installer correctly refused to run)
- `bench --site erp-developers.com list-apps`: Frappe **16.56.0**, ERPNext **16.55.0**, **no erpdevelopers app installed**
- `apps/erpdevelopers`: absent
- `sudo nginx -t`: syntax OK. **No evidence yet** of domain-specific vhost/DNS/TLS or actual HTTP routing.

**Use the EXISTING-site installer below. Do not run** `bench new-site`, do not delete the site, and do not use the existing-app *update* helper until ERP Developers is installed.

### Existing site, app NOT installed — correct initial deployment

Run these commands on erptest-lightnode as the Bench owner. They first clone the public source, then the guarded script backs up the existing site with files, downloads the app if necessary, tests it, installs it into the existing site and configures ERP Developers branding. It never recreates the site or alters Nginx.

~~~bash
(
  set -Eeuo pipefail
  export PATH="$HOME/.local/bin:$PATH"
  REPO="https://github.com/VoyaERP/erpdevelopers.git"
  SRC="$HOME/erpdevelopers-deploy-source"
  if [ ! -e "$SRC" ]; then
    git clone --branch version-16 --single-branch "$REPO" "$SRC"
  else
    test -d "$SRC/.git"
    test -z "$(git -C "$SRC" status --porcelain)"
    test "$(git -C "$SRC" branch --show-current)" = "version-16"
    test "$(git -C "$SRC" remote get-url origin)" = "$REPO"
    git -C "$SRC" pull --ff-only origin version-16
  fi
  bash "$SRC/scripts/install_existing_site_erptest_lightnode.sh"
)
~~~

**Important:** The existing-site script applies changes to the target site's **Website Settings** (home page, logo, favicon and language picker) after a successful backup. If that existing site carries another organization's live public website, do not run it until the intended ownership of the public pages has been reviewed. Existing ERPNext transactions remain untouched; page settings do change as requested. A backup is not a substitute for a confirmed restore plan.

Once installed, use the *update existing ERP Developers app* procedure later in this document. If the script stops partway through, inspect the partial app/site state; do not rerun fresh-site installer or recreate the DB.

## Login architecture (Green Box method)

The previous Green Box implementation preserved the **native Frappe login form**, password reset, signup configuration, social login and 2FA. ERP Developers follows this same safe approach: page-scoped CSS and an idempotent website header/footer script. The intersecting background is a local original SVG, not a new login template or authentication form. All auth/session/OTP logic stays in Frappe 16. The original form is not reparented and credentials never pass through custom JavaScript.

Arabic and English site chrome follow the server-rendered Frappe HTML language. The site-scoped setup enables Frappe's own language picker; the native picker is moved into the branded header, without replacing its event handlers. The app does not overwrite the Frappe language or localize validation/status messages with brittle JavaScript replacements.

## 1. Read-only preflight on erptest-lightnode

SSH into the target server as the Bench owner, **not root**, then run:

~~~bash
(
  set +e
  export PATH="$HOME/.local/bin:$PATH"
  echo "=== Host / user ==="
  uname -n
  id -un
  echo "=== Existing Bench ==="
  BENCH="/data/frappe/frappe-bench"
  test -d "$BENCH/apps/frappe" || {
    echo "STOP: Check the real Bench path; do not guess"; exit 1;
  }
  cd "$BENCH" || exit 1
  bench version
  git -C apps/frappe branch --show-current
  df -h .
  echo "=== Existing site folder names only ==="
  find sites -mindepth 2 -maxdepth 2 -name site_config.json -type f -printf '%h\n'
  test ! -e "sites/erp-developers.com" && echo "Target absent: fresh-site flow" || echo "Target exists: distinguish app-not-installed from app-installed"
  echo "=== Proxy tooling ==="
  command -v nginx || true
  command -v certbot || true
  echo "=== Public GitHub source ==="
  git ls-remote https://github.com/VoyaERP/erpdevelopers.git refs/heads/version-16
)
~~~

Do not print passwords, site_config.json, DB backups or live application data. The installer refuses a wrong hostname, root user, non-Frappe-16 Bench, missing Bench, existing target site, dirty app checkout or less than **3 GiB available disk**. A successful preflight does not prove all Frappe 16 dependencies are compatible.

## 2. Fresh installation from the public repository

Only run when the previous checks match the intended environment and the target site **does not exist**:

~~~bash
(
  set -Eeuo pipefail
  export PATH="$HOME/.local/bin:$PATH"
  SRC="$HOME/erpdevelopers-deploy-source"
  test ! -e "$SRC" || {
    echo "STOP: deployment source exists. Inspect it; do not overwrite."; exit 2;
  }
  git clone --branch version-16 --single-branch \
    https://github.com/VoyaERP/erpdevelopers.git "$SRC"

  BENCH="/data/frappe/frappe-bench" bash "$SRC/scripts/install_erptest_lightnode.sh"
)
~~~

The installer uses anonymous read-only HTTPS, checks the public branch and Bench, installs the app on a **new Frappe 16 site** only, configures that site's home page and logo, builds the app assets, runs source-only unit tests and clears the site's caches. It prompts interactively for MariaDB administrative and site Administrator passwords. No values are embedded in the code.

It does **not** run bench update, change the shared Bench default site, rewrite Nginx, provision TLS, restart services, or touch other sites. If it fails after creating a site/database, inspect the partial state before retrying.

## 3. DNS, reverse proxy, SSL (operator-reviewed)

1. Verify the server's public IP and external ingress, then point the apex DNS A record for erp-developers.com to that verified address. Add AAAA only when IPv6 is actually configured.
2. Inspect how this server manages Nginx/Frappe domains and **back up the existing proxy configuration**. Adding a vhost or running bench setup nginx may affect all other sites. Do not execute an unreviewed automatic rewrite.
3. Provision a trusted TLS certificate through the server's existing process. For Cloudflare-proxied traffic use **Full (strict)** and bypass caching for /login, /app, /api and /socket.io. Never use Flexible for a login site.
4. Once HTTPS is verified, set the site-specific absolute URL:

~~~bash
cd /data/frappe/frappe-bench
bench --site erp-developers.com set-config host_name https://erp-developers.com
~~~

A shared Bench process restart might be required for the new hooks to load. Schedule and verify that separately rather than blindly restarting multi-site services.

## 4. Verification after installation, routing and TLS

~~~bash
cd /data/frappe/frappe-bench

bench --site erp-developers.com list-apps

bench --site erp-developers.com execute \
  frappe.db.get_single_value --args '["Website Settings","home_page"]'

test -r sites/assets/erpdevelopers/css/login.css
test -r sites/assets/erpdevelopers/images/login-network.svg

curl -I https://erp-developers.com/
curl -I https://erp-developers.com/login
curl -I https://erp-developers.com/assets/erpdevelopers/css/login.css
curl -I https://erp-developers.com/assets/erpdevelopers/js/login_chrome.js
curl -I https://erp-developers.com/assets/erpdevelopers/images/login-network.svg
~~~

The public curl checks only pass once DNS and HTTPS are live. Browser UAT must check desktop/tablet/mobile breakpoints, Arabic/English Frappe locales, one header/footer, intact Frappe login fields, forgot-password, wrong password, 2FA, optional social login and no Console errors. Check existing sites still respond. **HTTP 200 is not a valid substitute for real authentication UAT**.

## 5. Update an already installed target site

Only use this path when the site and app are already installed on erptest-lightnode:

~~~bash
(
  set -Eeuo pipefail
  export PATH="$HOME/.local/bin:$PATH"
  SRC="$HOME/erpdevelopers-deploy-source"
  test -d "$SRC/.git" || { echo "STOP: source checkout is missing"; exit 2; }
  test -z "$(git -C "$SRC" status --porcelain)" || { echo "STOP: source checkout is dirty"; exit 2; }
  test "$(git -C "$SRC" branch --show-current)" = "version-16" || {
    echo "STOP: unexpected branch"; exit 2;
  }
  git -C "$SRC" pull --ff-only origin version-16
  BENCH="/data/frappe/frappe-bench" bash "$SRC/scripts/update_erptest_lightnode.sh"
)
~~~

The updater validates the target and clean checkout, backs up **erp-developers.com** with files, fast-forwards only the ERP Developers app, migrates the target site, builds assets and clears caches. Review impact on other sites using the same app; manual shared-service restart remains a separate gate.

## Security and rollback

Record deployed commit SHA, site backup path and proxy configuration checkpoint before upgrades. Never put tokens, PEM private keys, database passwords, cookies, site_config.json or backup archives in Git. The old GitHub App private-repository deployment helper was retired because the source is now public.

**Deployment is not complete until server commands and live browser acceptance have been confirmed.**
