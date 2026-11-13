# ERP Developers — erptest-lightnode deployment (Frappe v16)

**Public site:** https://erp-developers.com  
**Server:** erptest-lightnode  
**App:** VoyaERP/erpdevelopers, branch version-16  
**Site:** erp-developers.com  
**Bench:** /data/frappe/frappe-bench (observed previously; verify on server before executing)  
**Status:** Source prepared. No SSH server deployment, DNS, TLS or UAT has yet been performed.

## Implementation principles

Green Box reference: VoyaERP/greenbox.com.eg, main branch. Its production login approach kept Frappe's original /login authentication and 2FA while layering brand-specific CSS, header and footer. The v16 login markup differs from Green Box v15, so ERP Developers implements **new v16-specific styling and a small, idempotent JS site-chrome module**, without copying authentication code or replacing the native login template. No form, password handler, session handler or social/OTP handler is duplicated.

The login UI displays navigation and a responsive dark-blue/teal technology story next to the original form. The homepage is a dedicated route named erp-developers-home, avoiding collision with Frappe's /index, and native Frappe navbar/footer blocks are overridden there only to prevent duplicates. Site branding is applied through an **explicit CLI setup helper**, not a global after-install hook. SVG icon is a clean derivative of the approved growth/shield visual direction; replace it with final artwork only after visual sign-off.

## Private GitHub source: GitHub App (read-only)

Before running this installer, create and install a GitHub App limited to VoyaERP/erpdevelopers and Contents: Read-only. The first HTTPS clone is described in [GITHUB_APP_DEPLOY.md](GITHUB_APP_DEPLOY.md). No SSH Deploy Key, PAT or token-in-URL is required. The App private key remains off Git and the server uses an on-demand installation token for Git operations.

## Step 1 — Preflight on the intended server

Log in from your Mac using the SSH alias or IP already configured for erptest-lightnode. Do not assume that hostname resolves from outside the server.

~~~bash
(
  set +e
  export PATH="$HOME/.local/bin:$PATH"
  echo "Hostname: $(uname -n)"
  echo "User: $(id -un)"
  echo "Bench path: /data/frappe/frappe-bench"
  cd /data/frappe/frappe-bench || exit 1
  bench version
  git -C apps/frappe branch --show-current
  df -h .
  echo "Existing site folders (names only):"
  find sites -mindepth 2 -maxdepth 2 -name site_config.json -type f -printf '%h\n'
  echo "Target folder present?"
  test -e sites/erp-developers.com && echo "YES - STOP fresh install" || echo "No"
  echo "Nginx available?"; command -v nginx || true
  echo "GitHub App helper configured?"
  test -r "$HOME/.config/erpdevelopers/github_app_credential.py"
  # Private repo HTTPS access is verified in docs/GITHUB_APP_DEPLOY.md
  echo "Preflight complete"
)
~~~

Frappe 16 / ERPNext 16 on this server were reported in prior terminal output, but **must be verified again**. Do not read or print site_config.json secrets.

## Step 2 — Install only new app/site

Follow [GITHUB_APP_DEPLOY.md](GITHUB_APP_DEPLOY.md) for the one-time organization GitHub App registration, PEM transfer to the server, helper configuration and first **tokenless HTTPS** clone.

Once `$HOME/erpdevelopers-deploy-source` has been cloned to branch version-16 using that scoped GitHub App helper, execute this as the Bench owner on erptest-lightnode:

~~~bash
export BENCH="/data/frappe/frappe-bench"
bash "$HOME/erpdevelopers-deploy-source/scripts/install_erptest_lightnode.sh"
~~~

The installer independently reloads the scoped GitHub App credential helper. It refuses wrong host, root execution, non-Frappe-v16 Bench, an existing target site, dirty/conflicting app checkout and low disk space. It does not modify DNS/SSL/Nginx or restart shared services. Creating the separate site prompts interactively for database and Administrator credentials.

If a step fails after site creation, it may leave a partial site/database; inspect the exact failure, and do not delete/recreate automatically.

## Step 3 — DNS and reverse proxy (manual approval)

Create an A record for erp-developers.com to the server's verified public IPv4; optional AAAA only if configured. No server public IP is assumed. If using Cloudflare, use **Full (strict)** with valid origin TLS, not Flexible. Decide whether www should redirect to the apex host.

Check the current ingress (Nginx, Cloudflare, existing vhosts) and whether it is Bench-managed before any config generation. If this Bench already manages Nginx and you have backed up/reviewed its current configuration, typical steps are:

~~~bash
cd /data/frappe/frappe-bench
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
cd /data/frappe/frappe-bench
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

The target-only update helper sources the GitHub App credential helper itself, but the initial source checkout fast-forward requires the temporary Git credentials from section C of [GITHUB_APP_DEPLOY.md](GITHUB_APP_DEPLOY.md).

After the HTTPS source clone is updated to version-16:

~~~bash
bash "$HOME/erpdevelopers-deploy-source/scripts/update_erptest_lightnode.sh"
~~~

This backup-first update script affects the target site/app only (shared Bench assets are rebuilt). It does not execute bench update, bench restart, uninstall-app, drop-site or database changes on other sites.

## Important boundaries

- **No production deployment is claimed** until server execution and HTTPS/UAT results are returned.
- Root domain route uses the explicit Frappe Website Settings home page erp-developers-home.
- The current vector icon follows the selected brand direction but is not an exact vector conversion of the reference PNG.
- All private credentials, backups and session details remain off GitHub.
- Changes to main documentation STATUS.md and Issue #2 should be made after UAT, not marked Done just because code was pushed.
