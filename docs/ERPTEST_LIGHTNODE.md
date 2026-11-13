# ERP Developers — erptest-lightnode deployment (Frappe v16)

**Public site:** https://erp-developers.com  
**Server:** erptest-lightnode  
**App:** VoyaERP/erpdevelopers, branch version-16  
**Site:** erp-developers.com  
**Bench:** /home/manakhly/frappe-bench (confirm first)  
**Status:** Source prepared. No SSH server deployment, DNS, TLS or UAT has yet been performed.

## Implementation principles

Green Box reference: VoyaERP/greenbox.com.eg, main branch. Its production login approach kept Frappe's original /login authentication and 2FA while layering brand-specific CSS, header and footer. The v16 login markup differs from Green Box v15, so ERP Developers implements **new v16-specific styling and a small, idempotent JS site-chrome module**, without copying authentication code or replacing the native login template. No form, password handler, session handler or social/OTP handler is duplicated.

The login UI displays navigation and a responsive dark-blue/teal technology story next to the original form. The homepage is a dedicated route named erp-developers-home, avoiding collision with Frappe's /index, and native Frappe navbar/footer blocks are overridden there only to prevent duplicates. Site branding is applied through an **explicit CLI setup helper**, not a global after-install hook. SVG icon is a clean derivative of the approved growth/shield visual direction; replace it with final artwork only after visual sign-off.

## Step 1 — Preflight on the intended server

Log in from your Mac using the SSH alias or IP already configured for erptest-lightnode. Do not assume that hostname resolves from outside the server.

~~~bash
(
  set +e
  export PATH="$HOME/.local/bin:$PATH"
  echo "Hostname: $(uname -n)"
  echo "User: $(id -un)"
  echo "Bench path: $HOME/frappe-bench"
  cd "$HOME/frappe-bench" || exit 1
  bench version
  git -C apps/frappe branch --show-current
  df -h .
  echo "Existing site folders (names only):"
  find sites -mindepth 2 -maxdepth 2 -name site_config.json -type f -printf '%h\n'
  echo "Target folder present?"
  test -e sites/erp-developers.com && echo "YES - STOP fresh install" || echo "No"
  echo "Nginx available?"; command -v nginx || true
  echo "GitHub SSH access:"
  git ls-remote --exit-code git@github.com:VoyaERP/erpdevelopers.git refs/heads/version-16 >/dev/null
  echo "Preflight complete"
)
~~~

Frappe 16 / ERPNext 16 on this server were reported in prior terminal output, but **must be verified again**. Do not read or print site_config.json secrets.

## Step 2 — Install only new app/site

As the existing Bench owner:

~~~bash
(
  set -Eeuo pipefail
  export PATH="$HOME/.local/bin:$PATH"

  SRC="$HOME/erpdevelopers-deploy-source"
  if [ -d "$SRC/.git" ]; then
    test -z "$(git -C "$SRC" status --porcelain)"
    git -C "$SRC" switch version-16
    git -C "$SRC" pull --ff-only origin version-16
  elif [ ! -e "$SRC" ]; then
    git clone --single-branch --branch version-16 \
      git@github.com:VoyaERP/erpdevelopers.git "$SRC"
  else
    echo "STOP: unexpected source path"; exit 2
  fi

  bash "$SRC/scripts/install_erptest_lightnode.sh"
)
~~~

The install helper refuses the wrong host, root execution, non-Frappe-v16 Bench, an existing target site, dirty/conflicting app checkout and low disk space. It runs bench get-app (unless app already present), bench new-site, target-only install/migrate, explicit Website Settings setup, asset build, static tests and cache clearing. Interactive database/Administrator passwords are required, and must not be placed in scripts or Git.

If a step fails after creating a site, it may leave a partial site/database; **do not rerun blindly and do not drop/delete the site automatically**. Inspect the exact failure first.

## Step 3 — DNS and reverse proxy (manual approval)

Create an A record for erp-developers.com to the server's verified public IPv4; optional AAAA only if configured. No server public IP is assumed. If using Cloudflare, use **Full (strict)** with valid origin TLS, not Flexible. Decide whether www should redirect to the apex host.

Check the current ingress (Nginx, Cloudflare, existing vhosts) and whether it is Bench-managed before any config generation. If this Bench already manages Nginx and you have backed up/reviewed its current configuration, typical steps are:

~~~bash
cd "$HOME/frappe-bench"
bench setup nginx
sudo nginx -t
sudo systemctl reload nginx
~~~

This can affect all existing sites; **do not run it as part of the install helper**. If nginx is custom-managed, adjust the existing vhost/site routing instead. If an alias domain is needed, review bench setup add-domain. An exact-match Frappe site named erp-developers.com does not need a second alias for the same hostname.

After DNS is correct and port 80/443 are reachable, provision HTTPS through your existing certificate strategy (Certbot/ACME or managed origin certificate). Only after inspecting current Nginx setup could a Certbot invocation be appropriate:

~~~bash
sudo certbot --nginx -d erp-developers.com
sudo nginx -t
sudo systemctl reload nginx
~~~

Never guess certificates, Cloudflare status, firewall rules or paths.

After HTTPS is live, if needed set site-specific absolute URLs:

~~~bash
cd "$HOME/frappe-bench"
bench --site erp-developers.com set-config host_name https://erp-developers.com
~~~

## Step 4 — Verify before announcing deployment

~~~bash
cd "$HOME/frappe-bench"
bench --site erp-developers.com list-apps
bench --site erp-developers.com execute frappe.db.get_single_value \
  --args '["Website Settings","home_page"]'
curl -I -H 'Host: erp-developers.com' http://127.0.0.1/
curl -I -H 'Host: erp-developers.com' http://127.0.0.1/login
curl -I -H 'Host: erp-developers.com' http://127.0.0.1/assets/erpdevelopers/css/login.css
~~~

The curl loopback checks assume local Nginx port 80; inspect actual listening ports and route if different. A /login 200 does not prove that password login/2FA works; browser UAT is mandatory.

Public HTTPS checks after DNS:

~~~bash
curl -I https://erp-developers.com/
curl -I https://erp-developers.com/login
curl -I https://erp-developers.com/assets/erpdevelopers/css/login.css
curl -I https://erp-developers.com/assets/erpdevelopers/js/login_chrome.js
~~~

### UAT acceptance

- [ ] Homepage is ERP Developers on root, not Frappe/ERPNext default.
- [ ] One site header, one site footer, one Frappe login form, one brand symbol; no duplicate Home/logo.
- [ ] Login, wrong-password messaging, forgot password, signup (if enabled), OTP/2FA and social sign-in (if enabled) remain native.
- [ ] Responsive layout desktop / tablet / mobile; Arabic and English website locale; no forced translation hacks or RTL errors.
- [ ] No auth request interception, no guest privileged endpoints, no Desk CSS pollution.
- [ ] No missing fonts/assets, no HTTP mixed content, no console errors.
- [ ] Existing Bench sites work before and after any shared process restart.
- [ ] Issue evidence includes tested commit SHA, screenshots, date, operator and rollback checkpoint.

## Update flow

From the source checkout, after reviewing a change:

~~~bash
cd "$HOME/erpdevelopers-deploy-source"
git fetch origin version-16
git switch version-16
git pull --ff-only origin version-16
bash scripts/update_erptest_lightnode.sh
~~~

This backup-first update script affects the target site/app only, except that asset builds share Bench files. It does not execute bench update, bench restart, uninstall-app, drop-site or database changes on other sites.

## Important boundaries

- **No production deployment is claimed** until server execution and HTTPS/UAT results are returned.
- Root domain route uses the explicit Frappe Website Settings home page erp-developers-home.
- The current vector icon follows the selected brand direction but is not an exact vector conversion of the reference PNG.
- All private credentials, backups and session details remain off GitHub.
- Changes to main documentation STATUS.md and Issue #2 should be made after UAT, not marked Done just because code was pushed.
