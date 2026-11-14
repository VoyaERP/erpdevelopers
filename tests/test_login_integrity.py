from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


class TestNativeLogin(unittest.TestCase):
    def test_css_first_paint_without_auth_overrides(self):
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("web_include_css = [login_stylesheet_url()]", hooks)
        self.assertNotIn("web_include_js", hooks)
        self.assertNotIn("login_chrome.js", hooks)
        self.assertNotIn("override_whitelisted_methods", hooks)
        self.assertNotIn("base_template_map", hooks)
        self.assertFalse((APP / "public/js/login_chrome.js").exists())
        self.assertFalse((ROOT / "tests/login_chrome_dom.test.cjs").exists())
    def test_native_frappe_login_is_styled_without_dom_replacement(self):
        css = (APP / "public/css/login.css").read_text(encoding="utf-8")
        self.assertIn("FIRST PAINT", css)
        self.assertIn('body[data-path="login"]', css)
        self.assertIn('> nav.navbar', css)
        self.assertIn("#language-switcher", css)
        self.assertIn(".page-content-wrapper::before", css)
        self.assertIn(".page-content-wrapper > main", css)
        self.assertIn(".page-card-head .app-logo", css)
        self.assertIn("login-network.svg", css)
        self.assertIn('html[lang^="ar"]', css)
        self.assertIn("@media(max-width:720px)", css)
        self.assertNotIn(".ed-login-website", css)
        self.assertTrue((APP / "public/images/login-network.svg").is_file())
    def test_ci_checks_static_css_first_paint_contract(self):
        workflow = (ROOT / ".github/workflows/v16-static-validation.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertNotIn("login_chrome_dom", workflow)
        self.assertNotIn("login_chrome.js", workflow)
    def test_navbar_and_login_logo_use_unmodified_approved_png(self):
        from erpdevelopers import branding
        settings = branding.website_settings_values()
        self.assertEqual(settings["app_logo"], branding.LOGO_URL)
        self.assertEqual(
            branding.desk_navbar_settings_values()["app_logo"], branding.LOGO_URL
        )
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("app_logo_url = LOGO_URL", hooks)
        self.assertEqual(settings["banner_image"], branding.LOGO_URL)
        self.assertEqual(settings["favicon"], branding.FAVICON_URL)
        self.assertIn('src="' + branding.LOGO_URL + '"', settings["brand_html"])
        self.assertIn('alt="ERP Developers', settings["brand_html"])
        self.assertEqual(settings["show_language_picker"], 1)
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
        self.assertNotIn('node --check "$APP/erpdevelopers/public/js/login_chrome.js"', script)
        self.assertIn('test ! -e "$APP/erpdevelopers/public/js/login_chrome.js"', script)
        self.assertLess(script.index("unittest discover"), script.index('bench --site "$SITE" migrate'))

    def test_native_navbar_logo_parser_accepts_equivalent_html(self):
        from importlib.util import module_from_spec, spec_from_file_location
        spec = spec_from_file_location(
            "inspect_login_brand", ROOT / "scripts/inspect_login_brand.py"
        )
        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        logo = "/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
        for markup in (
            '<a class="navbar-brand"><img src="' + logo + '" alt="ERP Developers"></a>',
            "<a href='/' class='navbar-brand'><img width='210' alt='ERP Developers' src='"
            + logo + "'></a>",
            '<a class="navbar-brand"><img class="brand" src="https://erp-developers.com'
            + logo + '?v=4"></a>',
        ):
            with self.subTest(markup=markup):
                self.assertTrue(module.inspect_markup(markup)[0])

        self.assertFalse(
            module.inspect_markup('<a class="navbar-brand">ERP Developers</a>')[0]
        )
        self.assertFalse(
            module.inspect_markup('<a class="navbar-brand"><img src="/wrong.png"></a>'
                                  '<img class="app-logo" src="' + logo + '">')[0]
        )
        self.assertFalse(
            module.inspect_markup('<a class="navbar-brand">'
                                  '<img src="https://other.example' + logo + '"></a>')[0]
        )

    def test_frontend_verifier_compares_real_css_and_images(self):
        script = (ROOT / "scripts/verify_frontend.sh").read_text(encoding="utf-8")
        self.assertIn("--resolve", script)
        self.assertIn("brand.css?v=$DIGEST", script)
        self.assertIn('cmp -s "$APP/erpdevelopers/public/css/brand.css" "$TMP/brand.css"', script)
        self.assertIn("erpdevelopers-selected-logo.png", script)
        self.assertIn('scripts/inspect_login_brand.py', script)
        self.assertNotIn("grep -Fq '<img src=", script)
        self.assertIn("erpdevelopers-selected-favicon.png", script)
        self.assertIn('CARD_COUNT=', script)
        self.assertIn("Learning Academy", script)
        self.assertIn("LOGIN_DIGEST=", script)
        self.assertIn("LOGIN_CSS=", script)
        self.assertIn("SIGNIN_HREF=", script)
        self.assertIn('"/login?redirect-to=/desk"', script)
        self.assertIn("login_chrome.js", script)
        self.assertIn('cmp -s "$APP/erpdevelopers/public/css/login.css" "$TMP/login.css"', script)
        self.assertIn("?_lang=ar", script)
        self.assertIn("بوابة المطورين", script)
        self.assertIn('id="language-switcher"', script)
        self.assertNotIn("bench migrate", script)

    def test_existing_site_installer_recognizes_upstream_remote(self):
        installer = (ROOT / "scripts/install_existing_site_erptest_lightnode.sh").read_text(encoding="utf-8")
        self.assertIn("for name in upstream origin", installer)
        self.assertNotIn("remote set-url", installer)

    def test_native_login_views_stay_under_frappe_control(self):
        css = (APP / "public/css/login.css").read_text(encoding="utf-8")
        hooks = (APP / "hooks.py").read_text(encoding="utf-8")
        self.assertIn("web_include_css", hooks)
        self.assertNotIn("web_include_js", hooks)
        self.assertNotIn(".for-login {", css)
        self.assertNotIn(".for-forgot {", css)
        self.assertNotIn(".for-signup {", css)
        self.assertFalse((APP / "www/login.html").exists())
        self.assertFalse((APP / "www/login.py").exists())
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
        self.assertEqual(home.count('href="{{ desk_signin_url | e }}"'), 2)
        self.assertEqual(home.count('{{ _("Desk sign in") }}'), 2)
        self.assertNotIn('href="/login"', home)
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
