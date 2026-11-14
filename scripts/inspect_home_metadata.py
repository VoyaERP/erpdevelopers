"""Read-only OpenGraph validation; attribute order, quotes and spaces are immaterial."""
from html.parser import HTMLParser
from pathlib import Path
import argparse


class Metadata(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.in_head = False
        self.types = []
        self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.in_head = True
        if self.in_head and tag == "meta" and attrs.get("property", "").lower() == "og:type":
            self.types.append(attrs.get("content", "").strip())
    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False


def inspect_markup(source):
    values = Metadata(source).types
    if values != ["website"]:
        return ["Expected one head meta property og:type=website; observed " + repr(values)[:200]]
    return []


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path)
    args = parser.parse_args()
    errors = inspect_markup(args.html_file.read_text(encoding="utf-8"))
    if errors:
        raise SystemExit("STOP: " + "; ".join(errors))
    print("PASS: actual OpenGraph website metadata")


if __name__ == "__main__":
    main()
