# ERP Developers — Reference Architecture & Security Baseline

**Status:** Proposed architecture, to validate with ED-00 and ED-02. No statement in this document establishes that a module is already installed.

## 1. Architecture

**Framework:** Frappe v16 for the active application; Python 3.14, Node 24, MariaDB 11.8 and Redis/Valkey per the current Frappe installation documentation. Verify host-specific support. No mandatory ERPNext dependency for the public site.

**Phase 1 deployment:** separate v16 Bench and dedicated test site/database, service ports, logs, process boundary and backup policy. Other existing Frappe v15/production benches are never upgraded in place. Mac connects via loopback SSH tunnel to development services, not an exposed public port.

**App design:** keep a thin single Frappe app initially; organize code into clear bounded submodules when required. Prefer Frappe Website/Portal, User/Role, translations, permissions, standard notifications and audit capabilities over parallel duplicate implementations. Split into separate installed apps only when there is a defensible versioning, licensing or deployment boundary.

**Logical layers:** Website/CMS → Authenticated portal → Domain services (members/community/resources/courses/careers/AI/marketplace) → Permission-checked Frappe ORM/API → MariaDB + private file storage; with limited third-party adapters and audit/observability.

**Interfaces:** page templates and server-rendered routes for public pages; authenticated API endpoints only with explicit method permission checks, CSRF protections applicable to method, rate limits, schema validation, object-level authorization and audit. “Hidden” UI is not authorization.

## 2. Proposed domain model — NOT IMPLEMENTED

| Domain | Candidate entities / reuse question |
| --- | --- |
| Identity | Frappe User/Role/Profile, Member Profile, Organization, Membership (if needed) |
| Content | Frappe Website/CMS/Blog/Portal + scoped editorial approval fields |
| Community | Space, Topic, Post, Post Report, Moderation Decision |
| Developer Hub | Resource, Topic Taxonomy, Content Revision/Review, Code Repository Link |
| Academy | **First evaluate maintained Frappe LMS**; only build missing course/lesson/enrollment/assessment/certificate models as justified |
| Careers | Employer/Verification, Job Listing, External Source Registration, Candidate Consent, Application (optional) |
| AI | Knowledge Source, Security Scope, Retrieval Policy, Evaluation Set, Usage/Quota (sensitive conversation storage opt-in) |
| Commercial | Solution/Service Listing, Request/Lead, Approval, Transaction only after business/legal gate |

No new DocType should be created without confirming its ownership, state transitions, retention policy, indexing/performance and why an existing Frappe/maintained app entity cannot be reused.

## 3. Role / access matrix (proposal; requires owner sign-off)

| Persona | Public pages | Own profile/posts | Moderate content | Publish courses | Verify employer/jobs | Admin config |
| --- | --- | --- | --- | --- | --- | --- |
| Guest | Read | No | No | No | No | No |
| Member / Developer | Read | Own, subject to review | No | No | No | No |
| Mentor | Read | Own, relevant resources | No by default | No by default | No | No |
| Instructor | Read | Own | No by default | Assigned courses only | No | No |
| Employer | Read | Own organization | No | No | Request review | No |
| Moderator | Read | Scope assigned | Assigned queue with audit | No by default | Assigned queue if approved | No |
| Site Administrator | Read | Administrative scoped action | Administrative with audit | Administrative | Administrative | Configuration |

**Mandatory**: app-level and server-side permission checks, record ownership validation, organization boundary where applicable, protection from IDOR/direct file links, safe elevated actions and maker/approver separation when relevant. No default cross-organization visibility. Child table links and data exports inherit authorization.

## 4. Trust and data security

1. **Identity:** verified signup, phishing-resistant MFA policy for privileged users where supported, session hardening, safe password reset, deny default, optional SSO only after scoping and provider consent.
2. **Data classification:** Public, Internal, Private (CV/learning/communications), Restricted (credentials and administrative security data).
3. **Files:** private attachment storage, extension/content checks, malware scanning feasibility, signed access for protected media, no public backup or private-file links.
4. **Privacy:** collect minimum information, explain purposes, opt-in for communications/AI, define retention/export/delete before enabling applications or payments. Confirm applicable legal jurisdictions.
5. **Application:** input validation, SQL injection/XSS/CSRF defenses via maintained Frappe patterns, object-level permission tests, rate limits, spam/reporting, safe redirect policies.
6. **Dependencies:** pin version ranges, scan secrets and vulnerabilities, review license and supply-chain provenance, no unapproved external scripts.
7. **Operations:** TLS in production, reverse proxy/security headers tested with Frappe, backups including private files and restore drill, rotation and least-privilege service accounts, monitoring/incident runbooks.
8. **Workflow governance:** sensitive moderation, course approval, employer verification and AI external actions require auditable states and human review; context-dependent actions only.
9. **Performance:** paginate, index common filters and profile queries; safe caching boundaries; no large synchronous request blocks or unnecessary background batches.

## 5. External integration boundaries

Each adapter has a source/terms review, user/company consent, approved scopes, token vault, rate limits, expiry/revocation, failure policy, provenance and dedupe strategy. Prioritize authorized APIs/RSS/partner feeds. LinkedIn's restricted posting integration is **not** blanket permission to read/scrape jobs. No scraping or unofficial endpoints.

## 6. AI design gates

AI models may see only data retrieved **after permission filtering** for the requesting user and organization. Prompt content from users/documents is untrusted. Require citation/source metadata, evaluation of accuracy and policy, explicit tool permission checks, human confirmation before side effects, tenant-safe cache keys, logging without sensitive payloads and configurable cost/retention limits. Security testing must include prompt-injection and exfiltration attempts.

## 7. Build-vs-reuse decisions

- Standard Frappe CMS/Website and User/Role **first**.
- Evaluate Frappe LMS for v16 (features, maintainability, license, extensibility, tests) before custom LMS.
- Link GitHub repositories instead of duplicating code hosting.
- Reuse a vetted search/indexing abstraction; AI cannot bypass permission scopes.
- Prefer independently deployable integrations only after business validation.

## 8. Architectural acceptance

ADR covering sites/versions, domain boundaries, threat model, data/privacy classification, role matrix and third-party approvals must be signed off before ED-02+ and production commitments. This file is a proposal until that review.
