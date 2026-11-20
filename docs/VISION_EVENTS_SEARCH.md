# Vision, event publishing and search visibility

## Delivered

The Our Vision navigation remains /#vision. Its section now fills at least the
viewport below the sticky header and uses the existing local blue/teal technology
illustration, with dark contrast layers and responsive EN/AR text. This is brand
artwork, not a photograph of staff. No new remote image dependency, fullscreen
API, image library or logo change is introduced. Text can grow beyond one screen
on small devices instead of being clipped.

Two server-rendered educational guides are linked from the homepage:
/erp-development and /erpnext-development. They share one renderer/template,
have original English/Arabic content, distinct page titles/descriptions, explicit
?_lang=en and ?_lang=ar canonicals, reciprocal hreflang links, visible breadcrumbs
and matching WebPage/BreadcrumbList JSON-LD. Frappe's existing sitemap discovery
is enabled; no competing sitemap or crawler override is introduced. These are
editorial guides, not claims of vendor partnership/certification or available
services. The homepage description now reflects ERP/ERPNext guides and events.

## How a curator publishes an event

1. Sign in as a user with Website Manager or System Manager access. Open
   /desk/erp-developers-event, or choose Manage events on /events.
2. Create a record. Enter Title, Topic, Event type, Organizer, Attendance format,
   Event status, Description, Start date, End date, Event time zone and Official
   event URL. Add Arabic Title/Arabic description to display Arabic content.
3. Dates only avoids inventing unconfirmed start/end times. Otherwise enter Local
   start time and Local end time. Use venue time and an IANA zone, e.g. Africa/Cairo,
   Asia/Riyadh or Asia/Dubai. In-person/hybrid requires Country, City and Venue.
4. Keep Relevant to the Middle East audience checked. Verify details against the
   organizer and record Source verified on. Save, then choose Publication > Publish,
   or check Published and save. The server rejects publication without verification.
5. Check /events while signed out. The default view includes upcoming/ongoing rows
   whose derived UTC end is still in the future. Past entries appear under Past
   events. Reset country/topic/format filters when troubleshooting a missing card.

Saving data is not a code deployment: do not run bench migrate/build for each event.
No provider sync is active, no invented events are seeded and private Calendar
Event/appointment records remain outside this directory. Cancelled and Postponed
remain visible with their status; unpublish to remove a listing from public view.

## Google: operator work, not a ranking guarantee

Confirm successful live HTTP responses before submitting URLs. Persistent 5xx
responses prevent useful crawling. The previous operator report included a 502
after a Gunicorn restart; static CI cannot establish that the live site recovered.

Verify the erp-developers.com Domain property in Google Search Console with the
exact DNS verification record Google issues, at the authoritative DNS provider.
Do not invent a token or overwrite another verification record. Submit sitemap.xml,
inspect the homepage, both guide URLs in EN/AR and /events, and request indexing
only after live URL inspection succeeds. Search Console and DNS changes are NOT
performed by this release. Review indexing, queries, clicks and country/language
performance. A sitemap or an indexing request is not a guarantee of inclusion.

Prioritize the ERP Developers brand and specific topics (ERPNext customization,
Frappe integrations, ERP workflow development) before generic queries such as ERP
or development. Publish original project write-ups with permission, practical
examples, dated maintenance notes and genuine author expertise. Do not publish
confidential customer data, fabricated reviews, bought links, hidden keywords or
near-duplicate pages for every city/product. Platform-specific pages should reflect
work/content actually available; no official vendor affiliation is implied.

The event directory currently has a listing URL, not a dedicated indexed detail
URL for each event. Do not add misleading per-event rich-result claims to this
listing. Dedicated public event pages and their own eligible Event markup would
be a separate feature, subject to source verification and Google's requirements.

## Primary references reviewed 2026-11-14

- https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- https://developers.google.com/search/docs/specialty/international/localized-versions
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
- https://developers.google.com/crawling/docs/troubleshooting/http-status-codes
- https://support.google.com/webmasters/answer/9008080
- https://developers.google.com/search/docs/appearance/structured-data/event
- Frappe API/DocType/permissions references are linked in the ERPNext guide.

## Verification boundary

Pure tests and isolated browser fixtures validate code, markup, layout, language
metadata and navigation. They do not prove Google indexing, ranking, third-party
font delivery, real Frappe permissions/database behavior or production readiness.
Deploy the reviewed commit with the existing backup-first updater. After web
restart use a bounded localhost-origin readiness check before the full verifier.
