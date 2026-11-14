# ERP Developers - Frappe 16

**ERP: Engage. Reason. Progress.** Developers is the supporting brand signature.

A bilingual public technology website and editorial application built on Frappe
16 and ERPNext 16. Existing public pages are not a completed member community,
LMS, job aggregator, AI service, or operational project portal.

## Branches and evidence

| Branch | Purpose |
| --- | --- |
| `main` | Canonical plan, decisions and execution status; not application deployment source |
| `version-16` | Integration and ongoing Frappe 16 development |
| `production-v16` | Reviewed, commit-pinned release baseline; creation is not deployment or UAT sign-off |
| `refactor/*`, `feat/*`, `fix/*` | Isolated work, validated before promotion |

Frappe and ERPNext must remain on 16.x; declared Python runtime is 3.14+.
No Frappe 15 compatibility is asserted. CI tests Python 3.14 and browser fixtures;
a real Bench migration, authentication test and operational acceptance are separate.

**Last supplied deployment evidence:** `c8cb0deeb4eaeb14b30d3a931f717ad1dfe2bf60`
on `erp-developers.com`, with completed migration, asset checks and Arabic login
HTML verification. `3cddab9beb2d4b49427458befc1421bf7e8bcf71` introduced Projects,
Team Advice and the minimal footer in source; no later operator deployment log
was supplied during this refactor. Do not turn source/CI status into a live claim.

## Implemented capabilities

| Surface | Route / management |
| --- | --- |
| Brand website and full-height Vision | `/`, native EN/AR, Tajawal Arabic typography |
| Training playlists | `/training`; ERP Developers Playlist; public or permission-scoped private catalog |
| Reviewed knowledge sources | `/insights`; ERP Developers Resource and native Web Page |
| Regional events and photos | `/events`; ERP Developers Event, cover plus up to 8 gallery images |
| Public project stories | `/projects`; ERP Developers Publication, type Project |
| Team-authored advice | `/team-advice`; the same publication editor, type Team Advice |
| ERP/ERPNext guides | `/erp-development`, `/erpnext-development` |
| Consultation and privacy | `/lets-talk`, `/privacy`; native ERPNext appointment booking when explicitly enabled |
| Staff authentication | Native `/login?redirect-to=/desk`; no custom authentication implementation |

Footer text links are exactly **Let's Talk**, **Team Login**, and **Back to top**.
The shared header keeps the native language selector's space reserved from first
paint. Training opens a local modal only; no app-owned external YouTube button.
YouTube's own branding, authentication and embedding restrictions remain applicable.

## Publish content

Website Manager/System Manager maintains the editorial DocTypes. Records are not
public merely because they exist. Events need publication, regional relevance and
source verification. Publications require both **Approved for public sharing** and
**Published**; Team Advice also needs a public author name. A complete Arabic
version is used as a unit; partial publication translations fall back to English.

Read [Events](docs/EVENT_DIRECTORY.md), [image uploads](docs/EVENT_URLS_AND_IMAGES.md),
and [Projects and Team Advice](docs/PROJECTS_AND_TEAM_ADVICE.md). Content edits do
not require a build or migration. Public image uploads are accessible from upload,
even on drafts; unpublishing does not revoke the file URL. Never upload confidential
client material in public image fields. Private files are not silently made public.

## Security and module boundaries

Frappe owns authentication, sessions, password recovery, MFA and record permissions.
Guests receive curated, bounded public projections, not generic editorial DocType
read permissions. Private playlists use authenticated permission-filtered reads.
Project stories do not read ERPNext Project/Task/Customer/Employee/User records.

Native meeting booking remains behind `erpdev_meeting_booking_enabled`; availability,
email verification, capacity and CRM/calendar creation remain ERPNext's responsibility.
Legacy consultation intake is separate and disabled unless `erpdev_consultation_open`
is enabled. This refactor does not enable either flag or change privacy settings.
No unapproved provider feed, job scraping, scheduler or AI transfer is added.

The approved full PNG is unchanged, with SHA-256
`250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d`.
An Arabic logo is still awaiting name approval. Do not substitute branding silently.

See [Architecture](docs/ARCHITECTURE.md), [refactor audit](docs/REFACTOR_AUDIT.md),
and the [production release procedure](docs/PRODUCTION_RELEASE.md).

## Validation

From the repository root in an environment with the project's declared runtime,
Node.js, Babel and Pillow available:

```bash
bash scripts/check_source.sh
```

This single runner is used by both static CI and the pre-migration updater. It
checks Python, all shell/JavaScript files, unit/contract regressions, the playlist
DOM harness, and Arabic gettext compilation. It does not contact a site or database.
The browser workflows cover Chromium/Firefox and EN/AR desktop/mobile. The isolated
MariaDB job tests native pinned Frappe schema functions, not a full Bench install.
Production/refactor branches run the same checks as integration branches.

## Deploy or promote

Use the existing complete [deployment runner](scripts/deploy_erptest_lightnode.sh),
staged outside the mutable checkout, with an exact reviewed `EXPECTED_SHA`.
`RELEASE_BRANCH` defaults to `version-16` for compatibility. A first switch from
`version-16` to `production-v16` additionally requires `ALLOW_BRANCH_SWITCH=1`.
Subsequent production updates use `RELEASE_BRANCH=production-v16` without switching.
Never run an installer against an existing site or bypass a failed migration.

The runner backs up database/files, validates the target, refuses divergent history,
runs source checks before migration, builds and clears caches, then restarts only
the documented shared web process and verifies origin/public routes and Arabic copy.
The restart affects other sites sharing that process. Creating a GitHub branch does
not switch the server, run a migration, configure protection, or prove recovery readiness.
See the production procedure for commands and the remaining acceptance checklist.
Historical host troubleshooting remains in [ERPTEST_LIGHTNODE.md](docs/ERPTEST_LIGHTNODE.md).

## Roadmap - not implemented by this refactor

[The canonical plan on main](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/MASTER_PLAN.md)
and [execution status](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/STATUS.md)
remain the sources of truth. The new ideas are explicitly **Deferred / do not execute**:

- Entities such as `bedya`, `bdanexus` and `voyatours`; exact names, ownership and relationships need confirmation.
- Represent our own development work as projects.
- Later link to native ERPNext Project and use Task for assignments, rather than duplicate those engines.
- A permission-scoped portal for project owners and assignees.

No entity records, integration fields, task automation, new portal roles or portal
endpoints have been created. The existing public Projects showcase remains separate.
[Deferred scope and open decisions](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/DEFERRED_IDEAS.md).

## New isolated development sites

Follow [DEPLOYMENT.md](docs/DEPLOYMENT.md) and the host-specific guides. Never reuse
live site names or run `bench new-site`/reinstall for an update. The older MacVMs
installer is environment-specific and not a production deployment command.
