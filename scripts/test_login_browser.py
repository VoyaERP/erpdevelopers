"""Presentation QA on the native Frappe v16.56.0 login template.

Core sources are downloaded read-only and checked against inspected Git blob IDs.
The outer web shell and utility CSS are fixtures; no core file is overwritten.
We render native authentication states, not perform logins or test a real server.
No passwords, user data, mail requests or authentication calls are submitted.
"""
from hashlib import sha1
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, unquote, urlsplit
from urllib.request import urlopen, Request
import gettext
import mimetypes
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from babel.messages.mofile import write_mo
from babel.messages.pofile import read_po
from jinja2 import DictLoader, Environment, select_autoescape
from markupsafe import Markup
from playwright.sync_api import expect, sync_playwright
from erpdevelopers.hooks import web_include_css
from erpdevelopers.branding import LOGO_URL

APP = ROOT / "erpdevelopers"
PUBLIC = (APP / "public").resolve()
OUTPUT = ROOT / "test-artifacts/login"
SOURCES = {
    "www/login.html": "4302103f27d75c7bc14e18d3a2bc5477cfcc7fd1",
    "templates/includes/login/macros.html": "492254e64761966b5b0e561c057d837443d068f4",
    "templates/includes/login/login.js": "bb13da580bb6bc312a23b368a7f82ec5d61f2a97",
}


def load_core():
    result = {}
    for path, expected in SOURCES.items():
        request = Request("https://raw.githubusercontent.com/frappe/frappe/v16.56.0/frappe/" + path,
                          headers={"User-Agent": "ERPDevelopers-native-login-QA"})
        with urlopen(request, timeout=30) as response:
            content = response.read(500_000)
        digest = sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if digest != expected:
            raise RuntimeError("Core fixture hash changed; inspect source before updating pin: " + path)
        result[path] = content.decode("utf-8")
    return result


with (APP / "locale/ar.po").open("rb") as stream:
    catalog = read_po(stream, locale="ar")
compiled = BytesIO()
write_mo(compiled, catalog)
compiled.seek(0)
AR = gettext.GNUTranslations(compiled)

# Only the shell/utilities are fixtures. The forms, labels and messages are native.
BASE = '''<!doctype html><html lang="{{ boot.lang }}" dir="{{ 'rtl' if boot.lang == 'ar' else 'ltr' }}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body{margin:0} .flex{display:flex}.flex-col{flex-direction:column}.items-start{align-items:flex-start}
.gap-4{gap:16px}.gap-5{gap:20px}.gap-8{gap:32px}.gap-3{gap:12px}.gap-2{gap:8px}.gap-1\\.5{gap:6px}
.w-full,.email-field,.password-field{width:100%}.mb-0{margin-bottom:0}.mt-0{margin-top:0}.hidden{display:none}
.page_content>div>section{display:none}.page_content>div>section.for-{{ view }}{display:block}
input,button{font:inherit}.es-button{display:flex;align-items:center;justify-content:center;border:0;border-radius:8px;text-decoration:none;background:#f3f4f6}
.icon-sm{width:16px;height:16px}.page-card-head{text-align:left}.text-right{text-align:right}
</style>
{% for css in web_include_css %}<link rel="stylesheet" href="{{ css }}">{% endfor %}
{% block head_include %}{% endblock %}</head>
<body data-path="login"><nav class="navbar"><div class="container"><a class="navbar-brand" href="/"><img src="{{ logo }}" alt="ERP Developers"></a>
<div id="language-switcher"><select><option>{{ 'العربية' if boot.lang == 'ar' else 'English' }}</option></select></div></div></nav>
<div id="page-login"><div class="page-content-wrapper"><main><div class="page_content">{% block page_content %}{% endblock %}</div></main></div></div></body></html>'''
ENV = None


def render(params):
    lang = "ar" if params.get("_lang", ["en"])[0] == "ar" else "en"
    view = params.get("view", ["login"])[0]
    if view not in {"login", "forgot", "login-with-email-link", "signup"}:
        view = "login"
    return ENV.get_template("www/login.html").render(
        boot=SimpleNamespace(lang=lang), _=AR.gettext if lang == "ar" else (lambda text: text),
        web_include_css=web_include_css, view=view, logo=LOGO_URL,
        disable_signup=True, disable_user_pass_login=False, show_language_picker=True,
        login_with_email_link=True, social_login=False, ldap_settings=None,
        include_style=lambda path: Markup(""), for_test="Native login presentation test",
    ).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/login":
            payload, kind = render(parse_qs(url.query)), "text/html; charset=utf-8"
        elif url.path.startswith("/assets/erpdevelopers/"):
            path = (PUBLIC / unquote(url.path.removeprefix("/assets/erpdevelopers/"))).resolve()
            if not path.is_relative_to(PUBLIC) or not path.is_file():
                self.send_error(404); return
            payload = path.read_bytes()
            kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        else:
            self.send_error(404); return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    global ENV
    sources = load_core()
    messages = set()
    for source in sources.values():
        messages.update(m.group(2) for m in re.finditer(r'''\b_\(\s*(["'])(.*?)\1\s*\)''', source))
    missing = sorted(text for text in messages if text != "jane@example.com" and AR.gettext(text) == text)
    assert not missing, "Untranslated native login/JS messages: " + repr(missing)
    print(f"PASS: {len(messages) - 1} native login and JS message IDs have compiled Arabic translations", flush=True)
    sources["templates/web.html"] = BASE
    ENV = Environment(loader=DictLoader(sources), autoescape=select_autoescape(["html"]))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    cases = 0
    try:
        with sync_playwright() as playwright:
            for engine in (playwright.chromium, playwright.firefox):
                browser = engine.launch(headless=True)
                try:
                    for lang in ("en", "ar"):
                        for width in (1440, 390):
                            context = browser.new_context(viewport={"width": width, "height": 900})
                            context.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(content_type="text/css", body=""))
                            context.route("https://fonts.gstatic.com/**", lambda r: r.abort())
                            page = context.new_page()
                            errors = []
                            page.on("pageerror", lambda e: errors.append(str(e)))
                            for view in ("login", "forgot", "login-with-email-link", "signup"):
                                page.goto(f"{origin}/login?_lang={lang}&view={view}")
                                section = page.locator("section.for-" + view)
                                expect(section).to_be_visible()
                                heading = section.locator("h4")
                                expected = {"login": "Sign In", "forgot": "Forgot Password?", "login-with-email-link": "Sign In", "signup": "Sign Up"}[view]
                                expect(heading).to_have_text(AR.gettext(expected) if lang == "ar" else expected)
                                assert page.locator('nav.navbar .navbar-brand img').count() == 1
                                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                                geometry = page.evaluate('''() => {
                                  const wrapper = document.querySelector('.page-content-wrapper');
                                  const before = getComputedStyle(wrapper, '::before');
                                  const after = getComputedStyle(wrapper, '::after');
                                  const main = getComputedStyle(wrapper.querySelector('main'));
                                  return {beforeColumn:before.gridColumnStart,afterColumn:after.gridColumnStart,
                                    afterRow:after.gridRowStart,mainColumn:main.gridColumnStart,mainRow:main.gridRowStart,
                                    position:after.position,content:after.content};
                                }''')
                                assert geometry["content"] in ("none", "normal", '""'), "Login must not repeat the slogan"
                                assert geometry["beforeColumn"] == "1"
                                if width > 720:
                                    assert geometry["mainColumn"] == "2"
                                else:
                                    assert geometry["mainRow"] == "2"
                                if lang == "ar":
                                    assert "Tajawal" in heading.evaluate("e => getComputedStyle(e).fontFamily")
                                    assert "Engage" not in geometry["content"]
                                    for english in ("Sign In", "Welcome!", "Forgot password?", "Send login link", "Signups have been disabled"):
                                        assert english not in section.inner_text()
                                if view == "login":
                                    field = page.locator("#login_password")
                                    icon = page.locator(".toggle-password")
                                    expect(icon).to_be_visible()
                                    a, b = field.bounding_box(), icon.bounding_box()
                                    assert b["x"] > a["x"] + a["width"] / 2
                                    assert b["x"] + b["width"] <= a["x"] + a["width"]
                                    assert float(field.evaluate("e => parseFloat(getComputedStyle(e).paddingRight)")) >= 40
                                    if engine.name == "chromium":
                                        page.screenshot(path=str(OUTPUT / f"login-{lang}-{width}.png"), full_page=True)
                                assert not errors, errors
                                cases += 1
                            context.close()
                            print(f"PASS {engine.name}: {lang} {width}px, four native auth states, translation and layout", flush=True)
                finally:
                    browser.close()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
    print(f"{cases} presentation cases passed; real authentication and site overrides need live UAT.")


if __name__ == "__main__":
    main()
