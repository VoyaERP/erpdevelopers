# ERP Developers architecture - current Frappe 16 application

## Layer boundaries

| Layer | Responsibility |
| --- | --- |
| Native Frappe/ERPNext | Authentication, permission engine, File storage, ORM, migrations, Appointment/CRM/calendar behavior |
| Pure domain rules | `catalog_rules`, `intake_rules`, `meeting_rules`, `event_rules`, `publication_rules` |
| Shared editorial mechanics | `catalog_support.schema_status/page_number`, `taxonomy.TOPICS` |
| Shared public-media boundary | `public_media`: path validation, public File projection, permission and local image-byte checks |
| Domain projections | `catalog`, `events_catalog`, `publications`; fixed DocTypes/fields and mandatory publication filters |
| Event gallery | `event_media`; parent-scoped gallery, bounded rows, uses shared image checks |
| HTTP controllers | Thin `www/*.py` context providers and unchanged booking/legacy intake APIs |
| Presentation | Shared page/nav/footer templates; scoped CSS; native language picker; click-initiated player |
| Operations | Shared source check runner; pinned updater; complete deployment/readiness/HTTP verifier |

Publications no longer import event-specific media internals. Existing import names
are aliases to the shared functions, not duplicated implementations. Their pure
normalization can load without a Frappe runtime. Consultation topic choices remain
separate from the public editorial taxonomy because they describe different concepts.

## Authorization and data separation

Public projection is deliberately different from granting Guest permission to read
a DocType. Public queries have constant DocTypes, allowlisted fields, mandatory
publish/review/audience filters and bounded pagination. Internal notes are not
returned. Private playlists still require authenticated `get_list` permission checks.

The current Project publication is a public story. It is NOT an ERPNext Project,
a Task list or a client portal. The future entity/project/task/owner/assignee ideas
are documented only, with no schema, endpoint or permission expansion in this release.

Frappe retains native login, password reset, email links, MFA and session controls.
Meeting APIs remain opt-in and site-gated; ERPNext owns slot capacity and verification.
Legacy consultation intake/CRM handoff remains distinct. No automatic feature enabling,
remote importer, credentials or custom authentication is added.

`schema_status` detects absent tables/columns without suppressing unrelated database
errors. A temporarily empty directory during incomplete migration is not a declaration
that deployment succeeded. Existing URL Small Text storage and 1500-character server
validation are retained; native schema upgrade regressions remain in CI.

## Images, links and localization

Public images use native File records and local bytes. They are bounded to supported
formats, 5 MB and 24 megapixels. Remote fetches, arbitrary paths, SVG, private files,
traversal and silent privacy changes are rejected. Rendering rechecks current public
File references; upload/save verifies content and read permission. Public uploads are
public even on drafts and remain reachable after unpublishing unless removed separately.

URL validation normalizes event links but does not resolve DNS or verify redirects.
It must not be reused as a complete SSRF defense for future server-side importers.

EN/AR UI uses Frappe CSV/gettext. Public copy is escaped; Project/Advice body text is
plain text with preserved paragraphs. A publication uses a complete Arabic variant
or an explicit English fallback. Tajawal remains externally delivered as previously
configured; isolated tests do not establish real font/network availability.

## Stable UI and branding

One shared server-rendered header/footer; no injected second menu or login form.
The native picker retains its reserved geometry; mobile links scroll in one row.
Footer text links remain only Let's Talk, Team Login and local Back to top.
Playlist CSS overrides are consolidated in place without adding another stylesheet
or player script. The approved logo bytes are unchanged. Arabic-logo approval remains open.

Assets use content fingerprints. Python workers must load the new code to update
cached fingerprints; origin/public byte checks are separate from visual UAT.

## Deployment and evidence

`version-16` is integration; `production-v16` is the reviewed release branch; `main`
contains canonical governance. Promotion is pinned and explicit. Source checks are
shared by CI and the updater. No forced reset, downgrade, database deletion, core
modification or service-wide restart is introduced.

All original runtime module/endpoint paths and DocType schemas are preserved in this
refactor. Full Bench integration, actual publishing/upload/auth flows, backup restore,
mail delivery, access review, performance and operational sign-off remain release gates.
See [PRODUCTION_RELEASE.md](PRODUCTION_RELEASE.md) and [REFACTOR_AUDIT.md](REFACTOR_AUDIT.md).
