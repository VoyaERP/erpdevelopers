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
