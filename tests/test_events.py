"""Event validation, public read boundaries and page context without a live site."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest import TestCase
from unittest.mock import patch
import json
import sys

from erpdevelopers.event_rules import normalize_event, TOPICS, FORMATS, EVENT_TYPES, STATUSES
from erpdevelopers import events_catalog as catalog

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "erpdevelopers"
NOW = datetime(2026, 11, 14, 4, tzinfo=timezone.utc)


def record(**updates):
    data = dict(title="Architecture forum",title_ar="",description="Reviewed technical conference",description_ar="",
                organizer="Example organizer",topic="Solution Architecture",event_type="Conference",
                event_format="In person",event_status="Scheduled",country="Saudi Arabia",city="Riyadh",
                venue="Conference center",start_date="2030-05-10",end_date="2030-05-11",date_only=1,
                time_zone="Asia/Riyadh",event_url="https://events.example.org/forum",source_url="",
                source_provider="Manual",source_event_id="",published=0,verified_on="2020-01-01")
    data.update(updates)
    return data


class TestEventRules(TestCase):
    def test_date_only_inclusive_end_and_utc_conversion(self):
        values=normalize_event(record())
        self.assertEqual(values["start_utc"],datetime(2030,5,9,21))
        self.assertEqual(values["end_utc"],datetime(2030,5,11,21))
        self.assertIsNone(values["start_time"])
    def test_explicit_local_times(self):
        values=normalize_event(record(date_only=0,end_date="2030-05-10",start_time="09:00",end_time=timedelta(hours=18)))
        self.assertEqual(values["start_utc"],datetime(2030,5,10,6))
        self.assertEqual(values["end_utc"],datetime(2030,5,10,15))
    def test_rejects_reversed_dates_and_times(self):
        for updates in ({"end_date":"2029-01-01"},{"date_only":0,"end_date":"2030-05-10","start_time":"18:00","end_time":"09:00"}):
            with self.subTest(updates=updates),self.assertRaises(ValueError): normalize_event(record(**updates))
    def test_bad_zone_and_dst_gap_are_rejected(self):
        for updates in ({"time_zone":"Bad/Zone"},{"date_only":0,"time_zone":"America/New_York","start_date":"2026-03-08","end_date":"2026-03-08","start_time":"02:30","end_time":"04:30"}):
            with self.subTest(updates=updates),self.assertRaises(ValueError): normalize_event(record(**updates))
    def test_ambiguous_clock_change_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            normalize_event(record(date_only=0,time_zone="America/New_York",start_date="2026-11-01",end_date="2026-11-01",start_time="01:30",end_time="03:00"))
    def test_publish_needs_recorded_source_verification(self):
        with self.assertRaisesRegex(ValueError,"verification date"):
            normalize_event(record(published=1,verified_on=None))
        normalize_event(record(published=1))
    def test_online_does_not_require_a_physical_venue(self):
        normalize_event(record(event_format="Online",country="",city="",venue=""))
        with self.assertRaisesRegex(ValueError,"venue"):
            normalize_event(record(venue=""))
    def test_untrusted_links_and_invalid_enums_are_rejected(self):
        for updates in ({"event_url":"javascript:alert(1)"},{"source_url":"https://127.0.0.1/secret"},{"topic":"unreviewed"},{"event_status":"Public"}):
            with self.subTest(updates=updates),self.assertRaises(ValueError): normalize_event(record(**updates))
    def test_provider_identity_is_stable_and_namespace_scoped(self):
        a=normalize_event(record(source_provider="Partner",source_event_id="123"))
        b=normalize_event(record(source_provider="partner",source_event_id="123"))
        c=normalize_event(record(source_provider="Other",source_event_id="123"))
        self.assertEqual(a["source_key"],b["source_key"])
        self.assertNotEqual(a["source_key"],c["source_key"])
        self.assertIsNone(normalize_event(record())["source_key"])
    def test_publication_defaults_permissions_and_two_columns(self):
        schema=json.loads((APP / "erp_developers/doctype/erp_developers_event/erp_developers_event.json").read_text())
        fields={f["fieldname"]:f for f in schema["fields"]}
        self.assertEqual(fields["published"]["default"],"0")
        self.assertTrue(fields["source_key"]["unique"])
        self.assertEqual(fields["country"]["fieldtype"],"Link")
        self.assertEqual(fields["country"]["options"],"Country")
        self.assertNotIn("Guest",{p["role"] for p in schema["permissions"]})
        self.assertGreaterEqual(sum(f["fieldtype"]=="Column Break" for f in schema["fields"]),5)
        for key,choices in (("topic",TOPICS),("event_format",FORMATS),("event_type",EVENT_TYPES),("event_status",STATUSES)):
            self.assertEqual(fields[key]["options"].split("\n"),list(choices))
        self.assertNotIn("internal_notes",catalog.PUBLIC_FIELDS)
        self.assertNotIn("source_event_id",catalog.PUBLIC_FIELDS)


class TestEventDirectory(TestCase):
    def fake(self, rows=None, count=1):
        fake=ModuleType("frappe"); fake.queries=[]
        def query(doctype,**kwargs):
            fake.queries.append(kwargs)
            if kwargs["fields"]==["country"]: return [{"country":"Saudi Arabia"}]
            return rows if rows is not None else [{**record(),**normalize_event(record()),"name":"TEST-EVENT"}]
        fake.get_all=query
        fake.db=SimpleNamespace(count=lambda *args,**kwargs: count)
        return fake
    def run_directory(self, fake, params=None):
        with patch.dict(sys.modules,{"frappe":fake}),patch.object(catalog,"_schema_status",return_value={"table_present":True,"missing_columns":[]}):
            return catalog.get_event_directory(params,lang="en",now=NOW)
    def test_all_public_queries_require_publication_and_regional_relevance(self):
        fake=self.fake(); result=self.run_directory(fake)
        for query in fake.queries:
            self.assertEqual(query["filters"]["published"],1)
            self.assertEqual(query["filters"]["regional_relevance"],1)
        self.assertEqual(len(result["event_rows"]),1)
        self.assertEqual(fake.queries[-1]["limit_page_length"],12)
        self.assertEqual(fake.queries[-1]["filters"]["end_utc"],[">",datetime(2026,11,14,4)])
    def test_filters_and_pagination_are_bounded_and_encoded(self):
        fake=self.fake(count=25)
        result=self.run_directory(fake,{"page":"2","topic":"Solution Architecture","country":"Saudi Arabia","event_format":"Hybrid"})
        query=fake.queries[-1]
        self.assertEqual(query["limit_start"],12)
        self.assertEqual(query["filters"]["topic"],"Solution Architecture")
        self.assertEqual(result["pages"],3)
        self.assertIn("page=3",result["next_url"])
        self.assertIn("country=Saudi+Arabia",result["previous_url"])
    def test_invalid_filter_values_are_not_used_in_queries(self):
        fake=self.fake(); self.run_directory(fake,{"page":"evil","topic":"<script>","country":"unknown","event_format":"x"})
        self.assertNotIn("topic",fake.queries[-1]["filters"])
        self.assertNotIn("country",fake.queries[-1]["filters"])
        self.assertEqual(fake.queries[-1]["limit_start"],0)
    def test_missing_schema_is_an_empty_directory_without_queries(self):
        fake=self.fake()
        with patch.dict(sys.modules,{"frappe":fake}),patch.object(catalog,"_schema_status",return_value={"table_present":False,"missing_columns":[]}):
            result=catalog.get_event_directory(now=NOW)
        self.assertEqual(result["event_rows"],[])
        self.assertEqual(fake.queries,[])
    def test_unsafe_legacy_url_is_never_rendered(self):
        fake=self.fake(rows=[{**record(),"event_url":"https://localhost/private"}])
        self.assertEqual(self.run_directory(fake)["event_rows"],[])
    def test_events_route_is_public_without_a_guest_doctype_permission(self):
        from erpdevelopers.www import events
        fake=ModuleType("frappe"); fake.session=SimpleNamespace(user="Guest")
        fake.local=SimpleNamespace(lang="ar"); fake.form_dict={}
        fake.has_permission=lambda *a,**kw:self.fail("Guest attempted an administrative permission lookup")
        context=SimpleNamespace()
        with patch.dict(sys.modules,{"frappe":fake}),patch.object(events,"get_event_directory",return_value={"event_rows":[]}):
            events.get_context(context)
        self.assertFalse(context.can_manage_events)
        self.assertEqual(context.no_cache,1)
        self.assertIn("events.css?v=",context.events_css_url)
        self.assertEqual(events.sitemap,1)
