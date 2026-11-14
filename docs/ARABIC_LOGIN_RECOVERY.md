# Arabic native login and complete deployment runner

The supplied terminal input is visibly truncated/mixed around a Python expression
and a closing parenthesis; the `>` prompt is the shell asking for more input, not
a migration status. Cancel that pending input with Ctrl+C. Do not finish it by
adding guessed quotes or brackets. No successful deployment of the event-photo
release is inferred from that partial input.

The screenshot contains English Sign In, welcome text and Forgot password inside
an Arabic page. Exact native v16 login message IDs are now supplied in locale/ar.po,
including recovery, email-link, signup-disabled, validation and OTP messages.
Existing user Translation records are not overwritten. Runtime Frappe translations
continue to own all form text. No CSS-concealed/replacement headings, duplicated
login template, login JS, auth-route override or change to sign-up policy is added.

The decorative tagline used direction:ltr with an absolute logical inset, placing
it over the form when the grid was RTL. Both story and tagline now occupy the same
grid cell; the form stays in the other column or next mobile row. The Arabic
story/tagline use Tajawal, password text remains LTR with space for the native eye
icon, and long native option buttons wrap. Brand artwork and the approved English
logo are unchanged. An Arabic logo/name requires the owner's approval first.

scripts/deploy_erptest_lightnode.sh is a complete Bash runner saved outside the
checkout. It verifies host, non-root execution, paths, branch, clean checkout,
remote, exact SHA and fast-forward ancestry. It stages and calls the existing
backup/test/migration updater, then restarts only the specified web process,
checks Frappe pong with bounded retries, runs the existing frontend verifier, and
checks the actual served Arabic login section for remaining English labels.
This may briefly affect other sites sharing the web process. No automatic
rollback, repeated restart, broad package update or private-data exposure occurs.

Tests compile the real PO catalog and inspect actual native Frappe v16.56.0 login
sources with Git-blob pins. Browser fixtures render those native forms in EN/AR at
desktop/mobile widths in Chromium/Firefox. The outer shell and utility CSS are
fixtures; font delivery and live auth/database/SSO/OTP are not tested. No credentials
are submitted. The server-side verifier catches stale/overridden translations after
real deployment and does not silently replace administrator translations.
