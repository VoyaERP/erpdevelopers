# Regional Events and in-page-only training - 2026-11-14

## Delivered scope

- `/events`: public, bilingual, server-rendered directory with topic, country,
  attendance format, upcoming/ongoing and past filters, and 12-row pagination.
- Native `ERP Developers Event` DocType. Website Manager and System Manager
  curate records; Guest has no direct DocType read or write rights. The public
  controller selects an explicit field allowlist from Published + Regional records.
  Private Frappe Calendar Event and appointment data are never queried.
- Two-column grouped fields, separate Arabic title/description, native Country
  link, conditional physical venue fields, publication and status actions.
- Venue-local Date/Time inputs plus an explicit IANA zone produce indexed UTC
  boundaries. Date-only events include the whole end date. Invalid/ambiguous DST
  times are rejected rather than silently moved. Scheduled, Postponed and Cancelled
  are distinct from publication. Source verification is required before publishing.
- Official source attribution, verification date and provider/external-ID identity.
  Provider identity is unique when present, enabling future idempotent imports.
  Internal notes and integration identifiers are not public fields.
- No example events are inserted. No paid provider, remote fetching, API keys,
  scraping, scheduler or automatic publication is enabled by this release.
- All app-owned Open on YouTube links removed from Training cards and dialog.
  Watch here still opens one privacy-enhanced iframe after a user click. YouTube's
  own in-player controls/attribution are not hidden or blocked.
- OpenGraph smoke test parses head metadata rather than matching one exact string.
  Frappe v16's meta template can emit extra spaces between attributes. Missing or
  conflicting `og:type=website` still fails with observed values.

## Editorial use

After migration, search Desk for ERP Developers Event, or use Manage events on
`/events` as an authorized curator. Enter title, topic, type, organizer, format,
local dates and timezone, and a validated HTTPS official URL. Add physical venue
information for in-person/hybrid events. Verify against the organizer, enter the
verification date, then publish. Existing unpublished records are never auto-published.
Mark cancellations/postponements explicitly. Regional relevance includes events
in the region and online events useful to that audience; it is an editorial flag,
not a claim that a provider covers every country.

New Arabic messages use Frappe v16's native `locale/ar.po` catalog, compiled during
asset build and merged by Frappe with the unchanged legacy CSV translations.
Tajawal, English styling and the approved logo are preserved.

## API assessment (official sources checked 2026-11-14)

1. PredictHQ Events API: conference/expo categories, country/date/text filters,
   subscription-scoped geography and time ranges. Candidate for a paid discovery
   pilot; verify Saudi Arabia/UAE/Egypt/Qatar samples and public-display rights.
   https://docs.predicthq.com/api/events/search-events
2. Ticketmaster Discovery API: API-key access, country and keyword filters;
   documented default quota 5,000 calls/day and 5 requests/second. UAE is explicitly
   represented in the Discovery Feed. Supported country codes do not prove useful
   ERP/technology coverage. Secondary source, not the main business-events feed.
   https://developer.ticketmaster.com/products-and-docs/apis/discovery-api/v2/
   https://developer.ticketmaster.com/products-and-docs/apis/discovery-feed/
3. Meetup: current GraphQL API and OAuth; new OAuth consumers require active Pro
   membership and application approval. Useful to evaluate for approved community
   groups/networks, not unrestricted bulk regional harvesting.
   https://help.meetup.com/hc/en-us/articles/41453576628749-How-can-I-get-access-to-Meetup-s-API
   https://www.meetup.com/graphql/guide/
4. Eventbrite: general public Event Search was shut down on 12 December 2019.
   Do not base regional discovery on `/v3/events/search/`. Authorized organizer
   integrations are a separate use case.
   https://www.eventbrite.com/platform/docs/by-location

Recommended next integration: server-side provider adapter -> bounded import ->
provider ID deduplication -> draft review -> explicit publication. Store tokens
server-side in encrypted Password fields, never browser JS. Add allowlisted hosts,
request timeouts, pagination caps, rate-limit handling, source change/cancellation
tracking and audit logs. Keep sync manual/disabled until credentials, coverage,
licensing, retention and operating cadence are approved. Use organizer-provided
ICS/RSS feeds only where offered and permitted; no universal regional feed is assumed.

## Verification boundary

CI covers Python rules/access contracts, native gettext compilation, real-script
JavaScript cases and Chromium/Firefox fixtures using actual page templates and
styles. Provider and font responses are mocked. This is not a live database,
provider coverage, YouTube availability or production browser verification.
Deploy with the pinned backup-first updater, migrate/build, reload only the
confirmed web process and run read-only `scripts/verify_frontend.sh`.
