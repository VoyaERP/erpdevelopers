# ERP Developers — Execution Status / متابعة التنفيذ

**Snapshot date:** 2026-11-14 · **Scope:** VoyaERP/erpdevelopers · **Source of task detail:** [GitHub Issues](https://github.com/VoyaERP/erpdevelopers/issues) · **Master plan:** [MASTER_PLAN.md](MASTER_PLAN.md)

> حالة التنفيذ مبنية على أدلة من GitHub ومن مخرجات المستخدم فقط. لا يتم اعتبار الكود مختبرًا لمجرد رفعه.

## 2026-11-14 — Restore original orbit design, English/Arabic and single login header (CI passed; live deploy pending)

- User preferred the **earlier orbit-based visual direction and bilingual experience** and requested only tighter spacing, the exact selected PNG, and a fix for login loading two things. The earlier `ae1a44a` landing/login history and Frappe v16.56.0 template were reviewed before changes.
- Verified source-level duplicate-header condition: in Frappe 16, `www/login.html` renders the native `<nav class="navbar">` when `show_language_picker` is enabled; ERP Developers JS inserted another website header; old CSS hid `header.navbar` but not `nav.navbar`. Corrected scoped CSS hides the native navbar **only when the custom header has initialized**, reuses/moves its existing `#language-switcher`, suppresses redundant logo/footer chrome and restores a compact bilingual story aside next to the **unchanged Frappe auth form**. This is a source diagnosis; exact live meaning of the user's "2 things" still requires new screenshot/UAT.
- Restored the original bright/orbit hero and mission structure, but removed oversized 640px hero and 92px section padding; orbit center uses the **approved PNG's derived favicon**, not an invented substitute logo. Existing exact full customer logo preserved at header/footer and native login. Kept six typed planned ecosystem modules/AI/roadmap from the refactor.
- Restored native Frappe `#language-switcher` in custom homepage header (no separate cookie handler) and added **63 English-to-Arabic translations** in `erpdevelopers/translations/ar.csv`, rendered via server-side `_()`, Arabic-friendly CSS and Frappe RTL support. Original brand wording/tagline stays intact.
- Expanded source validation: Python translations coverage, screenshot-regression selectors, one-time native login JS behavior and zero-dependency Node DOM simulation verifying **one** header/story/footer/picker and a preserved original `<form>` even when JS executes twice. Enhanced read-only `scripts/verify_frontend.sh` checks Origin stylesheet/PNG bytes, six cards, English and Arabic render via `?_lang=en|ar`, native login markup, and public CSS/JS/HTTP.
- **Final source:** `version-16` commit **9a12af65800e623f19c6a15b34fbfcb588ead276**; [GitHub Actions CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43534766440) (Python 3.14, Node 24 JS+DOM, Bash syntax, contracts).
- **Not yet deployed or visually UAT-tested** on `erp-developers.com`. The previously reported unstyled homepage and doubled-login symptom need live before/after confirmation after a pinned backup-first existing-site update, site-only migration/build/cache clear, coordinated **web-only** Gunicorn restart, smoke checks and real English/Arabic/RTL/auth/2FA/other-site checks. Keep [Issue #13](https://github.com/VoyaERP/erpdevelopers/issues/13) open.

## 2026-11-14 — Maintainability/security refactor completed in GitHub (deployment and browser UAT pending)

- **Refactored `version-16` HEAD:** **404cfa128f47327fbc8467ba626fe3a4a85d380f**, [GitHub Actions CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43533258437): Python 3.14 compile, JavaScript syntax, Bash syntax and source/behavior tests passed. This is **not** a live Bench integration run.
- Added pure `erpdevelopers/branding.py` as canonical source of site hostname, Frappe homepage, original uploaded PNG/favicons, branded Website Settings and a 16-char content-addressed `brand.css` URL. `www/erp_developers_home.py` binds logo/style URLs to the Jinja page, which uses the native Frappe `head_include` block once. Removes stale hardcoded CSS cache date and repeated Python logo strings.
- Added typed `erpdevelopers/content.py` and loop-driven Jinja templates for three principles, six **planned** ecosystem features, four AI flow steps and four roadmap stages (no duplicated card HTML). Reformatted responsive CSS, scoped homepage variables to `.ed-site`, and consolidated decorative native login JS image/nav helpers. Exact customer PNG remains unchanged. No API, data model, privileged method, workflow or native auth override added.
- Added behavioral unit tests for wrong-site refusal before database access, idempotent site settings, static content, exact PNG hashes and page/CSS content fingerprint. Guarded updater now validates source **before migration**, supports strict `EXPECTED_SHA` comparison, checks approved logo, backs up target site with files and does not auto-restart shared services. New read-only `scripts/verify_frontend.sh` compares actual Origin CSS bytes, selected logos and six server-rendered cards; probes Cloudflare routes/assets.
- **Last user screenshot showed CSS not applying**. Prior patch `ec75d35` and this refactor address code-side loading/caching, but no server deployment evidence of the refactor, web restart, new HTML/CSS consistency or browser UAT is available. The previously confirmed server installation was `39659d4`; user may have advanced it independently. Keep [GitHub issue #13](https://github.com/VoyaERP/erpdevelopers/issues/13) OPEN. Operator must stage the pinned update script outside the mutable Git checkout, update the **existing** site, coordinate a web-only Gunicorn restart with shared-Bench sites, then run the read-only frontend verifier and real browser/auth/RTL UAT.

## 2026-11-14 — Homepage CSS loading bug found; route-scoped asset fix ready

- User screenshot after selected-logo deployment showed an **unstyled homepage**: visible skip-to-content link, enormous unstyled header text and misaligned navigation. Customer PNG itself loaded correctly. These symptoms show missing/inoperative `brand.css` in the browser; response/static-file diagnostics from the user's server have not yet been captured, so the precise transport/caching failure is unconfirmed.
- Frappe v16 [`templates/base.html`](https://github.com/frappe/frappe/blob/v16.56.0/frappe/templates/base.html) exposes a `head_include` block. On `version-16` commit **ec75d35f3e233660f062002076d348f8b0981aa2**, the homepage uses that supported block to include `/assets/erpdevelopers/css/brand.css?v=20261114-website-fix-1` explicitly, retaining `{{ super() }}`. Removed `brand.css` from global `web_include_css` to avoid duplication; `login.css` remains global and scoped to native login. No change to exact selected PNG, API, authentication, 2FA, or Frappe core.
- Added a contract test for explicit once-only route-scoped CSS, source file, media breakpoint and hook isolation. [GitHub Actions CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43532049626).
- **Not yet confirmed live**. Next operator action: guarded existing-site updater (backup, migrate, build, test, clear-cache), targeted web-only restart because `hooks.py` changed, then GET homepage verifying `brand.css?v=...` is in head and CSS endpoint returns HTTP 200 with expected selectors. Finally check refreshed browser on desktop/mobile and other shared-Bench sites.

## 2026-11-14 — Correct customer PNG deployed to source repository; cleaner website UI prepared

- Customer explicitly rejected the earlier Neural Intelligence concept logo and provided the actual selected raster image `ERP DEvlopers.png`. The original **2048×682 transparent RGBA PNG was committed byte-for-byte** at `erpdevelopers/public/images/erpdevelopers-selected-logo.png`, SHA-256 **250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d**, Git blob SHA-1 `2d60b2c4183a5813168949e89f1d8473da9be227`. No regeneration/retrace/recoloring. A 96×96 favicon was cropped from the exact supplied icon. Old unrelated SVG logo assets removed.
- Website Settings app logo and favicon now reference approved PNG assets, and the same exact full logo is used on homepage header, homepage hero brand panel, footer and native login's custom decorative header/footer. Authentication form, login endpoints, 2FA and language picker remain under Frappe.
- Home UI revised with smaller vertical gaps, brighter white/blue business palette, clear editorial hero and **logo-led preview card** (replacing artificial glow/orbit artwork), three-value Engage/Reason/Progress ribbon, compact 3×2 feature cards explicitly labeled **Planned module**, focused vision/AI/roadmap blocks and mobile breakpoints. Login frame height and outer margins reduced.
- Final source `version-16` commit **5e6cb556189a092bae69707a1af7b3f9f94be760**, [GitHub Actions CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43531485227) (includes exact PNG checksum contract and previous Frappe auth tests). This is source verification, **not yet live UI/browser acceptance**.
- Last verified server runtime remains installation SHA `39659d4`, although the operator may have independently deployed newer builds. Next: use guarded existing-site updater after confirming clean checkout/current SHA; backup with files, fast-forward to exact `5e6cb55`, migrate/configure/build/tests/clear cache; **targeted Supervisor web-only restart** to load changed Python/hook code, noting short impact to all sites sharing Gunicorn. Verify logo SHA and 200 for all critical routes + PNG assets, then human browser responsive/RTL/auth UAT.
- [GitHub Issue #13](https://github.com/VoyaERP/erpdevelopers/issues/13) remains OPEN.

## 2026-11-14 — Professional landing/login redesign and exact approved logo (awaiting deployment)

- User requested remove excess whitespace, make public site more polished and **use the exact previously chosen logo**. The approved asset, concept **01 — Neural Intelligence**, was recovered as the original `erp_developers_01_neural_intelligence.svg` (SHA-256 `9ff7a4b8409a3bbf1f5cf438e5d73fc3d3fd28f564576c720c572d55f6d93293`). No artwork redrawn. The source is preserved verbatim in `erpdevelopers/public/images/erp-developers-neural-intelligence.svg`; display `erp-developers-logo.svg` only adjusts SVG viewport, and `erp-mark.svg` uses the symbol cropped from the exact master for favicon/illustration.
- On `version-16`, latest SHA **88f2eba011df580bb8b0550fa6fa71c7918413c2**: redesigned homepage with compact responsive 2-column hero, original network symbol, balanced site navigation, denser 6 planned-module cards, security-conscious AI section, concise roadmap, compact footer; login spacing tightened, native Frappe form and locale/2FA preserved, branding unified across header/footer/login, site-specific Website Settings app logo updated.
- Added regression contract for original logo SHA-256 and SVG crop fidelity, brand placement, mobile breakpoints and Frappe-native auth integrity; [GitHub Actions CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43529628411). This is **source CI**, not live visual/UAT.
- **Not deployed on server yet**: last operator-confirmed running commit `39659d46422f7c45d9bc8ec75aafb91c1c1574e3`. Deployment operator should update only the existing site using the guarded `scripts/update_erptest_lightnode.sh` with backup, check final SHA, recheck assets and routes and browser visuals. Do not invoke new-site installer, core upgrades or broad service restarts. Confirm native login, Arabic/English, responsive screen widths, 2FA and other Bench sites before marking production-ready.

## 2026-11-14 — Targeted Gunicorn restart resolved origin/public HTTP 500

- Operator verified `./env/bin/python` imports both `erpdevelopers` and `erpdevelopers.erp_developers`. The deployed site remains `erpdevelopers 0.1.0`, SHA **39659d46422f7c45d9bc8ec75aafb91c1c1574e3**.
- Service ownership verified: Supervisor `frappe-bench-web:frappe-bench-frappe-web`, old Gunicorn master PID `9801`. Operator performed **targeted web-only restart**, not shared Bench/Redis/Nginx/worker restart. New Gunicorn master PID `11707`; new 5 worker processes started at `2026-11-14 07:38:25 +0800` in log.
- **Recovery confirmed:** direct local-Nginx Origin and Cloudflare **HTTP GET** for `/api/method/ping`, `/login` and `/` all returned **HTTP 200**. Previous tracebacks (`ModuleNotFoundError: erpdevelopers`, secondary `AttributeError: is_ajax`) were from old Gunicorn workers and no new exception appears after the restart in the provided log segment.
- **Runtime incident resolved**, but not a full production release: user has not yet confirmed site appearance, public CSS/JS/SVG asset status, browser console, actual session login/2FA/password reset, EN/AR mobile responsiveness, or other shared-Bench websites. Keep [GitHub #13](https://github.com/VoyaERP/erpdevelopers/issues/13) **OPEN** pending UAT.

## 2026-11-14 — Root cause isolated to Gunicorn web runtime

- Operator diagnostics: Cloudflare **and direct-local-Nginx** GET requests to `/`, `/login` and `/api/method/ping` all returned HTTP 500. Nginx listening 80/443; Gunicorn listening 127.0.0.1:8000 with 5 workers under `--preload`. This rules out a Cloudflare-only problem and shows the failure occurs before ordinary route handling.
- `logs/web.error.log` reports **`ModuleNotFoundError: No module named 'erpdevelopers'`** in Frappe `init_request → setup_module_map → get_module_list`; subsequent **`AttributeError: is_ajax`** is an exception-handler symptom. The Bench CLI can list and run the installed app, which suggests the web process may be retaining pre-install import state, but **stale Gunicorn not yet confirmed by comparing live PID start time with installation**.
- Source of Gunicorn service naming: [Bench v5.31 Supervisor template](https://github.com/frappe/bench/blob/v5.31.0/bench/config/templates/supervisor.conf#L5-L16), optionally [systemd template](https://github.com/frappe/bench/blob/v5.31.0/bench/config/templates/systemd/frappe-bench-frappe-web.service). Operator next: verify target Bench env Python import, confirm precise process manager and Gunicorn service ownership, perform **only targeted web process restart** if confirmed (short impact to shared-Bench sites), then repeat direct-origin `/api/method/ping`, `/login`, `/` GET and inspect fresh log only if still failing.
- No application source changes, Nginx changes or service restarts performed by assistant. Site UI/login UAT remains blocked and issue #13 OPEN.

## 2026-11-14 — App installed; public HTTP 500 remains open

- **Deployment completed on target site**, according to operator logs: `bench --site erp-developers.com list-apps` now reports Frappe **16.56.0**, ERPNext **16.55.0**, **erpdevelopers 0.1.0**, all `version-16`. ERP Developers SHA **39659d46422f7c45d9bc8ec75aafb91c1c1574e3**; application install, migration, site-specific Website Settings, assets build and translations succeeded.
- Website Settings changed for this site: `home_page=erp-developers-home`, app name/logo/favicon/title and language picker. Build succeeded (`DONE Total Build Time: 198.438ms`); warning regarding Node deprecated `url.parse()` not shown to be a fatal error.
- **Public web serving NOT OK**: `curl -I https://erp-developers.com/` and `curl -I https://erp-developers.com/login` returned **HTTP/2 500** with Cloudflare headers. This does not determine whether the exception is Frappe web rendering, stale workers, Nginx routing or another origin layer. No server traceback, direct-origin HTTP comparison or authenticated browser UAT evidence yet.
- Nginx configuration syntax previously passed and contained the apex domain and Cloudflare Origin cert file paths. The specific request handling is **not yet verified**; no restart or DNS/TLS change has been made by this assistant.
- **Next**: read-only direct-origin vs Cloudflare checks (using correct Host/SNI), log traceback and process health, classify before any targeted reload or source modification. Keep [Issue #13](https://github.com/VoyaERP/erpdevelopers/issues/13) OPEN.

## 2026-11-14 — Third installation attempt: missing declared Python module

- Operator fast-forwarded both clean Git checkouts to `bfe30a7`, ran the existing-site installer, backed up the target site with files, passed **13/13 source-only tests**, successfully registered ERP Developers in Bench `sites/apps.txt`, and preserved `apps.txt`/`apps.json` snapshots. The installer then reached Frappe's `sync_for` and stopped with `ModuleNotFoundError: No module named 'erpdevelopers.erp_developers'`.
- Root cause confirmed from `erpdevelopers/modules.txt` (`ERP Developers`) and [Frappe v16.56.0 model/sync.py:133](https://github.com/frappe/frappe/blob/v16.56.0/frappe/model/sync.py#L133-L135): the framework imports `erpdevelopers.erp_developers`. Python package directory/`__init__.py` was absent. No source or DB entries were deleted.
- Fixed on `version-16` at **39659d46422f7c45d9bc8ec75aafb91c1c1574e3**: added module `erpdevelopers/erp_developers/__init__.py`, a source contract test that imports every module declared in `modules.txt`, and a runtime import check in the guarded existing-site installer before trying `install-app`. [GitHub Actions CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43527703007), source validation only.
- **Not yet installed / not UAT-tested**. Next operator action: fast-forward both clean Git checkouts from `bfe30a7` to `39659d4` with expected-SHA checks, run a read-only check for any leftover `Module Def` entry, rerun the guarded existing-site installer (backup first), then check homepage, static assets, HTTPS and native login. Avoid `bench new-site`, `--force`, `bench update`, dropping the DB or restarting shared services blindly.

## 2026-11-14 — Second installation attempt: missing apps.txt registration

- User fast-forwarded both source checkouts to `560b23f...`, verified the Frappe asset discovery path and passed **12/12 source tests**; new with-files backup succeeded (database, config, public and private archives).
- Frappe `bench --site erp-developers.com install-app erpdevelopers` **stopped before site installation**: `App erpdevelopers not in apps.txt`. The first `bench get-app` had synchronized Bench apps before the missing `patches.txt` marker was fixed. No evidence of Frappe or ERPNext transaction data changes.
- Confirmed against [Frappe v16.56.0 installer](https://github.com/frappe/frappe/blob/v16.56.0/frappe/installer.py#L295-L318) and [Bench 5.31 BenchApps.sync](https://github.com/frappe/bench/blob/v5.31.0/bench/bench.py#L264-L289): the Frappe app must be present in Bench-wide `sites/apps.txt`. This is not the same as a per-site installed app.
- Committed guarded resume to `version-16` **bfe30a736d7484ab7af0b38e1795a08383715139**, which validates that the only newly discovered app is `erpdevelopers`, saves `apps.txt` and `apps.json` copies to the target's private backups, then calls Bench's own `BenchApps.sync` before attempting `install-app`. [GitHub CI PASS](https://github.com/VoyaERP/erpdevelopers/actions/runs/43527371529) (static only). App is **not yet reported as installed**; operator must fast-forward source/Bench Git checkouts and rerun the existing-site installer. Do not run `bench new-site`, delete the site, or restart shared services.

## 2026-11-14 — First existing-site installation blocked at Frappe asset discovery

- User executed the guarded existing-site installer on erptest-lightnode. With-files backup succeeded (DB ~1007 KiB, site config and two archives). App cloned into `apps/erpdevelopers` at `dfbbaaa4...` but `bench get-app` stopped during its **automatic esbuild**, before the target-site `install-app`. Verified with `bench --site erp-developers.com list-apps`: only Frappe 16.56.0 and ERPNext 16.55.0; ERP Developers is **not installed**.
- Build error: `TypeError [ERR_INVALID_ARG_TYPE]: paths[0] ... undefined` in Frappe `esbuild/esbuild.js:258`. Frappe [v16.56.0 esbuild/utils.js](https://github.com/frappe/frappe/blob/v16.56.0/esbuild/utils.js#L60-L110) `get_cloned_apps` / `is_frappe_app` requires `hooks.py`, `modules.txt`, and `patches.txt`; ERP Developers lacked `patches.txt` and was omitted from esbuild public path map. Production esbuild self-terminates on errors (exit 143); root cause is missing app marker, **not** disk exhaustion. `/data` 182 GiB free (3% utilized).
- Recovery patch on `version-16`: new `erpdevelopers/patches.txt`, regression test, existing-site installer recognizes `upstream` (Bench default Git remote) as well as `origin`. Source SHA **560b23f0d7588c78848a06e18afa69c1eb2857e3**, [static GitHub CI PASSED](https://github.com/VoyaERP/erpdevelopers/actions/runs/43526841363).
- Operator next: fast-forward **both clean** copies (`~/erpdevelopers-deploy-source` and `apps/erpdevelopers`) from `dfbbaaa...` to that pinned SHA (unshallow Bench app if needed), confirm esbuild recognizes it, then rerun the same **existing-site installer**. Do NOT delete site/DB, re-run new-site installer, or re-run `bench get-app` on an existing checkout. No live UAT or success claimed yet.
- Nginx config includes hostname and Cloudflare Origin certificate paths and passed `nginx -t`, but public HTTPS and routing remain unverified.
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
| [ED-01.1 #13](https://github.com/VoyaERP/erpdevelopers/issues/13) erptest-lightnode public deployment | **Original orbit layout + EN/AR + duplicate-login fix 9a12af6 CI PASS; not live yet** | Pinned deploy, coordinated web restart, Origin EN/AR/CSS/auth UAT and shared-site checks |
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
