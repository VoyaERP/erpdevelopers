"""Read-only checks on rendered public directories and the three-link footer."""
import argparse
from html.parser import HTMLParser
from pathlib import Path


class Page(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.footer_depth = 0
        self.footer_links = []
        self.headings = []
        self.heading = None
        self.styles = []
        self.ids = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if self.footer_depth:
                self.footer_depth += 1
            elif "ed-footer-links" in attrs.get("class", "").split():
                self.footer_depth = 1
        if tag == "a" and self.footer_depth:
            self.footer_links.append(attrs.get("href"))
        if tag == "h1" and attrs.get("id") == "ed-publications-title":
            self.heading = []
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.styles.append(attrs.get("href"))
        if attrs.get("id"):
            self.ids.append(attrs["id"])

    def handle_endtag(self, tag):
        if tag == "div" and self.footer_depth:
            self.footer_depth -= 1
        if tag == "h1" and self.heading is not None:
            self.headings.append("".join(self.heading).strip())
            self.heading = None

    def handle_data(self, text):
        if self.heading is not None:
            self.heading.append(text)


def inspect(source, route, language, stylesheet):
    page = Page(source)
    titles = {("projects", "en"): "Projects", ("projects", "ar"): "المشاريع",
              ("team-advice", "en"): "Team Advice", ("team-advice", "ar"): "نصائح الفريق"}
    errors = []
    if page.headings != [titles[(route, language)]]:
        errors.append("missing or untranslated publication heading")
    if page.footer_links != ["/lets-talk#meeting-start", "/login?redirect-to=/desk", "#top"]:
        errors.append("footer does not contain exactly the three requested links")
    if page.styles.count(stylesheet) != 1:
        errors.append("missing or stale publication stylesheet fingerprint")
    if page.ids.count("top") != 1 or page.ids.count("publications") != 1:
        errors.append("missing or duplicate directory/top anchor")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path)
    parser.add_argument("--route", choices=("projects", "team-advice"), required=True)
    parser.add_argument("--language", choices=("en", "ar"), required=True)
    parser.add_argument("--stylesheet", required=True)
    args = parser.parse_args()
    errors = inspect(args.html_file.read_text(encoding="utf-8"), args.route, args.language, args.stylesheet)
    if errors:
        raise SystemExit("STOP: " + "; ".join(errors))
    print(f"PASS: {args.route} {args.language}, three footer links and publication asset reference")


if __name__ == "__main__":
    main()
