# ERP Developers — Decision Register

**Scope:** Product and architecture decisions. Status **Accepted** means established by user preference or repo reality; **Proposed** means pending approval. When changing a decision, append a dated replacement entry rather than silently rewriting history.

| ID | Date | Status | Decision | Rationale / consequences |
| --- | --- | --- | --- | --- |
| ADR-001 | 2026-11-13 | **Accepted** | ERP = Engage. Reason. Progress.; Developers = secondary brand signature | Maintain hierarchy in website/app branding |
| ADR-002 | 2026-11-13 | **Accepted design direction** | Use blue/teal rounded shield/growth arrow logo selected in conversation | Original approved asset must be added and QA-checked; do not claim CSS temporary mark is final |
| ADR-003 | 2026-11-13 | **Operational baseline** | main = durable plan/governance, version-16 = active Frappe app | Avoid mixing untested app code with stable plan; update docs on main |
| ADR-004 | 2026-11-13 | **Proposed** | Keep existing v15 environments untouched; v15 compatibility requires separate assessment | Current repository does NOT contain a version-15 branch |
| ADR-005 | 2026-11-13 | **Proposed** | One thin Frappe app first, standard components before custom modules | Reduce duplication and maintenance risk |
| ADR-006 | 2026-11-13 | **Proposed security gate** | Deny-by-default, server-side object permissions and explicit human review for trust-sensitive workflow | Applies to Community, Academy, Careers and AI |
| ADR-007 | 2026-11-13 | **Proposed feasibility gate** | Evaluate a maintained v16-compatible Frappe LMS before writing custom LMS | Minimize duplicated code and unsupported upgrades |
| ADR-008 | 2026-11-13 | **Mandatory provider gate** | No job scraping; use only permitted third-party APIs/feeds with consent and contracts | LinkedIn Job Posting API requires provider approval; not all jobs integrations are possible |
| ADR-009 | 2026-11-13 | **Proposed AI gate** | Human-approved, permission-scoped retrieval; no model access to unauthorized documents or automatic privileged side effects | Evaluation, prompt-injection tests, quotas and provenance required |
| ADR-010 | 2026-11-13 | **Open** | Final public domain, hosting/proxy, business model, markets, payments, user acquisition and AI provider | No guesses, resolve before relevant production phase |
| ADR-011 | 2026-11-13 | **Observed, scope still to confirm** | MacVMs hosts existing Frappe 15 and `rasheed` app; is this the intended v16 target? | Existing four sites must be preserved; version-16 Bench not installed |
| ADR-012 | 2026-11-13 | **User direction accepted; prerequisites blocked** | Continue developing/testing Frappe v16 on existing MacVMs in **new isolated Bench**, not a new VM for now | Guarded installer requires >=8 GiB free storage; current disk only 3.6GB free. Back up before expansion, do not modify shared v15 Bench/DB, isolate Node24/ports. MariaDB 12.3 compatibility remains unverified. |

## Decision update format

### ADR-XXX — Short title (YYYY-MM-DD)
- **Status:** Proposed / Accepted / Superseded
- **Context:** What problem or requirement?
- **Options considered:** Include reuse/standard behavior.
- **Decision and rationale:** Who accepted, and why?
- **Security/operations effects:** Permissions, integrations, rollback.
- **Affected issues/PRs:** links.
- **Next validation:** evidence needed.

No timeline, compliance claim or licensing assumption becomes an accepted decision simply because a draft mentions it.

## Dated additions — 2026-11-14

### ADR-013 — Refactor existing application and separate production source

**Status:** Accepted implementation scope; operator deployment and operational approval pending.

The user requested a refactor of the existing app, a production branch, and updated
GitHub plan/README. `main` continues to hold canonical governance; `version-16`
continues as the integration branch. `production-v16` is the stable source branch,
created at tested commit `3054ebf389179c829e827d552b727c3291b8d28e`. This extends
ADR-003 without replacing its separation of application and planning history.

Reuse shared native/public catalog and image checks rather than duplicate them.
Preserve native Frappe authentication, existing DocTypes/endpoints, publication
filters, previous schema correction, the three-link footer and approved branding.
Keep one source-check runner for CI and pre-migration validation. Existing import
paths remain compatibility aliases, not parallel implementations.

The normal release path permits only pinned, clean, fast-forward updates. The
first `version-16` to `production-v16` server switch requires explicit operator
approval. Source promotion does not deploy, change repository protections, alter
credentials, recreate a site or approve launch. No forced history update was used.

**Next validation:** staging full migration, actual editorial/private/auth flows,
backup restore and shared-process restart acceptance. Evidence and CI links are
in [STATUS.md](STATUS.md). Existing release workstream: issue #10.

### ADR-014 — New entities and operational project portal remain deferred

**Status:** Recorded user ideas — Deferred / do not execute.

The user explicitly supplied `bedya`, `bdanexus`, `voyatours` and others as future
entities, requested recording our own development work as projects, and described
later ERPNext Project/Task linking, task assignment and an owner/assignee portal.
The instruction "dont execute" / "انا بسجل افكار" is the execution boundary.

Document these as IDEA-001..004 in [DEFERRED_IDEAS.md](DEFERRED_IDEAS.md). Do not
create entity records/DocTypes, operational project links, task automation, portal
roles/endpoints or public statements of ownership. Exact names, entity semantics,
mappings and permissions remain open. Prefer native Project/Task reuse later.

The existing public Projects page remains an explicitly reviewed publication
catalog, not an operational delivery portal. A future business project owner must
not be inferred from Frappe's creator field; assignment of one task must not grant
all-project visibility. These are design constraints to approve and test later,
not implemented authorization behavior.

**Resume gate:** explicit new implementation instruction, approved scope and
object-level access matrix, including cross-project/entity denial and revocation.

### ADR-015 — Observed deployment and branding evidence supersede stale assumptions

**Status:** Observed, limited to supplied evidence.

The successful operator log identifies `erp-developers.com` on `erptest-lightnode`
at `/data/frappe/frappe-bench`, with c8cb0de migration/build/readiness/frontend and
Arabic-login HTML checks complete. This resolves the observed public domain/host
portion of ADR-010 for this deployment only; business model, legal ownership,
markets, payments and providers remain undecided. ADR-011/012 are historical
separate-environment notes and do not authorize changing MacVMs/v15 workloads.

The exact approved PNG is already in application source, with SHA-256
`250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d`.
Its bytes and hierarchy remain unchanged, updating the source-asset state described
in ADR-002. An Arabic logo name has not been approved and no substitute is generated.

The latest supplied live evidence is c8cb0de, not the later Projects/Advice source
or the new refactor. Source CI and production branch creation are recorded
separately from deployment, interactive UAT and operational acceptance.
