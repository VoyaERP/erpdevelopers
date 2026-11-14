# ERP Developers — Master Implementation Plan / الخطة الرئيسية

**Plan ID:** ED-MP-001 · **Baseline:** v1.1 · **Updated:** 2026-11-14
**Repository:** VoyaERP/erpdevelopers · **Status:** Current planning and release-control baseline

> الكود والاختبارات والنشر الفعلي حالات مختلفة. أفكار الكيانات والمشروعات والبوابة مسجلة فقط، ولا يُسمح بتنفيذها قبل اعتماد نطاقها لاحقاً.

This revision retains the R0-R8 roadmap and engineering/security gates while
updating the public-website baseline, production-branch policy and newly recorded
ideas. The [unchanged prior baseline](https://github.com/VoyaERP/erpdevelopers/blob/e3f66469a6cca3c0b1b82d97e8a738b68749966e/docs/MASTER_PLAN.md)
remains available for history. Current evidence belongs in [STATUS.md](STATUS.md),
not in assumptions about a branch name.

## 1. Product vision / الرؤية

ERP means **Engage. Reason. Progress.** Developers remains the secondary signature.
Retain the approved blue/teal shield/growth identity; Arabic-logo naming is still
awaiting approval. No substitute logo is authorized by this refactor.

Build a commercial, vendor-neutral ecosystem for developers, solution architects,
learners, organizations, employers and consultants across ERP and non-ERP
technologies: business applications, cloud, software, data, cybersecurity,
automation and digital transformation.

North-star outcomes remain trustworthy collaboration, reusable knowledge,
evidence-based architecture decisions, career mobility, measurable learning and
qualified commercial leads. A credible and secure product takes priority over
feature count. Planned services must never be presented as operational.

## 2. Current scope and positioning

### Existing application source

- Bilingual Home/Vision, approved branding, Tajawal Arabic, responsive shared header,
  native login presentation, and the three-link footer: Let's Talk, Team Login, Back to top.
- Public Training with an in-page playlist player; private catalog access uses
  authentication plus native permissions. YouTube privacy remains independent.
- Insights through curated resources and published native Web Pages.
- Reviewed Middle East event directory, date/time-zone handling, cover and gallery.
- Public Projects and Team Advice through one editorial Publication DocType.
  These are curated stories, not native ERPNext operational projects or user profiles.
- ERP/ERPNext development guides, technical metadata, canonical URLs and existing sitemap.
- Native ERPNext appointment booking when explicitly enabled and configured;
  legacy consultation intake remains a separate disabled-by-default capability.

See the [application README](https://github.com/VoyaERP/erpdevelopers/blob/production-v16/README.md)
for exact routes, data boundaries and operating steps. Source presence does not
prove that booking mail, uploads, private access or Google indexing passed live UAT.

### Current authorized execution batch

Refactor existing code without adding future modules; remove duplication in shared
catalog/media/rules and release checks; preserve authentication, route contracts,
DocType schemas, publication permissions, URL protections and approved assets.
Establish `production-v16`, update documentation and validate before promotion.
This batch does not deploy to a server or enable configuration flags.

### Explicit non-goals

No new entity records, operational project model, Project/Task links, assignment
engine, owner/assignee portal, member signup, LMS, job feed, AI service, paid
workflow or automated event provider is authorized in this batch. Do not replace
ERPNext, Dynamics, SAP or GitHub; do not alter existing v15 environments.

## 3. Release strategy / استراتيجية الإصدارات

| Release | Scope retained from v1.0 | Exit gate |
| --- | --- | --- |
| R0 — Environment & Architecture Baseline | Host/site isolation, compatible runtime, native framework architecture and evidence | Named environment, migration/build/smoke evidence, legacy workloads unaffected |
| R1 — Public Brand Website | Approved branding, CMS, EN/AR, responsive UX, public directories, SEO, contact controls | Owner visual acceptance, actual publishing/auth checks, accessibility/mobile UAT |
| R2 — Identity & Trust | Verified members, scoped organizations, roles, privacy and moderation foundation | Object-level API/direct-route permission matrix and cross-organization deny tests |
| R3 — Community & Developer Hub | Moderated Q&A, profiles, topic groups, knowledge, snippets and architecture patterns | Contributor/member/moderator journeys, reporting and auditable moderation |
| R4 — Academy | Reuse-versus-extension LMS decision, courses, paths, assessment, progress and certificates | Native-v16 compatibility, student/instructor UAT, privacy and grade integrity |
| R5 — Career Connections | Verified employers, reviewed jobs and permitted provider-specific feeds | Anti-fraud, source approval, expiry/deduplication, consent and application privacy |
| R6 — Governed AI | Permission-scoped retrieval, grounded recommendations and human-reviewed assistance | Evaluated quality, citations, injection resistance, budgets and authorization |
| R7 — Commercial Marketplace | Curated services/solutions, leads and later approved billing | Business/legal/payment decisions and tested workflows |
| R8 — Production Hardening & Scale | Refactoring, release discipline, monitoring, capacity, backup/restore and incident response | Staging migration, restore drill, security/operations acceptance and explicit launch approval |

The public website is not the full ecosystem. R8 source hardening can proceed
alongside R1, but a production branch does not complete R8. Release names describe
scope and dependencies, not promised dates. No invented percentage or delivery date.

## 4. Branches and workstreams

| Branch | Responsibility |
| --- | --- |
| main | Canonical plan/status/decisions; not deployable application source |
| version-16 | Active integration; independently tested changes |
| production-v16 | Reviewed and pinned source baseline for controlled promotion |
| feat/*, fix/*, refactor/* | Isolated work, reviewed and validated before integration |

No forced release-branch update, automatic deployment, default-branch change or
permission/protection change is implied. The first server transition requires
explicit operator intent; later production updates remain commit-pinned.

Existing tracking remains valid; this revision does not silently close issues:

| Epic | Focus | Tracker |
| --- | --- | --- |
| ED-00 | Environment/isolation; historical Rasheed/MacVMs track retained separately | [#1](https://github.com/VoyaERP/erpdevelopers/issues/1) |
| ED-01 | Brand, public website, CMS, localization and SEO | [#2](https://github.com/VoyaERP/erpdevelopers/issues/2) |
| ED-02 | Identity, privacy, roles and security | [#3](https://github.com/VoyaERP/erpdevelopers/issues/3) |
| ED-03 | Community and moderation | [#4](https://github.com/VoyaERP/erpdevelopers/issues/4) |
| ED-04 | Developer Hub and knowledge | [#5](https://github.com/VoyaERP/erpdevelopers/issues/5) |
| ED-05 | Secure learning / LMS | [#6](https://github.com/VoyaERP/erpdevelopers/issues/6) |
| ED-06 | Careers and authorized providers | [#7](https://github.com/VoyaERP/erpdevelopers/issues/7) |
| ED-07 | Governed AI | [#8](https://github.com/VoyaERP/erpdevelopers/issues/8) |
| ED-08 | Marketplace and monetization | [#9](https://github.com/VoyaERP/erpdevelopers/issues/9) |
| ED-09 | CI/CD, quality and production release controls | [#10](https://github.com/VoyaERP/erpdevelopers/issues/10) |
| ED-00.1 | Historical host diagnostic blocker, not a new public-site outage claim | [#11](https://github.com/VoyaERP/erpdevelopers/issues/11) |
| ED-01.1 | Existing public-site rollout and UAT evidence | [#13](https://github.com/VoyaERP/erpdevelopers/issues/13) |

## 5. Recorded ideas — Deferred / do not execute

The user explicitly said these are ideas being recorded, not work to implement.
See [DEFERRED_IDEAS.md](DEFERRED_IDEAS.md) for the exact scope and open decisions.

| ID | Idea | Status / dependency |
| --- | --- | --- |
| IDEA-001 | Entities such as `bedya`, `bdanexus`, `voyatours`, and others | Deferred; confirm names, entity meaning, ownership and relationships |
| IDEA-002 | Represent our own development work as projects | Deferred; distinguish product, delivery project and public story |
| IDEA-003 | Later connect to native ERPNext Project and use Task for assignments | Deferred; approve mappings, source of truth and permissions; avoid duplicate engines |
| IDEA-004 | Portal for project owner and assignee | Deferred; approve membership, role/action/attachment matrix and cross-project isolation |

There are no entity seeds, Project/Task links, task automation or portal endpoints
from this batch. Recording an idea is not permission to create a DocType or expose
internal delivery data. Publication remains explicit and independent.

## 6. Experience and implementation conventions

Forms use logical two-column desktop grouping where practical, dependent filters,
contextual required/read-only/visible behavior and collapsible secondary controls.
Actions must have meaningful names, valid status/role conditions and server-side
enforcement. Every controlled status needs an authorized transition path.

Dashboards require balanced horizontal indicators, useful filters and drilldowns;
no fabricated live metrics. EN/AR uses Frappe localization and full RTL; labels do
not concatenate both languages. Long prose may wrap; short controls must not clip.

Security remains least privilege, native authentication/authorization, private
storage by default, explicit public-image consent, audit and appropriate independent
review for sensitive changes. Public editorial projections are not generic Guest
DocType access. Never infer task permission from a visible UI control.

Prefer existing framework components and shared code. Do not duplicate native
Project, Task, File, appointment, calendar or login engines. Keep pure rules separate
from database queries, bound pagination, preserve stable paths and add regressions
for failure cases. Avoid unnecessary schedulers and batches. No repository secrets.

## 7. Quality / Definition of Done

Work is Done only when applicable requirements, ownership, code and evidence exist:

1. Recorded scope and acceptance criteria, with explicit treatment of deferred items.
2. Reviewed commit/PR, migration notes and no duplicated business/framework function.
3. Unit, schema, integration, permission and workflow checks for the target version.
4. EN/AR, RTL, mobile, accessibility and relevant browser behavior checks.
5. Security review of data, endpoints, uploads, secrets, integrations and logs.
6. Named-site UAT at an exact commit, operator results and owner acceptance.
7. Backup/recovery, rollout and rollback plan, documentation and status updated.

Static tests, browser fixtures, focused MariaDB regression, live HTTP checks and
interactive acceptance are different evidence layers. Target Python is 3.14+ on
Frappe/ERPNext16. Do not infer full Bench compatibility from standalone CI.

Retain the original proposed quality targets, not claimed measurements: WCAG 2.2 AA
design intent; LCP <=2.5s, CLS <=0.1, INP <=200ms at p75; no known critical/high
security findings; documented restore drill before operational approval.

## 8. Open decisions and gates

- The observed public target is `erp-developers.com` on `erptest-lightnode`;
  the separate MacVMs/v15 investigation is historical and must not be altered.
- Production branch protection/review settings, staging, restore, monitoring,
  performance and business acceptance still need explicit operational evidence.
- Final legal entities, jurisdictions, budgets, staffing, timelines and monetization
  are not established by listing entity names or creating a production branch.
- Arabic logo naming remains pending. Approved English PNG stays unchanged.
- Provider event feeds, careers APIs, AI providers and LMS reuse each require current
  feasibility, permission/licensing, data-handling and cost decisions before build.
- Search Console ownership and indexing remain owner-operated; rankings are not promised.
- The historical GitHub App source-authentication preference remains documented in
  the prior plan; repository/credential state must be checked before any auth change.
  No registration, PEM handling or credential mutation occurs in this refactor.

## 9. Next controlled steps

Finish source review/CI and record the exact stable baseline; stage that release
on an approved clone; run actual editorial/private/auth and migration tests; confirm
backup recovery and shared-web restart impact; then obtain owner/operator approval
for deployment. Do not start IDEA-001..004 or later ecosystem modules without a
new implementation instruction and approved access model.

Status vocabulary remains Planned -> Ready -> In progress -> In review -> UAT ->
Done, with Blocked / Deferred / Cancelled reasons. GitHub issue closure is not
operational acceptance. Update [STATUS.md](STATUS.md), the relevant issue and
[DECISIONS.md](DECISIONS.md) when evidence or scope changes. No autonomous future
monitoring or updates are assumed.
