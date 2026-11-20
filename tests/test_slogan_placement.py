"""The standalone slogan has one intentional home; approved logo/SEO stay intact."""
from html.parser import HTMLParser
from pathlib import Path
from unittest import TestCase

from babel.messages.pofile import read_po
from erpdevelopers.branding import TAGLINE
from erpdevelopers.content import VALUES

APP = Path(__file__).resolve().parents[1] / 'erpdevelopers'


class SloganMarkup(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.section_ids = []
        self.placements = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section':
            self.section_ids.append(attrs.get('id'))
        if 'data-brand-slogan' in attrs:
            self.placements.append((tag, attrs, list(self.section_ids)))

    def handle_endtag(self, tag):
        if tag == 'section' and self.section_ids:
            self.section_ids.pop()


class TestSloganPlacement(TestCase):
    def test_one_signature_inside_vision_not_in_hero_or_shared_chrome(self):
        home = (APP / 'www/erp-developers-home.html').read_text()
        placements = SloganMarkup(home).placements
        self.assertEqual(len(placements), 1)
        tag, attrs, ancestors = placements[0]
        self.assertEqual(tag, 'p')
        self.assertIn('vision', ancestors)
        self.assertEqual(attrs['class'], 'ed-vision-signature')
        self.assertIn('lang', attrs)
        self.assertIn('dir', attrs)
        self.assertEqual(home.count('for value in values_items'), 1)
        for folder in ('www', 'templates'):
            for path in (APP / folder).rglob('*.html'):
                if path.name != 'erp-developers-home.html':
                    self.assertNotIn('data-brand-slogan', path.read_text(), str(path))

    def test_pill_rules_removed_instead_of_hidden_with_another_override(self):
        home = (APP / 'www/erp-developers-home.html').read_text()
        css = '\n'.join(path.read_text() for path in (APP / 'public/css').glob('*.css'))
        self.assertNotIn('ed-principles', home + css)
        self.assertNotIn('Engage.', css)
        self.assertNotIn('.page-content-wrapper::after', (APP / 'public/css/login.css').read_text())
        self.assertIn('.ed-vision-signature{display:flex;flex-wrap:wrap', css)
        self.assertNotIn('text-overflow:ellipsis', css)

    def test_canonical_words_and_complete_arabic_copy(self):
        self.assertEqual(' '.join(value.title for value in VALUES), TAGLINE)
        with (APP / 'locale/ar.po').open('rb') as stream:
            catalog = read_po(stream, locale='ar')
        for value in VALUES:
            translated = catalog.get(value.title)
            self.assertIsNotNone(translated)
            self.assertTrue(translated.string)
            self.assertNotEqual(translated.string, value.title)

    def test_existing_logo_alt_text_and_structured_slogan_are_not_removed(self):
        for part in ('nav', 'footer'):
            source = (APP / f'templates/includes/erpdevelopers_{part}.html').read_text()
            self.assertIn(TAGLINE, source)
            self.assertIn('brand_logo_url', source)
        self.assertIn('"slogan": TAGLINE', (APP / 'seo.py').read_text())
