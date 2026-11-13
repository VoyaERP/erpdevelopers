# ERP Developers — Execution Status / متابعة التنفيذ

**Snapshot date:** 2026-11-14 · **Scope:** VoyaERP/erpdevelopers · **Source of task detail:** [GitHub Issues](https://github.com/VoyaERP/erpdevelopers/issues) · **Master plan:** [MASTER_PLAN.md](MASTER_PLAN.md)

> حالة التنفيذ مبنية على أدلة من GitHub ومن مخرجات المستخدم فقط. لا يتم اعتبار الكود مختبرًا لمجرد رفعه.

## 2026-11-14 — Existing erptest-lightnode site confirmed (operator output)

- Operator used SSH to `erptest-lightnode` (Debian x86_64). Site folder `/data/frappe/frappe-bench/sites/erp-developers.com` **already exists**. The fresh-site installer correctly exited before creating or changing the site.
- `bench --site erp-developers.com list-apps` shows **frappe 16.56.0**, **erpnext 16.55.0**, with **no erpdevelopers installed**. `apps/erpdevelopers` is absent (Git reported cannot change directory).
- Operator `sudo nginx -t` reports syntax OK. This **does not** prove routing, DNS, TLS or an actual served home page.
- Canonical install path changed to **install app into existing site**, never run `bench new-site` and never drop the DB. New [backup-first existing-site installer](https://github.com/VoyaERP/erpdevelopers/blob/version-16/scripts/install_existing_site_erptest_lightnode.sh), updated guide and static contracts live on **version-16** at `dfbbaaa4d551b1f360ce696632b22ca119005a9f`; [GitHub Actions PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43526306183).
- Existing-site installer intentionally updates the exact site's Website Settings for ERP Developers home page/logo after successful backup and app installation; **existing ERPNext data is preserved**, though public site branding changes. No SSH installation or login/UAT has been completed by assistant.

## 2026-11-14 — Green Box-style login + public HTTPS deployment source

- **Ready in GitHub:** source branch `version-16` at `de86960ffa73c24fadba44723eb4bb5864aa6b87`; native Frappe 16 login preserved with local intersecting technology SVG, EN/AR chrome + native language selector; public anonymous HTTPS install/update helpers for erptest-lightnode; legacy GitHub App credential helper files removed from this branch.
- **Evidence:** [CI run 43525672861 — PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43525672861), source-only checks. This does not constitute authenticated login/UAT or server install evidence.
- **Block:** server connection not available to assistant, site/DNS/TLS/ingress not verified; issue #13 remains OPEN.

## Observed baseline

- **main:** repository entry/documentation branch; not a deployed release.
- **version-16:** native Frappe login styling, SVG backdrop, Frappe locale picker and homepage; public HTTPS installation scripts. Latest source SHA **dfbbaaa4d551b1f360ce696632b22ca119005a9f** adds backup-first installation into existing Frappe site. [Static CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43526306183). **Not yet installed/UAT-tested on erptest-lightnode.**
- **version-15:** no such branch in this repository as of the snapshot; possible existing v15 elsewhere is **unverified**.
- **MacVMs / existing Rasheed app:** actual host **MacVMs**, Arch Linux ARM aarch64. The existing `/home/manakhly/frappe-bench` runs **Frappe 15.118.0**, **ERPNext 15.121.0**, **rasheed app 0.0.1** and many other v15 apps; existing Frappe Git branch is `version-15`. This is a verified **v15 bench**, not a separate v16 host. User previously referred to “Rasheed local”; confirmed `rasheed` is an app present in this bench. Keep legacy workloads untouched. Python **3.14.7**, Node **20.20.2 by default**, **Node 24.22.3 installed successfully via user-level nvm** and verified **inside a subshell** (does not update default Node), Bench CLI **5.31.0**, Yarn **1.22.22**, Git **2.55.0**, Valkey **9.1.1**, MariaDB **12.3.2 server and client**. Ports `8000`, `9000`, `11000`, `13000`, `3306` are occupied; candidate alternative ports showed no listeners at the check instant.
- **Deployment:** Frappe v16 installation and Mac UAT **not started/verified**. **Latest critical storage blocker:** VM root `/dev/vda2` is **30 GB**, **25 GB used**, **3.6 GB available (88% used)** as confirmed by the 2026-11-13 follow-up; inode use is only **32%**, so the limiting resource is free storage. RAM **3.8 GiB total, ~2.5 GiB available**, swap **4 GiB**. Risk of out-of-space/build OOM while v15 workloads are running: **do not run `bench init` yet**. Recommended planning target for parallel test bench: at least **15–20 GB free disk** and **8 GiB RAM total or larger**, subject to measured workload; these are capacity recommendations, not claimed official Frappe minima. MariaDB **12.3.2 server** is different from documented v16 **11.8** baseline: compatibility is **unverified**, avoid changing shared DB. Valkey **9.1.1** exceeds documented 6+ baseline but integration still untested. **Arch Linux ARM not officially supported** for Frappe hosting; consider a separate supported Debian/Ubuntu ARM64 test VM if resources cannot be expanded. Docker and Podman commands absent. New Bench still requires distinct ports, isolated site/database and explicit per-shell `nvm use 24`.
- **Brand:** approved reference image exists in project conversation but production-ready approved files are **not committed to the repository**. Landing code currently uses a CSS temporary mark.
- **Testing:** latest version-16 GitHub static CI passed (Python compile, Node JS parse, Bash syntax and source contract unit tests; run 43525672861). No successful live erptest-lightnode or Rasheed/Mac browser UAT; no authenticated workflow or production verification.
- **Marketing/community/LMS/jobs/AI:** public landing scaffold mentions modules as planned. Do not represent them as implemented.

## Workstream dashboard

| Epic | Observed status | Next evidence required |
| --- | --- | --- |
| [ED-00 #1](https://github.com/VoyaERP/erpdevelopers/issues/1) Environment | **Blocked: disk capacity + compatibility review** | Current-host guarded installer available, 3.6GB fails >=8GiB preflight; MariaDB v12.3 compatibility, Mac smoke |
| [ED-01 #2](https://github.com/VoyaERP/erpdevelopers/issues/2) Public brand/site | **Green Box-style native login, homepage and static CI ready; UAT pending** | Final approved logo asset, EN/AR content, SEO, device/auth UAT |
| [ED-01.1 #13](https://github.com/VoyaERP/erpdevelopers/issues/13) erptest-lightnode public deployment | **Existing Frappe 16/ERPNext 16 site confirmed; app absent; existing-site installer/CI ready** | Backup, install app on existing site, DNS/TLS, native auth UAT |
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

## User direction: test on existing MacVMs (2026-11-13)

- User instructed to proceed on the **current MacVMs host**, not create a new VM at this stage.
- **Safe interpretation:** attempt a **separate v16 Bench** on this host, never upgrade the four existing v15 sites in place.
- Added a [guarded v16 installer](https://github.com/VoyaERP/erpdevelopers/blob/version-16/scripts/install_local_v16.sh) to the `version-16` branch. It checks the preserved v15 branch/site, **at least 8 GiB free storage**, >=2GiB available RAM, Node24 within nvm, GitHub SSH, and distinct ports before it creates a new v16 site.
- **Current 3.6 GB free fails the preflight**; *no install has been executed* on MacVMs and no safe capacity exception was granted. Required next step is to expand the disk or deliberately reclaim verified expendable storage until the guard passes. Preserve backup/restore options before modifying disk.
- Frappe v16's published MariaDB **11.8** target differs from MacVMs MariaDB **12.3.2**: test compatibility only on a new database, never change the shared DB service for an unverified install.
- This is for local development and Mac SSH-tunnel UAT only, **not production readiness**.

## GitHub App deployment decision (2026-11-14)

- The user selected a dedicated **GitHub App** for private repository authentication on **erptest-lightnode**, replacing the previous SSH Deploy Key / account SSH key guidance for this target.
- Implemented and merged in **version-16**, [PR #15](https://github.com/VoyaERP/erpdevelopers/pull/15), commit **a668ba53146d193de32940083f2c94c9a31fe1e4**.
- New source-of-truth guide: [docs/GITHUB_APP_DEPLOY.md](https://github.com/VoyaERP/erpdevelopers/blob/version-16/docs/GITHUB_APP_DEPLOY.md). The installer and updater now access the private GitHub repository using tokenless HTTPS plus a Git credential helper that issues a short-lived **Contents:read** GitHub App installation token scoped to **VoyaERP/erpdevelopers**.
- Credentials remain **off GitHub**: downloaded App PEM/config stored securely under `~/.config/erpdevelopers` on the server (0600 files). Neither token nor PEM is saved in the repository or in Git remote URLs.
- **Pending:** user/organization owner must register and install the App (only selected repository), download and transfer its PEM, configure numeric App ID, verify HTTPS Git, then execute new-site installer on erptest-lightnode. **No App creation, server installation, DNS/TLS, CI pass or UAT is claimed.** Existing failing CI gate remains open.
- Target Bench: `/data/frappe/frappe-bench`. The **MacVMs/Frappe15 environment is a separate workstream**, unaffected by this GitHub App change.

## Private-repository SSH deployment refinement (2026-11-14)

- GitHub repository `VoyaERP/erpdevelopers` is **private**. Git operations performed by erptest-lightnode must authenticate using an **existing SSH key authorized for this repository**; ChatGPT's GitHub connector does not confer server SSH access.
- Corrected `erptest-lightnode` Bench default to `/data/frappe/frappe-bench` (not MacVMs' `~/frappe-bench`). Both installer and updater now honor an explicit `BENCH` override.
- Preflight uses `ssh -o BatchMode=yes` with `git ls-remote`, to stop with guidance instead of blocking on an encrypted key's passphrase. Load the *existing* key into `ssh-agent` first; no new SSH key or token is created by the script.
- Changes merged into `version-16` through [PR #14](https://github.com/VoyaERP/erpdevelopers/pull/14), commit **3a0f9bd11ad678370740c5ae2d91504e65e5a591**; runbook: [private GitHub access](https://github.com/VoyaERP/erpdevelopers/blob/version-16/docs/ERPTEST_LIGHTNODE.md).
- **Server authentication check, site installation, CI and UAT remain unverified.** Track [ED-01.1 #13](https://github.com/VoyaERP/erpdevelopers/issues/13) before approving release.

## erptest-lightnode public site deployment (new scope, 2026-11-14)

- Domain: **erp-developers.com**; distinct from existing MacVMs v15/Rasheed audit.
- Frappe v16 source code staged and PR **[#12](https://github.com/VoyaERP/erpdevelopers/pull/12)** merged into **version-16**, commit **ae1a44a777e89f7a55ee212a90a5c378321572df**.
- Green Box reference reviewed: **VoyaERP/greenbox.com.eg** retains native Frappe /login and layers website CSS and Chrome only. ERP Developers adaptation targets **native Frappe v16** markup and does not replace authentication, 2FA, forgot-password or social-login behavior.
- Home route: **erp-developers-home** configured through explicit CLI-only method; site-specific install/update scripts and guide at [docs/ERPTEST_LIGHTNODE.md](https://github.com/VoyaERP/erpdevelopers/blob/version-16/docs/ERPTEST_LIGHTNODE.md).
- First GitHub Actions static-validation workflow ran but returned **failure**, with no accessible step-level logs via the current connector. **CI remains unresolved**; do not mark R1 Done.
- No actual erptest-lightnode SSH install, DNS, Nginx, HTTPS, responsive/auth browser UAT or public go-live has been verified. Source SVG is a directionally matched icon, **not** an exact editable conversion of the approved PNG.
- Next owner action: execute read-only preflight and guarded install on erptest-lightnode, verify route and native login, then configure TLS safely. Track [Issue #13](https://github.com/VoyaERP/erpdevelopers/issues/13).

## Evidence ledger

| Date | Scope | Evidence | Result |
| --- | --- | --- | --- |
| 2026-11-13 | GitHub | branch version-16, scaffold commit 344c771 | **Committed only; not runtime tested** |
| 2026-11-13 | MacVMs first shell | output: hostname command not found; SSH session closed due to shell error handling | **Initial diagnostic failed** |
| 2026-11-13 | MacVMs second shell | safe audit: Arch Linux ARM, Python 3.14.7, Node 20.20.2, MariaDB client 12.3.2, occupied ports 8000/9000/11000/13000/3306 | **Host inventoried; v16 runtime still unverified** |
| 2026-11-13 | MacVMs readiness | Frappe 15.118.0, ERPNext 15.121.0, `rasheed` 0.0.1; 30G root with 3.8G free; 3.8GiB RAM, 2.5GiB available; MariaDB 12.3.2 server, Valkey 9.1.1, Yarn 1.22.22; Node 24.22.3 installed via nvm | **R0 blocked on disk capacity and compatibility validation; v15 untouched** |
| 2026-11-13 | Storage/site inventory | 30G root, **3.6G free (88%)**, inodes 32%; Bench 6.1G; VS Code remote 3.1G; four v15 sites; ext4 `/dev/vda2` | **Blocker confirmed; expansion/VM isolation decision pending** |
| 2026-11-13 | QEMU guest tool audit | `systemd-detect-virt=qemu`, `resize2fs` present, `growpart` absent, `vda2` ext4 | **Virtualization engine verified; Mac VM manager/backups remain unknown** |
| 2026-11-13 | In-place v16 installation decision | User requests current MacVMs; guarded install script committed on `version-16` (Node24 scoped, free-space/port/v15 safety gates) | **Script ready, not run; disk preflight blocked at 3.6GiB free** |
| 2026-11-14 | Private GitHub App source authentication | PR #15 merged to version-16 (a668ba5); GitHub App helper, tokenless HTTPS installer and setup guide | **Code ready; App installation/server Git auth pending; CI unresolved** |
| 2026-11-14 | erptest-lightnode website/Login | PR #12 merged on version-16 commit ae1a44a; deployment guide + guarded script + v16-native /login CSS/JS | **Source merged; CI failure unresolved; no server/UAT proof** |
| 2026-11-13 | Project governance | Master plan + epic issue board created | **Documented; execution gates pending** |

## How to update this file

On each verified delivery event update: date, phase, issue URL, branch/commit, site/environment, acceptance evidence, failed checks, reviewer, next blockers and rollback. Only move work to **Done** after [governance definition of done](GOVERNANCE.md) is met. Do not invent test results, ETAs or completion percentages.
