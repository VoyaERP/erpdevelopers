"""Read-only checks of actual server-rendered Training HTML, without browser JS."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import argparse


class Markup(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.tags=[]; self.head_scripts=[]; self.in_head=False; self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs); self.tags.append((tag,attrs))
        if tag=="head": self.in_head=True
        if tag=="script" and self.in_head: self.head_scripts.append(attrs)
    def handle_endtag(self, tag):
        if tag=="head": self.in_head=False


def inspect_markup(source):
    markup=Markup(source); errors=[]
    dialogs=[a for t,a in markup.tags if t=="dialog" and a.get("id")=="ed-playlist-dialog"]
    if len(dialogs)!=1: errors.append("Expected exactly one native playlist dialog")
    frames=[a for t,a in markup.tags if t=="iframe" and "data-player-frame" in a]
    if len(frames)!=1:
        errors.append("Expected exactly one playlist frame")
    else:
        frame=frames[0]
        if "src" in frame or "srcdoc" in frame: errors.append("Player must not load third-party content before a click")
        if frame.get("referrerpolicy")!="strict-origin-when-cross-origin": errors.append("Playlist frame referrer policy is missing")
    controls=[(t,a) for t,a in markup.tags if "data-playlist-open" in a]
    if not controls and any("ed-resource-card" in a.get("class","").split() for _,a in markup.tags):
        errors.append("Published cards have no in-page player control")
    for tag,attrs in controls:
        if tag!="button" or attrs.get("type")!="button" or "href" in attrs or "target" in attrs or attrs.get("aria-controls")!="ed-playlist-dialog":
            errors.append("Watch here must be a local dialog button"); break
    for tag,attrs in markup.tags:
        if tag=="a":
            host=urlsplit(attrs.get("href","")).hostname or ""
            if "data-player-external" in attrs or host in {"youtube.com","www.youtube.com","youtu.be"}:
                errors.append("App-owned YouTube navigation must not appear on Training"); break
    scripts=[a for a in markup.head_scripts if urlsplit(a.get("src","")).path=="/assets/erpdevelopers/js/catalog.js"]
    if len(scripts)!=1: errors.append("Expected exactly one catalog script in the page head")
    elif "defer" not in scripts[0] or scripts[0].get("data-cfasync")!="false": errors.append("Catalog script must be deferred and excluded from Rocket Loader")
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument("html_file",type=Path); args=parser.parse_args()
    errors=inspect_markup(args.html_file.read_text(encoding="utf-8"))
    if errors: raise SystemExit("STOP: "+"; ".join(errors))
    print("PASS: local playlist button, no app-owned YouTube links, deferred script")


if __name__ == "__main__": main()
