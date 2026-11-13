# ERP Developers — GitHub App authentication (read-only)

Target: private VoyaERP/erpdevelopers → erptest-lightnode → Frappe v16.
This is a **server GitHub App**, distinct from the GitHub connector available in ChatGPT.
Status: GitHub App creation, GitHub installation and server tests are NOT YET VERIFIED.

## A. Create the GitHub App in GitHub UI (organization owner action)

1. Open VoyaERP → Settings → Developer settings → GitHub Apps → New GitHub App (organization admin required).
2. Use a unique name such as erpdevelopers-erptest-deployer and Homepage URL https://erp-developers.com.
3. Disable Webhook Active. No incoming webhook endpoint is required.
4. Repository permission: **Contents = Read-only**. All other repository/organization/account permissions No access. Metadata read is implicit.
5. Keep App private/organization-only, create, and note the numeric **App ID** (not Client ID).
6. Under Private keys click Generate a private key. A PEM file downloads to your Mac. **Never commit or share it.**
7. Install the GitHub App on the VoyaERP organization, select **Only select repositories → erpdevelopers**, and approve.

GitHub will let the App issue installation access tokens scoped to this repo with Contents: read. They expire after one hour. The helper generates a new token when Git asks for a password.

Official sources:
- https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation
- https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/managing-private-keys-for-github-apps

## B. Bootstrap on erptest-lightnode (no GitHub SSH key)

Because this repository is private, the first clone cannot fetch its own credential helper. Download the *non-secret source file* scripts/github_app_credential.py to your Mac from the repository in GitHub's web UI (or the supplied chat artifact).

On erptest-lightnode, using the Bench owner account **manakhly**:

~~~bash
umask 077
install -d -m 700 "$HOME/.config/erpdevelopers"
~~~

On your **Mac Terminal** (not inside server SSH), substitute the actual PEM download path:

~~~bash
scp "$HOME/Downloads/github_app_credential.py" \
  manakhly@erptest-lightnode:/home/manakhly/.config/erpdevelopers/github_app_credential.py
scp "/path/to/downloaded-github-app-private-key.pem" \
  manakhly@erptest-lightnode:/home/manakhly/.config/erpdevelopers/github-app.pem
~~~

Back on **erptest-lightnode**:

~~~bash
CONF="$HOME/.config/erpdevelopers"
chmod 700 "$CONF"
chmod 600 "$CONF/github_app_credential.py" "$CONF/github-app.pem"
read -r -p "Numeric GitHub App ID: " APP_ID
case "$APP_ID" in ''|*[!0-9]*) echo "Invalid App ID"; exit 2 ;; esac
umask 077
printf '{"app_id":"%s","private_key_path":"%s/github-app.pem"}\n' \
  "$APP_ID" "$CONF" > "$CONF/github_app.json"
chmod 600 "$CONF/github_app.json"
python3 "$CONF/github_app_credential.py" --check
~~~

A successful --check prints OK without displaying an access token. Requirements: python3, openssl, correct system clock and outbound HTTPS/443 to api.github.com. The helper validates that the private key and config are regular files owned by the current user with no group/other read bits.

**Never put the PEM, JWT, Installation Token or config JSON inside Git, a Frappe public directory or a support ticket.**

## C. First HTTPS clone and install

On erptest-lightnode, in a new normal user shell:

~~~bash
(
  set -Eeuo pipefail
  HELPER="$HOME/.config/erpdevelopers/github_app_credential.py"
  test -r "$HELPER"
  export GIT_CONFIG_COUNT=3
  export GIT_CONFIG_KEY_0=credential.helper
  export GIT_CONFIG_VALUE_0=
  export GIT_CONFIG_KEY_1=credential.helper
  export GIT_CONFIG_VALUE_1="!python3 \"$HELPER\""
  export GIT_CONFIG_KEY_2=credential.useHttpPath
  export GIT_CONFIG_VALUE_2=true
  export GIT_TERMINAL_PROMPT=0

  REPO="https://github.com/VoyaERP/erpdevelopers.git"
  git ls-remote --exit-code "$REPO" refs/heads/version-16
  SRC="$HOME/erpdevelopers-deploy-source"

  if [ -d "$SRC/.git" ]; then
    test -z "$(git -C "$SRC" status --porcelain)"
    test "$(git -C "$SRC" remote get-url origin)" = "$REPO" || {
      echo "STOP: source remote must be the tokenless HTTPS URL"; exit 2;
    }
    git -C "$SRC" fetch origin version-16
    git -C "$SRC" switch version-16
    git -C "$SRC" merge --ff-only origin/version-16
  elif [ ! -e "$SRC" ]; then
    git clone --single-branch --branch version-16 "$REPO" "$SRC"
  else
    echo "STOP: unexpected source directory"; exit 2
  fi

  export BENCH="/data/frappe/frappe-bench"
  bash "$SRC/scripts/install_erptest_lightnode.sh"
)
~~~

The install script sources scripts/github_app_auth.sh inside its own subshell, so bench get-app inherits an ephemeral credential helper. No token is placed in any remote URL, Git config file or shell history. The installer refuses an existing target site.

If the source or app checkout already exists with an SSH remote, do NOT overwrite or delete it. After validating the clean and correct repository, an operator can change **that single checkout** to the tokenless HTTPS remote. No other Frappe/ERPNext remotes are changed.

## D. Updates and security

After setup, the same credential helper and the update script scripts/update_erptest_lightnode.sh perform private fetches with a fresh one-hour token. Running git commands manually requires the temporary Git credential environment shown in section C; NEVER use a token inside a URL.

- Keep ~/.config/erpdevelopers mode 700; PEM and JSON mode 600. Backup PEM securely outside application/browser assets and rotate app keys as needed.
- GitHub App Installation scope: Only erpdevelopers, Contents: read-only.
- On a 404 during installation lookup, verify App ID, app installation and selected repository.
- On a 403 verify permissions/approval; on a 401 verify key/JWT and clock skew.
- For HTTPS Git, use github.com on port 443; ssh -T git@github.com and port 22 are not involved.
- Never run set -x around this helper; debugging authentication headers can leak secrets.
- Frappe, MariaDB, Bench and erp-developers.com DNS/TLS/UAT are **separate deployment requirements**.

This file is the canonical setup for GitHub App deployment; do not maintain a duplicate server SSH authentication guide.
