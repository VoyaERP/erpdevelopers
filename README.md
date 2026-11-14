# ERP Developers — Frappe 16

**Engage. Reason. Progress.**

Frappe custom app powering the ERP Developers website. This is a **public landing-page MVP**, not a completed LMS, community, job aggregation service or AI assistant.

## Compatibility

- Branch: `version-16`
- Python: 3.14+ (Frappe 16 runtime)
- Framework: Frappe 16.x (no ERPNext dependency)
- Frappe 15 is a separate compatibility target; do not install this branch on a v15 bench.

## Install on a NEW isolated development site only (not the live site)

```bash
cd /path/to/frappe-v16-bench
bench get-app --branch version-16 https://github.com/VoyaERP/erpdevelopers.git
bench new-site erpdev.localhost
bench --site erpdev.localhost install-app erpdevelopers
bench --site erpdev.localhost migrate
bench build --app erpdevelopers
bench --site erpdev.localhost list-apps
```

Run the isolated development bench with `bench start` and visit the site. Set the Host header to `erpdev.localhost` when accessing through a port or SSH tunnel. For a dedicated site, use `bench use erpdev.localhost` only on the isolated bench.

## Branding — exact selected PNG

The canonical ERP Developers brand asset is the **exact original image uploaded by the customer**, preserved byte-for-byte at `erpdevelopers/public/images/erpdevelopers-selected-logo.png` (RGBA PNG, 2048 × 682, transparent background, SHA-256 `250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d`). No regenerated artwork or reconstructed wordmark is used.

`erpdevelopers/public/images/erpdevelopers-selected-favicon.png` is an icon-only crop of the same approved image, supplied for favicon use. All active website, native login branding, and site-specific Website Settings point to these assets. The old unrelated Neural Intelligence SVG concept was removed.

## Original-design restoration and bilingual login (2026-11-14)

The original human-collaboration/orbit hero composition has been restored with **less whitespace**, the original customer-approved shield icon extracted from the same PNG, and no alternate/generated logo. Home includes six planned modules, focused vision, AI and roadmap, with compact desktop/mobile/RTL spacing.

**English + Arabic** site content is translated through `erpdevelopers/translations/ar.csv`; Frappe's native `#language-switcher` appears in the custom homepage header and uses the framework's own locale cookie. For any language without supplied product-copy translations, website copy falls back to English. The literal approved logo and its tagline are not redrawn or reworded.

Frappe 16 [login.html](https://github.com/frappe/frappe/blob/v16.56.0/frappe/www/login.html) renders its standard navbar while `show_language_picker` is enabled. The previous enhancement added another navbar, resulting in **two headers**. The scoped new CSS hides Frappe's navbar and footer **only when** the custom login header/footer have been added, while moving the **same native picker** to that header. Original split-panel styling returns as a sibling aside to the original Frappe `<main>`. No login/signup/reset/2FA form or endpoint is duplicated or replaced. A zero-dependency Node DOM test executes the login script twice and verifies idempotence and native form preservation.

`scripts/verify_frontend.sh` now checks Origin CSS bytes, exact logo/favicons, six rendered modules, English/Arabic server responses, the native login's language picker and public asset routes. This is distinct from visual browser UAT.

## Refactored website architecture

- `erpdevelopers/branding.py`: one pure-Python source of truth for identity, site targeting, uploaded PNG and favicon, and a content-hashed homepage CSS URL.
- `erpdevelopers/www/erp_developers_home.py`: route controller supplies branded assets and SEO context. Frappe v16 maps `erp-developers-home.html` to the underscore-named Python controller.
- `erpdevelopers/content.py`: immutable, typed content lists for 3 brand principles, 6 planned ecosystem capabilities, 4 AI steps and 4 roadmap milestones; no repeated card markup.
- `erpdevelopers/www/erp-developers-home.html`: Jinja page with one explicit stylesheet link in its supported `head_include` block, loop-driven sections and no duplicate Frappe navbar/footer.
- `public/css/brand.css`: homepage-only rules and scoped variables. `public/css/login.css`: independent styles restricted to the native `/login` page.
- `public/js/login_chrome.js`: decorative login header/footer only; shares a single brand-image helper and never handles credentials.
- `site_setup.py`: explicit administrator command for exactly `erp-developers.com`, idempotent and site-scoped. No after-install mutation or public API.
- `scripts/update_erptest_lightnode.sh`: guarded backup, optional pinned `EXPECTED_SHA`, source validation **before** target-site migration, then assets build and cache clearing.
- `scripts/verify_frontend.sh`: read-only direct-origin/public checks for rendered CSS fingerprint, actual stylesheet bytes, exact selected logo and favicon.

See [architecture and trust boundaries](docs/ARCHITECTURE.md) for design invariants and release gates.

## Security and scope

- No privileged API endpoints or guest-writable records.
- No direct LinkedIn scraping or unapproved third-party job APIs.
- No active AI inference or personal-data processing.
- Use Frappe's server-side permission checks for future authenticated routes.
- Community, LMS, and job connections must be introduced as independently tested modules.

## Test from a Mac via an SSH tunnel

On the Rasheed host run the isolated bench's development server bound to loopback. On the Mac:

```bash
ssh -N -L 8000:127.0.0.1:8000 YOUR_USER@RASHEED_HOST
```

Then run:

```bash
curl -I -H 'Host: erpdev.localhost' http://127.0.0.1:8000/
```

When the Frappe server uses hostname-based site selection, set an entry `127.0.0.1 erpdev.localhost` in the Mac's `/etc/hosts` and visit `http://erpdev.localhost:8000`.

Do not bind the development server to a publicly accessible interface. No production traffic or data should be involved.

## Governing Master Plan (source of truth)

The full roadmap, security/architecture gates, issue board and live status are maintained on the `main` branch to avoid duplicating plans across versioned code branches:

- [Master Implementation Plan](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/MASTER_PLAN.md)
- [Current Status](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/STATUS.md)
- [Rasheed/MacVMs Safe Audit and Mac UAT](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/LOCAL_RASHEED.md)
- [GitHub delivery issues](https://github.com/VoyaERP/erpdevelopers/issues)

Only mark release work complete after real v16 test-site evidence, security checks and UAT; an app commit by itself is not deployment proof.

## MacVMs in-place install (guarded)

Use [scripts/install_local_v16.sh](scripts/install_local_v16.sh) **only on MacVMs** after increasing disk free space to **at least 8 GiB** and verifying an off-VM backup. It refuses to write if the existing v15 Frappe branch is unexpected, target Bench/site already exists, or disk/memory requirements are not met. It uses Node 24 in its own subshell, allocates a distinct Bench, checks port conflicts, then creates only a **new v16 site**. On the documented 2026-11-13 machine state (**3.6 GiB free**) the script intentionally **stops before initialization**. The shared MariaDB server is 12.3.2 whereas Frappe's published v16 baseline is 11.8; a successful dev experiment is not production validation. Do not run this script as root, bypass guards or execute it on the v15 Bench.

    # Clone the small repo once, then run the reviewed script:
    git clone --branch version-16 --single-branch https://github.com/VoyaERP/erpdevelopers.git ~/erpdevelopers-source
    cd ~/erpdevelopers-source
    bash scripts/install_local_v16.sh

The canonical roadmap and environment state stay on `main` in `docs/MASTER_PLAN.md`, `docs/STATUS.md`, and `docs/LOCAL_RASHEED.md`.

## ERP Developers public website on erptest-lightnode (Frappe 16)

The current homepage route is **erp-developers-home** and the native Frappe 16 **/login** receives only a website header/footer, intersecting image-backed technology background, and scoped CSS; there is **no replacement authentication handler or form**. The styling follows Green Box's verified native-login approach while using the ERP Developers navy/blue/teal brand.

**Deployed test target:** erp-developers.com on erptest-lightnode; Frappe v16 app 0.1.0 installation and HTTP 200 confirmed on 2026-11-14. Full browser UAT and production acceptance are still outstanding.

**Server installation and update:** See [erptest-lightnode deployment guide](docs/ERPTEST_LIGHTNODE.md). Scripts: [new-site installer](scripts/install_erptest_lightnode.sh) and [target-site updater](scripts/update_erptest_lightnode.sh). No shared Bench restart/Nginx rewrites are automated.

The exact user-selected PNG is now used across the homepage, login and site branding. The native Frappe authentication handlers remain untouched.

### Existing-site updates (do not create the site again)

The app is already installed on `erp-developers.com` in the shared Frappe 16 Bench at `/data/frappe/frappe-bench`. The site and ERPNext database must not be recreated or overwritten.

Use the reviewed, **pinned** commit with the guarded updater; the current deployment commands and frontend checks are maintained in [docs/ERPTEST_LIGHTNODE.md](docs/ERPTEST_LIGHTNODE.md). Update the web-only Gunicorn service separately when Python/hooks change (brief shared Bench HTTP impact). Static CI is not a substitute for browser or authentication UAT.

