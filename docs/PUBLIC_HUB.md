# ERP Developers — Public Hub (Frappe 16 + ERPNext 16)

## Status and deployment boundary

The public hub is developed on the `version-16` branch of `VoyaERP/erpdevelopers` and installed into the existing `erp-developers.com` ERPNext site. A GitHub merge is **not** evidence of live deployment or acceptance. Only the guarded, pinned existing-site updater may be used; do not create another site, patch ERPNext core or restart all Bench services.

## Public routes

| Public route | Purpose | Source |
|---|---|---|
| `/` | Brand homepage and service navigation | Current Frappe route |
| `/training` | Curated multiple YouTube playlists | `ERP Developers Playlist` records, published only |
| `/insights` | Reviewed links, practical advice and original articles | `ERP Developers Resource` records; original content in native `Web Page` |
| `/lets-talk` | Consultation request for staff review | `ERP Developers Consultation` private DocType |
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

## Let's Talk / scheduling lifecycle

1. Visitor opens `/lets-talk`, reads the privacy notice, provides consent, topic, date, time window and IANA time zone. Requested date and window **are not an actual reservation**.
2. Public intake is disabled until site administration deliberately sets `erpdev_consultation_open=1`, after approving the privacy/retention notice, staff ownership, abuse monitoring and notification rules.
3. When enabled, Frappe's built-in CSRF protection and site-specific rate limiter apply; backend validates form fields and creates only `ERP Developers Consultation` with status **Requested**. Honeypot requests create no record. The API returns no record IDs or other visitors' data.
4. An authorized ERPNext Sales Manager/System Manager reviews the private record. The grouped **CRM → Create or Link ERPNext Lead** action checks both consultation-write and CRM permissions and reuses an accessible Lead with the same email to reduce duplicates.
5. Staff coordinate availability and create an `Event` through Frappe Calendar, link it to the consultation, then set status **Confirmed**. Saving as Confirmed without a Calendar Event is rejected. Email/calendar invitations, allocation rules and reminders must be configured and tested separately.

**Activation (only after release UAT and privacy approval):**

```bash
cd /data/frappe/frappe-bench
bench --site erp-developers.com set-config erpdev_consultation_open 1
# Coordinate targeted web reload; verify session/CSRF/role checks and the new request flow.
```

Do **not** enable guest intake on other sites sharing the Bench. Make a backup and agree on staff response ownership and data retention first. No unconditional guest-write permission is granted to the DocType.

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
- Verify `/lets-talk` disabled by default; after controlled enablement test valid/invalid fields, duplicate Lead prevention, confirmation requiring Event and no guest reads.
- Inspect EN/AR mobile/desktop, RTL, localized validation, keyboard focus, native language picker, login recovery and staff navigation.
- Verify public canonical/SEO metadata and `sitemap.xml`; verify that no private content is indexed, external embeds are not auto-loaded and no user data is sent to LinkedIn/AI.
- A static GitHub CI success is **not** a successful deploy or a browser/auth security pass.
