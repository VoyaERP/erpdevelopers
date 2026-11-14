# Training player and Arabic typography recovery - 2026-11-14

## Evidence and scope

The operator's 05:44 log fast-forwarded to 0cc8b56 but stopped before migration,
build and cache clearing. unittest.mock introspected the unbound frappe.session
proxy while constructing a mock. The isolated test now substitutes a complete
ModuleType in sys.modules instead of touching that proxy. Production session
checks are unchanged.

Watch here previously was an external anchor. Initialization failures deliberately
fell through to YouTube; a newly required loading-status element could also
abort initialization against stale markup. Watch here is now a disabled-until-bound
button with no external URL. The separately labelled Open on YouTube link is the
only external navigation. The loading message is optional and outside the frame,
so it cannot cover the player indefinitely. Native close/Escape stops playback
and returns focus. The script is loaded once, deferred in the page head, with
Cloudflare Rocket Loader exclusion. No global script or second player is added.

Tajawal is confirmed in VoyaERP/greenbox.com.eg, production,
greenbox/public/css/site.css. Arabic-only typography reuses the family and
400/500/700/800 weights through Google Fonts, with scoped heading, reading and
form styles. English and Desk are not restyled; no font binaries are distributed.

The obsolete Desk script that forcibly unpublished private collections is removed.
Published and Visibility remain independent. Guests still get Public + Published
only; private data still requires Frappe authentication and permission-filtered
reads. Existing unpublished private records are NOT automatically published.

## Validation and deployment

CI runs the full Python contracts and 14 real-script Node cases. A separate
Chromium/Firefox test renders the actual Training template and app styles in an
isolated Frappe-shell fixture: EN/AR at desktop/mobile sizes, no YouTube request
before click, a local modal without a new tab, explicit external-link navigation,
Escape cleanup, Arabic font-family rules and missing-script behavior. Font and
YouTube responses are stubbed; this does not verify real video playback, font
network availability, live CSP or the Frappe database.

Use the pinned updater staged from the chosen commit outside the checkout. It
backs up the existing site and runs both Python and Node tests before migration.
Then reload only the confirmed web service, clear the browser cache and test a
real public playlist as Guest and private access with authorized/unauthorized
users. Do not reinstall the site, disable tests or modify Frappe core. YouTube's
own private-video and embedding restrictions remain independent of Frappe access.
