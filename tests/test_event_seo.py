"""Pure event SEO regression tests; no live Frappe site required."""
import json
import unittest
from erpdevelopers.event_seo import event_path, event_name_from_path, event_jsonld


class EventSEOTests(unittest.TestCase):
    def sample(self, **updates):
        event = {
            "name": "abc1234567", "title": "ERPNext Workshop", "title_ar": "ورشة ERPNext",
            "description": "ERP architecture and integration",
            "description_ar": "تطوير وإدارة أنظمة ERP",
            "organizer": "ERP Developers", "event_status": "Scheduled",
            "date_only": 1, "start_date": "2027-03-05", "end_date": "2027-03-05",
            "event_format": "Online", "event_url": "https://events.example.com/register",
            "media": {"cover": None, "gallery": []},
        }
        event.update(updates)
        return event

    def test_link_round_trip_and_slug_is_not_an_identifier(self):
        event = self.sample()
        self.assertEqual(event_name_from_path(event_path(event)), "abc1234567")
        self.assertEqual(event_name_from_path("new-title-abc1234567"), "abc1234567")
        for invalid in ("../../secret", "something", "abc1234567%2Fapi"):
            self.assertIsNone(event_name_from_path(invalid))

    def test_schema_uses_real_event_facts(self):
        data = json.loads(event_jsonld(self.sample()))
        self.assertEqual(data["@type"], "Event")
        self.assertEqual(data["startDate"], "2027-03-05")
        self.assertEqual(data["eventAttendanceMode"], "https://schema.org/OnlineEventAttendanceMode")
        self.assertEqual(data["location"]["@type"], "VirtualLocation")
        self.assertNotIn("offers", data)
        self.assertNotIn("aggregateRating", data)

    def test_cancelled_event_is_not_falsely_advertised_as_scheduled(self):
        data = json.loads(event_jsonld(self.sample(event_status="Cancelled")))
        self.assertEqual(data["eventStatus"], "https://schema.org/EventCancelled")

    def test_jsonld_escapes_script_breakout_and_preserves_unicode(self):
        schema = event_jsonld(self.sample(description="</script><script>alert(1)</script>"), language="ar")
        self.assertNotIn("</script>", schema)
        self.assertEqual(json.loads(schema)["name"], "ورشة ERPNext")


if __name__ == "__main__":
    unittest.main()
