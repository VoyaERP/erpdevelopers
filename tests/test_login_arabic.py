"""Native Arabic login copy, RTL layout and complete deployment-runner contracts."""
from importlib.util import module_from_spec, spec_from_file_location
from io import BytesIO
from pathlib import Path
from unittest import TestCase
import gettext
import re
import subprocess
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"


def compiled_catalog():
    with (APP / "locale/ar.po").open("rb") as stream:
        catalog = read_po(stream, locale="ar")
    output = BytesIO()
    write_mo(output, catalog)
    output.seek(0)
    return gettext.GNUTranslations(output)


class TestArabicNativeLogin(TestCase):
    def test_screenshot_strings_are_real_compiled_translations(self):
        translator = compiled_catalog()
        for text in ("Sign In", "Welcome! Please sign in to continue.", "Forgot password?",
                     "Email", "Password", "Continue", "Login with Email Link"):
            with self.subTest(text=text):
                translated = translator.gettext(text)
                self.assertNotEqual(text, translated)
                self.assertRegex(translated, r"[\u0600-\u06ff]")
        self.assertEqual(translator.gettext("Sign In"), "تسجيل الدخول")

    def test_recovery_email_link_and_verification_copy_is_covered(self):
        translator = compiled_catalog()
        for text in ("Forgot Password?", "Please enter your email, we'll send you password reset link",
                     "Send Link", "Back to sign in", "Please check your email.",
                     "Didn't receive the link?", "Resend", "Send login link", "Login with password",
                     "Verification", "Verification Code", "Verify", "Login token required",
                     "Invalid credentials, try again.", "Email is required.", "Password is required."):
            with self.subTest(text=text):
                self.assertNotEqual(translator.gettext(text), text)

    def test_translation_format_parameters_are_preserved(self):
        with (APP / "locale/ar.po").open("rb") as stream:
            catalog = read_po(stream, locale="ar")
        for message in catalog:
            if message.id and isinstance(message.id, str):
                with self.subTest(text=message.id):
                    self.assertEqual(set(re.findall(r"\{\d+\}", message.id)),
                                     set(re.findall(r"\{\d+\}", message.string or "")))

    def test_login_has_no_repeated_slogan_and_preserves_native_forms(self):
        css = (APP / "public/css/login.css").read_text()
        self.assertNotIn(".page-content-wrapper::after", css)
        self.assertNotIn("Engage.", css)
        self.assertNotIn("نتواصل.", css)
        self.assertIn("padding-inline-end:44px", css)
        self.assertIn('font-family:"Tajawal",Arial,sans-serif', css)
        self.assertNotIn("Noto Sans Arabic", css)
        self.assertNotIn('content:"تسجيل الدخول"', css, "Native headings are translated, not concealed with CSS")
        self.assertFalse((APP / "www/login.html").exists())
        self.assertFalse((APP / "www/login.py").exists())


class TestArabicLoginInspector(TestCase):
    @classmethod
    def setUpClass(cls):
        spec = spec_from_file_location("login_ar_inspector", ROOT / "scripts/inspect_arabic_login.py")
        cls.module = module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_translated_visible_section_passes(self):
        html = '<html lang="ar"><section class="for-login"><h4>تسجيل الدخول</h4><p>مرحباً بك!</p><a>هل نسيت كلمة المرور؟</a></section></html>'
        self.assertEqual(self.module.inspect_markup(html), [])

    def test_english_heading_fails_despite_arabic_elsewhere(self):
        html = '<html lang="ar"><section class="for-login"><h4>Sign In</h4><p>Welcome! Please sign in to continue.</p></section><footer>تسجيل الدخول مرحباً بك!</footer></html>'
        self.assertTrue(self.module.inspect_markup(html))

    def test_native_javascript_literals_do_not_create_false_positives(self):
        html = '<html lang="ar"><section class="for-login"><h4>تسجيل الدخول</h4><p>مرحباً بك!</p></section><script>const source="Sign In";</script></html>'
        self.assertEqual(self.module.inspect_markup(html), [])

    def test_untranslated_action_is_detected(self):
        html = '<html lang="ar"><section class="for-login"><h4>تسجيل الدخول</h4><p>مرحباً بك!</p><a>Forgot password?</a></section></html>'
        self.assertTrue(self.module.inspect_markup(html))


class TestCompleteDeploymentRunner(TestCase):
    def test_script_is_complete_bash_without_running_it(self):
        script = ROOT / "scripts/deploy_erptest_lightnode.sh"
        result = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_runner_reuses_updater_and_gates_restart_and_verification(self):
        script = (ROOT / "scripts/deploy_erptest_lightnode.sh").read_text()
        self.assertIn('EXPECTED_SHA="${EXPECTED_SHA:-}"', script)
        self.assertIn('git -C "$APP" merge-base --is-ancestor HEAD "$EXPECTED_SHA"', script)
        self.assertIn('scripts/update_erptest_lightnode.sh', script)
        update = script.index('bash "$TMP/update.sh"')
        restart = script.index('sudo supervisorctl restart "$WEB"')
        readiness = script.index('"https://$SITE/api/method/ping"')
        verify = script.index('bash "$APP/scripts/verify_frontend.sh"')
        self.assertLess(update, restart)
        self.assertLess(restart, readiness)
        self.assertLess(readiness, verify)
        self.assertIn('value.get("message") != "pong"', script)
        self.assertIn('--retry-max-time 60', script)
        self.assertIn('inspect_arabic_login.py', script)
        self.assertNotIn('bench --site', script, "The existing updater is the single migration implementation")
        self.assertNotIn('restart all', script.split('# Confirm')[0])
        self.assertNotIn('bench restart', script)
        self.assertNotIn('git reset', script)
        self.assertNotIn('eval ', script)
