# Rasheed local — Frappe 16 UAT

1. Inspect `bench version`, `bench list-sites`, `python3 --version`, `node --version`, ports and services on Rasheed.
2. If the existing bench is version 15, **do not upgrade it in place**. Initialize a separate v16 bench, with independent config/ports and a new test database.
3. Check available Redis and socket.io ports before running a second bench. Adjust the new bench config to avoid collisions.
4. Confirm MariaDB and Redis are installed and accessible; Frappe's `bench init --frappe-branch version-16` requires its toolchain and services.
5. Run the install steps from README on the new bench; verify `bench --site erpdev.localhost list-apps`.
6. Start isolated development services and use an SSH local port forward from the Mac. Avoid publishing raw port 8000 to the internet.
7. Verify homepage, CSS, mobile breakpoints, lack of broken links, and guest access to public page.
8. Before production: TLS, backups, deploy user, CSP/security headers validated against Frappe, rate limits for interactive modules, CI, accessibility and independent security review.

Never store DB passwords, tokens, secrets, user information or backups in Git.
