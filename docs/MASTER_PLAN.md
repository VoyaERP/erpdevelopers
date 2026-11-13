# ERP Developers — Master Implementation Plan / الخطة الرئيسية

**Plan ID:** ED-MP-001 · **Baseline:** v1.0 · **Updated:** 2026-11-13 · **Status:** Active planning baseline · **Repository:** VoyaERP/erpdevelopers

> المرجع الرئيسي لتنفيذ منصة ERP Developers. كل مرحلة لها نطاق ومعايير قبول واختبارات وأدلة على التنفيذ. الكود المرفوع ليس دليلًا على اكتمال الميزة بدون اختبار فعلي. سيتم تحديث هذه الخطة عند اعتماد قرارات جديدة، مع تحديث GitHub Issues و STATUS.md في نفس دورة المراجعة.

## 1. Product vision / الرؤية

**Brand:** ERP = **Engage. Reason. Progress.**; **Developers** is the secondary brand signature. The preferred visual direction is the approved blue-to-teal rounded shield with rising analytics bars and an upward growth arrow.

Build a **commercial, vendor-neutral technology ecosystem** for developers, solution architects, learners, organizations, employers and consultants. The platform should connect people, knowledge and useful AI across ERP and non-ERP technologies: business applications, cloud, software, data, cybersecurity, automation and digital transformation.

**North-star outcomes:** trustworthy collaboration; reusable knowledge; evidence-based architecture decisions; career mobility; measurable learning; qualified commercial leads. A credible, secure platform is more important than the fastest feature count.

**Important distinctions:**
- Planned features are **not** currently available to users.
- “AI capabilities” means opt-in, governed features backed by actual models, evaluated retrieval and authorized data access; an AI-looking icon alone is not an AI system.
- Integration with **all job sites** is not technically or contractually assured. Each source must pass an integration feasibility/approval gate.
- No assumptions about the final public domain, payment jurisdiction, legal entity, team size, budgets or production environment.

## 2. Scope and positioning

### In scope
1. Official company website: services, solutions, thought leadership, portfolio, contact, SEO, bilingual English/Arabic.
2. Developer Hub: moderated reusable knowledge, documentation, snippets, architecture patterns and links to source repositories.
3. Community: Q&A, topic groups, member profiles, expert discovery, reporting and moderation.
4. Learning Academy: courses, learning paths, assessments, progress, certificates, instructor controls; evaluate reuse of existing LMS technology first.
5. Careers: verified jobs/employers, search and applications; third-party feeds only where authorized.
6. Intelligent services: user-permitted knowledge search, guided recommendations, learning assistance and human-reviewed advisory.
7. Commercial marketplace: services/solutions directory, lead workflow and potential paid offerings after legal feasibility.
8. Administration and analytics: content approvals, roles, audit, exception handling, safe reports and privacy-aware metrics.

### Explicit non-goals for initial release
- Replacing ERPNext, Dynamics, SAP or GitHub as full products.
- Creating a new LMS engine if a compatible maintained solution already meets requirements.
- Scraping LinkedIn or other sites, bypassing API restrictions, promising a universal live job feed.
- Unreviewed AI executing privileged changes, sharing another member's data or training on user data by default.
- Enabling public registration, payment processing or private file uploads without security and legal gates.
- Migrating/upgrading any existing v15 bench in place.

## 3. Release strategy / استراتيجية الإصدارات

| Target | Scope | Exit gate |
| --- | --- | --- |
| **R0 – Environment & Architecture Baseline** | Host inspection, v16 isolation, validated bench/site, local Mac UAT, threat model, CI baseline | Host and site audit with documented successful smoke tests |
| **R1 – Public Brand Website (MVP)** | Approved logo, pages/CMS, EN/AR, SEO, accessibility, contact control and analytics consent | Product owner visual sign-off, no critical accessibility/security issue, mobile UAT |
| **R2 – Identity & Trust** | Verified members, role/organization rules, privacy, moderation foundation | Permission/security regression incl. direct API access and cross-organization isolation |
| **R3 – Community & Developer Hub** | Moderated Q&A, expertise/resources and publishing workflows | End-to-end member/moderator/contributor UAT |
| **R4 – Academy** | LMS choice, course paths, enrollments, assessment and certificate workflow | Learning data privacy and grade/integrity tests |
| **R5 – Career Connections** | Verified employers, approved job listings and provider integrations if allowed | Anti-fraud, retention and integration authorization tests |
| **R6 – Governed AI Services** | Source-grounded, permission-scoped assistants and measurable evaluation | Authorization, hallucination, prompt-injection and cost-control gates |
| **R7 – Commercial Marketplace** | Service listings, leads, optional billing/payments after review | Legal, security, support/operations and business model approval |
| **R8 – Production Hardening & Scale** | DR, observability, performance, release operations and scalability | Restore drill, rollback, operational acceptance and launch approval |

The **R0/R1 MVP is a fully functional public website**, not a full LMS/community/jobs/AI platform. All later modules depend on security and moderation foundation. Release names express **sequence, not delivery dates**; capacity and estimates will be assigned after environment and scope discovery.

## 4. Workstreams and live GitHub tracking

**GitHub Issues carry item-level statuses, ownership, acceptance criteria and evidence.** This table remains the stable roadmap; [STATUS.md](STATUS.md) tracks the most recent observed state.

| Epic | Focus | Priority | Dependencies | Tracker |
| --- | --- | --- | --- | --- |
| ED-00 | Rasheed/MacVMs v16 environment and Mac test | P0 | host inventory | [#1](https://github.com/VoyaERP/erpdevelopers/issues/1) |
| ED-01 | Brand, website, CMS, localization, SEO | P0 | ED-00 for runtime | [#2](https://github.com/VoyaERP/erpdevelopers/issues/2) |
| ED-02 | Identity, privacy, roles, security | P0 | ED-00 | [#3](https://github.com/VoyaERP/erpdevelopers/issues/3) |
| ED-03 | Community and moderation | P1 | ED-02 | [#4](https://github.com/VoyaERP/erpdevelopers/issues/4) |
| ED-04 | Developer Hub and knowledge | P1 | ED-02 | [#5](https://github.com/VoyaERP/erpdevelopers/issues/5) |
| ED-05 | Secure learning / LMS | P2 | ED-02, LMS feasibility | [#6](https://github.com/VoyaERP/erpdevelopers/issues/6) |
| ED-06 | Jobs and authorized job-provider integrations | P2 | ED-02, partner access | [#7](https://github.com/VoyaERP/erpdevelopers/issues/7) |
| ED-07 | Permission-scoped AI and knowledge | P2 | ED-02, ED-04, evaluation | [#8](https://github.com/VoyaERP/erpdevelopers/issues/8) |
| ED-08 | Marketplace and monetization | P3 | ED-02 and legal/business decisions | [#9](https://github.com/VoyaERP/erpdevelopers/issues/9) |
| ED-09 | CI/CD, quality, release operations | P0 ongoing | every epic | [#10](https://github.com/VoyaERP/erpdevelopers/issues/10) |
| ED-00.1 | Failed host diagnostic shell | P0 blocker | ED-00 | [#11](https://github.com/VoyaERP/erpdevelopers/issues/11) |

### R0 – Discovery and environment readiness: first

Deliverables:
- Inventory target host identity, OS, toolchain and installed Frappe sites/branches, without exposing credentials.
- Resolve the missing hostname command/SSH exit and confirm whether MacVMs is actually the Rasheed target.
- Validate Frappe 16 prerequisites against official docs: Python 3.14, Node 24, MariaDB 11.8, Redis/Valkey 6+, package tooling and available resources.
- Create a **separate** v16 Bench and test database/site; reserve independent ports/services; keep any v15/production workloads untouched.
- Clone the existing **version-16** code; install on test site; record exact commit, migration/build/test evidence.
- SSH tunnel to Mac for visual/browser smoke tests, CSS asset checks, logs and accessibility checks.
- Produce architecture ADRs, role matrix and a release gate before accepting implementation.

**R0 acceptance:** Verified runtime logs and a working site, plus evidence that legacy sites were unchanged. The deployed app must be verified, not inferred from a GitHub commit.

### R1 – Brand & public website (initial go-live)

User journeys: visitor understands the company offering, navigates services, can explore planned ecosystem offerings accurately, can submit a secure contact request if enabled, and can switch between English and Arabic without mixed-language labels.

Key requirements:
- Approved real brand assets: full/compact/icon-only, light/dark and favicons, with correct proportions and text; **no visual replacement without approval**.
- Full responsive layout and accessible design system; balanced cards and typography; subtle animation with reduced-motion support.
- Standard Frappe CMS/website capabilities preferred before custom DocTypes, reusable components and configurable content.
- Pages: Home, About/Vision, Services & Solutions, Use Cases, Developer Hub teaser, Community teaser, Academy teaser, Careers teaser, Contact, Privacy and Terms.
- Arabic/English translations via localization, with RTL layout; content may have per-language versions; do not concatenate bilingual labels.
- Technical SEO: sitemap, canonical URLs, alt text, metadata, social previews and structured data where supported; analytics only after consent review.
- Contact pipeline with anti-spam, least-privilege handling and retention policy.

**R1 acceptance:** Product owner signs off branding/UI; all routes, language/RTL, mobile, contact flow (if enabled), SEO and accessibility checks pass.

### R2 – Membership, trust & access model

User roles: **Guest, Member, Developer, Mentor, Instructor, Employer, Moderator, Site Administrator**. Privileged functions have explicit role scopes and statuses, not merely hidden buttons. Use Frappe permissions and server-side checks; no role is trusted because of client-supplied fields. Add organization associations only where justified and define isolation rules.

Capabilities: controlled signup, email verification, privileged MFA policy, session safeguards, private files, consent, reporting, audit events, data export/retention/deletion and abuse prevention. Two-person review where sensitive approvals require separation.

**R2 acceptance:** An access matrix and automated deny/allow tests for API, direct document URL, roles, organizations and state transitions; zero known critical/high authorization defects.

### R3 – Community & Developer Hub

Community: categories, discussion threads, Q&A, contribution profiles, topic following, moderation queue, report/appeal, spam control and privacy settings. Developer Hub: guides, examples, code links, reusable patterns, technology tags, revision workflow, contributor recognition and versioned resources.

**R3 acceptance:** Users can submit, review, publish, search and report content with auditable moderation and no cross-member private-data exposure.

### R4 – Learning Academy / LMS

Before coding, record an explicit **reuse vs extension vs custom** decision for a maintained Frappe-compatible LMS (including the current v16 support position). Scope includes learning paths, lessons, instructor course review, enrollments, progress, assessments, retakes, certificate verification and mobile learning.

Security: no public CV/grade access, private content access/stream controls, attempt integrity, input sanitization and audit. Paid courses require an independent payment/legal decision.

**R4 acceptance:** Student/instructor/admin end-to-end UAT and privacy/integrity tests on actual v16 site.

### R5 – Careers & external jobs

Launch with **verified organizations and manually reviewed job posts**. Employer approval, expiry, deduplication, category/location/remote filters, user consent and moderation are baseline. Applications may start via explicit external apply links; storing CVs requires a separate privacy design.

Every provider is evaluated independently (partner agreement, API scopes, usage terms, refresh/attribution, pagination, errors, rate limits). **LinkedIn Job Posting API access is restricted** and cannot be assumed, and it is not a universal jobs-read API.

**R5 acceptance:** Verified employer publication and candidate workflow pass; each enabled connector has written approval and test evidence.

### R6 – AI-enabled knowledge and intelligent assistance

Potential use cases (subject to assessment): architecture discovery, developer knowledge Q&A, learning recommendations, semantic search, job-skills matching and commercial inquiry triage.

Required controls: authorization-scoped retrieval before model use, citations, source freshness, consent, data minimization, model/provider abstraction, explicit review before privileged actions, prompt-injection defenses, cost/rate budgets, evaluation dataset and fallback to human review.

**R6 acceptance:** No private-context retrieval for unauthorized users; measurable answer quality; fail-safe tool authorization; observability and spend limits.

### R7/R8 – Commercial model and operations

Marketplace: curated solutions, verified providers, leads and possibly subscriptions/payment later. Final commercial model, payment gateway, invoicing/tax requirements and target jurisdictions **must be approved** before build.

Operations: production architecture, backups and restore drills, TLS, CI/CD, threat tests, observability, capacity/performance, incident response, data-retention policy and rollback. Do not make a public release by merging source code alone.

## 5. Experience & implementation conventions (binding engineering rules)

- **Forms:** minimum two-column desktop layout where practical; fields grouped logically; dependent filters; context-based readonly/required/visible logic; collapse secondary controls rather than long descriptions.
- **Actions:** meaningful verb labels; only actions valid for current status and role are displayed; every status-controlled DocType needs an authorized transition path; server-side enforcement is mandatory.
- **Dashboards:** readable, balanced horizontal KPI cards where space permits, clear filters and meaningful drilldowns; do not claim live metrics without source.
- **Languages:** EN/AR user interface via Frappe i18n, full RTL and translated content. Avoid mixing English | Arabic inside a single field label.
- **Security:** least privilege, verified documents/attachments as necessary, maker/reviewer separation for sensitive operations, private storage by default, organization-scoped records where applicable.
- **Engineering:** prefer Frappe standard primitives and reusable components; do not duplicate standard framework code or business logic; small testable modules; indexes/pagination and performance budgets; avoid unneeded background batches.
- **AI/Integrations:** explicit approval, scoped tokens, terms compliance, bounded retries and audit. No secrets in repository.

## 6. Quality / Definition of Done

A GitHub issue can be marked **Done only when all applicable evidence exists**:
1. Requirement/acceptance criteria and owner are recorded.
2. Change linked to a PR/commit, with migration notes and **no duplicate existing functionality**.
3. Unit + integration + permission + role/workflow tests pass in the target version.
4. UX, mobile, accessibility and relevant English/Arabic/RTL checks pass.
5. Security review covers data exposure, API/endpoint authorization, uploads, secrets, logs and external integrations.
6. UAT runs on a named site and commit; operator records passed/failed cases and signs off.
7. Backward compatibility, rollback and docs/status updated together.

Use proposed quality targets when applicable, not fabricated current results: WCAG 2.2 AA design intent; Core Web Vitals LCP ≤2.5s, CLS ≤0.1, INP ≤200ms at p75 for public pages; zero known critical/high security findings; documented restore test before production. Verify actual metrics in UAT.

## 7. Ownership, cadence and status vocabulary

**Issue state:** Planned → Ready → In progress → In review → UAT → Done; alternate Blocked / Deferred / Cancelled with reason. GitHub open/closed state is not the same as product readiness.

**Roles (people to assign):** Product Owner, Solution Architect, Frappe Lead, UI/UX & Content, Security Reviewer, QA/UAT Owner, Operations Owner. One person may cover several roles in a small team, but security-critical approvals should remain independent.

**Update ritual:** when work changes, update **the Issue** (source for tasks), attach tests/commit/evidence, then update **STATUS.md** (source for current overall picture). Review open issues regularly while active; mark dates and evidence. Changes to priorities/architecture are logged in **DECISIONS.md**. We do not claim autonomous future updates: changes occur as people/agents perform and verify them.

## 8. Constraints, assumptions to verify, and decision gates

1. **Rasheed vs MacVMs:** output identifies an SSH host named MacVMs and address 192.168.64.15; verify whether it is the intended Rasheed test host.
2. **v15:** no version-15 branch found in THIS repo; do not create an untested v15 copy or alter another project.
3. **Licensing:** asset rights, code/open-source license and third-party terms must be established. App metadata alone is not license review.
4. **Platform users/legal markets:** geography, personal-data rules, employment/job regulations, consent and commercial terms need owner/legal decisions.
5. **LMS:** Frappe LMS v16 compatibility requires evaluation before commit to a build approach.
6. **Job providers:** LinkedIn and other sites are connector-by-connector, with approvals and provider-specific terms.
7. **AI:** provider, storage/retention, model policy, cost and opt-in are decisions, not implicit requirements.
8. **Scale/timeline:** estimate after R0 and MVP requirements are validated. No invented deadlines or progress percentages.

## 9. First execution batch (next five controlled actions)

1. Resolve [ED-00.1](https://github.com/VoyaERP/erpdevelopers/issues/11) using [safe host audit](LOCAL_RASHEED.md).
2. Record v16 compatibility and write environment/site isolation plan in [ED-00](https://github.com/VoyaERP/erpdevelopers/issues/1).
3. Enable foundational CI/test evidence and PR quality gate in [ED-09](https://github.com/VoyaERP/erpdevelopers/issues/10).
4. Replace temporary visual brand with approved real assets; run R1 responsive and bilingual UI audit in [ED-01](https://github.com/VoyaERP/erpdevelopers/issues/2).
5. Draft and approve the identity/roles/organization-scoping matrix in [ED-02](https://github.com/VoyaERP/erpdevelopers/issues/3).

**Do not jump to Community, LMS, Jobs, AI or paid workflows before foundational access and deployment gates.**

## Official technical references

- [Frappe Installation prerequisites](https://docs.frappe.io/framework/user/en/installation)
- [Frappe Portal Pages](https://docs.frappe.io/framework/user/en/portal-pages)
- [Frappe architecture](https://docs.frappe.io/framework/user/en/basics/architecture)
- [LinkedIn Job Posting API authorization](https://learn.microsoft.com/en-us/linkedin/talent/job-postings/api/overview?view=li-lts-2026-03)

This plan is version-controlled. For changed scope, add a decision, amend the affected epic acceptance criteria, and update the status snapshot.
