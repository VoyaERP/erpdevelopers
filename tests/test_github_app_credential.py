"""Security guardrails for the read-only GitHub App credential helper."""
import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "erpdevelopers_github_app_credentials", ROOT / "scripts/github_app_credential.py"
)
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


class TestGitHubAppHelper(unittest.TestCase):
    def test_only_expected_https_repo_gets_credentials(self):
        cases = [
            ("https", "github.com", "VoyaERP/erpdevelopers.git", True),
            ("https", "github.com", "VoyaERP/other.git", False),
            ("https", "evil.example.com", "VoyaERP/erpdevelopers.git", False),
            ("http", "github.com", "VoyaERP/erpdevelopers.git", False),
            ("https", "github.com", "other/erpdevelopers.git", False),
        ]
        for protocol, host, path, expected in cases:
            inp = io.StringIO(f"protocol={protocol}\nhost={host}\npath={path}\n\n")
            out = io.StringIO()
            with patch.object(HELPER, "_installation_token", return_value="TEST_ONLY"), \
                 patch.object(sys, "stdin", inp), contextlib.redirect_stdout(out):
                HELPER._credential_get()
            self.assertEqual("username=x-access-token" in out.getvalue(), expected)

    def test_installation_token_requests_only_read_contents(self):
        with patch.object(HELPER, "_config", return_value=("12345", Path("/not/a/real/key"))), \
             patch.object(HELPER, "_jwt", return_value="JWT_TEST_ONLY"), \
             patch.object(HELPER, "_api_json") as request:
            request.side_effect = [{"id": 67890}, {"token": "TOKEN_TEST_ONLY"}]
            self.assertEqual(HELPER._installation_token(), "TOKEN_TEST_ONLY")
            self.assertEqual(request.call_count, 2)
            url, jwt, payload = request.call_args.args
            self.assertEqual(url, "/app/installations/67890/access_tokens")
            self.assertEqual(payload, {"repositories": ["erpdevelopers"], "permissions": {"contents": "read"}})

    def test_installer_and_updater_use_https_git_app_auth(self):
        for name in ("install_erptest_lightnode.sh", "update_erptest_lightnode.sh"):
            script = (ROOT / "scripts" / name).read_text()
            self.assertIn("erpdev_enable_github_app_git", script)
            self.assertNotIn("git@github.com", script)
        auth = (ROOT / "scripts/github_app_auth.sh").read_text()
        self.assertIn("credential.useHttpPath", auth)
        self.assertIn("GIT_TERMINAL_PROMPT=0", auth)


if __name__ == "__main__":
    unittest.main()
