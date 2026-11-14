"""Real Events template and image layout in isolated EN/AR browser fixtures.

No production uploads/permissions are exercised. Generated raster bytes are test
fixtures only and are not seeded or deployed as real event photographs.
"""
from http.server import ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

from PIL import Image
from playwright.sync_api import expect, sync_playwright
from test_training_browser import ENV, ARABIC, Handler as BaseHandler, routes, web_include_css
from erpdevelopers.public_pages import set_public_context
from erpdevelopers.branding import versioned_public_asset
from erpdevelopers.event_rules import TOPICS, FORMATS

ARTIFACTS = Path("test-artifacts/event-media")
ARTIFACTS.mkdir(parents=True, exist_ok=True)
stream = BytesIO()
Image.new("RGB", (960, 540), (22, 103, 150)).save(stream, format="PNG")
IMAGE = stream.getvalue()


def render(lang):
    ctx = SimpleNamespace()
    set_public_context(ctx, slug="events", title="Events", description="Isolated photo fixture")
    caption = "Poster <script>bad()</script>"
    arabic_caption = "\u063a\u0644\u0627\u0641 \u0627\u0644\u0641\u0639\u0627\u0644\u064a\u0629"
    row = dict(title="Test technology event", title_ar="\u0641\u0639\u0627\u0644\u064a\u0629 \u062a\u0642\u0646\u064a\u0629", topic="Solution Architecture",
        event_format="In person", event_type="Conference", event_status="Scheduled", organizer="Test organizer",
        description="Test-only event", description_ar="", city="Riyadh", country="Saudi Arabia", venue="Test venue",
        start_date="2030-05-10", end_date="2030-05-10", start_date_label="10 May 2030", date_only=1,
        time_zone="Asia/Riyadh", verified_on_label="14 Nov 2026", event_url="https://example.com/event", source_url="",
        media={"cover": {"url": "/files/cover.png", "caption": caption, "caption_ar": arabic_caption},
               "gallery": [{"url": "/files/room.png", "caption": "Room", "caption_ar": "\u0627\u0644\u0642\u0627\u0639\u0629"},
                           {"url": "/files/agenda.png", "caption": "Agenda", "caption_ar": "\u0627\u0644\u0628\u0631\u0646\u0627\u0645\u062c"}]})
    values = vars(ctx)
    values.update(boot=SimpleNamespace(lang=lang), fixture_route="events", web_include_css=web_include_css,
        _=(lambda value: ARABIC.get(value, value)) if lang == "ar" else (lambda value: value),
        event_rows=[row], countries=["Saudi Arabia"], topics=TOPICS, formats=FORMATS,
        selected={"country": "", "topic": "", "event_format": "", "period": "upcoming", "page": 1},
        total=1, pages=1, previous_url=None, next_url=None, can_manage_events=False,
        events_css_url=versioned_public_asset("css/events.css"))
    return ENV.get_template("www/events.html").render(values).encode()


class Handler(BaseHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/events":
            lang = parse_qs(url.query).get("_lang", ["en"])[0]
            payload, kind = render(lang), "text/html; charset=utf-8"
        elif url.path in ("/files/cover.png", "/files/room.png", "/files/agenda.png"):
            payload, kind = IMAGE, "image/png"
        else:
            return super().do_GET()
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    count = 0
    try:
        with sync_playwright() as p:
            for engine in (p.chromium, p.firefox):
                browser = engine.launch(headless=True)
                try:
                    for lang in ("en", "ar"):
                        for width in (1440, 390):
                            context = browser.new_context(viewport={"width": width, "height": 1000})
                            routes(context, [])
                            page = context.new_page()
                            errors = []
                            page.on("pageerror", lambda e: errors.append(str(e)))
                            page.goto(f"http://127.0.0.1:{server.server_port}/events?_lang={lang}")
                            card = page.locator(".ed-event-card")
                            card.scroll_into_view_if_needed()
                            cover = card.locator(".ed-event-cover img")
                            expect(cover).to_be_visible()
                            page.wait_for_function("document.querySelector('.ed-event-cover img').naturalWidth === 960")
                            expect(card.locator("script")).to_have_count(0)
                            self_caption = "\u063a\u0644\u0627\u0641 \u0627\u0644\u0641\u0639\u0627\u0644\u064a\u0629" if lang == "ar" else "Poster <script>bad()</script>"
                            expect(cover).to_have_attribute("alt", self_caption)
                            expect(card.locator(".ed-event-cover figcaption")).to_have_text(self_caption)
                            gallery = card.locator(".ed-event-gallery")
                            expect(gallery.locator(".ed-event-gallery-grid")).not_to_be_visible()
                            gallery.locator("summary").focus()
                            page.keyboard.press("Enter")
                            expect(gallery.locator(".ed-event-gallery-grid")).to_be_visible()
                            expect(gallery.locator("img")).to_have_count(2)
                            assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1")
                            assert len(context.pages) == 1
                            assert errors == [], errors
                            if engine.name == "chromium":
                                card.screenshot(path=str(ARTIFACTS / f"event-photos-{lang}-{width}.png"))
                            context.close()
                            count += 1
                            print(f"PASS {engine.name}: event cover/gallery {lang}, {width}px, image bytes/keyboard/escaping/overflow", flush=True)
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(f"{count} event photo browser cases passed; native Frappe upload UAT is separate.")


if __name__ == "__main__":
    main()
