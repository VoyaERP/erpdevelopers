# Login logo and language - 2026-11-14

## Delivered scope

- The original approved PNG is unchanged. The single header logo now uses 260px
  width on desktop and up to 200px on mobile (180px at a 320px viewport), keeping
  the original 2048:682 proportions. Its dimensions are reserved before loading.
- A visible globe plus Arabic/English link occupies a stable 46px-high target.
  It uses the same macro and deferred language.js as the public header rather
  than another picker implementation. No delayed empty select or duplicate header.
- One site/route-scoped update_website_context hook sets base_template_path only
  for /login on erp-developers.com. The base extends native templates/base.html
  and replaces only the navbar block; native www/login.html, login.py, login.js,
  forms, SSO, LDAP, recovery, email-link and verification handling stay untouched.
- Native login.html requires show_language_picker to render its navbar. The
  context keeps that flag enabled, while the base_scripts block disables only
  window.show_language_picker before loading core scripts, preventing the old
  Guest-only AJAX picker from also running. Website Settings are not changed.
- The server fallback preserves only a bounded local redirect-to parameter and
  the selected _lang. The shared script additionally preserves current query and
  hash values on an explicit language click, including #forgot and the email-link
  state. It does not read, store, transmit or repopulate form field values; changing
  language reloads the page and unsent entries must be entered again.
- Native authentication remains unchanged. No user language, permissions, database
  schema, logo identity, slogan placement or deferred feature scope is modified.

## Validation

Unit contracts cover route/site isolation, idempotence, preserved auth context,
local redirect fallback, one shared control and script, and proportional sizing.
The existing login browser fixture now renders the actual pinned Frappe login and
web templates through the app base extension; only the outer base/utility CSS and
request/session data are fixtures. It checks four native presentation states at
320, 390, 768 and 1440px in EN/AR on Chromium and Firefox, keyboard language changes,
local redirect and recovery fragment preservation, no form-value persistence,
no-JavaScript fallback, one header and one visible original logo.

This is not a live login, SSO/LDAP/2FA, email-delivery or Frappe database test.
No authentication request is submitted by the isolated browser checks. Font
responses are stubbed. Actual font delivery and real login need live UAT.

The deployment verifier checks the actual login HTML contains one server-rendered
language link and one deferred language asset, and compares its served bytes.
Use the existing pinned backup-first runner, preserve the current release branch,
and account for the shared web-process restart. There is no automatic deployment.
