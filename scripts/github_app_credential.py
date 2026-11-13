#!/usr/bin/env python3
"""Git credential helper for read-only GitHub App installation access.

No persistent tokens. Only serves HTTPS credentials for VoyaERP/erpdevelopers.
Install outside the web root, under ~/.config/erpdevelopers/.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO = "VoyaERP/erpdevelopers"
CONFIG = Path.home() / ".config" / "erpdevelopers" / "github_app.json"
API = "https://api.github.com"
API_VERSION = "2026-03-10"


def _private_file(path: Path) -> None:
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.geteuid():
        raise RuntimeError(f"Invalid file ownership or type: {path}")
    if info.st_mode & 0o077:
        raise RuntimeError(f"File must not be accessible by group/others: {path}")


def _config() -> tuple[str, Path]:
    _private_file(CONFIG)
    data = json.loads(CONFIG.read_text(encoding="utf-8"))
    app_id = str(data["app_id"])
    if not app_id.isdigit():
        raise RuntimeError("app_id must be the numeric GitHub App ID")
    key_path = Path(data["private_key_path"]).expanduser().resolve(strict=True)
    if str(key_path).startswith(str(Path.home() / ".config" / "erpdevelopers") + os.sep) is False:
        raise RuntimeError("Private key must be inside ~/.config/erpdevelopers")
    _private_file(key_path)
    return app_id, key_path


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _jwt(app_id: str, private_key: Path) -> str:
    now = int(time.time())
    header = _b64(b'{"alg":"RS256","typ":"JWT"}')
    payload = _b64(json.dumps({"iat": now - 60, "exp": now + 540, "iss": app_id}, separators=(",", ":")).encode())
    body = f"{header}.{payload}".encode("ascii")
    signature = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(private_key)],
        input=body, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=True, timeout=10,
    ).stdout
    return f"{body.decode('ascii')}.{_b64(signature)}"


def _api_json(path: str, jwt: str, payload: dict | None = None) -> dict:
    headers = {
        "Authorization": f"Bearer {jwt}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "erpdevelopers-erptest-deployer",
    }
    encoded = json.dumps(payload).encode("utf-8") if payload is not None else None
    if encoded is not None:
        headers["Content-Type"] = "application/json"
    req = Request(API + path, data=encoded, headers=headers,
                  method="POST" if payload is not None else "GET")
    with urlopen(req, timeout=20) as response:
        return json.load(response)


def _installation_token() -> str:
    app_id, key_path = _config()
    jwt = _jwt(app_id, key_path)
    installation = _api_json(f"/repos/{REPO}/installation", jwt)
    installation_id = int(installation["id"])
    result = _api_json(
        f"/app/installations/{installation_id}/access_tokens",
        jwt,
        {"repositories": ["erpdevelopers"], "permissions": {"contents": "read"}},
    )
    token = result.get("token", "")
    if not token or not isinstance(token, str):
        raise RuntimeError("GitHub App did not return an installation token")
    return token


def _credential_get() -> None:
    request = {}
    for line in sys.stdin:
        line = line.rstrip("\r\n")
        if not line:
            break
        if "=" in line:
            key, value = line.split("=", 1)
            request[key] = value
    if (request.get("protocol") != "https"
        or request.get("host") != "github.com"
        or request.get("path", "").rstrip("/") not in (REPO, REPO + ".git")):
        return
    token = _installation_token()
    sys.stdout.write(f"username=x-access-token\npassword={token}\n\n")


def main() -> int:
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "get":
        _credential_get()
    elif action == "--check":
        _installation_token()
        print("OK: GitHub App installation token issued for VoyaERP/erpdevelopers (not displayed)")
    elif action not in ("store", "erase"):
        raise RuntimeError("Use as a Git credential helper, or run --check")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (HTTPError, URLError) as err:
        code = getattr(err, "code", "network")
        print(f"GitHub App API authentication failed (HTTP {code}); verify App installation and Contents: read permission", file=sys.stderr)
        raise SystemExit(1)
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.CalledProcessError) as err:
        print(f"GitHub App credential helper error: {err}", file=sys.stderr)
        raise SystemExit(1)
