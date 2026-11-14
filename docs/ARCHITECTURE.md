# ERP Developers — Frappe 16 architecture and refactor contracts

## Product and compatibility boundary

The `version-16` branch is a **website-only MVP**, not a deployed community/LMS/careers/marketplace/AI platform. It runs as an installed Frappe 16 app within an existing shared Bench; ERPNext remains an independently managed app. No new DocType, API endpoint, guest-writable record, background job, permission override or login endpoint is introduced by the website refactor.

## Responsibilities (single-purpose modules)

| File | Responsibility |
|---|---|
| `erpdevelopers/branding.py` | Canonical approved logo/favicons, exactly one allowed site, homepage route, pure settings mapping and content-hashed CSS URL |
| `erpdevelopers/content.py` | Immutable, typed public site values, planned capabilities, AI steps and roadmap content |
| `erpdevelopers/translations/ar.csv` | Arabic equivalents of homepage strings; Frappe's built-in locale resolver and language picker are authoritative |
| `erpdevelopers/site_setup.py` | Explicit, idempotent CLI-only changes to the approved site's Website Settings; never an install hook |
| `erpdevelopers/www/erp_developers_home.py` | Route controller, SEO context and safe asset URLs supplied to Jinja |
| `erpdevelopers/www/erp-developers-home.html` | Public semantic page and one linked stylesheet through Frappe's supported head block |
| `erpdevelopers/public/css/brand.css` | Scoped homepage style variables, layout and responsive rules |
| `erpdevelopers/public/css/login.css` | First-paint CSS-only styling for the Frappe native login, header and language picker; no DOM mutations |
| `scripts/update_erptest_lightnode.sh` | Safe backup, pinned source update, pre-migration tests and target-site operations |
| `scripts/verify_frontend.sh` | Non-mutating HTTP+asset consistency smoke tests, direct-origin and public |

## Original visual direction and Frappe multilingual behavior

The approved original hero uses the open background and orbit illustration, with a compact two-column composition instead of excessive whitespace. The orbit center displays the **icon crop from the customer's approved PNG**, never a placeholder or a replacement wordmark. The same unmodified full PNG stays in header, footer and login.

The homepage header contains the native Frappe `#language-switcher` markup. Frappe's `frappe.website.show_language_picker()` populates the select and persists `preferred_language` for Guest users; server-side `{{ _("...") }}` and `{{ _(item.title) }}` use `translations/ar.csv`. Logged-in users' language is governed by their Frappe user preferences. Supported custom site-copy localizations for this release: **English and Arabic**. Browser UAT must confirm RTL and keyboard navigation.

Frappe v16 `www/login.html` already emits a native navbar (including `#language-switcher`) and the native form. The earlier DOM enhancement inserted a *second* navbar and story after load, causing a visible first-paint flash and unreliable logo. That JavaScript hook and file have now been removed. Frappe's original navbar and login form are laid out **immediately by CSS** from `web_include_css`. CSS pseudo-elements provide the decorative, bilingual story beside the unchanged `<main>` without modifying form structure, sign-in/recovery/signup views or server-side authentication.

## Login destination and user-type boundaries

The site intentionally sets `Website Settings.home_page = erp-developers-home` for the **public** community homepage. Frappe v16's native login handler uses the `redirect-to` query when supplied, otherwise `data.home_page`. The two current site links labeled `Desk sign in` use `branding.DESK_SIGNIN_URL = "/login?redirect-to=/desk"` and bind it through the homepage controller. This is a deliberate **System User** entry point: Frappe continues to enforce native Desk permissions. Do not rewrite `frappe.auth`, global `get_default_path`, `Website Settings.home_page` or a website-member user's default route just to redirect staff. A future community-member area will require its own authorized entry/navigation.

The guarded updater has no dependency on the removed `login_chrome.js` and asserts the obsolete script and DOM test are absent. Its current source checks must succeed **before** `bench migrate`; if any step stops, treat the site as partially updated, inspect before resuming, and never run a site installer or reset DB.

## Styling and caching

Frappe's `www/erp-developers-home.html` controller is `www/erp_developers_home.py`: Frappe v16 converts hyphens to underscores when resolving the Python file. The controller binds `brand_logo_url` and `homepage_css_url`; Jinja escapes both. The CSS URL contains a 16-hex-character SHA-256 prefix computed **from the actual `brand.css` bytes**, cached for one process. On deploy, new Gunicorn workers must be loaded so their cache uses the new stylesheet hash. The independently served CSS must match the source file byte-for-byte. Homepage CSS is not inserted into global `web_include_css`; only the **content-hashed native-login stylesheet** is added to the website head before any HTML form rendering.

CSS custom properties are scoped under `.ed-site`, not `:root`, to avoid modifying Frappe Desk or unrelated website styles. Native login styles are gated only by Frappe's server-rendered `body[data-path="login"]` (or `/login`) selector; no client-applied enhancement class is necessary. Accessibility: semantic headings, focus outlines and focus-only skip link. Visual acceptance still requires real browsers and EN/AR/RTL inspection.

## Branding fidelity

**Never redraw, retrace, generate or substitute a logo.** The user-approved original at `erpdevelopers/public/images/erpdevelopers-selected-logo.png` is byte-identical to the uploaded PNG (SHA-256 `250df1886e13229aa0e260949f66cb91a627b220a03c36b5c1d4ede1ad06d95d`). The icon-only favicon is cropped from the same source. All homepage image references are supplied by the Python brand module. Frappe's own navbar uses the site-specific `Website Settings.brand_html` and `banner_image` values built from the same canonical `LOGO_URL`; `app_logo` also points to that file. No JavaScript changes or replaces the logo at runtime. No hidden user uploads or remote fonts are embedded.

## Security invariants

1. `site_setup.configure_website` checks `frappe.local.site` *before reading or mutating* any database state, does not use a whitelisted RPC endpoint, and saves/commits only when values differ.
2. Login remains Frappe-owned (password reset, session cookies, 2FA, social auth, throttling and permissions). **No custom login JavaScript executes**, and no form, login endpoint or template is overridden.
3. No secrets, backups, private keys or site configuration files belong in Git. No unauthorized job scraping or external AI API calls.
4. Deployment works on `erp-developers.com` **only**. Remote URL, branch, source SHA, app status, backup and fast-forward are guarded; source tests run before migration.
5. Restarting shared Gunicorn is a separately reviewed operator action. The app script does not restart Redis, Nginx, workers or other Bench services.

## Validation and rollback

CI checks Python 3.14 syntax, Bash syntax and behavior tests for branding, the CSS-first login contract and site setup. Production claims require a real test site, public URL and browser UAT. The smoke test also checks that six data-driven ecosystem cards render (not merely that an HTTP 200 page is returned). After an approved update, run `scripts/verify_frontend.sh` to check CSS URL, Origin bytes, correct logo and public 200 GETs, then test interactive login and multiple viewport widths.

On failure, retain the target site's `backup --with-files` archives and the previous recorded commit. **Do not automatically hard-reset or drop databases.** Diagnose migration/source/runtime state first; roll back the Git checkout only via a reviewed plan that accounts for schema changes. The HTTP smoke script is read-only.

## Future extension approach

Developer Hub, community, LMS, recruitment and marketplace must use separate feature modules with explicit permissions, data contracts, migration/tests, and audit and privacy design. Maintain one shared identity surface rather than duplicating native Frappe authentication.
