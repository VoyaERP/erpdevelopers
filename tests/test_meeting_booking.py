"""Native ERPNext v16 scheduler contracts and guarded guest booking tests.

Mocked native ERPNext calls check delegation and payload handling only. Actual
site appointment verification/calendar tests must run against a configured
Frappe/ERPNext v16 staging environment.
"""
from datetime import date, datetime, timedelta
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
from zoneinfo import ZoneInfo
import importlib
import json
import sys

from erpdevelopers.branding import EXPECTED_SITE
from erpdevelopers.meeting_rules import (
    available_slot_matches, validate_booking_date, validate_meeting_contact,
    validate_slot_time,
)
from erpdevelopers.intake_rules import TOPICS

ROOT = Path(__file__).resolve().parents[1] / "erpdevelopers"


class TestBookingRules(TestCase):
    def test_date_is_in_visitors_timezone_and_within_configured_window(self):
        now = datetime(2026, 11, 14, 10, 0, tzinfo=ZoneInfo("Africa/Cairo"))
        self.assertEqual(
            validate_booking_date("2026-11-20", "Africa/Cairo", 7, now=now),
            "2026-11-20",
        )
        for value in ("2026-11-13", "2026-11-22", "", "11/20/2026"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_booking_date(value, "Africa/Cairo", 7, now=now)

    def test_slot_matches_native_time_and_availability(self):
        dt = datetime(2026, 11, 20, 11, 30, tzinfo=ZoneInfo("Africa/Cairo"))
        rows = [{"time": dt, "availability": True}]
        self.assertTrue(available_slot_matches(rows, "2026-11-20", "11:30:00"))
        self.assertFalse(available_slot_matches(rows, "2026-11-20", "11:35:00"))
        self.assertFalse(available_slot_matches(
            [{"time": "2026-11-20T11:30:00+02:00", "availability": False}],
            "2026-11-20", "11:30:00"))
        self.assertTrue(available_slot_matches(
            [{"time": "2026-11-20T11:30:00+02:00", "availability": True}],
            "2026-11-20", "11:30:00"))

    def test_invalid_times_are_rejected(self):
        self.assertEqual(validate_slot_time("09:05:00"), "09:05:00")
        for value in ("25:00:00", "9:05", "09:60:00", "09:00:00;DROP", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_slot_time(value)

    def test_contact_validation_and_consent(self):
        good = {
            "name": "Visitor", "email": "visitor@example.org", "topic": TOPICS[0],
            "phone": "+20 12345678", "company": "Example", "message": "ERP integration",
            "consent": 1, "website": "",
        }
        self.assertEqual(validate_meeting_contact(good)["name"], "Visitor")
        for overrides in ({"consent": 0}, {"website": "http://spam.example"},
                          {"topic": "Unapproved topic"}, {"name": "<b>Admin</b>"},
                          {"message": "x" * 1501}):
            with self.subTest(fields=overrides), self.assertRaises(ValueError):
                validate_meeting_contact({**good, **overrides})


class TestStatusGate(TestCase):
    def test_default_disabled_and_other_sites_cannot_enable(self):
        from erpdevelopers.meeting_status import booking_state
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=EXPECTED_SITE)
        frappe.conf = {}
        fake_utils = ModuleType("frappe.utils")
        fake_utils.cint = lambda value: int(value or 0)
        with patch.dict(sys.modules, {"frappe": frappe, "frappe.utils": fake_utils}):
            self.assertEqual(booking_state(), {"enabled": False})
            frappe.conf["erpdev_meeting_booking_enabled"] = 1
            frappe.local.site = "other-tenant.example"
            self.assertEqual(booking_state(), {"enabled": False})

    def test_missing_mail_config_disables_public_booking(self):
        from erpdevelopers.meeting_status import booking_state
        frappe = ModuleType("frappe")
        frappe.local = SimpleNamespace(site=EXPECTED_SITE)
        frappe.conf = {"erpdev_meeting_booking_enabled": 1}
        frappe.db = SimpleNamespace(exists=lambda dt, value: dt != "Email Account")
        frappe.get_single = lambda _: SimpleNamespace(
            enable_scheduling=1, enable_appointment_portal=1, holiday_list="Holidays",
            availability_of_slots=[object()], number_of_agents=1, agent_list=[object()],
            advance_booking_days=15, appointment_duration=30,
        )
        fake_utils = ModuleType("frappe.utils")
        fake_utils.cint = lambda value: int(value or 0)
        with patch.dict(sys.modules, {"frappe": frappe, "frappe.utils": fake_utils}):
            self.assertFalse(booking_state()["enabled"])
            frappe.db.exists = lambda dt, value: True
            ready = booking_state()
        self.assertTrue(ready["enabled"])
        self.assertEqual(ready["advance_booking_days"], 15)
        self.assertTrue(ready["email_confirmation_required"])


class TestNativeAPIBoundary(TestCase):
    def _modules(self, *, available=True):
        calls = []
        app = ModuleType("frappe")
        app.local = SimpleNamespace(request=None)
        app.whitelist = lambda **kw: lambda fn: fn
        app.PermissionError = PermissionError
        app._ = lambda value: value
        app.as_json = json.dumps
        def fail(message, exception=ValueError):
            raise exception(message)
        app.throw = fail
        limits = ModuleType("frappe.rate_limiter")
        limits.rate_limit = lambda **kw: lambda fn: fn
        utils = ModuleType("frappe.utils")
        utils.validate_email_address = lambda email, throw=True: email

        native = ModuleType("erpnext.www.book_appointment.index")
        day = (datetime.now(ZoneInfo("UTC")).date() + timedelta(days=1)).isoformat()
        slot = {"time": day + "T11:30:00+00:00", "availability": available}
        native.get_appointment_slots = lambda d, tz: [slot]
        native.create_appointment = lambda *args: calls.append(args)
        mods = {
            "frappe": app, "frappe.rate_limiter": limits, "frappe.utils": utils,
            "erpnext": ModuleType("erpnext"), "erpnext.www": ModuleType("erpnext.www"),
            "erpnext.www.book_appointment": ModuleType("erpnext.www.book_appointment"),
            "erpnext.www.book_appointment.index": native,
        }
        return mods, day, calls

    def test_booking_creates_only_native_unverified_appointment(self):
        mods, day, calls = self._modules()
        with patch.dict(sys.modules, mods):
            sys.modules.pop("erpdevelopers.meeting_booking", None)
            module = importlib.import_module("erpdevelopers.meeting_booking")
            with patch.object(module, "booking_state", lambda: {
                "enabled": True, "advance_booking_days": 14
            }):
                result = module.book_meeting(day, "11:30:00", "UTC", json.dumps({
                    "name": "Visitor", "email": "visitor@example.org", "phone": "",
                    "topic": TOPICS[0], "company": "Example",
                    "message": "Architecture discussion", "consent": 1,
                }))
                slots = module.get_meeting_slots(day, "UTC")
        self.assertTrue(result["accepted"])
        self.assertTrue(result["email_confirmation_required"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0:3], (day, "11:30:00", "UTC"))
        details = json.loads(calls[0][3])
        self.assertEqual(details["email"], "visitor@example.org")
        self.assertIn("ERP Developers meeting request", details["notes"])
        self.assertEqual(slots[0]["availability"], True)
        self.assertNotIn("lead", result)
        self.assertNotIn("appointment", result)

    def test_foreign_origin_is_rejected_before_booking(self):
        mods, day, calls = self._modules()
        mods["frappe"].local = SimpleNamespace(
            request=SimpleNamespace(headers={"Origin": "https://untrusted.example"})
        )
        with patch.dict(sys.modules, mods):
            sys.modules.pop("erpdevelopers.meeting_booking", None)
            module = importlib.import_module("erpdevelopers.meeting_booking")
            with patch.object(module, "booking_state", lambda: {
                "enabled": True, "advance_booking_days": 14
            }):
                with self.assertRaises(PermissionError):
                    module.book_meeting(day, "11:30:00", "UTC", {
                        "name": "Visitor", "email": "visitor@example.org",
                        "topic": TOPICS[0], "consent": 1
                    })
        self.assertEqual(calls, [])

    def test_rejects_multiple_email_recipients(self):
        mods, day, calls = self._modules()
        with patch.dict(sys.modules, mods):
            sys.modules.pop("erpdevelopers.meeting_booking", None)
            module = importlib.import_module("erpdevelopers.meeting_booking")
            with patch.object(module, "booking_state", lambda: {
                "enabled": True, "advance_booking_days": 14
            }):
                with self.assertRaisesRegex(ValueError, "Review"):
                    module.book_meeting(day, "11:30:00", "UTC", {
                        "name": "Visitor", "email": "one@example.org, two@example.org",
                        "topic": TOPICS[0], "consent": 1
                    })
        self.assertEqual(calls, [])

    def test_book_unavailable_slot_does_not_create_appointment(self):
        mods, day, calls = self._modules(available=False)
        with patch.dict(sys.modules, mods):
            sys.modules.pop("erpdevelopers.meeting_booking", None)
            module = importlib.import_module("erpdevelopers.meeting_booking")
            with patch.object(module, "booking_state", lambda: {
                "enabled": True, "advance_booking_days": 14
            }):
                with self.assertRaisesRegex(ValueError, "no longer available"):
                    module.book_meeting(day, "11:30:00", "UTC", {
                        "name": "Visitor", "email": "visitor@example.org",
                        "topic": TOPICS[0], "consent": 1
                    })
        self.assertEqual(calls, [])

    def test_public_booking_disabled_by_default(self):
        mods, day, calls = self._modules()
        with patch.dict(sys.modules, mods):
            sys.modules.pop("erpdevelopers.meeting_booking", None)
            module = importlib.import_module("erpdevelopers.meeting_booking")
            with patch.object(module, "booking_state", lambda: {"enabled": False}):
                self.assertEqual(module.get_meeting_settings(), {"enabled": False})
                with self.assertRaises(PermissionError):
                    module.get_meeting_slots(day, "UTC")
        self.assertEqual(calls, [])

    def test_public_js_never_creates_lead_or_writes_local_storage(self):
        script = (ROOT / "public/js/meeting.js").read_text()
        backend = (ROOT / "meeting_booking.py").read_text()
        self.assertIn('get_meeting_slots', script)
        self.assertIn('book_meeting', script)
        self.assertIn("get_appointment_slots", backend)
        self.assertIn("create_appointment", backend)
        self.assertNotIn('frappe.get_doc({"doctype": "Lead"', backend)
        self.assertNotIn("localStorage", script)
        self.assertNotIn("innerHTML", script)
        self.assertNotIn("fetch(", script)
        self.assertIn("data-meeting-stage", (ROOT / "www/lets-talk.html").read_text())


if __name__ == "__main__":
    import unittest
    unittest.main()
