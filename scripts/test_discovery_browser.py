"""Vision and guide browser checks; reuse the existing isolated HTTP/Jinja fixture.

Real application templates, navigation, footer and styles are used. Frappe's
outer shell and font delivery are fixtures, not live production verification.
"""
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
import json

import test_training_browser as fixture
from playwright.sync_api import expect, sync_playwright
from erpdevelopers.guide_content import GUIDES, set_guide_context
from erpdevelopers.www.erp_developers_home import get_context as homepage_context

# Retain real navigation/footer, but not the unrelated floating assistant.
for part in ("nav", "footer"):
    fixture.OVERRIDES.pop(f"templates/includes/erpdevelopers_{part}.html", None)
fixture.OVERRIDES["templates/web.html"] = fixture.BASE.replace(
    "<style>body{margin:0}</style>",
    "<style>body{margin:0}</style><title>{{ title | e }}</title>"
    '<meta name="description" content="{{ description | e }}">'
)


def render(route, lang):
    ctx = SimpleNamespace()
    if not route or route == "erp-developers-home":
        homepage_context(ctx)
        template = "erp-developers-home"
    else:
        set_guide_context(ctx, route, lang)
        template = route
    values = vars(ctx)
    values.update(boot=SimpleNamespace(lang=lang), web_include_css=fixture.web_include_css,
                  fixture_route=route, _=(lambda s: fixture.ARABIC.get(s, s)) if lang == "ar" else (lambda s:s))
    return fixture.ENV.get_template(f"www/{template}.html").render(values).encode()


class Handler(fixture.Handler):
    def do_GET(self):
        url = urlsplit(self.path)
        route = url.path.lstrip("/")
        if route not in ("", "erp-developers-home", *GUIDES):
            return super().do_GET()
        cookie = SimpleCookie(self.headers.get("Cookie", ""))
        preferred = cookie.get("preferred_language")
        default = preferred.value if preferred else "en"
        language = parse_qs(url.query).get("_lang", [default])[0]
        language = "ar" if language == "ar" else "en"
        payload = render(route, language)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    output = Path("test-artifacts/discovery")
    output.mkdir(parents=True, exist_ok=True)
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
                        for width in (1440, 768, 390, 320):
                            context = browser.new_context(viewport={"width": width, "height": 900})
                            fixture.routes(context, [])
                            context.add_cookies([dict(name="preferred_language", value=lang, url=origin)])
                            page = context.new_page()
                            errors = []
                            page.on("pageerror", lambda error: errors.append(str(error)))
                            page.goto(f"{origin}/?_lang={lang}")
                            page.locator('a[href="/#vision"]').click()
                            expect(page).to_have_url(f"{origin}/#vision")
                            vision = page.locator("#vision")
                            expect(vision).to_be_visible()
                            signature = vision.locator("[data-brand-slogan]")
                            expect(page.locator("[data-brand-slogan]")).to_have_count(1)
                            expect(page.locator(".ed-principles")).to_have_count(0)
                            expect(signature).to_be_visible()
                            expected_words = [fixture.ARABIC.get(word, word) if lang == "ar" else word
                                              for word in ("Engage.", "Reason.", "Progress.")]
                            expect(signature.locator("span")).to_have_text(expected_words)
                            assert signature.get_attribute("dir") == ("rtl" if lang == "ar" else "ltr")
                            assert signature.locator("a,button").count() == 0
                            assert signature.bounding_box()["y"] >= page.locator("#ed-vision-heading").bounding_box()["y"] + page.locator("#ed-vision-heading").bounding_box()["height"]
                            words = signature.locator("span").evaluate_all("els=>els.map(e=>({y:e.getBoundingClientRect().y,bg:getComputedStyle(e).backgroundColor,border:getComputedStyle(e).borderTopWidth}))")
                            assert max(w["y"] for w in words) - min(w["y"] for w in words) < 1, "Slogan wraps at normal mobile size"
                            assert all(w["bg"] == "rgba(0, 0, 0, 0)" and w["border"] == "0px" for w in words), "No pill decoration"
                            page.wait_for_function("document.querySelector('.ed-vision-image').complete && document.querySelector('.ed-vision-image').naturalWidth > 0")
                            size = vision.bounding_box()
                            offset = vision.evaluate("e => parseFloat(getComputedStyle(e).getPropertyValue('--ed-header-anchor-offset'))")
                            assert size["height"] >= 900 - offset - 1
                            header = page.locator(".ed-nav").bounding_box()
                            heading = page.locator("#ed-vision-heading").bounding_box()
                            assert heading["y"] >= header["y"] + header["height"] - 1, "Sticky header covers vision text"
                            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                            assert len(context.pages) == 1
                            assert errors == [], errors
                            if engine.name == "chromium":
                                page.screenshot(path=str(output / f"vision-{lang}-{width}.png"), animations="disabled")
                            cases += 1
                            print(f"PASS {engine.name}: vision {lang} {width}px, local image, full height, anchor and header", flush=True)

                            for slug in GUIDES:
                                page.goto(f"{origin}/{slug}?_lang={lang}")
                                expect(page.locator("h1")).to_have_count(1)
                                expect(page.locator("#ed-guide-title")).to_have_text(GUIDES[slug][lang]["heading"])
                                expect(page).to_have_title(GUIDES[slug][lang]["title"] + " | ERP Developers")
                                expect(page.locator(".ed-guide-article > section")).to_have_count(6 if slug == "erpnext-development" else 5)
                                canonical = f"https://erp-developers.com/{slug}?_lang={lang}"
                                expect(page.locator('link[rel="canonical"]')).to_have_count(1)
                                assert page.locator('link[rel="canonical"]').get_attribute("href") == canonical
                                for code in ("en", "ar"):
                                    assert page.locator(f'link[hreflang="{code}"]').get_attribute("href") == f"https://erp-developers.com/{slug}?_lang={code}"
                                graph = json.loads(page.locator('script[type="application/ld+json"]').inner_text())
                                assert graph["@graph"][0]["url"] == canonical
                                assert graph["@graph"][0]["inLanguage"] == lang
                                assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
                                if lang == "ar":
                                    assert "Tajawal" in page.locator("#ed-guide-title").evaluate("e => getComputedStyle(e).fontFamily")
                                assert errors == [], errors
                                cases += 1
                                print(f"PASS {engine.name}: {slug} {lang} {width}px, content and SEO metadata", flush=True)
                            context.close()
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(f"{cases} discovery browser cases passed; not a live indexing or production test.")


if __name__ == "__main__":
    main()
