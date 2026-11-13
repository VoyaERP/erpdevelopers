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

## Private GitHub repository — reuse existing SSH key (no duplicate key)

The repository **VoyaERP/erpdevelopers** is private. The GitHub connector authorized in ChatGPT does **not** authenticate Git operations from erptest-lightnode; the server's existing SSH identity must itself have read access to this repository.

- Use the existing private key on the server, under the **Bench owner account**, with a configured GitHub account that has VoyaERP/erpdevelopers repository read permission.
- Do **not** copy a private key into GitHub, chat, a shell command, repository, site config or CI variables. Only public key material belongs in GitHub's SSH key settings.
- A GitHub **account SSH key** can access multiple repositories based on the account's permissions. A **repository deploy key** is scoped to one repository and normally cannot be reused for a different repository; if the current key is a deploy key for another repo, use an account key with access or a new repository-specific deploy key after approval.
- If the key is protected by a passphrase, load it into **ssh-agent** in your current login session; the install helper uses \`BatchMode=yes\` for its preflight so it will stop instead of hanging on a passphrase prompt.
- **Do not change any existing Frappe/ERPNext remote URLs**. Only this app checkout uses the repository's SSH URL \`git@github.com:VoyaERP/erpdevelopers.git\`.

### Read-only SSH preflight, as \`manakhly\` on erptest-lightnode

~~~bash
(
  set +e
  echo "=== Who owns the Bench ==="
  stat -c '%U %n' /data/frappe/frappe-bench
  echo "=== Existing local public-key filenames (safe metadata only) ==="
  find "$HOME/.ssh" -maxdepth 1 -type f -name '*.pub' -printf '%f\n'
  echo "=== SSH agent identities ==="
  ssh-add -l || true
  echo "=== SSH GitHub account identity ==="
  ssh -T git@github.com || true
  echo "=== Actual private repository access ==="
  git ls-remote --exit-code \
    git@github.com:VoyaERP/erpdevelopers.git refs/heads/version-16
)
~~~

**Success criterion:** \`git ls-remote\` prints one commit SHA for \`refs/heads/version-16\`, not \`Permission denied (publickey)\` or \`Repository not found\`. \`ssh -T git@github.com\` normally returns exit status **1** despite a successful greeting; do not treat that alone as failure.

### If the server already has a passphrase-protected key but no loaded agent

From the **interactive erptest-lightnode shell**, not in a one-off subshell:

~~~bash
# Only if no useful SSH agent is available:
eval "$(ssh-agent -s)"

# Check which private-key path actually exists before choosing.
ls -l "$HOME/.ssh/"*.pub 2>/dev/null || true

# Example ONLY if this is the existing registered key:
ssh-add "$HOME/.ssh/id_ed25519"

# Verify repository authorization, not merely GitHub SSH identity.
git ls-remote --exit-code \
  git@github.com:VoyaERP/erpdevelopers.git refs/heads/version-16
~~~

If the existing key has a different filename, pass that actual **private** key path to \`ssh-add\`; never paste the key's contents. If the greeting identifies a GitHub account that cannot read \`VoyaERP/erpdevelopers\`, grant that account repository access or configure a permitted repository-specific key. There is no reason to create a duplicate key while the existing account key can be authorized.

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
