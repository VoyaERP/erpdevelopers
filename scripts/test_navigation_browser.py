"""Measure the real shared header before/after delayed native language hydration.

Reuses existing actual-template fixtures, restoring the real nav and footer.
Frappe's pinned picker method runs with an isolated AJAX/DOM adapter. No live
account, cookie, database or network service is modified. External font responses
are stubbed; this does not test real font delivery or the complete Frappe runtime.
"""
from hashlib import sha1
from pathlib import Path
from threading import Thread
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit
from urllib.request import urlopen
import json

import test_training_browser as fixture
from erpdevelopers.www.erp_developers_home import get_context as home_context
from playwright.sync_api import expect, sync_playwright

OUT = fixture.ROOT / "test-artifacts/navigation"
WIDTHS = (320, 390, 540, 768, 1100, 1101, 1440)
NATIVE_URL = "https://raw.githubusercontent.com/frappe/frappe/v16.56.0/frappe/website/js/website.js"
NATIVE_SHA = "c29cd08cdcecc823194efe98636af4602fd5afbe"
OLD_CSS_URL = "https://raw.githubusercontent.com/VoyaERP/erpdevelopers/8c24b9a33a171c3f6a7a00d3fc3c0f3b22331dfd/erpdevelopers/public/css/brand.css"
OLD_CSS_SHA = "786d080ff7d7642d103bd9775e2c203ebcd0b418"


def pinned_text(url, blob_sha):
    with urlopen(url, timeout=25) as response:
        payload = response.read()
    actual = sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
    if actual != blob_sha:
        raise RuntimeError("Pinned source bytes do not match: " + url)
    return payload.decode("utf-8")


# Keep the real header/footer, unlike older isolated content-only browser tests.
for component in ("nav", "footer"):
    fixture.OVERRIDES.pop(f"templates/includes/erpdevelopers_{component}.html", None)
fixture.ENV.cache.clear()
ORIGINAL_RENDER = fixture.render


def render_home(params):
    lang = "ar" if params.get("_lang", ["en"])[0] == "ar" else "en"
    context = SimpleNamespace()
    home_context(context)
    values = vars(context)
    values.update(boot=SimpleNamespace(lang=lang), fixture_route="home",
        web_include_css=fixture.web_include_css,
        _=(lambda value: fixture.ARABIC.get(value, value)) if lang == "ar" else (lambda value: value))
    return fixture.ENV.get_template("www/erp-developers-home.html").render(values).encode()


class Handler(fixture.Handler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/":
            data = render_home(parse_qs(url.query))
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            super().do_GET()


SNAPSHOT = """() => {
 const selectors=['.ed-nav','.ed-brand','.ed-brand img','.ed-nav-links','.ed-nav-tools','#language-switcher','.ed-nav-cta'];
 const elements=selectors.map(s=>document.querySelector(s)).concat([...document.querySelectorAll('.ed-nav-links a')]);
 return elements.map(el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};});
}"""


def max_delta(a, b):
    return max(abs(first[key] - second[key]) for first, second in zip(a, b) for key in first)


def install_native_picker(page, method, lang, mismatch=False):
    # Tiny jQuery subset used only by the unmodified, pinned picker method.
    bootstrap = """({language, mismatch}) => {
      window.$ = value => {
        const nodes = typeof value === 'string'
          ? (value.startsWith('<option') ? [document.createElement('option')] : [...document.querySelectorAll(value)])
          : [value];
        return {
          nodes,
          attr(key,value){nodes.forEach(n=>n.setAttribute(key,value));return this;},
          text(value){nodes.forEach(n=>n.textContent=value);return this;},
          append(child){nodes.forEach(n=>child.nodes.forEach(c=>n.appendChild(c)));return this;},
          removeClass(value){nodes.forEach(n=>n.classList.remove(value));return this;},
          val(value){if(value===undefined)return nodes[0]?.value;nodes.forEach(n=>n.value=value);return this;},
          change(fn){nodes.forEach(n=>n.addEventListener('change',fn));return this;}
        };
      };
      window.show_language_picker=true;
      window.frappe={session:{user:'Guest'},get_cookie:()=>mismatch?'':language,
        call:()=>new Promise(resolve=>window.finishPicker=()=>resolve({message:[
          {language_code:'en',language_name:'English'},
          {language_code:'ar',language_name:'\\u0627\\u0644\\u0639\\u0631\\u0628\\u064a\\u0629'}
        ]}))};
    }"""
    page.evaluate(bootstrap, {"language": lang, "mismatch": mismatch})
    page.evaluate("Object.assign(frappe, {" + method + "}); frappe.show_language_picker();")


def assert_labels(page):
    assert page.locator("header.ed-nav").count() == 1
    assert page.locator("#language-switcher").count() == 1
    assert page.locator(".ed-nav-links a").count() == 6
    problems = page.locator(".ed-nav-links a, .ed-nav-cta, .ed-footer-links a").evaluate_all("""els => els.flatMap(el=>{
      const range=document.createRange();range.selectNodeContents(el);
      const lines=[...new Set([...range.getClientRects()].filter(r=>r.width>0).map(r=>Math.round(r.y)))];
      return lines.length>1 || el.scrollWidth>el.clientWidth+1 ? [el.textContent.trim()] : [];
    })""")
    assert not problems, "Wrapped or clipped short controls: " + repr(problems)
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), "Page overflows viewport"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    native = pinned_text(NATIVE_URL, NATIVE_SHA)
    method = native[native.index("\tshow_language_picker() {"):native.index("\n\tsetup_videos:")].strip().rstrip(",")
    old_css = pinned_text(OLD_CSS_URL, OLD_CSS_SHA)
    # Model the framework's hide utility, rather than testing the app CSS alone.
    fixture.OVERRIDES["templates/web.html"] = fixture.BASE.replace(
        "body{margin:0}", "body{margin:0}.hide{display:none!important}")
    fixture.ENV.cache.clear()
    server = fixture.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    origin = f"http://127.0.0.1:{server.server_port}"
    results = []
    try:
        with sync_playwright() as p:
            for engine in (p.chromium, p.firefox):
                browser = engine.launch(headless=True)
                try:
                    # Reproduce the existing visible movement with the old exact CSS.
                    old = browser.new_context(viewport={"width":1440,"height":900})
                    fixture.routes(old, [])
                    old.route("**/assets/erpdevelopers/css/brand.css*", lambda r:r.fulfill(content_type="text/css",body=old_css))
                    page = old.new_page(); page.goto(origin + "/training?_lang=en")
                    initial = page.evaluate(SNAPSHOT)
                    install_native_picker(page, method, "en")
                    page.evaluate("finishPicker()")
                    expect(page.locator("#language-switcher")).to_be_visible()
                    baseline_delta = max_delta(initial, page.evaluate(SNAPSHOT))
                    assert baseline_delta > 10, "Old stylesheet did not reproduce the hydration shift"
                    print(f"REPRODUCED {engine.name}: old picker hydration moves geometry {baseline_delta:.2f}px", flush=True)
                    old.close()
                    for lang in ("en", "ar"):
                        for width in WIDTHS:
                            for path in ("/", "/training", "/events"):
                                context = browser.new_context(viewport={"width":width,"height":900},locale="en-US",reduced_motion="reduce")
                                fixture.routes(context, [])
                                page = context.new_page(); errors=[]
                                page.on("pageerror", lambda err:errors.append(str(err)))
                                target = origin + path + "?_lang=" + lang
                                page.goto(target)
                                initial = page.evaluate(SNAPSHOT)
                                assert page.locator("#language-switcher").evaluate("e=>getComputedStyle(e).visibility") == "hidden"
                                install_native_picker(page, method, lang)
                                page.wait_for_timeout(80)  # Deliberately leave the native response unresolved.
                                assert max_delta(initial,page.evaluate(SNAPSHOT)) < 0.5
                                page.evaluate("finishPicker()")
                                expect(page.locator("#language-switcher")).to_be_visible()
                                delta = max_delta(initial,page.evaluate(SNAPSHOT))
                                assert delta < 0.5, (engine.name,lang,width,path,delta)
                                assert_labels(page)
                                if width <= 1100:
                                    assert page.locator(".ed-nav-links").bounding_box()["width"] >= page.locator(".ed-nav-inner").bounding_box()["width"] - 1
                                    # Keyboard focus can reach and reveal every item in the scroll strip.
                                    for link in page.locator(".ed-nav-links a").all():
                                        link.focus()
                                        expect(link).to_be_focused()
                                        link.evaluate("e=>e.scrollIntoView({block:'nearest',inline:'nearest'})")
                                        bounds=link.bounding_box(); track=page.locator(".ed-nav-links").bounding_box()
                                        assert bounds["x"] >= track["x"] - 1 and bounds["x"]+bounds["width"] <= track["x"]+track["width"]+1
                                    page.locator(".ed-nav-links a").first.evaluate("e=>e.scrollIntoView({block:'nearest',inline:'nearest'})")
                                page.evaluate("window.scrollTo(0,300)")
                                expect(page.locator(".ed-nav")).to_be_visible()
                                assert abs(page.locator(".ed-nav").bounding_box()["y"]) < 1
                                page.evaluate("window.scrollTo(0,0)")
                                if engine.name == "chromium" and path == "/" and width in (390,1440):
                                    page.screenshot(path=OUT/f"header-{lang}-{width}.png")
                                # Refresh returns the same boxes before hydration, not an alternate header.
                                page.reload(); refreshed=page.evaluate(SNAPSHOT)
                                assert max_delta(initial,refreshed) < 0.5
                                assert not errors, errors
                                results.append(dict(engine=engine.name,lang=lang,width=width,path=path,delta=delta))
                                context.close()
                            print(f"PASS {engine.name}: {lang} {width}px, 3 routes, delayed picker/refresh/nowrap/keyboard/sticky",flush=True)
                    # Explicit request language can differ from browser language in native v16.
                    context=browser.new_context(viewport={"width":390,"height":900},locale="en-US")
                    fixture.routes(context,[]); page=context.new_page();page.goto(origin+"/training?_lang=ar")
                    initial=page.evaluate(SNAPSHOT)
                    install_native_picker(page,method,"ar",mismatch=True);page.evaluate("finishPicker()")
                    expect(page.locator("#language-switcher")).to_be_visible()
                    assert page.locator("html").get_attribute("lang")=="en", "Expected native language guess"
                    assert page.locator("header.ed-nav").get_attribute("lang")=="ar"
                    assert page.locator("header.ed-nav").evaluate("e=>getComputedStyle(e).direction")=="rtl"
                    assert max_delta(initial,page.evaluate(SNAPSHOT)) < 0.5
                    context.close()
                    print(f"PASS {engine.name}: rendered Arabic header stays RTL despite native root-language guess",flush=True)
                finally:
                    browser.close()
    finally:
        server.shutdown();server.server_close();thread.join(timeout=5)
    (OUT/"measurements.json").write_text(json.dumps(results,indent=2))
    print(f"{len(results)} EN/AR route/viewport cases passed, plus 2 baseline reproductions and 2 native-language mismatch cases.")


if __name__ == "__main__":
    main()
