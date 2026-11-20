"""Browser regressions for actual Training and Events templates.

Only Frappe's outer shell/nav/footer and external responses are fixtures.
No production site, database, YouTube playback or font delivery is tested here.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, unquote, urlsplit
import csv
import mimetypes
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from babel.dates import format_date
from babel.messages.pofile import read_po
from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import expect, sync_playwright
from erpdevelopers.hooks import web_include_css
from erpdevelopers.public_pages import set_public_context
from erpdevelopers.branding import versioned_public_asset
from erpdevelopers.event_rules import TOPICS, FORMATS

APP=ROOT/"erpdevelopers"
PUBLIC=(APP/"public").resolve()
PLAYLIST="PLabcdefghijklmnopqrst0123456"
with (APP/"translations/ar.csv").open(encoding="utf-8",newline="") as stream:
    ARABIC=dict(csv.reader(stream))
with (APP/"locale/ar.po").open("rb") as stream:
    ARABIC.update({m.id:m.string for m in read_po(stream,locale="ar") if m.id and isinstance(m.id,str) and m.string})
BASE='''<!doctype html><html lang="{{ boot.lang }}" dir="{{ 'rtl' if boot.lang == 'ar' else 'ltr' }}"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>body{margin:0}</style>
{% block head_include %}{% for css in web_include_css %}<link rel="stylesheet" href="{{ css }}">{% endfor %}{% endblock %}
</head><body data-path="{{ fixture_route }}">{% block navbar %}{% endblock %}{% block page_container %}{% endblock %}{% block footer %}{% endblock %}</body></html>'''
OVERRIDES={"templates/web.html":BASE}
for part in ("nav","footer","assistant"):
    OVERRIDES[f"templates/includes/erpdevelopers_{part}.html"]=""
ENV=Environment(loader=ChoiceLoader([DictLoader(OVERRIDES),FileSystemLoader(APP)]),autoescape=select_autoescape(["html"]))


def render(route,params):
    lang="ar" if params.get("_lang",["en"])[0]=="ar" else "en"
    ctx=SimpleNamespace()
    set_public_context(ctx,slug=route,title=route.title(),description="Isolated regression fixture")
    values=vars(ctx)
    values.update(boot=SimpleNamespace(lang=lang),web_include_css=web_include_css,fixture_route=route,
                  _=(lambda s:ARABIC.get(s,s)) if lang=="ar" else (lambda s:s))
    if route=="training":
        values.update(is_authenticated=False,topics=["Solution Architecture"],playlists=[dict(
            title="Public playlist",title_ar="\u0642\u0627\u0626\u0645\u0629 \u0639\u0627\u0645\u0629",topic="Solution Architecture",level="Beginner",language="English",
            description="Reviewed training collection",visibility="Public",playlist_id=PLAYLIST,
            watch_url=f"https://www.youtube.com/playlist?list={PLAYLIST}")])
    else:
        selected={key:params.get(key,[""])[0] for key in ("topic","country","event_format")}
        selected.update(period=params.get("period",["upcoming"])[0],page=1)
        example=dict(title="Architecture forum <script>bad()</script>",title_ar="\u0645\u0644\u062a\u0642\u0649 \u0647\u0646\u062f\u0633\u0629 \u0627\u0644\u062d\u0644\u0648\u0644",description="Reviewed description <img src=x onerror=bad()>",description_ar="\u0648\u0635\u0641 \u0645\u0631\u0627\u062c\u0639",organizer="Example organizer",topic="Solution Architecture",event_type="Conference",event_format="In person",event_status="Scheduled",country="Saudi Arabia",city="Riyadh",venue="Example venue",start_date="2030-05-10",end_date="2030-05-11",date_only=1,time_zone="Asia/Riyadh",event_url="https://events.example.org/forum",source_url="",verified_on_label="1 Jan 2020")
        from datetime import date
        example["start_date_label"]=format_date(date(2030,5,10),locale=lang)
        example["end_date_label"]=format_date(date(2030,5,11),locale=lang)
        rows=[example,dict(example,title="Cloud session",title_ar="\u0644\u0642\u0627\u0621 \u0633\u062d\u0627\u0628\u064a",topic="Cloud & DevOps",country="United Arab Emirates",city="Dubai",time_zone="Asia/Dubai",event_status="Postponed")]
        rows=[row for row in rows if all(not selected[key] or selected[key]==row[key] for key in ("topic","country","event_format"))]
        if selected["period"]=="past": rows=[]
        values.update(event_rows=rows,countries=["Saudi Arabia","United Arab Emirates"],topics=TOPICS,formats=FORMATS,
                      selected=selected,total=len(rows),pages=1,previous_url=None,next_url=None,can_manage_events=False,
                      events_css_url=versioned_public_asset("css/events.css"))
    return ENV.get_template(f"www/{route}.html").render(values).encode()


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_GET(self):
        url=urlsplit(self.path)
        if url.path in ("/training","/events"):
            payload,kind=render(url.path[1:],parse_qs(url.query)),"text/html; charset=utf-8"
        elif url.path.startswith("/assets/erpdevelopers/"):
            relative=unquote(url.path.removeprefix("/assets/erpdevelopers/"))
            path=(PUBLIC/relative).resolve()
            if not path.is_relative_to(PUBLIC) or not path.is_file(): self.send_error(404); return
            payload=path.read_bytes(); kind=mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        else: self.send_error(404); return
        self.send_response(200); self.send_header("Content-Type",kind); self.send_header("Content-Length",str(len(payload)))
        self.end_headers(); self.wfile.write(payload)


def routes(context,requests):
    def embed(route):
        requests.append(route.request.url)
        route.fulfill(content_type="text/html",body="<!doctype html><title>Mock video embed</title>")
    context.route("https://www.youtube-nocookie.com/**",embed)
    context.route("https://fonts.googleapis.com/**",lambda r:r.fulfill(content_type="text/css",body=""))
    context.route("https://fonts.gstatic.com/**",lambda r:r.abort())


def main():
    server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
    thread=Thread(target=server.serve_forever,daemon=True); thread.start()
    origin=f"http://127.0.0.1:{server.server_port}"
    cases=0
    try:
        with sync_playwright() as p:
            for engine in (p.chromium,p.firefox):
                browser=engine.launch(headless=True)
                try:
                    for lang in ("en","ar"):
                        for width in (1440,390):
                            context=browser.new_context(viewport={"width":width,"height":900})
                            requests=[]; routes(context,requests)
                            page=context.new_page(); errors=[]
                            page.on("pageerror",lambda error:errors.append(str(error)))
                            page.goto(f"{origin}/training?_lang={lang}")
                            watch=page.locator("[data-playlist-open]")
                            expect(watch).to_be_enabled()
                            assert watch.evaluate("e=>e.tagName")=="BUTTON"
                            assert watch.get_attribute("href") is None
                            assert requests==[],"Third-party content loaded before click"
                            assert page.locator('a[href*="youtube"], [data-player-external]').count()==0
                            if lang=="ar":
                                assert "Tajawal" in watch.evaluate("e=>getComputedStyle(e).fontFamily")
                            watch.click()
                            dialog=page.locator("#ed-playlist-dialog")
                            expect(dialog).to_be_visible()
                            assert dialog.evaluate("e=>e.matches(':modal')")
                            assert len(context.pages)==1
                            assert page.url==f"{origin}/training?_lang={lang}"
                            frame=page.locator("[data-player-frame]")
                            src=urlsplit(frame.get_attribute("src"))
                            assert src.netloc=="www.youtube-nocookie.com"
                            assert parse_qs(src.query)["list"]==[PLAYLIST]
                            page.keyboard.press("Escape"); expect(dialog).not_to_be_visible()
                            page.wait_for_function("!document.querySelector('[data-player-frame]').hasAttribute('src')")
                            expect(watch).to_be_focused()
                            assert errors==[],errors
                            context.close(); cases+=1
                            print(f"PASS {engine.name}: training {lang} {width}px, modal only, no external app links",flush=True)

                            context=browser.new_context(viewport={"width":width,"height":900}); routes(context,[])
                            page=context.new_page(); errors=[]
                            page.on("pageerror",lambda error:errors.append(str(error)))
                            page.goto(f"{origin}/events?_lang={lang}")
                            expect(page.locator("#ed-events-title")).to_be_visible()
                            expect(page.locator(".ed-event-card")).to_have_count(2)
                            assert page.locator('a[href="/desk/erp-developers-event"]').count()==0
                            assert page.locator(".ed-event-card script, .ed-event-card img").count()==0
                            if lang=="ar":
                                assert "Tajawal" in page.locator("#ed-events-title").evaluate("e=>getComputedStyle(e).fontFamily")
                                assert "\u0627\u0644\u0641\u0639\u0627\u0644\u064a\u0627\u062a" in page.locator(".ed-events-filters").inner_text()
                            page.select_option("#ed-event-country","Saudi Arabia")
                            page.locator(".ed-events-filters button[type=submit]").click()
                            expect(page.locator(".ed-event-card")).to_have_count(1)
                            assert parse_qs(urlsplit(page.url).query)["_lang"]==[lang]
                            page.select_option("#ed-event-period","past")
                            page.locator(".ed-events-filters button[type=submit]").click()
                            expect(page.locator(".ed-empty")).to_be_visible()
                            assert errors==[],errors
                            context.close(); cases+=1
                            print(f"PASS {engine.name}: events {lang} {width}px, filters, empty state, escaping, typography",flush=True)
                    context=browser.new_context(); routes(context,[])
                    context.route("**/assets/erpdevelopers/js/catalog.js*",lambda r:r.abort())
                    page=context.new_page(); page.goto(f"{origin}/training")
                    expect(page.locator("[data-playlist-open]")).to_be_disabled()
                    assert page.locator('a[href*="youtube"], [data-player-external]').count()==0
                    context.close(); cases+=1
                    print(f"PASS {engine.name}: blocked player script cannot navigate away",flush=True)
                finally: browser.close()
    finally:
        server.shutdown(); server.server_close(); thread.join(timeout=5)
    print(f"{cases} isolated browser cases passed; live provider playback and site integration still need UAT.")


if __name__=="__main__": main()
