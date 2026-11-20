"""Regression cases for event links without weakening resource/private URL rules."""
from unittest import TestCase
from unittest.mock import patch
from erpdevelopers.catalog_rules import EventLinkError, event_https_url, external_https_url
from erpdevelopers.event_rules import normalize_event
from test_events import record


class TestEventURLs(TestCase):
    def test_pasted_public_links_are_normalized(self):
        examples = {
            "www.example.com/events": "https://www.example.com/events",
            " example.com/events ": "https://example.com/events",
            "http://www.example.com/events": "https://www.example.com/events",
            "http://example.com:80/event": "https://example.com/event",
            "//example.com/event": "https://example.com/event",
            "HTTPS://WWW.EXAMPLE.COM:443/event?ref=one#agenda": "https://www.example.com/event?ref=one#agenda",
            "https://example.com/event name": "https://example.com/event%20name",
            "https://example.com/event%20name": "https://example.com/event%20name",
        }
        for source, expected in examples.items():
            with self.subTest(source=source):
                self.assertEqual(event_https_url(source), expected)
                self.assertEqual(event_https_url(expected), expected)

    def test_own_public_domain_is_not_a_private_address(self):
        for source in ("https://erp-developers.com/events", "erp-developers.com/", "www.erp-developers.com/training"):
            result = normalize_event(record(event_url=source, source_url=source))
            self.assertEqual(result["event_url"], event_https_url(source))
            self.assertEqual(result["source_url"], result["event_url"])

    def test_unicode_host_and_path(self):
        result = event_https_url("https://\u0645\u062b\u0627\u0644.com/\u0641\u0639\u0627\u0644\u064a\u0629")
        self.assertTrue(result.startswith("https://xn--"))
        self.assertIn("%", result)
        self.assertEqual(result, event_https_url(result))

    def test_private_unsafe_and_obfuscated_addresses_are_rejected(self):
        sources = ["localhost", "https://intranet/", "https://127.0.0.1/", "https://192.168.1.4/",
            "https://[::1]/", "https://8.8.8.8/", "https://2130706433/", "https://127.1/",
            "https://0x7f.0x0.0x0.0x1/", "https://intranet.local/", "https://service.internal/",
            "https://local.lan/", "https://demo.localhost/", "https://x.test/",
            "javascript:alert(1)", "data:text/html,evil", "file:///etc/passwd", "ftp://example.com/",
            "https://user:password@example.com/", "https://@example.com/", "https://example.com:8443/",
            "https://example.com\\@localhost/", "https://bad host.com/", "https://example..com/",
            "https://example.com/%xx", "https://example.com/\nsecret", "https://example.com:bad/"]
        for source in sources:
            with self.subTest(source=source), self.assertRaises(ValueError):
                event_https_url(source)

    def test_private_own_site_routes_are_rejected_even_when_encoded(self):
        for path in ("/desk", "/api/method/ping", "/private/files/test.png", "/login", "/app",
                     "/%64esk", "/a/../desk", "/%252fdesk", "/%5Cdesk", "/me"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                event_https_url("https://erp-developers.com" + path)

    def test_error_identifies_the_wrong_field_and_optional_source_is_allowed(self):
        self.assertIsNone(normalize_event(record(source_url=""))["source_url"])
        for field in ("event_url", "source_url"):
            with self.subTest(field=field), self.assertRaises(EventLinkError) as caught:
                normalize_event(record(**{field: "https://127.0.0.1/"}))
            self.assertEqual(caught.exception.fieldname, field)
            self.assertIn("IP address", str(caught.exception))

    def test_resource_validator_stays_https_only(self):
        for source in ("http://example.com/", "www.example.com", "//example.com", "https://erp-developers.com/events"):
            with self.subTest(source=source), self.assertRaises(ValueError):
                external_https_url(source)
        self.assertEqual(external_https_url("https://example.com/"), "https://example.com/")

    def test_validation_never_resolves_or_fetches_a_url(self):
        with patch("socket.getaddrinfo", side_effect=AssertionError("No DNS here")):
            self.assertEqual(event_https_url("example.com/event"), "https://example.com/event")
