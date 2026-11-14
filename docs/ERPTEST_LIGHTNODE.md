# ERP Developers — deployment on erptest-lightnode

## Bilingual UI and login duplication regression (2026-11-14)

The initial orbit-based layout and original bilingual story login have been restored, with compact spacing and the exact approved logo. The earlier doubled header arose because Frappe 16's `login.html` renders a native navbar for the language picker and the custom script also added a header; CSS hid `header.navbar` but not the actual `nav.navbar`.

A reviewed deployment must confirm after the **web-only** Gunicorn reload: the homepage is styled (skip link visible only on focus); the English/Arabic picker changes the homepage translations and direction; `/login` shows **one** website header, **one** picker, and the native sign-in form beside a single story panel; forgotten-password, signup/LDAP/social login and 2FA retain Frappe's native behavior where enabled. Confirm there is no duplicate footer and all shared-Bench sites remain functional.

Run the pinned existing-site update below, then the read-only `scripts/verify_frontend.sh` for real Origin English/Arabic/CSS and public asset checks. Static CI and HTTP 200 do not replace browser/auth UAT.

## Current update procedure (existing site, not a new installation)

**Current state (2026-11-14):** `erp-developers.com` already exists and `erpdevelopers` was installed on it. Earlier site-creation and missing-module/app-registration sections below are preserved as **incident history only**. Never run a new-site installer, `bench get-app`, `bench update`, `drop-site` or any database reset on this existing site.

Use a clean `version-16` checkout; select a **reviewed 40-character commit SHA** that passed GitHub CI. From `/data/frappe/frappe-bench`, stage the update script **outside the Git checkout** so Git cannot replace the script while it is executing:

~~~bash
(
  set -Eeuo pipefail
  BENCH="/data/frappe/frappe-bench"
  APP="$BENCH/apps/erpdevelopers"
  RELEASE_SHA="<reviewed-40-character-commit>"
  test -f "$BENCH/sites/erp-developers.com/site_config.json"
  test -z "$(git -C "$APP" status --porcelain)"
  test "$(git -C "$APP" branch --show-current)" = "version-16"
  test "$(git -C "$APP" remote get-url upstream)" = "https://github.com/VoyaERP/erpdevelopers.git"
  git -C "$APP" fetch upstream version-16
  test "$(git -C "$APP" rev-parse FETCH_HEAD)" = "$RELEASE_SHA"
  TEMP_SCRIPT="$(mktemp)"
  trap 'rm -f "$TEMP_SCRIPT"' EXIT
  git -C "$APP" show "$RELEASE_SHA:scripts/update_erptest_lightnode.sh" > "$TEMP_SCRIPT"
  BENCH="$BENCH" EXPECTED_SHA="$RELEASE_SHA" bash "$TEMP_SCRIPT"
)
~~~

The updater creates another **site-targeted DB + files backup**, checks exact remote SHA and fast-forward, validates Python/JS/source logo, runs tests **before migrate**, changes only that site's Website Settings, builds assets and clears caches. It intentionally does **not** restart shared services.

After scheduling the impact with other site users, verify the actual Supervisor-managed Gunicorn program and restart **web only**:

~~~bash
sudo supervisorctl status frappe-bench-web:frappe-bench-frappe-web
sudo supervisorctl restart frappe-bench-web:frappe-bench-frappe-web
~~~

Now run:

~~~bash
cd /data/frappe/frappe-bench
BENCH=/data/frappe/frappe-bench bash apps/erpdevelopers/scripts/verify_frontend.sh
~~~

This checks rendered HTML includes `/assets/erpdevelopers/css/brand.css?v=<content-hash>`, compares direct-origin CSS/logo/favicon response bytes to the files on disk, and verifies public `/`, `/login`, `/api/method/ping`, CSS and image assets. A 200 response alone is not sufficient to prove CSS delivery.

Finally inspect desktop (at least 1440 and 1024px), tablet and mobile (390px) screens; EN/AR, keyboard focus/skip link, native sign-in, password reset, configured 2FA and other sites sharing the Bench. Keep deployment/UAT issue open until these pass.



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

## Recovery from missing Python module (2026-11-14)

Third installation attempt got past Bench registry sync, passed **13/13 source-only tests** and the with-files backup. Site installation then failed in Frappe's DocType sync:

```
ModuleNotFoundError: No module named 'erpdevelopers.erp_developers'
```

The app's `erpdevelopers/modules.txt` declares `ERP Developers`. Frappe v16 uses `scrub()` to resolve that declaration as the Python module `erpdevelopers.erp_developers` while running [`sync_for`](https://github.com/frappe/frappe/blob/v16.56.0/frappe/model/sync.py#L133-L135). The package folder and `__init__.py` were missing. The corrected branch now includes `erpdevelopers/erp_developers/__init__.py`, a source regression test that imports every declared module, and a runtime import preflight before `install-app`.

A previous failed installation may have attempted to create a Module Def row before the import failure. Do not use `--force` as a workaround or delete rows without inspecting them. Fast-forward the deployment-source and Bench app checkouts to the tested commit, then rerun the guarded existing-site installer. It creates another targeted site backup and retains the Bench registry backup already present. No site reinstall, global Bench update, or Frappe core change is needed.

## Recovery from missing Bench apps.txt entry (2026-11-14)

Second operator attempt confirmed source recovery to `560b23f0d7588c78848a06e18afa69c1eb2857e3`, valid `get_public_path`, backup with DB and file archives, and **12/12 source contract tests passed**. The next error was:

~~~text
An error occurred while installing erpdevelopers: App erpdevelopers not in apps.txt
~~~

Frappe [installer.py (v16.56.0)](https://github.com/frappe/frappe/blob/v16.56.0/frappe/installer.py#L295-L318) refuses installation until the app is in the Bench-wide `sites/apps.txt`. The first failed `bench get-app` happened when `patches.txt` was missing, so [Bench 5.31 `BenchApps.sync`](https://github.com/frappe/bench/blob/v5.31.0/bench/bench.py#L264-L289) did not discover this app. The new recovery helper invokes **Bench's own registration sync**, after checking that the discovered apps are precisely the previously registered list plus `erpdevelopers`. It saves Bench `apps.txt` and optional `apps.json` copies in the existing site's private backup directory, and refuses unexpected app changes.

**Do not manually add the app to a specific site's installed-app list**, run `bench new-site`, or delete the checkout. Fast-forward both source and Bench checkouts to the tested fix commit and rerun the *existing-site installer*. It takes another backup. No server install success has yet been confirmed.

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

Follow the **Current update procedure** at the top of this guide. Do not run a stale, unpinned `git pull` script or re-install the app. Update only the existing `erp-developers.com` site, record the exact deployed commit and backup location, and run the origin/public frontend integrity checker after a reviewed web-only reload.

## Security and rollback

Record deployed commit SHA, site backup path and proxy configuration checkpoint before upgrades. Never put tokens, PEM private keys, database passwords, cookies, site_config.json or backup archives in Git. The old GitHub App private-repository deployment helper was retired because the source is now public.

**Deployment is not complete until server commands and live browser acceptance have been confirmed.**
