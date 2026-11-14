"""Real public header: visible locale links, no hydration shift, EN/AR navigation.

Frappe's outer shell and session identities are isolated fixtures, not real logins.
The shipped script is tested with JS blocked/disabled and with the language API
unavailable. Native authentication and external font delivery are not tested here.
"""
from pathlib import Path
from threading import Thread
from types import ModuleType, SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch
import json
import os
import sys

import test_training_browser as fixture
from erpdevelopers.www.erp_developers_home import get_context as home_context
from playwright.sync_api import expect, sync_playwright

OUT = fixture.ROOT / "test-artifacts/navigation"
WIDTHS = (320, 390, 540, 768, 1100, 1101, 1360, 1361, 1440)
SCRIPT = fixture.APP / "public/js/language.js"
for part in ("nav", "footer"):
    fixture.OVERRIDES.pop(f"templates/includes/erpdevelopers_{part}.html", None)
fixture.OVERRIDES["templates/web.html"] = fixture.BASE.replace(
    "body{margin:0}", "body{margin:0}.hide{display:none!important}").replace(
    "</head>", "<script>window.show_language_picker={{ show_language_picker or 'false' }};</script></head>")
fixture.ENV.cache.clear()
ORIGINAL_RENDER = fixture.render


def request_module(params):
    fake = ModuleType("frappe")
    fake.local = SimpleNamespace(form_dict={key: value[0] for key, value in params.items()})
    fake.session = SimpleNamespace(user=params.get("test_user", ["Guest"])[0])
    return fake


def render(route, params):
    with patch.dict(sys.modules, {"frappe": request_module(params)}):
        return ORIGINAL_RENDER(route, params)


fixture.render = render


def render_home(params):
    lang = "ar" if params.get("_lang", ["en"])[0] == "ar" else "en"
    context = SimpleNamespace()
    with patch.dict(sys.modules, {"frappe": request_module(params)}):
        home_context(context)
    values = vars(context)
    values.update(boot=SimpleNamespace(lang=lang), fixture_route="home",
                  web_include_css=fixture.web_include_css,
                  _=(lambda s: fixture.ARABIC.get(s, s)) if lang == "ar" else (lambda s: s))
    return fixture.ENV.get_template("www/erp-developers-home.html").render(values).encode()


class Handler(fixture.Handler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/":
            payload = render_home(parse_qs(url.query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()


SNAPSHOT = """() => [...document.querySelectorAll(
 '.ed-nav,.ed-brand,.ed-brand img,.ed-nav-links,.ed-nav-tools,#language-switcher,.ed-nav-cta,.ed-nav-links a'
)].map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};})"""


def max_delta(before, after):
    assert len(before) == len(after)
    return max(abs(a[key] - b[key]) for a, b in zip(before, after) for key in a)


def check_header(page, lang):
    switch = page.locator("#language-switcher")
    expect(switch).to_be_visible()
    expect(switch).to_have_text("English" if lang == "ar" else "\u0627\u0644\u0639\u0631\u0628\u064a\u0629")
    assert switch.evaluate("e=>e.tagName") == "A"
    assert switch.get_attribute("data-language-switch") == ("en" if lang == "ar" else "ar")
    assert page.locator("header.ed-nav").count() == 1
    assert page.locator("#language-switcher").count() == 1
    assert page.locator(".ed-nav-links a").count() == 8
    assert page.evaluate("window.show_language_picker") is False
    assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    bad = page.locator(".ed-nav-links a,.ed-nav-cta,.ed-footer-links a,#language-switcher span").evaluate_all("""els=>els.flatMap(el=>{
      const range=document.createRange();range.selectNodeContents(el);
      const ys=[...new Set([...range.getClientRects()].filter(r=>r.width>0).map(r=>Math.round(r.y)))];
      return ys.length>1||el.scrollWidth>el.clientWidth+1?[el.textContent.trim()]:[];
    })""")
    assert not bad, bad
    bounds, tools = switch.bounding_box(), page.locator(".ed-nav-tools").bounding_box()
    assert bounds["height"] >= 44
    assert switch.evaluate("e=>e.scrollWidth<=e.clientWidth+1")
    assert bounds["x"] >= tools["x"] - 1
    assert bounds["x"] + bounds["width"] <= tools["x"] + tools["width"] + 1


def context_for(browser, width=390, **options):
    context = browser.new_context(viewport={"width": width, "height": 900}, reduced_motion="reduce", **options)
    fixture.routes(context, [])
    calls = []
    context.route("**/api/method/frappe.translate.get_all_languages*",
                  lambda route: (calls.append(route.request.url), route.abort()))
    return context, calls


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    server = fixture.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    measurements = []
    behavior_cases = 0
    try:
        with sync_playwright() as p:
            for engine_name in os.environ.get("ERPDEV_TEST_ENGINES", "chromium,firefox").split(","):
                engine = getattr(p, engine_name)
                executable = os.environ.get("CHROMIUM_EXECUTABLE") if engine_name == "chromium" else None
                browser = engine.launch(headless=True, **({"executable_path": executable} if executable else {}))
                try:
                    for lang in ("en", "ar"):
                        for width in WIDTHS:
                            for route in ("/", "/training", "/events"):
                                context, calls = context_for(browser, width)
                                context.route("**/assets/erpdevelopers/js/language.js*", lambda r: r.abort())
                                page = context.new_page()
                                errors = []
                                page.on("pageerror", lambda e: errors.append(str(e)))
                                page.goto(f"{origin}{route}?_lang={lang}")
                                check_header(page, lang)  # Visible even when its script cannot load.
                                before = page.evaluate(SNAPSHOT)
                                page.add_script_tag(path=str(SCRIPT))
                                page.add_script_tag(path=str(SCRIPT))  # Re-evaluation is idempotent.
                                delta = max_delta(before, page.evaluate(SNAPSHOT))
                                assert delta < 0.5, (lang, width, route, delta)
                                check_header(page, lang)
                                if width <= 1360:
                                    track = page.locator(".ed-nav-links")
                                    for link in page.locator(".ed-nav-links a").all():
                                        link.focus()
                                        expect(link).to_be_focused()
                                        link.evaluate("e=>e.scrollIntoView({block:'nearest',inline:'nearest'})")
                                        box, outer = link.bounding_box(), track.bounding_box()
                                        assert box["x"] >= outer["x"] - 1
                                        assert box["x"] + box["width"] <= outer["x"] + outer["width"] + 1
                                    page.locator(".ed-nav-links a").first.evaluate("e=>e.scrollIntoView({block:'nearest',inline:'nearest'})")
                                page.evaluate("window.scrollTo(0,300)")
                                assert abs(page.locator(".ed-nav").bounding_box()["y"]) < 1
                                page.evaluate("window.scrollTo(0,0)")
                                page.reload()
                                check_header(page, lang)
                                assert max_delta(before, page.evaluate(SNAPSHOT)) < 0.5
                                assert calls == [] and errors == [], (calls, errors)
                                if route == "/" and width in (390, 1440) and engine_name == "chromium":
                                    page.screenshot(path=OUT / f"language-{lang}-{width}.png")
                                measurements.append(dict(engine=engine_name, lang=lang, width=width, route=route, delta=delta))
                                context.close()
                            print(f"PASS {engine_name}: {lang} {width}px, visible control, fixed layout, refresh and keyboard", flush=True)

                    for user in ("Guest", "member@example.invalid", "Administrator"):
                        for javascript in (True, False):
                            context, calls = context_for(browser, java_script_enabled=javascript)
                            if javascript:
                                context.add_init_script("window.frappe={session:{user:" + json.dumps(user) + "}};")
                            page = context.new_page()
                            url = f"{origin}/events?topic=Cloud%20%26%20DevOps&country=United%20Arab%20Emirates&_lang=en"
                            page.goto(url + "#content")
                            if javascript:
                                page.evaluate("location.hash = 'top'")
                            switch = page.locator("#language-switcher")
                            expect(switch).to_be_visible()
                            switch.click()
                            expect(page.locator("header.ed-nav")).to_have_attribute("lang", "ar")
                            current = urlsplit(page.url)
                            query = parse_qs(current.query)
                            assert query["topic"] == ["Cloud & DevOps"]
                            assert query["country"] == ["United Arab Emirates"]
                            assert query["_lang"] == ["ar"]
                            if javascript:
                                assert current.fragment == "top"
                                assert any(c["name"] == "preferred_language" and c["value"] == "ar" and c["path"] == "/" for c in context.cookies())
                                assert page.locator('form[method="get"] input[name="_lang"]').count() == 1
                                page.locator('.ed-nav-links a[href="/training"]').click()
                                assert parse_qs(urlsplit(page.url).query)["_lang"] == ["ar"]
                                expect(page.locator("header.ed-nav")).to_have_attribute("lang", "ar")
                            assert calls == []
                            context.close()
                            behavior_cases += 1
                            print(f"PASS {engine_name}: {user}, JavaScript={javascript}, native _lang request and filter preservation", flush=True)
                    # Language enhancement cannot alter unrelated/private destinations.
                    context, calls = context_for(browser)
                    page = context.new_page()
                    page.goto(origin + "/?_lang=ar")
                    result = page.evaluate("""() => {
                      const paths=['https://example.org/event','/desk','/api/method/ping','/files/photo.png','#top','mailto:team@example.org'];
                      return paths.map(href=>{
                        const a=document.createElement('a');a.href=href;
                        a.addEventListener('click',e=>e.preventDefault());
                        document.querySelector('.ed-site').appendChild(a);a.click();
                        const result=a.getAttribute('href');a.remove();return result;
                      });
                    }""")
                    assert result == ['https://example.org/event', '/desk', '/api/method/ping', '/files/photo.png', '#top', 'mailto:team@example.org']
                    assert calls == []
                    context.close()
                    behavior_cases += 1
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    (OUT / "measurements.json").write_text(json.dumps(measurements, indent=2))
    print(f"PASS: {len(measurements)} layout cases and {behavior_cases} language/fallback/boundary cases. No live account tested.")


if __name__ == "__main__":
    main()
