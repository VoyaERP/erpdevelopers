# ERP Developers — Execution Status / متابعة التنفيذ

**Snapshot:** 2026-11-14 · **Repository:** VoyaERP/erpdevelopers
**Plan:** [ED-MP-001 v1.1](MASTER_PLAN.md) · **Ideas:** [Deferred, not implemented](DEFERRED_IDEAS.md)

> الكود المختبر ليس نشراً فعلياً. فرع الإنتاج لا يُعد اعتماداً تشغيلياً، وأفكار الكيانات والمشروعات والبوابة مسجلة دون تنفيذ.

## Current release position

| Layer | Observed state |
| --- | --- |
| Application source | `3054ebf389179c829e827d552b727c3291b8d28e` |
| Production source branch | `production-v16` created at that exact tested commit |
| Integration source branch | `version-16` fast-forwarded to the same commit; remains the development/integration branch |
| Isolated work branch | `refactor/production-readiness-20261114` retained for traceability |
| Canonical documentation | This `main` branch: README, Master Plan, Status, Decisions and Deferred Ideas |
| Last supplied successful live deployment | `c8cb0deeb4eaeb14b30d3a931f717ad1dfe2bf60` on `erp-developers.com` / `erptest-lightnode` |
| Deployment of this refactor | NOT performed; no operator evidence of server promotion or new migration supplied |
| Launch/operational acceptance | Still requires staging, live UAT, restore and operator/owner approval |

Creating the production branch did not change the server checkout, DNS, site
configuration, user permissions, repository default branch, branch protections,
credentials or running services. No force-push or automatic deployment was used.

## Application-wide refactor completed in source

Based on `3cddab9beb2d4b49427458befc1421bf7e8bcf71`, with existing features preserved:

- Shared catalog schema probing, bounded page parsing and playlist URL projection;
  plain-dictionary resource rows no longer depend on Frappe attribute access.
- Shared public-image path/File/content-validation boundary for event galleries
  and publication covers; native permissions and current File privacy remain checked.
- Pure publication rules separated from page rendering, with a common editorial
  topic vocabulary. Compatibility imports reference the same implementation.
- Playlist CSS declarations consolidated in place; obsolete external-link and
  loading-overlay selectors removed without adding a second player or stylesheet.
- One source-check runner reused by CI and the pre-migration updater. It checks
  Python, shell, all application JavaScript, player behavior and Arabic compilation.
- Explicit, pinned production-branch policy. First integration-to-production switch
  needs operator consent; unknown branches, divergent history, implicit switch and
  production-to-integration downgrade are refused by the normal deployment path.
- Application README rewritten; architecture, refactor audit and production runbook
  added; the earlier host guide preserved unchanged as historical documentation.

No runtime endpoint, existing DocType schema, publication permission, authentication
implementation, approved logo or public route was replaced. No deferred entity,
operational Project/Task integration, assignment engine or owner/assignee portal
was implemented. This is a maintainability/release pass, not a guarantee of zero bugs.

Details: [refactor audit](https://github.com/VoyaERP/erpdevelopers/blob/production-v16/docs/REFACTOR_AUDIT.md),
[architecture](https://github.com/VoyaERP/erpdevelopers/blob/production-v16/docs/ARCHITECTURE.md),
[release procedure](https://github.com/VoyaERP/erpdevelopers/blob/production-v16/docs/PRODUCTION_RELEASE.md).

## Validation evidence for the exact release commit

| Check | Result | Evidence |
| --- | --- | --- |
| Python 3.14 source/contract regressions | 199 tests passed | [Validation job](https://github.com/VoyaERP/erpdevelopers/actions/runs/43590202044/job/132433125947) |
| Playlist JavaScript behavior | 14 tests passed, zero failures | Same validation job; runs shipped script with DOM harness |
| Python/shell/all-app JavaScript syntax and Arabic gettext | Passed | Shared `scripts/check_source.sh` in the validation job |
| Existing-table schema-upgrade regression | Passed | [MariaDB job](https://github.com/VoyaERP/erpdevelopers/actions/runs/43590202044/job/132433126000) |
| Training, Events, Vision/guides, event images and Arabic login fixtures | Passed in Chromium/Firefox | [Browser job](https://github.com/VoyaERP/erpdevelopers/actions/runs/43590202044/job/132433125842) |
| Shared navigation first paint, EN/AR, refresh and mobile behavior | Passed | [Navigation run](https://github.com/VoyaERP/erpdevelopers/actions/runs/43590202150) |
| Projects/Team Advice, review filtering and minimal footer | Passed | [Publications run](https://github.com/VoyaERP/erpdevelopers/actions/runs/43590202049) |

These runs checked commit `3054ebf389179c829e827d552b727c3291b8d28e` before stable
promotion. The new branch triggers the same checks; it does not deploy the app.
Local validation also passed 199 Python and 14 Node cases; the release gate above
uses the declared Python 3.14 CI runtime rather than relying on the local 3.13 run.

Browser tests use actual app templates and styles inside isolated fixtures, with
external font/video responses stubbed where documented. They do not prove live
Frappe login, private-data access, native uploads, mail delivery or video availability.
The MariaDB fixture tests pinned Frappe schema functions and data preservation,
not a complete production `bench migrate` or restore drill.

## Last supplied operator evidence

The terminal log confirms the c8cb0de update completed backup, 166 Python and 14
Node tests, full site migration, asset build, web restart, readiness and frontend
verification. A temporary 502 immediately after restart recovered; the final
messages explicitly report public-route/asset and Arabic-login verification PASS.

That log predates source release `3cddab9`, which added Projects, Team Advice and
the three-link footer. No deployment log for that release or the current refactor
was supplied. Do not infer either from the existence of a commit or CI result.
The prior 99156e9 URL-length migration failure was corrected in the intervening
release; it is historical regression evidence, not a claim of a current outage.

## Ideas and remaining work

| Item | Status |
| --- | --- |
| Entities: `bedya`, `bdanexus`, `voyatours` and others | Deferred — record only; names/types/relationships not finalized |
| Our development initiatives as projects | Deferred — distinct from the existing public Projects stories |
| Native ERPNext Project/Task linking and assignment | Deferred — no new links or task automation |
| Portal for project owners and assignees | Deferred — no new roles, endpoints or access grants |
| Arabic logo | Name approval still pending; approved existing logo unchanged |
| Staging full migration and native publishing/upload/auth tests | Pending operator execution |
| Backup restore, monitoring, performance and release acceptance | Pending operational evidence |
| Required-review/branch-protection settings | Not configured by this change |

The next controlled step is staging and acceptance of the pinned production
baseline, not implementation of the deferred ideas. Deployment must use the
complete backup-first runner and account for the shared web-process restart.

## History and tracker discipline

The [previous complete status log](https://github.com/VoyaERP/erpdevelopers/blob/e3f66469a6cca3c0b1b82d97e8a738b68749966e/docs/STATUS.md)
retains earlier installation, branding and recovery details. It is historical,
not the current readiness snapshot. Existing issue scope and acceptance gates
remain; this documentation update does not silently close implementation or UAT
issues. Record new operator evidence and decisions when they actually occur.
