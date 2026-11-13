# ERP Developers — Execution Status / متابعة التنفيذ

**Snapshot date:** 2026-11-13 · **Scope:** VoyaERP/erpdevelopers · **Source of task detail:** [GitHub Issues](https://github.com/VoyaERP/erpdevelopers/issues) · **Master plan:** [MASTER_PLAN.md](MASTER_PLAN.md)

> حالة التنفيذ مبنية على أدلة من GitHub ومن مخرجات المستخدم فقط. لا يتم اعتبار الكود مختبرًا لمجرد رفعه.

## Observed baseline

- **main:** repository entry/documentation branch; not a deployed release.
- **version-16:** application scaffold pushed; last *observed code* commit before plan: **344c771a6df6c9ea617095104fc0a01ad798b17f**.
- **version-15:** no such branch in this repository as of the snapshot; possible existing v15 elsewhere is **unverified**.
- **MacVMs / existing Rasheed app:** actual host **MacVMs**, Arch Linux ARM aarch64. The existing `/home/manakhly/frappe-bench` runs **Frappe 15.118.0**, **ERPNext 15.121.0**, **rasheed app 0.0.1** and many other v15 apps; existing Frappe Git branch is `version-15`. This is a verified **v15 bench**, not a separate v16 host. User previously referred to “Rasheed local”; confirmed `rasheed` is an app present in this bench. Keep legacy workloads untouched. Python **3.14.7**, Node **20.20.2 by default**, **Node 24.22.3 installed successfully via user-level nvm** and verified **inside a subshell** (does not update default Node), Bench CLI **5.31.0**, Yarn **1.22.22**, Git **2.55.0**, Valkey **9.1.1**, MariaDB **12.3.2 server and client**. Ports `8000`, `9000`, `11000`, `13000`, `3306` are occupied; candidate alternative ports showed no listeners at the check instant.
- **Deployment:** Frappe v16 installation and Mac UAT **not started/verified**. **Latest critical storage blocker:** VM root `/dev/vda2` is **30 GB**, **25 GB used**, **3.6 GB available (88% used)** as confirmed by the 2026-11-13 follow-up; inode use is only **32%**, so the limiting resource is free storage. RAM **3.8 GiB total, ~2.5 GiB available**, swap **4 GiB**. Risk of out-of-space/build OOM while v15 workloads are running: **do not run `bench init` yet**. Recommended planning target for parallel test bench: at least **15–20 GB free disk** and **8 GiB RAM total or larger**, subject to measured workload; these are capacity recommendations, not claimed official Frappe minima. MariaDB **12.3.2 server** is different from documented v16 **11.8** baseline: compatibility is **unverified**, avoid changing shared DB. Valkey **9.1.1** exceeds documented 6+ baseline but integration still untested. **Arch Linux ARM not officially supported** for Frappe hosting; consider a separate supported Debian/Ubuntu ARM64 test VM if resources cannot be expanded. Docker and Podman commands absent. New Bench still requires distinct ports, isolated site/database and explicit per-shell `nvm use 24`.
- **Brand:** approved reference image exists in project conversation but production-ready approved files are **not committed to the repository**. Landing code currently uses a CSS temporary mark.
- **Testing:** no successful Rasheed/Mac browser UAT evidence or verified CI workflow in this repository.
- **Marketing/community/LMS/jobs/AI:** public landing scaffold mentions modules as planned. Do not represent them as implemented.

## Workstream dashboard

| Epic | Observed status | Next evidence required |
| --- | --- | --- |
| [ED-00 #1](https://github.com/VoyaERP/erpdevelopers/issues/1) Environment | **Blocked: disk capacity + compatibility review** | Free disk/RAM capacity, MariaDB v12.3 vs v16 baseline, separate ports/site, Mac smoke |
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
2. [x] Confirm observed MacVMs host has the existing Frappe v15 bench and `rasheed` app; inventory MariaDB server 12.3.2, Valkey 9.1.1, Yarn 1.22.22, and system resources. Individual v15 site names **not yet listed** due unsupported `bench list-sites` command.
3. [x] Node 24.22.3 **installed successfully with nvm**; use via `nvm use 24` in the new Bench shell, do not change default Node 20.
4. [ ] **Stop before installing:** expand VM storage / provision a separate test VM; conservatively target at least 15–20GB free and 8GiB RAM for concurrent benches, then verify MariaDB 12.3 compatibility or provision isolated tested 11.8 DB.
5. [ ] Verify real site inventory, distinct ports, and then create isolated v16 bench and collect migration/build/Mac smoke evidence. Add brand/UI and CI gates later.

## Fourth audit — Storage breakdown and protected site inventory (2026-11-13)

- Root `/dev/vda2` **ext4**, 30G total / 25G used / **3.6G available**, **88%**; inode usage **32%** (1,328,838 free).
- Home total `~16G`, including current `~/frappe-bench` **6.1G**: `apps` **4.1G**, `sites` **981M**, `env` **935M**, `logs` **96M**, `archived` **57M**.
- Other sizeable user paths: `~/.vscode-server` **3.1G**, `~/mobile` **2.2G**, `~/.nvm` **1.2G**, `~/.cache` **815M**, `~/.codex` **503M**, `~/.npm` **385M**, `~/bk` **443M**, `~/emqx-install` **325M**; `/var/cache/pacman/pkg` **890M**.
- **Four confirmed v15 sites:** `frappiq-cert.local`, `s1.mac.dynamicsforall.com`, `frappe.localhost`, `lg.mac.dynamicsforall.com`. **Do not delete or migrate them.**
- `vda` is a 30G virtual disk; `vda1` 200M VFAT `/boot`; `vda2` 29.8G ext4 for root and `/boot/dtbs`. Both disk *partition* and ext4 filesystem must be extended **after** hypervisor expansion, with off-VM backup/snapshot and verified process.
- **Pending choice:** provision separate supported Ubuntu/Debian ARM64 VM **or** resize this virtual disk from 30G to a proposed **80G** and preferably increase memory to **8GiB**, subject to actual Mac host capacity and verified backup. This is a *recommendation awaiting user/host approval*, not a completed action.
- **No cleanup performed.** Do not remove `frappe-bench`, `sites`, `apps`, `bk`, `mobile`, `~/.vscode-server`, Node 20, logs or backups blindly. Read-only inspection first; cache cleanup would not replace storage expansion.

## Fifth audit — QEMU guest + partition tooling (2026-11-13)

- **Virtualization detected:** `systemd-detect-virt` returns **qemu**. This identifies the hypervisor, **not** which macOS manager (UTM / QEMU / other) owns the disk; host-side manager still unverified.
- Guest block layout reconfirmed: `/dev/vda` **30G**; `/dev/vda1` **200M vfat** mounted at `/boot`; `/dev/vda2` **29.8G ext4** mounted at `/` and `/boot/dtbs`. No host image expansion done.
- `resize2fs` is installed at `/usr/bin/resize2fs`; `growpart` absent; `paccache` was not run because not available.
- Correct growth sequence: external backup/snapshot → identify Mac hypervisor and disk image → stop VM completely → grow backing virtual disk (proposed 80G, pending available host space and approval) → boot/review `lsblk` → extend `vda2` using a **verified host-specific partition procedure** → grow ext4 using `resize2fs` → verify `df`, site/backup health, v15 regression.
- **Do not execute** `resize2fs /dev/vda2` or any partition writer until the VM actually exposes a larger `vda`, a valid off-VM backup exists, and partition layout/backup is verified. Partition resizing and filesystem resizing are separate tasks.
- Official references: [QEMU disk resize](https://www.qemu.org/docs/master/tools/qemu-img.html), [GNU Parted resizepart](https://www.gnu.org/software/parted/manual/html_node/resizepart.html), [UTM Drive](https://docs.getutm.app/settings-apple/drive/) (only if host confirms UTM).

**Next non-destructive evidence required:** On Mac host, `df -h "$HOME"`, the virtualization application/VM owner, and confirmation of off-VM backup. This is a **decision gate**, not permission to modify a running disk.

## Evidence ledger

| Date | Scope | Evidence | Result |
| --- | --- | --- | --- |
| 2026-11-13 | GitHub | branch version-16, scaffold commit 344c771 | **Committed only; not runtime tested** |
| 2026-11-13 | MacVMs first shell | output: hostname command not found; SSH session closed due to shell error handling | **Initial diagnostic failed** |
| 2026-11-13 | MacVMs second shell | safe audit: Arch Linux ARM, Python 3.14.7, Node 20.20.2, MariaDB client 12.3.2, occupied ports 8000/9000/11000/13000/3306 | **Host inventoried; v16 runtime still unverified** |
| 2026-11-13 | MacVMs readiness | Frappe 15.118.0, ERPNext 15.121.0, `rasheed` 0.0.1; 30G root with 3.8G free; 3.8GiB RAM, 2.5GiB available; MariaDB 12.3.2 server, Valkey 9.1.1, Yarn 1.22.22; Node 24.22.3 installed via nvm | **R0 blocked on disk capacity and compatibility validation; v15 untouched** |
| 2026-11-13 | Storage/site inventory | 30G root, **3.6G free (88%)**, inodes 32%; Bench 6.1G; VS Code remote 3.1G; four v15 sites; ext4 `/dev/vda2` | **Blocker confirmed; expansion/VM isolation decision pending** |
| 2026-11-13 | QEMU guest tool audit | `systemd-detect-virt=qemu`, `resize2fs` present, `growpart` absent, `vda2` ext4 | **Virtualization engine verified; Mac VM manager/backups remain unknown** |
| 2026-11-13 | Project governance | Master plan + epic issue board created | **Documented; execution gates pending** |

## How to update this file

On each verified delivery event update: date, phase, issue URL, branch/commit, site/environment, acceptance evidence, failed checks, reviewer, next blockers and rollback. Only move work to **Done** after [governance definition of done](GOVERNANCE.md) is met. Do not invent test results, ETAs or completion percentages.
