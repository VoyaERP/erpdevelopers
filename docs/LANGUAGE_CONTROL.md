# Visible website language control - 2026-11-14

> Login now shares the visible control; see [Login logo and language](LOGIN_LOGO_LANGUAGE.md).

## Root cause and change

The shared header used an empty hidden `#language-switcher` select. Frappe
v16.56.0 `website.js:show_language_picker` populates it only for Guest sessions
and after the language-list AJAX call succeeds. Signed-in visitors therefore
have no visible control; a failed/blocked call also leaves Guests without it.
The earlier fixed-width slot prevented layout movement but did not fix visibility.

The custom public header now renders one visible globe/text link beside Team
Login. English pages offer العربية; Arabic pages offer English. Both labels use
fixed existing header tracks and a 44px target. No injected header, cloned menu,
loading animation or second stylesheet is added. The approved logo is unchanged.

The link uses Frappe's native `_lang` request parameter, which is resolved before
both the Guest cookie and a signed-in user's account language. The server copies
only known bounded directory filters to its no-JavaScript fallback link.
A single, deferred, content-fingerprinted language.js enhances this link to retain
current query/fragment values, writes the native preferred_language cookie on an
explicit language click, and carries _lang through known public-page navigation
and GET filters. It does not intercept external, Desk, API, file or download links,
modify user profiles, replace authentication or access private data.

Only contexts using the custom header set show_language_picker=0, so Frappe's
Guest-only handler is not also attached. Native login, Website Settings and Desk
keep their existing behavior. The script is loaded once per custom public page,
not through a global web_include_js hook, and repeated execution is idempotent.
With JavaScript disabled the visible link still switches the current page and
preserves server-known filters; cookie persistence, fragment preservation and
subsequent navigation enhancement require JavaScript.

## Validation boundaries

Source checks cover allowed query projection, request-free contexts, signed-in
and Guest context equivalence, single script inclusion and untouched native login.
The navigation browser suite checks the actual shared templates/CSS/script at
320-1440px, EN/AR, Chromium/Firefox. It blocks the language API, tests missing and
disabled JavaScript, repeated initialization, filter/fragment preservation,
keyboard access, refresh, sticky positioning and unrelated/private destinations.
Session identities and the Frappe outer shell are fixtures; fonts are stubbed.
This is not a live authentication, font-network or production deployment test.

No new DocTypes, permissions, project/entity/portal features or scheduled jobs.
Deploy using the existing pinned backup-first runner without changing the server's
release branch implicitly. Afterwards test Guest and signed-in website navigation,
EN/AR mobile/desktop, directory filters and the native login page on the real site.
