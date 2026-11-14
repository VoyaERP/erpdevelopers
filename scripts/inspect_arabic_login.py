"""Read-only check of Arabic text in the native login section of served HTML."""
from html.parser import HTMLParser
from pathlib import Path
import argparse


class LoginText(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.active = False
        self.ignored = 0
        self.text = []
        self.lang = ""
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang", "")
        if tag == "section":
            self.active = "for-login" in attrs.get("class", "").split()
        if self.active and tag in ("script", "style"):
            self.ignored += 1

    def handle_endtag(self, tag):
        if self.active and tag in ("script", "style"):
            self.ignored = max(0, self.ignored - 1)
        if tag == "section":
            self.active = False

    def handle_data(self, data):
        if self.active and not self.ignored:
            self.text.append(data)


def inspect_markup(source):
    page = LoginText(source)
    errors = []
    text = " ".join(" ".join(page.text).split())
    if not page.lang.startswith("ar"):
        errors.append("Expected Arabic html language")
    for expected in ("تسجيل الدخول", "مرحباً بك!"):
        if expected not in text:
            errors.append("Missing Arabic login heading or welcome text")
    for english in ("Sign In", "Welcome! Please sign in to continue.", "Forgot password?", "Login with Email Link"):
        if english in text:
            errors.append("Untranslated native login text: " + english)
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", type=Path)
    args = parser.parse_args()
    errors = inspect_markup(args.html_file.read_text(encoding="utf-8"))
    if errors:
        raise SystemExit("STOP: " + "; ".join(errors) + ". Check Arabic catalogs, overrides and web cache.")
    print("PASS: Arabic native login heading, welcome and action text")


if __name__ == "__main__":
    main()
