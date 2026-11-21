# ERP Developers — current release and promotion procedure

**Updated: 2026-11-21.** This replaces the former `production-v16` procedure.
The [four-branch policy](https://github.com/VoyaERP/erpdevelopers/blob/main/docs/BRANCH_STRATEGY.md) is authoritative; older host
notes are historical and must not be applied to another VM without an audit.

## Branch roles

- `main`: GitHub default branch with current reviewed v16 application and governance.
- `dev`: v16 integration branch.
- `version-16`: pinned v16 deploy source.
- `version-15`: independent v15 deploy source and compatibility tests.

Frappe 15 and 16 use different `pyproject.toml` dependency ranges and hook
registration. **Never switch a site between major versions by changing Git branch.**

## Existing Azure Frappe 16 VM

- Host: `erpdevelopers`; site: `erp-developers.com`.
- Bench owner: `frappe`; Bench: `/home/frappe/frappe-bench`.
- Git remote: `upstream`, `git@github.com:VoyaERP/erpdevelopers.git`.
- Read-only deploy key: `/home/frappe/.ssh/github_erpdevelopers`.
- Services: systemd, not the historical erptest-lightnode Supervisor services.
- Source branch: `version-16` with an exact, operator-reviewed full SHA.

The scripts named `*_erptest_lightnode.sh` are **legacy, host-specific** and
must not run on this Azure VM. They are retained for older installations and
refuse unrelated hostnames. Do not rewrite those host constraints to bypass checks.

### Deployment checklist (operator-controlled)

1. Verify all required source, browser navigation, publications, schema-upgrade
   and Arabic/English CI checks at the **exact target commit**. A pending or
   failed run is not a passed release gate.
2. Confirm installed Frappe/ERPNext major version, clean app checkout, enough
   disk space, database/Redis health, backups with files, and a tested rollback
   procedure. Verify that `version-16` is a descendant of the deployed SHA.
3. Fetch `version-16` with the existing deploy key as `frappe`, verify
   `FETCH_HEAD` equals the approved SHA, and switch using a fast-forward-only
   update. No `reset --hard`, `--force`, or reinstall.
4. Execute the application's source checks. Migrate the site only when a
   schema/hook change requires it and after inspecting the migration impact.
   Build `erpdevelopers` assets, clear site and website caches.
5. Restart the exact Frappe **web** systemd unit with the operator's sudo
   privileges after a successful build. Clear cache alone does not reload
   Python modules in an existing web process.
6. Verify `/api/method/ping`, the home page and critical routes at the Azure
   loopback origin using `curl --resolve erp-developers.com:443:127.0.0.1`.
   Compare the `brand.css?v=<sha256-prefix>` fingerprint with the deployed
   file and compare the response bytes to the served CSS.
7. Repeat checks against the public domain separately. If public and origin
   differ, investigate DNS/Cloudflare cache before editing CSS again.
8. Confirm English, Arabic RTL, desktop/tablet/mobile navigation, Team Login,
   language preservation and owner visual acceptance. Record the site, SHA,
   CI links, service status, browser evidence, and rollback reference.

The last supplied Azure operator evidence was an HTTP 200 and successful asset
build on the earlier release candidate `4ee493fa`. That is **not** evidence
that newer commits have been installed or that the public browser sees Azure.

## Frappe 15 acceptance

Build and migrate `version-15` only on a separate v15-compatible Bench/site;
validate native v15 login/Desk branding and the publication, event and playlist
roles there. CI source/browser fixtures are not a replacement for live v15 UAT.
Keep v15 settings and hooks separate from v16.

## Four-branch cleanup

Before removing any obsolete GitHub branch, switch all live checkouts to one
of the four maintained branches. Archive old heads as **remote tags** pointing
to their exact Git commit IDs, verify the archives, and then delete the old
remote branch refs using exact expected-SHA leases. Divergent old feature
commits must remain recoverable from tags even when not merged.

Do not run Git branch deletion from the Azure read-only deploy key. Use a
write-authorized workstation clone and review PRs and branch-protection rules.
If any verification fails, stop without deleting the unverified heads.
