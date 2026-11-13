# ERP Developers — Execution Status / متابعة التنفيذ

**Snapshot date:** 2026-11-13 · **Scope:** VoyaERP/erpdevelopers · **Source of task detail:** [GitHub Issues](https://github.com/VoyaERP/erpdevelopers/issues) · **Master plan:** [MASTER_PLAN.md](MASTER_PLAN.md)

> حالة التنفيذ مبنية على أدلة من GitHub ومن مخرجات المستخدم فقط. لا يتم اعتبار الكود مختبرًا لمجرد رفعه.

## Observed baseline

- **main:** repository entry/documentation branch; not a deployed release.
- **version-16:** application scaffold pushed; last *observed code* commit before plan: **344c771a6df6c9ea617095104fc0a01ad798b17f**.
- **version-15:** no such branch in this repository as of the snapshot; possible existing v15 elsewhere is **unverified**.
- **Rasheed/MacVMs:** safe follow-up diagnostic completed on `MacVMs` (prior SSH endpoint `192.168.64.15`). OS **Arch Linux ARM rolling (archarm)**, Python **3.14.7**, Node **20.20.2**, Bench CLI **5.31.0**, Git **2.55.0**. Installed MariaDB **client 12.3.2**, **server version unverified**; existing Bench at `/home/manakhly/frappe-bench`. Ports `8000`, `9000`, `11000`, `13000`, `3306` are occupied. `hostname` remains unavailable, but `uname -n` worked and SSH remained connected. Need explicit confirmation that `MacVMs` is the intended Rasheed host.
- **Deployment:** Frappe 16 installation and site reachability **not verified**. **R0 blockers:** upgrade Node in a per-shell nvm environment to v24, check actual MariaDB **server** compatibility with Frappe v16 documented **11.8**, verify Redis/Valkey, disk/RAM, existing Bench version/site, and reserve free ports. Arch Linux ARM is **not officially supported by Frappe's current install guide** (macOS and Debian/Ubuntu are listed).
- **Brand:** approved reference image exists in project conversation but production-ready approved files are **not committed to the repository**. Landing code currently uses a CSS temporary mark.
- **Testing:** no successful Rasheed/Mac browser UAT evidence or verified CI workflow in this repository.
- **Marketing/community/LMS/jobs/AI:** public landing scaffold mentions modules as planned. Do not represent them as implemented.

## Workstream dashboard

| Epic | Observed status | Next evidence required |
| --- | --- | --- |
| [ED-00 #1](https://github.com/VoyaERP/erpdevelopers/issues/1) Environment | **Discovery evidence received; prerequisites blocked** | Node 24, server DB/Redis/resources/ports, isolated v16 site + Mac smoke |
| [ED-01 #2](https://github.com/VoyaERP/erpdevelopers/issues/2) Public brand/site | **Scaffold committed, UAT pending** | Approved asset + CMS/i18n/SEO + browser UAT |
| [ED-02 #3](https://github.com/VoyaERP/erpdevelopers/issues/3) IAM/privacy | **Planned** | Role matrix + threat model |
| [ED-03 #4](https://github.com/VoyaERP/erpdevelopers/issues/4) Community | **Planned** | ED-02 approval |
| [ED-04 #5](https://github.com/VoyaERP/erpdevelopers/issues/5) Developer Hub | **Planned** | ED-02 approval |
| [ED-05 #6](https://github.com/VoyaERP/erpdevelopers/issues/6) Academy | **Planned** | LMS v16 reuse decision |
| [ED-06 #7](https://github.com/VoyaERP/erpdevelopers/issues/7) Careers | **Planned** | Employer trust + provider rights |
| [ED-07 #8](https://github.com/VoyaERP/erpdevelopers/issues/8) AI | **Planned** | Scoping + role-safe RAG design |
| [ED-08 #9](https://github.com/VoyaERP/erpdevelopers/issues/9) Marketplace | **Planned** | Business/legal decisions |
| [ED-09 #10](https://github.com/VoyaERP/erpdevelopers/issues/10) DevOps / QA | **Planned / cross-cutting** | CI, release and test-evidence gates |
| [ED-00.1 #11](https://github.com/VoyaERP/erpdevelopers/issues/11) Shell failure | **Resolved via safe audit** | `uname -n` works; avoid parent `set -e` |

## Immediate next actions (ordered)

1. [x] Safe, non-destructive host inventory collected: `uname -n` works; SSH session preserved.
2. [ ] Confirm `MacVMs` is the intended Rasheed target and collect **existing Bench/site versions** plus actual MariaDB **server** version, Redis version, RAM/disk, free port scan.
3. [ ] Install/use **Node 24 via nvm for the new bench only**, preserving Node 20 for existing workloads.
4. [ ] Confirm compatible database runtime and independent ports, then create an isolated Frappe 16 test Bench/site with migration/build/smoke evidence.
5. [ ] Add approved logo assets and perform brand/mobile/bilingual UAT; establish CI and access-control matrix.

## Evidence ledger

| Date | Scope | Evidence | Result |
| --- | --- | --- | --- |
| 2026-11-13 | GitHub | branch version-16, scaffold commit 344c771 | **Committed only; not runtime tested** |
| 2026-11-13 | MacVMs first shell | output: hostname command not found; SSH session closed due to shell error handling | **Initial diagnostic failed** |
| 2026-11-13 | MacVMs second shell | safe audit: Arch Linux ARM, Python 3.14.7, Node 20.20.2, MariaDB client 12.3.2, occupied ports 8000/9000/11000/13000/3306 | **Host inventoried; v16 runtime still unverified** |
| 2026-11-13 | Project governance | Master plan + epic issue board created | **Documented; execution gates pending** |

## How to update this file

On each verified delivery event update: date, phase, issue URL, branch/commit, site/environment, acceptance evidence, failed checks, reviewer, next blockers and rollback. Only move work to **Done** after [governance definition of done](GOVERNANCE.md) is met. Do not invent test results, ETAs or completion percentages.
