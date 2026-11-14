# ERP Developers — Public Hub (Frappe 16 + ERPNext 16)

## Status and deployment boundary

The public hub is developed on the `version-16` branch of `VoyaERP/erpdevelopers` and installed into the existing `erp-developers.com` ERPNext site. A GitHub merge is **not** evidence of live deployment or acceptance. Only the guarded, pinned existing-site updater may be used; do not create another site, patch ERPNext core or restart all Bench services.

## Public routes

| Public route | Purpose | Source |
|---|---|---|
| `/` | Brand homepage and service navigation | Current Frappe route |
| `/training` | Curated multiple YouTube playlists | `ERP Developers Playlist` records, published only |
| `/insights` | Reviewed links, practical advice and original articles | `ERP Developers Resource` records; original content in native `Web Page` |
| `/lets-talk` | Live slot booking with email verification | Native ERPNext `Appointment Booking Settings`, `Appointment`, `Lead`, `Event` |
| `/privacy` | Intake data notice (operational draft) | Static page; obtain legal approval |
| `/login?redirect-to=/desk` | **Team Login** (System Users) | Native Frappe authentication |

The brand header/footer and small local FAQ guide are shared Jinja includes. The assistant is **FAQ-only** and makes no network or AI calls. Website CSS/JS assets use content fingerprints; no auth templates or global Frappe assets are replaced.

## Backend / permission model

| DocType | Manager roles | Guest |
|---|---|---|
| `ERP Developers Playlist` | System Manager / Website Manager (read/write/publish) | No DocType read/write; approved fields rendered on `/training` only |
| `ERP Developers Resource` | System Manager / Website Manager (read/write/publish) | No DocType read/write; approved fields rendered on `/insights` only |
| `ERP Developers Consultation` | System Manager / Sales Manager (review/update); Sales User (read) | No DocType read/write. A site-guarded, POST-only rate-limited intake endpoint may create a request after explicit enablement |
| `Lead` (ERPNext) | Existing ERPNext CRM role permissions | Never created or queried by visitors |

The public controllers use server-side `published=1` filters, and return a fixed set of fields with a 60-row cap; internal resources additionally require the linked `Web Page` to be published. Source links are validated; external content is not copied, scraped or proxied.

## Let's Talk / live meeting booking lifecycle

This replaces the **public consultation enquiry** with a Greenbox-style,
two-stage booking experience. It does not build a second appointment engine.

- Visitors choose a **topic, date, IANA timezone and actual available slot**
  from ERPNext's native `get_appointment_slots` endpoint, then enter
  contact information and explicit contact consent.
- Site-scoped, rate-limited guest GET/POST methods enforce the approved host,
  input bounds, timezone, date window, current slot availability and CRM-safe
  note content. No visitor can choose an agent, DocType, lead or calendar ID.
- `book_meeting` delegates to ERPNext v16's native `create_appointment`.
  The standard Appointment is **Unverified** until the emailed confirmation
  link is opened. Native ERPNext then verifies capacity, links or creates the
  correct CRM **Lead/Customer**, assigns an agent and creates a Calendar
  **Event**. The public API returns only acceptance, never internal IDs.
- This flow creates **no parallel custom Consultation record**, Lead or Event.
  Existing `ERP Developers Consultation` records and legacy staff CRM
  action remain available for historical enquiries, but the old public
  `erpdev_consultation_open` endpoint is separate and should stay disabled.
- The page degrades to a branded availability message while prerequisites
  are missing; it does not show fictitious time slots or claim a booking is
  finalized before email verification.

### Site setup required before enabling public booking

Configure on **`erp-developers.com`** (not shared globally):

1. In **Appointment Booking Settings**, enable Appointment Scheduling and
   Appointment Booking Through Portal, set appointment duration, advance
   booking days, available weekday windows and a valid Holiday List.
2. Assign eligible **Agents** / scheduling users and ensure that they have
   appropriate CRM and Calendar permissions.
3. Configure and validate a **default outgoing Email Account**. Native
   portal verification sends a confirmation email. Without outgoing email
   the public booking page intentionally remains unavailable.
4. Approve the site's final privacy notice, consent wording, staff response
   process and retention policy.
5. Run the read-only diagnostic below. Only after prerequisites, backup,
   UAT and privacy approval, enable the per-site feature flag:

```bash
cd /data/frappe/frappe-bench
bench --site erp-developers.com execute erpdevelopers.meeting_status.diagnose_meeting_booking
bench --site erp-developers.com set-config erpdev_meeting_booking_enabled 1
bench --site erp-developers.com clear-cache
# Coordinate a targeted web-only worker reload and recheck the site.
```

Run the diagnostic again after enabling the flag; `ready` must be true.
Do not enable `erpdev_consultation_open` merely to use meeting booking.

### Acceptance and security

Test availability across Egypt/Saudi time zones, holidays, month boundaries,
fully booked slots and concurrent bookings. A fake slot must be rejected.
Verify an emailed link is delivered, only verified Appointments enter
the CRM/Calendar workflow, duplicate Leads are avoided through the
existing ERPNext logic, and no names, tokens or booking IDs are returned to
anonymous browsers. Check Guest/CRM/System Manager permissions and
rate limits; no workflows can be approved by the guest endpoint.

## Training catalogue: ideas and curation

Recommended learning tracks, **not seeded as invented playlists**:

- **ERP Foundations:** processes, accounting, inventory, procurement, sales, project costing.
- **Frappe & ERPNext Development:** DocTypes, hooks, workflows, permissions, API design, automated tests and deployment.
- **Dynamics 365 Business Central:** architecture, extensions/AL, integration patterns, operational controls.
- **Solution Architecture:** requirements discovery, C4 diagrams, ADRs, security, NFRs, integrations.
- **Cloud & Cybersecurity:** Azure, identity, API security, infrastructure-as-code, observability.
- **Data, AI & Automation:** practical analytics, responsible LLM workflows and enterprise governance.

An authorized curator creates a **Playlist** record with original title, optional Arabic title, YouTube playlist URL, topic, level, language, description, sort order and Published flag. Controller parses the actual YouTube `list` identifier; only HTTPS `/playlist?list=...` links from approved YouTube hosts are allowed. Videos open on YouTube, not autoplayed in the ERP Developers site. No YouTube API key or scraping is needed for this v1 directory.

A future sync may use the official `playlistItems.list` API to retrieve video metadata with quota controls, caching, API-key storage and editorial review. It must not treat video existence, copyright, availability, or accuracy as guaranteed.

For a real LMS, **evaluate Frappe Learning `version-16`** in an isolated compatibility test first; do not build another enrollment/certificate/grade engine inside this directory. Progress, certificates, assessment and private course content are **not yet implemented**.

## Smart insights

- **Original articles:** Use Frappe v16's supported `Web Page` DocType. Create, edit and publish the page there (Frappe's Blog module was moved out of Framework in v16).
- **Curated external reading:** Use `ERP Developers Resource` with Source Kind = External Source, HTTPS URL, publisher name and editorial note. The page links visitors to the original publisher; no copyrighted copying, automated scraping or unreviewed AI summaries.
- **Index:** Each approved resource is listed on `/insights`, with topic filtering and explanation of why the source is useful. The Jinja view escapes all publisher-controlled strings.
- **Next stage:** content freshness review date, moderation queues, source attribution, explicit editorial approval and semantic retrieval are separate governed features.

## LinkedIn integration readiness (not connected)

Native Frappe `Social Login Key` supports a **Custom OAuth provider**, with secrets kept in Password fields in the database. Before enabling LinkedIn sign-in, verify product approval and exact OpenID Connect scopes/redirect URI, configure a least-privilege OAuth client on the live site, decide whether external identities may create Member accounts, and regression-test existing staff/2FA login. Do not override `/login` and do not put client secrets in code or site pages.

Job-site aggregation is a separate integration: official LinkedIn Job Posting API access is restricted and is not a general-purpose read-all-jobs API. Do not scrape LinkedIn or promise universal job feeds; create an integration only with a signed-off API product, scopes, contract and privacy policy. Start with verified manual jobs and partner feeds when available.

## Governed AI assistant roadmap (not connected)

The live widget is a local FAQ guide for anonymous visitors: predefined questions/answers only. It makes no external request and does not read ERPNext data. A future AI adapter must use:

1. Explicit per-site feature flag and per-user consent.
2. Retrieval scoped to published knowledge and authorized ERPNext documents; no cross-tenant disclosure.
3. Citation/provenance validation, freshness metadata and prompt-injection resilience.
4. Service credentials in encrypted site configuration/secret manager; never in Git or browser code.
5. Rate/quota and spend limits, abuse handling, privacy retention, redaction and audit logging.
6. No autonomous CRM writes, publication, user access changes or workflow approval; human confirmation required.

## Release/UAT gates

- Back up the existing site with files, verify clean `version-16` checkout and exact intended commit, run static CI **before** `bench migrate`.
- Verify new DocTypes and permissions on real Frappe/ERPNext v16; check Website Manager, Sales Manager, Sales User, Guest, System Manager, cross-site behavior and CSRF/rate limiting.
- Verify `/training` and `/insights` both empty and with curator-provided published content; test invalid source URLs and unpublished original Web Pages.
- Verify `/lets-talk` is disabled until native calendar/email prerequisites and site flag are met; test current native slots, date/time zones, email verification, Lead/Event materialization, capacity and no guest reads.
- Inspect EN/AR mobile/desktop, RTL, localized validation, keyboard focus, native language picker, login recovery and staff navigation.
- Verify public canonical/SEO metadata and `sitemap.xml`; verify that no private content is indexed, external embeds are not auto-loaded and no user data is sent to LinkedIn/AI.
- A static GitHub CI success is **not** a successful deploy or a browser/auth security pass.
