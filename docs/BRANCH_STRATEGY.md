# ERP Developers — Four-branch policy (2026-11-21)

This is the current branch policy, superseding any older branch-layout descriptions in governance history.

| Branch | Role | Supported platform |
| --- | --- | --- |
| `main` | Reviewed default branch containing deployable v16 application source **and** retained governance documents | Frappe/ERPNext 16 |
| `dev` | Integration and validation of the next v16 changes | Frappe/ERPNext 16 |
| `version-16` | Maintained v16 release source for pinned deployments | Frappe/ERPNext 16 |
| `version-15` | Maintained, independently validated v15 compatibility line | Frappe/ERPNext 15 |

Do not install `main`, `dev`, or `version-16` on Frappe 15. Do not merge the v16-only hooks, Python minimum, or ERPNext dependency versions into `version-15`.

The shared public header is the single Jinja include `erpdevelopers/templates/includes/erpdevelopers_nav.html`; its styles live in `erpdevelopers/public/css/brand.css`, and its progressive locale enhancement lives in `erpdevelopers/public/js/language.js`. No parallel navigation scripts or second header CSS file.

Shared public asset fingerprinting is centralized in `erpdevelopers/branding.py`. Stylesheets use content-hashed URLs to avoid stale browser assets. Existing backend catalog/media validation and native authentication remain intact.

**Gates before promotion:** run `bash scripts/check_source.sh`, browser navigation checks, schema-upgrade CI, relevant Frappe 15/16 install/upgrade verification, Arabic/English RTL/mobile UAT, and recorded restore procedures. GitHub source commits and HTTP 200 are not proof of visual UAT.

**Deployment:** use explicit commit pins; update the checked-out Azure branch to `version-16` before retiring previous release branch names. Restart the Frappe web service after application-code changes, verify that the CSS link fingerprint matches source, and compare Azure origin versus public DNS/Cloudflare.

**Legacy branch removal:** preserve the head of every outgoing branch in a remote `archive/pre-four-branch-20261121/<old-branch>` tag, verify tags remotely, check all currently deployed checkouts, and only then remove superseded remote heads using write-authorized Git credentials. Never force-push or remove the four maintained branches.
