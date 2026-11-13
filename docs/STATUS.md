# ERP Developers — Execution Status / متابعة التنفيذ

**Snapshot date:** 2026-11-13 · **Scope:** VoyaERP/erpdevelopers · **Source of task detail:** [GitHub Issues](https://github.com/VoyaERP/erpdevelopers/issues) · **Master plan:** [MASTER_PLAN.md](MASTER_PLAN.md)

> حالة التنفيذ مبنية على أدلة من GitHub ومن مخرجات المستخدم فقط. لا يتم اعتبار الكود مختبرًا لمجرد رفعه.

## Observed baseline

- **main:** repository entry/documentation branch; not a deployed release.
- **version-16:** application scaffold pushed; last *observed code* commit before plan: **344c771a6df6c9ea617095104fc0a01ad798b17f**.
- **version-15:** no such branch in this repository as of the snapshot; possible existing v15 elsewhere is **unverified**.
- **Rasheed/MacVMs:** host identified as MacVMs in the supplied shell session, SSH endpoint 192.168.64.15. Missing hostname command caused diagnostic to stop under interactive set -e. No subsequent audit results yet.
- **Deployment:** Frappe 16 installation and site reachability **not verified**.
- **Brand:** approved reference image exists in project conversation but production-ready approved files are **not committed to the repository**. Landing code currently uses a CSS temporary mark.
- **Testing:** no successful Rasheed/Mac browser UAT evidence or verified CI workflow in this repository.
- **Marketing/community/LMS/jobs/AI:** public landing scaffold mentions modules as planned. Do not represent them as implemented.

## Workstream dashboard

| Epic | Observed status | Next evidence required |
| --- | --- | --- |
| [ED-00 #1](https://github.com/VoyaERP/erpdevelopers/issues/1) Environment | **Blocked / Audit required** | Safe host inventory + isolated v16 site + Mac smoke |
| [ED-01 #2](https://github.com/VoyaERP/erpdevelopers/issues/2) Public brand/site | **Scaffold committed, UAT pending** | Approved asset + CMS/i18n/SEO + browser UAT |
| [ED-02 #3](https://github.com/VoyaERP/erpdevelopers/issues/3) IAM/privacy | **Planned** | Role matrix + threat model |
| [ED-03 #4](https://github.com/VoyaERP/erpdevelopers/issues/4) Community | **Planned** | ED-02 approval |
| [ED-04 #5](https://github.com/VoyaERP/erpdevelopers/issues/5) Developer Hub | **Planned** | ED-02 approval |
| [ED-05 #6](https://github.com/VoyaERP/erpdevelopers/issues/6) Academy | **Planned** | LMS v16 reuse decision |
| [ED-06 #7](https://github.com/VoyaERP/erpdevelopers/issues/7) Careers | **Planned** | Employer trust + provider rights |
| [ED-07 #8](https://github.com/VoyaERP/erpdevelopers/issues/8) AI | **Planned** | Scoping + role-safe RAG design |
| [ED-08 #9](https://github.com/VoyaERP/erpdevelopers/issues/9) Marketplace | **Planned** | Business/legal decisions |
| [ED-09 #10](https://github.com/VoyaERP/erpdevelopers/issues/10) DevOps / QA | **Planned / cross-cutting** | CI, release and test-evidence gates |
| [ED-00.1 #11](https://github.com/VoyaERP/erpdevelopers/issues/11) Shell failure | **Open** | Non-destructive audit from host |

## Immediate next actions (ordered)

1. [ ] Reconnect safely and run the [LOCAL_RASHEED.md](LOCAL_RASHEED.md) diagnostic without a persistent interactive set -e.
2. [ ] Confirm actual target host, OS/runtime compatibility and v15/production isolation.
3. [ ] Set up isolated Frappe 16 test site and collect migration/build/smoke evidence; never operate blindly on a live site.
4. [ ] Add approved logo assets and complete brand/mobile/bilingual acceptance.
5. [ ] Set up CI and publish first permission/threat-model matrix.

## Evidence ledger

| Date | Scope | Evidence | Result |
| --- | --- | --- | --- |
| 2026-11-13 | GitHub | branch version-16, scaffold commit 344c771 | **Committed only; not runtime tested** |
| 2026-11-13 | MacVMs shell | output: hostname command not found; SSH session closed | **Diagnostic failed; environment unknown** |
| 2026-11-13 | Project governance | Master plan + epic issue board created | **Documented; execution gates pending** |

## How to update this file

On each verified delivery event update: date, phase, issue URL, branch/commit, site/environment, acceptance evidence, failed checks, reviewer, next blockers and rollback. Only move work to **Done** after [governance definition of done](GOVERNANCE.md) is met. Do not invent test results, ETAs or completion percentages.
