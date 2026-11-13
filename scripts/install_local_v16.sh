#!/usr/bin/env bash
# ERP Developers - safe, isolated Frappe v16 install on MacVMs (Arch Linux ARM).
# This is an opt-in local development install, NOT production.
# Never alter Frappe v15 or shared services. Stop when capacity is inadequate.
(
  set -Eeuo pipefail
  trap 'printf "\nINSTALL STOPPED near line %s; inspect the error. No automatic cleanup attempted.\n" "$LINENO" >&2' ERR

  SITE="erpdev.localhost"
  LEGACY="$HOME/frappe-bench"
  TARGET="$HOME/frappe-bench-erpdev-v16"
  MIN_FREE_KIB=$((8 * 1024 * 1024))
  MIN_STAGE_FREE_KIB=$((3 * 1024 * 1024))

  echo "=== Safety & isolation preflight ==="
  test "$(uname -s)" = "Linux" || { echo "Run inside MacVMs Linux, not on macOS"; exit 2; }
  test "$(uname -m)" = "aarch64" || { echo "Unexpected architecture: stop"; exit 2; }
  test -d "$LEGACY/apps/frappe" || { echo "Legacy v15 Bench not found: stop"; exit 2; }
  test ! -e "$TARGET" || { echo "Target Bench exists: stop; inspect rather than overwrite"; exit 2; }
  test ! -e "$LEGACY/sites/$SITE" || { echo "Site name already exists in legacy Bench: stop"; exit 2; }

  LEGACY_SHA="$(git -C "$LEGACY/apps/frappe" rev-parse HEAD)"
  BRANCH="$(git -C "$LEGACY/apps/frappe" branch --show-current)"
  test "$BRANCH" = "version-15" || { echo "Legacy Frappe branch changed ($BRANCH): stop"; exit 2; }
  echo "Legacy v15 HEAD: $LEGACY_SHA; untouched"

  command -v bench >/dev/null
  command -v uv >/dev/null
  command -v git >/dev/null
  command -v python3.14 >/dev/null
  command -v node >/dev/null
  command -v yarn >/dev/null

  available_kib="$(df -Pk "$HOME" | awk 'NR==2 {print $4}')"
  printf 'Free disk: %s KiB\n' "$available_kib"
  if [ -z "$available_kib" ] || [ "$available_kib" -lt "$MIN_FREE_KIB" ]; then
    echo "STOP: Need at least 8 GiB free before bench init."
    echo "Current MacVMs has only ~3.6 GiB free. Expand storage or safely reclaim space first."
    exit 3
  fi
  mem_kib="$(awk '/MemAvailable:/ {print $2}' /proc/meminfo)"
  echo "MemAvailable: $mem_kib KiB"
  if [ -n "$mem_kib" ] && [ "$mem_kib" -lt $((2 * 1024 * 1024)) ]; then
    echo "STOP: less than 2 GiB available memory; avoid OOM while v15 runs."
    exit 3
  fi

  export NVM_DIR="$HOME/.nvm"
  test -s "$NVM_DIR/nvm.sh" || { echo "nvm missing"; exit 2; }
  . "$NVM_DIR/nvm.sh"
  nvm use --silent 24
  test "$(node -p 'process.versions.node.split(".")[0]')" = "24"
  python3.14 --version
  node --version
  # nvm global packages are isolated per Node major version.
  # Yarn was observed under Node 20; verify/reinstall only for Node 24 as needed.
  if ! command -v yarn >/dev/null 2>&1; then
    echo "Installing Yarn 1.22.22 into Node 24's own nvm prefix"
    npm install -g yarn@1.22.22
  fi
  yarn --version

  echo "=== Test GitHub access before large downloads ==="
  git ls-remote --exit-code git@github.com:VoyaERP/erpdevelopers.git refs/heads/version-16 >/dev/null || {
    echo "Cannot reach the private repository; verify SSH key and permissions."; exit 4;
  }

  echo "=== Initialize a *separate* Frappe 16 Bench ==="
  cd "$HOME"
  bench init --frappe-branch version-16 --python "$(uv python find 3.14)" "$TARGET"

  echo "=== Check generated ports and conflicts, without printing secrets ==="
  python3.14 - "$TARGET" <<'PY'
import json
import pathlib
import socket
import sys
from urllib.parse import urlparse

bench = pathlib.Path(sys.argv[1])
cfg = json.loads((bench / "sites/common_site_config.json").read_text())
names = ("webserver_port", "socketio_port", "file_watcher_port",
         "redis_cache", "redis_queue", "redis_socketio")
ports = {}
for key in names:
    value = cfg.get(key)
    if value is None:
        continue
    if key.startswith("redis_"):
        port = urlparse(value).port
    else:
        port = int(value)
    if port:
        ports[key] = port
print("New Bench ports:", ", ".join(f"{k}={v}" for k, v in ports.items()))
for port in set(ports.values()):
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError as exc:
        raise SystemExit(f"STOP: selected port {port} is already in use ({exc})")
    finally:
        sock.close()
web = ports.get("webserver_port", 8000)
(bench / ".erpdev_port").write_text(str(web))
print(f"Port check passed; proposed browser port {web}")
PY

  available_kib="$(df -Pk "$HOME" | awk 'NR==2 {print $4}')"
  if [ "$available_kib" -lt "$MIN_STAGE_FREE_KIB" ]; then
    echo "STOP: less than 3 GiB free after init; no DB/site changes attempted."
    exit 3
  fi

  cd "$TARGET"
  echo "=== Clone ERP Developers v16 (private repository) ==="
  bench get-app --branch version-16 git@github.com:VoyaERP/erpdevelopers.git

  available_kib="$(df -Pk "$HOME" | awk 'NR==2 {print $4}')"
  if [ "$available_kib" -lt "$MIN_STAGE_FREE_KIB" ]; then
    echo "STOP: less than 3 GiB free after app clone; DB/site not created."
    exit 3
  fi

  echo "=== New v16 site: prompts for database/admin credentials ==="
  test ! -e "$TARGET/sites/$SITE"
  bench new-site "$SITE" --db-type mariadb
  bench --site "$SITE" install-app erpdevelopers
  bench --site "$SITE" migrate
  bench build --app erpdevelopers
  python3.14 -m unittest discover -s "$TARGET/apps/erpdevelopers/tests" -v
  bench --site "$SITE" list-apps

  echo "=== Final preservation and disk check ==="
  test "$(git -C "$LEGACY/apps/frappe" rev-parse HEAD)" = "$LEGACY_SHA" || {
    echo "WARNING: legacy git HEAD changed unexpectedly"; exit 5;
  }
  df -h /
  echo "SUCCESS: installed on isolated test Bench (not yet UAT verified)."
  echo "Web port: $(cat "$TARGET/.erpdev_port")"
  echo "Start in a separate shell with: cd $TARGET; . ~/.nvm/nvm.sh; nvm use 24; bench start"
)
