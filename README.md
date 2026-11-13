# ERP Developers — Frappe 16

**Engage. Reason. Progress.**

Frappe custom app powering the ERP Developers website. This is a **public landing-page MVP**, not a completed LMS, community, job aggregation service or AI assistant.

## Compatibility

- Branch: `version-16`
- Python: 3.14+ (Frappe 16 runtime)
- Framework: Frappe 16.x (no ERPNext dependency)
- Frappe 15 is a separate compatibility target; do not install this branch on a v15 bench.

## Install on an existing isolated Frappe 16 bench

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

## Branding

The selected logo is a blue/teal ascending-growth mark. This scaffold provides a CSS-only temporary brand mark to avoid pretending an exact vector of the supplied reference was produced. Place the approved original PNG or an approved vector inside `erpdevelopers/public/images/` in a separate branding commit after verifying the asset visually.

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
    git clone --branch version-16 --single-branch git@github.com:VoyaERP/erpdevelopers.git ~/erpdevelopers-source
    cd ~/erpdevelopers-source
    bash scripts/install_local_v16.sh

The canonical roadmap and environment state stay on `main` in `docs/MASTER_PLAN.md`, `docs/STATUS.md`, and `docs/LOCAL_RASHEED.md`.

## ERP Developers public website on erptest-lightnode (Frappe 16)

The current homepage route is **erp-developers-home** and the native Frappe 16 **/login** receives only a website header/footer, AI-themed decorative panel, and scoped CSS; there is **no replacement authentication handler or form**. The styling follows Green Box's verified native-login approach while using the ERP Developers navy/blue/teal brand.

**Production target:** erp-developers.com (DNS, TLS and server deployment not yet executed).

**Server installation and update:** See [erptest-lightnode deployment guide](docs/ERPTEST_LIGHTNODE.md). Scripts: [new-site installer](scripts/install_erptest_lightnode.sh) and [target-site updater](scripts/update_erptest_lightnode.sh). No shared Bench restart/Nginx rewrites are automated.

The reference logo approved in conversation is not yet an exact source-vector asset. The app includes a small branded SVG mark approximating its selected growth/shield direction, with a pending visual approval step.

### Private GitHub App access for erptest-lightnode

The supported deployment credential is now a **read-only GitHub App installation token**, retrieved on demand over HTTPS (no permanent token in Git and no server SSH Deploy Key). Set up the App under the VoyaERP organization, select only the erpdevelopers repository, and follow [docs/GITHUB_APP_DEPLOY.md](docs/GITHUB_APP_DEPLOY.md) to bootstrap the first clone securely. GitHub App creation and server deployment require operator action and are not yet verified.
