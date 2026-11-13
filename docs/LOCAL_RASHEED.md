# ERP Developers — Rasheed/MacVMs safe environment audit and Mac UAT

**State:** R0 / ED-00, host not verified. **Do not install or upgrade anything on an unidentified or production host.**

## 1. Observed symptom

The user executed commands while connected to a shell whose prompt was **[manakhly@MacVMs ~]** and later received:

~~~text
-bash: hostname: command not found
Connection to 192.168.64.15 closed.
~~~

The script began with **set -euo pipefail**, apparently in the interactive session. A failing command under set -e can exit the shell, which closes the SSH connection. A missing hostname binary may mean a restricted PATH or minimal OS package, **not** a Frappe failure. Confirm whether **MacVMs** and **Rasheed** refer to the same target.

## Third audit — confirmed capacity and stack (2026-11-13)

User-provided terminal evidence from `[manakhly@MacVMs ~]`:

| Resource | Actual observation | Decision |
| --- | --- | --- |
| Architecture | `aarch64` / Arch Linux ARM | Outside officially supported Frappe distro list |
| Root filesystem | `/dev/vda2`: **30G total, 25G used, 3.8G free, 87% used** | **HARD STOP** for another Bench; capacity first |
| RAM | **3.8 GiB total**, about **2.5 GiB available**; 4GiB swap | Concurrent v15+v16 builds may suffer memory pressure |
| MariaDB | `SELECT VERSION()` and `mariadbd --version`: **12.3.2** | Server confirmed; not documented v16 11.8 target; compatibility requires test |
| Redis/Valkey | Valkey **9.1.1** is present through both `redis-server` and `valkey-server` | v16 6+ prerequisite met by version, integration not tested |
| Yarn | **1.22.22** | Meets official 1.22+ |
| Frappe existing | **15.118.0**, ERPNext **15.121.0**, app `rasheed 0.0.1`, branch **version-15** | Preserve existing bench/services/apps |
| Installed Node 24 | `nvm install 24` completed; **v24.22.3**, npm **11.19.1** | Installed; default shell still Node 20.20.2 unless `nvm use 24` invoked |
| Candidate ports | No listeners reported for `8001`, `8002`, `9001`, `11001`, `13001`, `18080` at scan moment | Must revalidate before `bench start`; don't assume auto-allocation |
| Containers | `docker` and `podman` not found | Do not prescribe immediate container commands without installation plan |

**R0 conclusion:** **Do NOT run `bench init`, `bench new-site`, `bench update`, `bench restart`, database version changes, or cache cleanup on the existing v15 bench yet.** Source code work can continue independently in GitHub. Storage expansion or separate supported development VM is the safest path. Suggested *capacity planning target* (not an official framework minimum): **15–20 GB free disk** and **>=8 GiB total RAM** when planning to operate v15 and v16 side by side. Prefer a **separate Debian 13 / Ubuntu 24.04+ ARM64 VM** with sufficient resources, to avoid unsupported Arch-specific packaging and shared database risks.

### Read-only storage and existing-sites inspection

Run inside a subshell on MacVMs; does not delete or modify anything:

~~~bash
(
  set +e
  echo "=== Root disk/inodes ==="; df -h /; df -i /
  echo "=== Home directory sizes ==="
  du -x -h -d 1 "$HOME" 2>/dev/null | sort -h | tail -n 20
  echo "=== Existing Bench major sizes ==="
  du -x -h -d 1 "$HOME/frappe-bench" 2>/dev/null | sort -h | tail -n 20
  echo "=== Other possible disk caches (read-only) ==="
  du -sh "$HOME/.cache" "$HOME/.local" "$HOME/.nvm" /var/cache/pacman/pkg 2>/dev/null || true
  echo "=== Disk partitions ==="
  command -v lsblk >/dev/null 2>&1 && lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS || true
  echo "=== Current Frappe v15 site names (no secrets) ==="
  find "$HOME/frappe-bench/sites" -mindepth 2 -maxdepth 2 -type f -name site_config.json -printf '%h\n' 2>/dev/null
  echo "=== Current Frappe branch ==="
  git -C "$HOME/frappe-bench/apps/frappe" branch --show-current
  echo "=== END ==="
)
~~~

**Note:** `bench list-sites` is not a valid command in this installation (observed `No such command 'list-sites'`). Use the read-only `find` above or `bench --site all list-apps` when actually needed, according to Frappe docs. Never display `site_config.json`: it includes secrets.

**Safe options after inspection:** (1) expand the VM's existing 30GB virtual disk and filesystem with a verified backup and host-specific runbook, or (2) create an **isolated supported Debian/Ubuntu ARM64 VM** with its own compatible MariaDB 11.8, Node 24 and Frappe 16. Do not delete unknown backups, logs, package caches or existing Frappe assets without reviewing retention and recovery needs. Do not upgrade/downgrade shared MariaDB 12.3.2.

---

## Fourth audit — confirmed disk directory sizes and sites (2026-11-13)

**Updated observations:** `df -h /`: `/dev/vda2` 30G / 25G used / **3.6G free**, **88% used**; `df -i /`: **32% inode usage**; `lsblk`: `vda1` 200M VFAT `/boot`, `vda2` 29.8G ext4 `/` and `/boot/dtbs`. `~/frappe-bench` 6.1G, including `apps` 4.1G, `sites` 981M and `env` 935M. `~/.vscode-server` 3.1G, `~/mobile` 2.2G, `~/.cache` 815M, `/var/cache/pacman/pkg` 890M, `~/.nvm` 1.2G.

**Existing v15 site inventory (names only, no credentials):** `frappiq-cert.local`, `s1.mac.dynamicsforall.com`, `frappe.localhost`, `lg.mac.dynamicsforall.com`. Preserve all.

### Preferred isolation decision (pending host approval)

1. **Safer option:** new Debian 13 / Ubuntu 24.04+ ARM64 VM with adequate CPU/RAM, 60–80GB disk, own validated MariaDB 11.8 and v16 Bench; Mac tunnel for local testing. No disturbance to MacVMs v15.
2. **On MacVMs:** after an external VM snapshot/verified backup, enlarge the VM's backing virtual disk from 30GB to a proposed 80GB (conditional on host free space); preferably increase RAM to 8GiB if feasible. Existing Arch Linux ARM and MariaDB 12.3 remain extra compatibility risks, so test v16 in an isolated Bench and DB after resizing, not on a live site.

### Non-destructive next inspection

~~~bash
(
  set +e
  echo "=== VM and storage ==="
  command -v systemd-detect-virt >/dev/null 2>&1 && systemd-detect-virt || true
  command -v findmnt >/dev/null 2>&1 && findmnt -no SOURCE,FSTYPE,SIZE,AVAIL / || true
  lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS
  echo "=== Tools to grow (do NOT invoke yet) ==="
  command -v growpart || true
  command -v resize2fs || true
  echo "=== Review optional caches (no deletion) ==="
  du -x -h -d 1 "$HOME/.vscode-server" 2>/dev/null | sort -h | tail -n 12
  du -x -h -d 1 "$HOME/.cache" 2>/dev/null | sort -h | tail -n 12
  if command -v paccache >/dev/null 2>&1; then
    paccache --dryrun --keep 2
  else
    echo "paccache unavailable; no cleanup attempted"
  fi
  echo "=== END / no changes made ==="
)
~~~

`paccache --dryrun --keep 2` **does not remove anything** and documents possible old package candidates. Use [Arch paccache man page](https://man.archlinux.org/man/paccache.8) before contemplating package-cache retention. Do not delete VS Code remote server files while attached, backup directories or production/legacy site files.

### Conditional partition/FS extension — NOT YET APPROVED

Only **after** (1) an off-VM backup/snapshot; (2) identifying the Mac virtualization provider; (3) increasing virtual disk size in the provider UI while VM stopped or as supported; (4) confirming `lsblk` reports a larger `vda`; (5) checking tooling and `growpart -N` dry-run; can a privileged host-specific runbook expand partition `/dev/vda2` and then the ext4 filesystem. **Do not paste destructive partition commands until all preconditions are verified.**

**Acceptance gate for R0:** usable free space, verified protected v15 sites and separate v16 DB/ports, reproducible Frappe v16 install/build and Mac UAT evidence. No such install has yet occurred.

---

## Verified host snapshot — 2026-11-13 (from user terminal)

| Property | Observed value | Consequence |
| --- | --- | --- |
| Hostname | `MacVMs` from `uname -n` | Resolve whether this is also the intended `Rasheed` target |
| OS | `Arch Linux ARM` / `archarm`, rolling | **Not among officially supported Frappe host distros**; app may work but environment needs extra validation |
| Python | `python3.14 3.14.7` | v16 Python prerequisite present |
| Node.js | `v20.20.2` from user-level `nvm` | **Blocker:** v16 requires Node 24; do not alter Node 20 default on existing Bench |
| Bench CLI | `5.31.0` | Installed; test v16 compatibility during isolated setup |
| Git | `2.55.0` | Available |
| MariaDB client | `12.3.2` | **Server version not known**; v16 documents 11.8; cannot infer compatibility from client |
| Existing Bench | `/home/manakhly/frappe-bench` | Do not mutate or restart until inspected |
| Listening ports | `8000, 9000, 11000, 13000, 3306` | Reserve nonconflicting ports for new Bench |
| Missing command | `hostname` | Not required to fix to proceed; `uname -n` is a working alternative |

Current official installation guide: https://docs.frappe.io/framework/user/en/installation . Its official support list is **macOS or Debian/Ubuntu** (not Arch). This is a **development compatibility experiment**, not an officially supported production deployment.

### Next safe inventory command (read-only)

Paste this as a single subshell **on MacVMs via SSH**. It does not modify databases, existing sites, npm defaults or Bench configs.

~~~bash
(
  set +e
  echo "== Identity / architecture =="; uname -n; uname -m
  echo "== Resources =="; command -v free >/dev/null && free -h; df -h "$HOME"
  echo "== MariaDB server (read-only) =="
  if command -v mariadb >/dev/null 2>&1; then
    mariadb -N -B -e 'SELECT VERSION();' 2>&1 || echo "Local DB login unavailable; server version still unknown"
  fi
  command -v mariadbd >/dev/null 2>&1 && mariadbd --version || true
  echo "== Redis or Valkey =="
  command -v redis-server >/dev/null 2>&1 && redis-server --version || true
  command -v valkey-server >/dev/null 2>&1 && valkey-server --version || true
  echo "== nvm versions and Yarn =="
  if [ -s "$HOME/.nvm/nvm.sh" ]; then
    . "$HOME/.nvm/nvm.sh"
    nvm ls
  fi
  yarn --version 2>&1 || true
  echo "== Existing Bench, read-only =="
  if [ -d "$HOME/frappe-bench/apps/frappe" ]; then
    (cd "$HOME/frappe-bench" &&
      printf 'Frappe branch: ' && git -C apps/frappe branch --show-current &&
      bench version &&
      bench list-sites)
  fi
  echo "== Free port candidates =="
  ss -ltn | grep -E ':(8001|8002|9001|9002|11001|13001|18080) ' || echo "No candidate collisions shown"
  echo "== Docker / Podman availability =="
  command -v docker || true
  command -v podman || true
  echo "== END =="
)
~~~

### Optional: install Node 24 ONLY into existing user-level nvm

Do this in a **dedicated v16 shell** once resources are checked. `nvm install 24` does not uninstall Node 20; **do not run `nvm alias default 24`**, upgrade system Node, or restart existing Bench services.

~~~bash
(
  set -e
  export NVM_DIR="$HOME/.nvm"
  test -s "$NVM_DIR/nvm.sh"
  . "$NVM_DIR/nvm.sh"
  nvm install 24
  nvm use 24
  node --version
  npm --version
  yarn --version
)
~~~

Because this example runs in a subshell, it verifies Node 24 without changing the interactive parent environment. **When initializing the new Bench**, source `"$HOME/.nvm/nvm.sh"` and `nvm use 24` in the *actual* separate install shell first; verify `node --version` before `bench init`. No need to change the existing Node 20 default.

### MariaDB v16 decision gate

Do **not** downgrade/upgrade the shared MariaDB instance merely because the client reports 12.3.2. Inspect server `SELECT VERSION()`; check if it meets **the specific v16 11.8 tested/documented target**, then decide whether an isolated compatible database service is needed (for example a vetted ARM64 MariaDB 11.8 container if available). The separate v16 site must never reuse or overwrite an existing site DB.

### Port decision gate

Bench [multi-bench behavior](https://github.com/frappe/bench/wiki/Multi-Bench-Setup) can allocate separate ports when it detects sibling Benches, but **do not assume allocation**. After `bench init`, inspect the new Bench's `sites/common_site_config.json` **without disclosing secrets**, and confirm actual Procfile/Redis/socket.io ports are unused, before `bench start`. On this host 8000/9000/11000/13000 are already occupied.

---

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
