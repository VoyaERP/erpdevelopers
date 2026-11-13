# ERP Developers — Rasheed/MacVMs safe environment audit and Mac UAT

**State:** R0 / ED-00, host not verified. **Do not install or upgrade anything on an unidentified or production host.**

## 1. Observed symptom

The user executed commands while connected to a shell whose prompt was **[manakhly@MacVMs ~]** and later received:

~~~text
-bash: hostname: command not found
Connection to 192.168.64.15 closed.
~~~

The script began with **set -euo pipefail**, apparently in the interactive session. A failing command under set -e can exit the shell, which closes the SSH connection. A missing hostname binary may mean a restricted PATH or minimal OS package, **not** a Frappe failure. Confirm whether **MacVMs** and **Rasheed** refer to the same target.

## 2. Safe, read-only audit — paste inside the new remote SSH session

**Important:** the surrounding parentheses contain any shell-option changes inside a subprocess. We deliberately do NOT enable set -e on the interactive parent shell. This script only reads host information.

~~~bash
(
  set +e

  echo "=== Identification ==="
  printf 'User: %s\n' "${USER:-unknown}"
  printf 'HOME: %s\n' "${HOME:-unknown}"
  printf 'PATH: %s\n' "${PATH:-unset}"
  printf 'Kernel hostname: '
  if command -v uname >/dev/null 2>&1; then
      uname -n
  elif [ -x /usr/bin/uname ]; then
      /usr/bin/uname -n
  else
      printf 'unavailable\n'
  fi

  echo "=== Hostname utility ==="
  command -v hostname || true
  [ -x /usr/bin/hostname ] && /usr/bin/hostname || true
  [ -x /bin/hostname ] && /bin/hostname || true

  echo "=== OS and resources ==="
  if [ -r /etc/os-release ]; then
      sed -n '1,8p' /etc/os-release
  else
      uname -a 2>/dev/null || true
  fi
  command -v free >/dev/null 2>&1 && free -h || true
  command -v df >/dev/null 2>&1 && df -h "${HOME:-/}" || true

  echo "=== Command availability ==="
  for tool in python3 python3.14 uv node npm yarn bench git mariadb redis-server ss netstat ssh; do
      printf '%-15s ' "$tool"
      command -v "$tool" || printf 'NOT FOUND\n'
  done

  echo "=== Runtime versions (when available) ==="
  for tool in python3 python3.14 node npm yarn bench git mariadb redis-server; do
      if command -v "$tool" >/dev/null 2>&1; then
          printf '\n--- %s ---\n' "$tool"
          "$tool" --version 2>&1 | head -n 2
      fi
  done

  echo "=== Bench candidate paths ==="
  if command -v find >/dev/null 2>&1; then
      find "$HOME" -maxdepth 4 -name common_site_config.json -print 2>/dev/null
  fi

  echo "=== Existing default bench (read-only) ==="
  if [ -d "$HOME/frappe-bench/apps/frappe" ] && command -v bench >/dev/null 2>&1; then
      (cd "$HOME/frappe-bench" && bench version && bench list-sites)
  else
      printf 'No default ~/frappe-bench detected or bench unavailable\n'
  fi

  echo "=== Listening ports (read-only) ==="
  if command -v ss >/dev/null 2>&1; then
      ss -ltn 2>&1 | grep -E ':(8000|8001|18080|9000|9001|11000|12000|13000|6379|3306) ' || true
  elif command -v netstat >/dev/null 2>&1; then
      netstat -ltn 2>&1 | head -n 40
  else
      printf 'Neither ss nor netstat is available\n'
  fi

  echo "=== END OF READ-ONLY AUDIT ==="
)
~~~

If a basic utility is missing because PATH is restricted, inspect **PATH** and shell initialization; only add the normal system bin directories after confirming the actual OS, such as temporary **PATH=/usr/local/bin:/usr/bin:/bin:$PATH** inside a *new subshell*. Do not globally overwrite the parent environment before inspection.

**Never paste passwords, private keys, site_config.json or access tokens** into a ticket or chat output.

## 3. Readiness check before v16 installation

| Component | Official current Frappe v16 expectation | To verify |
| --- | --- | --- |
| OS | Recommended Debian 13+/Ubuntu 24.04+, or macOS per upstream installation guide | Actual Rasheed/MacVMs OS and constraints |
| Python | 3.14 | command location, executable used by Bench |
| Node.js | 24 | active nvm/Node, not v15 Node |
| MariaDB | 11.8 | version/service and separate DB access |
| Redis/Valkey | 6+ | existing services and collisions |
| Frappe | version-16 branch | separate Bench path |
| Existing v15 | never upgrade in place | inventory all active Bench/site paths |

**Use the current official prerequisites:** https://docs.frappe.io/framework/user/en/installation .

### Isolation gate

Identify a **new** Bench path (candidate: ~/frappe-bench-erpdev-v16) and dedicated site (candidate: erpdev.localhost). Confirm existing HTTP, Redis, socket.io, file watcher ports BEFORE initializing another Bench; inspect the new Bench Procfile/config after creation. Do not blindly run two benches with default overlapping ports.

- New Bench v16 has its own environment, apps, log/process configs and site.
- New site has separate DB and backups.
- New test process is not exposed to the public internet.
- Existing v15 and production workflows remain untouched.
- Clone via authorized GitHub access to the private repository.

## 4. Example installation *only after* the R0 audit passes

This is an illustrative sequence; adjust paths/dependencies and process ports to the host-specific approved plan.

~~~bash
cd "$HOME"
test ! -e "$HOME/frappe-bench-erpdev-v16" || {
  echo "STOP: target bench already exists"; false;
}

# Confirm uv, Bench, MariaDB, Redis and Node 24 first.
# Python 3.14 path is resolved from uv rather than assumed in PATH.
bench init --frappe-branch version-16 \
  --python "$(uv python find 3.14)" \
  frappe-bench-erpdev-v16

cd "$HOME/frappe-bench-erpdev-v16"

# Before starting services, inspect Procfile and port configurations
# and ensure no collisions with existing benches.
bench get-app --branch version-16 git@github.com:VoyaERP/erpdevelopers.git
bench new-site erpdev.localhost
bench --site erpdev.localhost install-app erpdevelopers
bench --site erpdev.localhost migrate
bench build --app erpdevelopers
bench --site erpdev.localhost list-apps
~~~

If a step fails, **stop**, capture sanitized logs, and fix the actual cause. Do not attempt destructive site recreation or config overwrites automatically.

## 5. Browse from the Mac through SSH, after the test Bench starts

From an authorized SSH session on Rasheed/MacVMs, start the isolated development Bench with an approved, non-conflicting port using **bench start**. The default development web port often is 8000, but MUST be verified; the SSH tunnel's remote port must match the confirmed webserver port.

On the **Mac terminal** (new window, not inside SSH), replace the placeholders:

~~~bash
ssh -N -L 18080:127.0.0.1:8000 YOUR_USER@YOUR_RASHEED_HOST
~~~

Test site selection from another Mac terminal:

~~~bash
curl -I -H 'Host: erpdev.localhost' http://127.0.0.1:18080/
~~~

To browse visually, use **http://erpdev.localhost:18080** if it resolves to loopback, or map erpdev.localhost to 127.0.0.1 on the Mac. Confirm the Frappe host-routing behavior and static asset URLs. Never public-port-forward this dev process to the internet.

**UAT evidence to record:** date, OS/versions, Bench/site, branch/commit, install/migrate/build results, HTTP response, browser screenshot, responsive checks, asset/network errors, logs, impacted existing sites (none).

## 6. After audit

- Copy *sanitized* output into [ED-00](https://github.com/VoyaERP/erpdevelopers/issues/1); resolve [ED-00.1](https://github.com/VoyaERP/erpdevelopers/issues/11) when the cause is known.
- Update [STATUS.md](STATUS.md) with evidence.
- Keep this document as the reusable safe audit. Do not create multiple competing server scripts.
