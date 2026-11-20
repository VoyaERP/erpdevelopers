"""Actual new controllers and templates, mocked DB only; no production data.

Reuse the existing isolated HTTP/assets fixture, restoring the real nav/footer.
No credentials are submitted and no published examples are inserted into a site.
"""
from http.server import ThreadingHTTPServer
from threading import Thread
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
import sys

import test_training_browser as base
from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import expect, sync_playwright
from erpdevelopers import publications as p

OVERRIDES = {"templates/web.html": base.BASE, "templates/includes/erpdevelopers_assistant.html": ""}
ENV = Environment(loader=ChoiceLoader([DictLoader(OVERRIDES), FileSystemLoader(base.APP)]), autoescape=select_autoescape(["html"]))
OUT = base.ROOT / "test-artifacts/publications"
OUT.mkdir(parents=True, exist_ok=True)


def render(route, params):
    lang = "ar" if params.get("_lang", ["en"])[0] == "ar" else "en"
    fake = ModuleType("frappe")
    fake.local = SimpleNamespace(lang=lang)
    fake.session = SimpleNamespace(user="Guest")
    fake.form_dict = {k: v[0] for k, v in params.items()}
    fake._ = (lambda s: base.ARABIC.get(s, s)) if lang == "ar" else (lambda s: s)
    fake.has_permission = lambda *a, **kw: False
    kind = p.KINDS[route]
    rows = [{"name": "public-example", "publication_type": kind, "topic": p.TOPICS[0],
             "title": "Example only: project or advice", "title_ar": "مثال اختباري: مشروع أو نصيحة",
             "summary": "A synthetic fixture, not a claim about client work.", "summary_ar": "بيانات للاختبار وليست ادعاءً بتنفيذ مشروع لعميل.",
             "content": "Plain text example <script>window.bad=true</script>\n\nAnother paragraph.",
             "content_ar": "نص للاختبار <script>window.bad=true</script>\n\nفقرة أخرى.",
             "industry": "Manufacturing", "technologies": "ERPNext / Frappe", "author_name": "Example editorial team",
             "author_name_ar": "فريق التحرير التجريبي", "published": 1, "public_reviewed": 1,
             "internal_notes": "SECRET MUST NOT RENDER", "cover_image": ""}]
    def get_all(doctype, **kw):
        assert doctype == p.DOCTYPE, doctype
        assert kw["filters"]["published"] == 1 and kw["filters"]["public_reviewed"] == 1
        return [r for r in rows if all(r.get(k) == v for k, v in kw["filters"].items())]
    fake.get_all = get_all
    context = SimpleNamespace()
    with patch.dict(sys.modules, {"frappe": fake}), patch.object(p, "_schema_status", return_value={"table_present": True, "missing_columns": []}):
        p.set_publication_context(context, route)
    values = vars(context)
    values.update(boot=SimpleNamespace(lang=lang), web_include_css=base.web_include_css,
                  fixture_route=route, _=fake._)
    return ENV.get_template(f"www/{route}.html").render(values).encode()


class Handler(base.Handler):
    def do_GET(self):
        url = urlsplit(self.path)
        route = url.path.strip("/")
        if route not in p.KINDS:
            return super().do_GET()
        payload = render(route, parse_qs(url.query))
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    cases = 0
    try:
        with sync_playwright() as pw:
            for engine in (pw.chromium, pw.firefox):
                browser = engine.launch(headless=True)
                try:
                    for lang in ("en", "ar"):
                        for width in (320, 390, 768, 1360, 1361, 1440):
                            for route in p.KINDS:
                                context = browser.new_context(viewport={"width": width, "height": 900})
                                base.routes(context, [])
                                page = context.new_page()
                                errors = []
                                page.on("pageerror", lambda e: errors.append(str(e)))
                                page.goto(f"{origin}/{route}?_lang={lang}")
                                expect(page.locator("#ed-publications-title")).to_have_text("المشاريع" if lang == "ar" and route == "projects" else "نصائح الفريق" if lang == "ar" else "Projects" if route == "projects" else "Team Advice")
                                assert page.locator(".ed-nav").count() == 1
                                assert page.locator(".ed-nav-links > a").count() == 8
                                assert page.locator(".ed-footer-links > a").evaluate_all("es=>es.map(e=>e.getAttribute('href'))") == ["/lets-talk#meeting-start", "/login?redirect-to=/desk", "#top"]
                                assert page.locator('a[href^="/desk/erp-developers-publication"]').count() == 0
                                expect(page.locator(".ed-publication-card")).to_have_count(1)
                                assert "SECRET MUST NOT RENDER" not in page.content()
                                assert page.locator(".ed-publication-copy script").count() == 0
                                page.locator(".ed-publication-details > summary").click()
                                expect(page.locator(".ed-publication-copy")).to_be_visible()
                                assert page.evaluate("window.bad") is None
                                assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
                                # The language link is visible immediately and keeps its fixed slot.
                                before = page.locator(".ed-nav-links").bounding_box()
                                expect(page.locator("#language-switcher")).to_be_visible()
                                assert page.locator("#language-switcher").evaluate("e=>e.tagName") == "A"
                                after = page.locator(".ed-nav-links").bounding_box()
                                assert all(abs(before[k] - after[k]) <= 1 for k in ("x", "y", "width", "height"))
                                for link in page.locator(".ed-nav-links > a").all():
                                    assert link.evaluate("e=>e.scrollWidth<=e.clientWidth+1"), link.inner_text()
                                page.locator('.ed-footer-links a[href="#top"]').click()
                                assert page.url.endswith("#top") and urlsplit(page.url).path == "/" + route
                                if engine.name == "chromium" and width in (390, 1440):
                                    page.screenshot(path=str(OUT / f"{route}-{lang}-{width}.png"), full_page=True)
                                page.select_option("#ed-publication-topic", p.TOPICS[2])
                                page.locator('form[method="get"] button').click()
                                expect(page.locator(".ed-empty")).to_be_visible()
                                expect(page.locator(".ed-publication-card")).to_have_count(0)
                                assert errors == [], errors
                                context.close()
                                cases += 1
                                print(f"PASS {engine.name}: {route} {lang} {width}px, footer/filter/escape/navigation", flush=True)
                finally:
                    browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print(f"PASS: {cases} publication browser cases; live native Desk publishing remains a site UAT check.")


if __name__ == "__main__":
    main()
