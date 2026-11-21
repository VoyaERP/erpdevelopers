# ERP Developers - Frappe 16

**ERP: Engage. Reason. Progress.** Developers is the supporting brand signature.

A bilingual public technology website and editorial application built on Frappe
16 and ERPNext 16. Existing public pages are not a completed member community,
LMS, job aggregator, AI service, or operational project portal.

## Branches, compatibility, and evidence

The maintained branches are **main**, **dev**, **version-15**, and **version-16**.
`main` is the default reviewed Frappe 16 application + governance source;
`dev` is its integration stream; `version-16` is its release stream;
`version-15` is a separately compatible Frappe 15 release line.
These are Git refs, not evidence of installation.

This `dev` source targets Frappe/ERPNext 16. The v16 application requires Python 3.14+, and its site-scoped boot and login context hooks are enabled.

The public header is one Jinja include and the public CSS is one `brand.css` file;
one shared branding helper computes content-fingerprinted asset URLs without
retaining an old fingerprint in the web process. No duplicate navigation script
or second header stylesheet is introduced by this refactor.

See [current branch policy](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/BRANCH_STRATEGY.md)
and the [release checklist](docs/PRODUCTION_RELEASE.md). CI fixture tests and
source existence do **not** prove Azure DNS, Cloudflare, live authentication,
Frappe 15 runtime behavior, or owner visual approval.

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

## Deployment and promotion

Run only the version-compatible, commit-pinned release on an independently
validated site. The existing `scripts/deploy_erptest_lightnode.sh` and
`scripts/update_erptest_lightnode.sh` target the **historical**
`erptest-lightnode` host with a different Bench directory and Supervisor service.
**Do not run those scripts on the current Azure `erpdevelopers` VM.**

The Azure v16 host uses `/home/frappe/frappe-bench` owned by `frappe`,
a repository-specific SSH key and systemd web service. Deployment requires an
operator-verified backup, compatible installed Frappe major version, matching
commit pin, clean checkout, source/build checks, cache clear, controlled web
process restart, exact CSS fingerprint verification, and localhost-origin versus
public-CDN comparison. See the [branch strategy](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/BRANCH_STRATEGY.md).
No code change automatically deploys to that host.

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
