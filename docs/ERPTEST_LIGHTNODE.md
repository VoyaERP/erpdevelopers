# ERP Developers on erptest-lightnode

## Current target and operating boundary

The existing site is `erp-developers.com`, in `/data/frappe/frappe-bench`, operated
as `manakhly`. Frappe/ERPNext remain on v16. Never recreate or reinstall this site
as an update. Other sites share the Bench web process.

Use [PRODUCTION_RELEASE.md](PRODUCTION_RELEASE.md) for the current pinned update
and explicit `version-16` to `production-v16` procedure. The deployment runner
reuses the existing backup-first updater; it does not upgrade core, rewrite Nginx,
change DNS, enable guest APIs, or restart all Bench services.

The managed web process is `frappe-bench-web:frappe-bench-frappe-web`. Its targeted
restart briefly affects every site using that process. Coordinate this with the
operator. Creating or promoting a GitHub branch does not execute a server update.

## Evidence, not assumptions

The latest supplied operator log confirmed `c8cb0deeb4eaeb14b30d3a931f717ad1dfe2bf60`
with completed migration/build and successful origin/public/Arabic-login checks.
A transient 502 during readiness recovered in that run. There is no supplied
later deployment evidence for Projects/Team Advice or the production refactor.

A source test pass alone is not native Desk/auth/upload UAT. Keep database/files
backups, run full migration on a staging clone and record the exact versions and
acceptance results before production promotion. Do not force-reset, use
`--skip-failing`, manually alter DocField types, or restore a backup blindly.

## Read-only verification

After an approved deployment, the complete runner performs the existing
`scripts/verify_frontend.sh`, Arabic-login inspection, both publication pages in
EN/AR, the minimal footer and served asset byte checks. It does not verify actual
mail delivery, user authentication, YouTube availability or a backup restore.

## Historical notes

[The unchanged earlier host guide](history/ERPTEST_LIGHTNODE_20261114.md) retains
installation and failure-recovery evidence. Its older commit pins and commands
are historical references, not the current release procedure. The new-site and
MacVMs installers are only for their separately approved isolated environments.
