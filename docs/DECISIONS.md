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
| ADR-012 | 2026-11-13 | **Open — capacity decision** | Choose separate supported ARM64 VM or expand MacVMs 30GB virtual disk (proposed 80GB) and RAM (proposed 8GiB) | Root only 3.6GB free (88% full); do not install/cleanup until approved and externally backed up |

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
