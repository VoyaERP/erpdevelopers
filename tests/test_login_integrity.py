from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


class TestNativeLogin(unittest.TestCase):
    def test_assets_not_auth_overrides(self):
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("web_include_js", hooks)
        self.assertIn("login_chrome.js", hooks)
        self.assertIn("login.css", hooks)
        self.assertNotIn("override_whitelisted_methods", hooks)

    def test_no_custom_form_or_auth_interception(self):
        js = (APP / "public/js/login_chrome.js").read_text(encoding="utf-8")
        self.assertIn('document.getElementById("page-login")', js)
        self.assertIn('const LOGIN_PATH = "/login"', js)
        self.assertIn('if (path !== LOGIN_PATH)', js)
        self.assertIn("document.body.dataset.edLoginEnhanced", js)
        self.assertIn("document.body.prepend(skip, top)", js)
        self.assertIn('document.getElementById("language-switcher")', js)
        for forbidden in ('innerHTML', 'create("form")', 'createElement("form")',
                          "frappe.call(", "fetch(", "XMLHttpRequest",
                          "document.documentElement.lang =", "wrapper.insertBefore("):
            self.assertNotIn(forbidden, js)

    def test_dom_simulation_is_run_by_ci(self):
        workflow = (ROOT / ".github/workflows/v16-static-validation.yml").read_text(encoding="utf-8")
        self.assertIn("node --test tests/login_chrome_dom.test.cjs", workflow)
        self.assertTrue((ROOT / "tests/login_chrome_dom.test.cjs").is_file())

    def test_login_uses_one_header_and_native_auth_view(self):
        js = (APP / "public/js/login_chrome.js").read_text(encoding="utf-8")
        css = (APP / "public/css/login.css").read_text(encoding="utf-8")
        self.assertIn('document.querySelector(".ed-login-header")', js)
        self.assertEqual(js.count('document.body.prepend(skip, top)'), 1)
        self.assertEqual(js.count('wrapper.prepend(aside)'), 1)
        self.assertIn('document.getElementById("language-switcher")', js)
        self.assertIn('top.querySelector(".ed-login-current").before(picker)', js)
        self.assertIn('.ed-login-website nav.navbar', css)
        self.assertIn('.ed-login-website .web-footer', css)
        self.assertIn('.page-card-head .app-logo {display:none!important}', css)
        self.assertIn('grid-template-columns:minmax(0,1.04fr) minmax(340px,.96fr)', css)
        self.assertNotIn('create("form"', js)
        self.assertNotIn("window.location.reload()", js)

    def test_declared_frappe_modules_are_python_packages(self):
        # Frappe v16 install sync_for imports app_name + "." + scrub(module).
        # A missing package caused ModuleNotFoundError during site installation.
        from importlib import import_module

        declared = [
            value.strip()
            for value in (APP / "modules.txt").read_text(encoding="utf-8").splitlines()
            if value.strip() and not value.lstrip().startswith("#")
        ]
        self.assertTrue(declared, "modules.txt must declare a Frappe module")
        for module_name in declared:
            slug = module_name.replace(" ", "_").replace("-", "_").lower()
            module_path = APP / slug / "__init__.py"
            with self.subTest(module=module_name):
                self.assertTrue(module_path.is_file(), f"Missing module: {module_path}")
                imported = import_module(f"erpdevelopers.{slug}")
                self.assertIsNotNone(imported.__file__)

    def test_v16_asset_discovery_markers_exist(self):
        # frappe v16 esbuild/utils.js is_frappe_app() checks all three files.
        for filename in ("hooks.py", "modules.txt", "patches.txt"):
            with self.subTest(filename=filename):
                self.assertTrue((APP / filename).is_file(), filename)

    def test_updater_uses_pinned_release_and_pre_migration_checks(self):
        script = (ROOT / "scripts/update_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn('EXPECTED_SHA="${EXPECTED_SHA:-}"', script)
        self.assertIn("rev-parse FETCH_HEAD", script)
        self.assertIn("merge-base --is-ancestor", script)
        self.assertIn("backup --with-files", script)
        self.assertLess(script.index("backup --with-files"), script.index("merge --ff-only"))
        self.assertLess(script.index("unittest discover"), script.index('bench --site "$SITE" migrate'))
        self.assertNotIn("bench new-site", script)
        self.assertNotIn("bench update", script)
        self.assertNotIn("supervisorctl restart", script)

    def test_frontend_verifier_compares_real_css_and_images(self):
        script = (ROOT / "scripts/verify_frontend.sh").read_text(encoding="utf-8")
        self.assertIn("--resolve", script)
        self.assertIn("brand.css?v=$DIGEST", script)
        self.assertIn('cmp -s "$APP/erpdevelopers/public/css/brand.css" "$TMP/brand.css"', script)
        self.assertIn("erpdevelopers-selected-logo.png", script)
        self.assertIn("erpdevelopers-selected-favicon.png", script)
        self.assertIn('CARD_COUNT=', script)
        self.assertIn("Learning Academy", script)
        self.assertIn("?_lang=ar", script)
        self.assertIn("بوابة المطورين", script)
        self.assertIn('id="language-switcher"', script)
        self.assertNotIn("bench migrate", script)

    def test_existing_site_installer_recognizes_upstream_remote(self):
        installer = (ROOT / "scripts/install_existing_site_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn("for name in upstream origin", installer)
        self.assertNotIn("remote set-url", installer)

    def test_native_sections_remain_unmodified(self):
        js = (APP / "public/js/login_chrome.js").read_text(encoding="utf-8")
        self.assertNotIn("page.querySelectorAll(", js)
        self.assertNotIn("MutationObserver", js)
        css = (APP / "public/css/login.css").read_text(encoding="utf-8")
        self.assertIn('body[data-path="login"]', css)
        self.assertIn(".ed-login-website", css)
        self.assertIn('url("/assets/erpdevelopers/images/login-network.svg")', css)
        self.assertTrue((APP / "public/images/login-network.svg").is_file())

    def test_site_setup_is_explicit_and_site_scoped(self):
        setup = (APP / "site_setup.py").read_text(encoding="utf-8")
        self.assertIn("from erpdevelopers.branding import EXPECTED_SITE", setup)
        self.assertIn("frappe.local.site != EXPECTED_SITE", setup)
        self.assertNotIn("@frappe.whitelist", setup)

    def test_homepage_single_chrome(self):
        home = (APP / "www/erp-developers-home.html").read_text(encoding="utf-8")
        self.assertIn("{% block navbar %}{% endblock %}", home)
        self.assertIn("{% block footer %}{% endblock %}", home)
        self.assertIn("{% block page_container %}", home)
        self.assertIn('href="/login"', home)
        self.assertFalse((APP / "www/index.html").exists())

    def test_existing_site_installer_never_recreates_site(self):
        script = (ROOT / "scripts/install_existing_site_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn('test -f "$BENCH/sites/$SITE/site_config.json"', script)
        self.assertIn('backup --with-files', script)
        self.assertIn('install-app erpdevelopers', script)
        self.assertIn('site_setup.configure_website', script)
        self.assertNotIn("bench new-site", script)
        self.assertNotIn("bench update", script)
        self.assertNotIn("drop-site", script)
        self.assertNotIn("bench restart", script)
        self.assertLess(script.index("backup --with-files"), script.index("bench get-app"))
        self.assertLess(script.index("backup --with-files"), script.index("install-app erpdevelopers"))

    def test_bench_registration_uses_supported_api_and_preserves_apps(self):
        script = (ROOT / "scripts/install_existing_site_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn("Bench(str(root))", script)
        self.assertIn("bench.apps.sync(app_name=app_name, app_dir=app_name, branch=\"version-16\")", script)
        self.assertIn('expected = set(old) | {app_name}', script)
        self.assertIn("shutil.copy2(source, destination)", script)
        self.assertLess(script.index("backup --with-files"), script.index("bench.apps.sync"))
        self.assertLess(script.index("bench.apps.sync"), script.index("install-app erpdevelopers"))
        self.assertNotIn("drop-site", script)
        self.assertNotIn("bench restart", script)

    def test_install_is_site_guarded(self):
        script = (ROOT / "scripts/install_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn('test ! -e "$BENCH/sites/$SITE"', script)
        self.assertIn("bench new-site", script)
        self.assertNotIn("bench update", script)
        self.assertNotIn("drop-site", script)


if __name__ == "__main__":
    unittest.main()
