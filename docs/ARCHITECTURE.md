# ERP Developers — Frappe 16 architecture and refactor contracts

## Product and compatibility boundary

The `version-16` branch is a **website-only MVP**, not a deployed community/LMS/careers/marketplace/AI platform. It runs as an installed Frappe 16 app within an existing shared Bench; ERPNext remains an independently managed app. No new DocType, API endpoint, guest-writable record, background job, permission override or login endpoint is introduced by the website refactor.

## Responsibilities (single-purpose modules)

| File | Responsibility |
|---|---|
| `erpdevelopers/branding.py` | Canonical approved logo/favicons, exactly one allowed site, homepage route, pure settings mapping and content-hashed CSS URL |
| `erpdevelopers/site_setup.py` | Explicit, idempotent CLI-only changes to the approved site's Website Settings; never an install hook |
| `erpdevelopers/www/erp_developers_home.py` | Route controller, SEO context and safe asset URLs supplied to Jinja |
| `erpdevelopers/www/erp-developers-home.html` | Public semantic page and one linked stylesheet through Frappe's supported head block |
| `erpdevelopers/public/css/brand.css` | Scoped homepage style variables, layout and responsive rules |
| `erpdevelopers/public/css/login.css` | Login-page scoped visuals, no auth implementation |
| `erpdevelopers/public/js/login_chrome.js` | Decorative header/footer for native Frappe login, locale-aware copy and official language picker |
| `scripts/update_erptest_lightnode.sh` | Safe backup, pinned source update, pre-migration tests and target-site operations |
| `scripts/verify_frontend.sh` | Non-mutating HTTP+asset consistency smoke tests, direct-origin and public |

## Styling and caching

Frappe's `www/erp-developers-home.html` controller is `www/erp_developers_home.py`: Frappe v16 converts hyphens to underscores when resolving the Python file. The controller binds `brand_logo_url` and `homepage_css_url`; Jinja escapes both. The CSS URL contains a 16-hex-character SHA-256 prefix computed **from the actual `brand.css` bytes**, cached for one process. On deploy, new Gunicorn workers must be loaded so their cache uses the new stylesheet hash. The independently served CSS must match the source file byte-for-byte. Homepage CSS is not inserted into global `web_include_css`; only the native-login stylesheet remains there.

CSS custom properties are scoped under `.ed-site`, not `:root`, to avoid modifying Frappe Desk or unrelated website styles. Native login styles are gated by the Frappe `data-path` and `.ed-login-website` class. Accessibility: semantic headings, focus outlines and focus-only skip link. Visual acceptance still requires real browsers and EN/AR/RTL inspection.

## Branding fidelity

**Never redraw, retrace, generate or substitute a logo.** The user-approved original at `erpdevelopers/public/images/erpdevelopers-selected-logo.png` is byte-identical to the uploaded PNG (SHA-256 `250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d`). The icon-only favicon is cropped from the same source. All homepage image references are supplied by the Python brand module. The browser login chrome includes a fixed same-site fallback to that exact image; tests require the fallback path to match the canonical Python path. No hidden user uploads or remote fonts are embedded.

## Security invariants

1. `site_setup.configure_website` checks `frappe.local.site` *before reading or mutating* any database state, does not use a whitelisted RPC endpoint, and saves/commits only when values differ.
2. Login remains Frappe-owned (password reset, session cookies, 2FA, social auth, throttling and permissions). The JS script never intercepts login, creates inputs, posts credentials or modifies native form fields.
3. No secrets, backups, private keys or site configuration files belong in Git. No unauthorized job scraping or external AI API calls.
4. Deployment works on `erp-developers.com` **only**. Remote URL, branch, source SHA, app status, backup and fast-forward are guarded; source tests run before migration.
5. Restarting shared Gunicorn is a separately reviewed operator action. The app script does not restart Redis, Nginx, workers or other Bench services.

## Validation and rollback

CI checks Python 3.14 syntax, JS syntax (Node 24), Bash syntax and behavior tests for branding and site setup. Production claims require a real test site, public URL and browser UAT. After an approved update, run `scripts/verify_frontend.sh` to check CSS URL, Origin bytes, correct logo and public 200 GETs, then test interactive login and multiple viewport widths.

On failure, retain the target site's `backup --with-files` archives and the previous recorded commit. **Do not automatically hard-reset or drop databases.** Diagnose migration/source/runtime state first; roll back the Git checkout only via a reviewed plan that accounts for schema changes. The HTTP smoke script is read-only.

## Future extension approach

Developer Hub, community, LMS, recruitment and marketplace must use separate feature modules with explicit permissions, data contracts, migration/tests, and audit and privacy design. Maintain one shared identity surface rather than duplicating native Frappe authentication.
