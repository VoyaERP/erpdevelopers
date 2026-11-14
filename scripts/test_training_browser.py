"""Isolated browser regression on the real Training Jinja/CSS/JS.

This fixture replaces only Frappe's outer web shell and shared nav/footer.
YouTube and font requests are stubbed: this is NOT proof of live video playback.
Run with Playwright 1.57.0 browsers and Jinja2 3.1.6; no site or DB is touched.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, unquote, urlsplit
import csv
import mimetypes
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import expect, sync_playwright
from erpdevelopers.hooks import web_include_css
from erpdevelopers.public_pages import set_public_context

APP = ROOT / "erpdevelopers"
PUBLIC = (APP / "public").resolve()
PLAYLIST = "PLabcdefghijklmnopqrst0123456"
with (APP / "translations/ar.csv").open(encoding="utf-8", newline="") as stream:
    ARABIC = dict(csv.reader(stream))
BASE = '''<!doctype html><html lang="{{ boot.lang }}" dir="{{ 'rtl' if boot.lang == 'ar' else 'ltr' }}">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{% block head_include %}{% for css in web_include_css %}<link rel="stylesheet" href="{{ css }}">{% endfor %}{% endblock %}
</head><body data-path="training">{% block navbar %}{% endblock %}{% block page_container %}{% endblock %}{% block footer %}{% endblock %}</body></html>'''
OVERRIDES = {"templates/web.html": BASE}
for part in ("nav", "footer", "assistant"):
    OVERRIDES[f"templates/includes/erpdevelopers_{part}.html"] = ""
ENV = Environment(loader=ChoiceLoader([DictLoader(OVERRIDES), FileSystemLoader(APP)]),
                  autoescape=select_autoescape(["html"]))


def render(lang):
    ctx = SimpleNamespace()
    set_public_context(ctx, slug="training", title="Training", description="Browser regression fixture")
    values = vars(ctx)
    values.update(
        boot=SimpleNamespace(lang=lang), web_include_css=web_include_css,
        _=(lambda value: ARABIC.get(value, value)) if lang == "ar" else (lambda value: value),
        is_authenticated=False, topics=["Solution Architecture"],
        playlists=[dict(title="Public playlist", title_ar="\u0642\u0627\u0626\u0645\u0629 \u062a\u0634\u063a\u064a\u0644 \u0639\u0627\u0645\u0629", topic="Solution Architecture",
                        level="Beginner", language="English", description="Reviewed training collection",
                        visibility="Public", playlist_id=PLAYLIST,
                        watch_url=f"https://www.youtube.com/playlist?list={PLAYLIST}")],
    )
    return ENV.get_template("www/training.html").render(values).encode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/training":
            lang = parse_qs(url.query).get("lang", ["en"])[0]
            payload, kind = render(lang), "text/html; charset=utf-8"
        elif url.path.startswith("/assets/erpdevelopers/"):
            relative = unquote(url.path.removeprefix("/assets/erpdevelopers/"))
            path = (PUBLIC / relative).resolve()
            if not path.is_relative_to(PUBLIC) or not path.is_file():
                self.send_error(404)
                return
            payload = path.read_bytes()
            kind = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def routes(context, requests):
    def embed(route):
        requests.append(route.request.url)
        route.fulfill(content_type="text/html", body="<!doctype html><title>Mock YouTube embed</title>")
    context.route("https://www.youtube-nocookie.com/**", embed)
    context.route("https://www.youtube.com/**", lambda r: r.fulfill(content_type="text/html", body="<title>External YouTube</title>"))
    context.route("https://fonts.googleapis.com/**", lambda r: r.fulfill(content_type="text/css", body=""))
    context.route("https://fonts.gstatic.com/**", lambda r: r.abort())


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    cases = 0
    try:
        with sync_playwright() as p:
            for engine in (p.chromium, p.firefox):
                browser = engine.launch(headless=True)
                try:
                    for lang in ("en", "ar"):
                        for width in (1440, 390):
                            context = browser.new_context(viewport={"width": width, "height": 900})
                            requests = []
                            routes(context, requests)
                            page = context.new_page()
                            errors = []
                            page.on("pageerror", lambda error: errors.append(str(error)))
                            page.goto(f"{origin}/training?lang={lang}")
                            watch = page.locator("[data-playlist-open]")
                            expect(watch).to_be_enabled()
                            assert watch.evaluate("e => e.tagName") == "BUTTON"
                            assert watch.get_attribute("href") is None
                            assert requests == [], "YouTube was contacted before consent"
                            if lang == "ar":
                                for selector in ("#ed-training-title", "[data-playlist-open]"):
                                    assert "Tajawal" in page.locator(selector).evaluate("e => getComputedStyle(e).fontFamily")
                            watch.click()
                            dialog = page.locator("#ed-playlist-dialog")
                            expect(dialog).to_be_visible()
                            assert dialog.evaluate("e => e.matches(':modal')")
                            assert len(context.pages) == 1, "Watch here opened a tab"
                            assert page.url == f"{origin}/training?lang={lang}"
                            frame = page.locator("[data-player-frame]")
                            src = urlsplit(frame.get_attribute("src"))
                            assert src.netloc == "www.youtube-nocookie.com"
                            assert parse_qs(src.query)["list"] == [PLAYLIST]
                            page.keyboard.press("Escape")
                            expect(dialog).not_to_be_visible()
                            assert frame.get_attribute("src") is None
                            expect(watch).to_be_focused()
                            with context.expect_page() as pending:
                                page.locator(".ed-playlist-actions > a").click()
                            popup = pending.value
                            popup.wait_for_load_state("domcontentloaded")
                            assert popup.url == f"https://www.youtube.com/playlist?list={PLAYLIST}"
                            assert errors == [], errors
                            context.close()
                            cases += 1
                            print(f"PASS {engine.name}: {lang}, {width}px, modal/external/focus/typography", flush=True)
                    context = browser.new_context()
                    routes(context, [])
                    context.route("**/assets/erpdevelopers/js/catalog.js*", lambda r: r.abort())
                    page = context.new_page()
                    page.goto(f"{origin}/training")
                    expect(page.locator("[data-playlist-open]")).to_be_disabled()
                    assert page.locator("[data-playlist-open]").get_attribute("href") is None
                    expect(page.locator(".ed-playlist-actions > a")).to_be_visible()
                    context.close()
                    cases += 1
                    print(f"PASS {engine.name}: blocked script leaves a disabled button, not a disguised link", flush=True)
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(f"{cases} isolated browser cases passed. Live YouTube playback remains a site UAT check.")


if __name__ == "__main__":
    main()
