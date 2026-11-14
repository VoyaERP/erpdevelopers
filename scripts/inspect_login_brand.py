#!/usr/bin/env python3
"""Read-only verifier for Frappe's server-rendered native navbar logo.

Avoid brittle literal HTML substrings: HTML may use different quote styles,
attribute orders or whitespace while still rendering the identical <img>.
"""

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

APPROVED_LOGO = "/assets/erpdevelopers/images/erpdevelopers-selected-logo.png"
APPROVED_HOST = "erp-developers.com"


class LoginBrandParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.brand_anchors = 0
        self.brand_images = []
        self.other_images = []
        self._in_brand = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        classes = set((attrs.get("class") or "").split())

        if tag == "a" and "navbar-brand" in classes:
            self.brand_anchors += 1
            self._in_brand = True
        elif tag == "img":
            image = {
                "src": attrs.get("src") or "",
                "class": attrs.get("class") or "",
            }
            if self._in_brand:
                self.brand_images.append(image)
            else:
                self.other_images.append(image)

    def handle_endtag(self, tag):
        if tag == "a" and self._in_brand:
            self._in_brand = False


def is_approved_logo(src, site=APPROVED_HOST):
    """Only approve the exact site asset, not arbitrary external-host images."""
    parsed = urlsplit(src)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme != "https" or parsed.netloc != site:
            return False
    return parsed.path == APPROVED_LOGO


def inspect_markup(html, site=APPROVED_HOST):
    parser = LoginBrandParser()
    parser.feed(html)
    approved = [img for img in parser.brand_images if is_approved_logo(img["src"], site)]
    messages = [
        f"Frappe navbar-brand elements: {parser.brand_anchors}",
        "Navbar image sources: " + repr([img["src"] for img in parser.brand_images]),
        "Other page image sources: " + repr([img["src"] for img in parser.other_images[:8]]),
    ]
    if parser.brand_anchors == 1 and len(approved) == 1:
        messages.insert(0, "PASS: approved PNG is an image inside the native Frappe navbar")
        return True, "\n".join(messages)
    messages.insert(0, "FAIL: approved PNG not confirmed as a native navbar image")
    if any(is_approved_logo(img["src"], site) for img in parser.other_images):
        messages.append(
            "The approved logo exists elsewhere (possibly the hidden login app-logo) "
            "but not inside the native navbar."
        )
    messages.append(
        "Inspect Website Settings.brand_html, banner_image, navbar_template, "
        "and the rendered HTML before modifying branding."
    )
    return False, "\n".join(messages)


def main():
    args_parser = argparse.ArgumentParser(description=__doc__)
    args_parser.add_argument("html_file", type=Path)
    args_parser.add_argument("--site", default=APPROVED_HOST)
    args = args_parser.parse_args()
    ok, result = inspect_markup(args.html_file.read_text(encoding="utf-8"), args.site)
    print(result)
    return 0 if ok else 3


if __name__ == "__main__":
    raise SystemExit(main())
