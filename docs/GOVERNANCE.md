# ERP Developers — Delivery Governance / قواعد التنفيذ

## Source of truth

- **docs/MASTER_PLAN.md on main:** roadmap, release scope, approved constraints and gates.
- **GitHub Issues:** the authoritative work backlog. One issue/epic has requirements, owner, priority, dependencies, acceptance criteria, commit/PR links and evidence.
- **docs/STATUS.md on main:** dated summary of reality, blockers and observed UAT (must not replace issues).
- **docs/DECISIONS.md:** architecture/product decisions, options, approvals and impacts.
- **version-16:** code; do not represent code commit as successful installation.

No duplicate plan copies across branches or detached spreadsheets. Versioned Markdown and Issues are durable; links in other branches point to these main documents.

## Release & Git flow

1. Open or select GitHub Issue and document acceptance criteria.
2. Create branch **feat/ED-XX-short-name** or **fix/ED-XX-short-name** from active implementation base (version-16).
3. Make a scoped change; avoid duplication of standard Frappe functionality or existing project code.
4. Add migration, permission, regression and bilingual/RTL checks as needed.
5. PR into **version-16** for review. Avoid unreviewed force push. Reserve main for governance until release policy changes are explicitly agreed.
6. Verify automated tests and actual test-site UAT, attach evidence and rollback.
7. Update Issue state and docs/STATUS.md. Record changes to architecture/scope in docs/DECISIONS.md.
8. Promote only after release acceptance; maintain a verified commit/tag and rollback plan.

**Branch governance:** main and version-16 are not yet protected. Enable branch protection, required checks and review rules in GitHub settings when CI and team permissions are ready; do not claim enabled now. version-15 is not currently present; creating a branch must follow a compatibility decision, not copy untested v16 code.

## Status vocabulary and evidence

| State | Meaning |
| --- | --- |
| Planned | Idea defined but no approved build commitment |
| Ready | Requirements, dependencies, owner and acceptance criteria agreed |
| In progress | Engineering/authoring active; may not be deployable |
| In review | PR/design review, comments unresolved or acceptance pending |
| UAT | Deployed to named test site, active verification ongoing |
| Done | Tests and security relevant to scope passed, UAT accepted, documentation and rollback reviewed |
| Blocked | Explicit missing prerequisite; document owner and unblock step |
| Deferred | Deliberately postponed and reason recorded |

For every status transition to Done record: **date; Issue; branch/commit; site; tests and results; browser/manual evidence if UI; reviewer; outstanding risks; rollback**.

## Non-negotiable engineering controls

- Least privilege; server-side role and record authorization for every protected action; status-based action feasibility.
- For form-heavy modules: 2-column desktop layout, meaningful sections, dependent filters, conditional required/read-only fields, minimized clutter and logical workflow groups.
- UI language handled via translations (English and Arabic as separate locales), not concatenated labels.
- Business evidence and approvals separate maker/reviewer for sensitive trust actions.
- Code review for no duplicated components, duplicate business rules or custom substitutes for framework-standard features.
- Performance budgets, pagination and indexes; no uncontrolled jobs or background batches.
- No hardcoded credentials, tokens, production data or personally identifiable records in Git.
- No LinkedIn scraping, unapproved job feeds, unreviewed AI external actions or paid functionality without explicit policy gate.

## PR and UAT checklist

- [ ] Linked Issue / accepted scope.
- [ ] Architecture impact evaluated; ADR when significant.
- [ ] Unit/integration/regression tests pass on the actual target Frappe version.
- [ ] All relevant roles/actions/status transitions tested; direct API authorization checked.
- [ ] UI responsive, accessible, EN/AR and RTL validation where relevant.
- [ ] Security/privacy/third-party terms reviewed.
- [ ] Migrations and deployment/rollback documented.
- [ ] Manual UAT with site and exact commit recorded.
- [ ] STATUS.md and Issue updated together.

## Review cadence

During active work, review open P0/blocked items and new PRs regularly; at each accepted work increment commit status/evidence updates. A periodic weekly review is recommended, but **not automatically scheduled**. To make a future update, inspect GitHub state first, then amend Issues and the single STATUS snapshot. Never infer completion from unchecked boxes alone.
