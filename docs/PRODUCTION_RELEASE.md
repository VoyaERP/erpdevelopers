# Production-v16 release and promotion

## Meaning of the production branch

`production-v16` contains a tested source baseline. It is not evidence that a server
was switched, that every business flow passed UAT, or that branch protection exists.
`version-16` remains the integration branch. `main` remains canonical governance;
never merge its older application scaffold into the running code branch.

Release flow: isolated change -> code review -> all CI checks -> integration ->
explicit stable-branch promotion -> staging/owner acceptance -> operator deployment.
Prefer reviewed fast-forward promotion; never force-push either release branch.
Configure required checks and reviewer protection in GitHub separately. This work
does not change repository permissions, protections, secrets or the default branch.

## Existing erptest-lightnode site

The existing target is `erp-developers.com` in `/data/frappe/frappe-bench`, owned by
`manakhly`. The complete runner checks hostname, non-root execution, clean checkout,
expected repository remote, installed app, exact target SHA and fast-forward ancestry.
It reuses one updater; source checks run before migration, and web restart only follows
successful update/build. The only managed service is
`frappe-bench-web:frappe-bench-frappe-web`; other sites share this HTTP process.

**No command in this document has been run on the operator's server by this refactor.**
Choose an approved full commit SHA, not a moving branch name. Keep the runner outside
the checkout. For an explicit first promotion, run the following lines one at a time,
stopping immediately on an error. Replace the SHA placeholder with the reviewed commit.

```bash
APP="/data/frappe/frappe-bench/apps/erpdevelopers"
SHA="PASTE_REVIEWED_40_CHARACTER_COMMIT"
RUNNER="$(mktemp /tmp/erpdev-deploy.XXXXXX)"
git -C "$APP" fetch upstream production-v16
git -C "$APP" show "${SHA}:scripts/deploy_erptest_lightnode.sh" > "$RUNNER"
test -s "$RUNNER" && bash -n "$RUNNER" && EXPECTED_SHA="$SHA" RELEASE_BRANCH=production-v16 ALLOW_BRANCH_SWITCH=1 bash "$RUNNER"
```

For later updates on `production-v16`, use the same procedure without
`ALLOW_BRANCH_SWITCH=1`. On integration keep `RELEASE_BRANCH=version-16`.
Unknown branches, detached HEAD, missing/invalid pins, unapproved branch switching,
divergent existing production history and production-to-integration switching fail
before branch/database mutation. No silent rollback is performed.

If tests or migration fail, preserve the backup and exact state. Do not use
`--skip-failing`, recreate the site, manually edit DocField types, reset history or
restore blindly. A transient readiness 502 is retried; sustained failure prints
web-process diagnostics and stops. Public TLS checks never use an insecure override;
`-k` remains restricted to the documented localhost origin verification.

## Validation layers

| Layer | What it proves | What it does not prove |
| --- | --- | --- |
| `scripts/check_source.sh` | Python/shell/JS checks, unit/contracts, 14 player DOM tests, Arabic compilation | Live Frappe, browser or database integration |
| Browser workflows | Actual templates/styles with isolated fixtures in Chromium/Firefox, EN/AR and narrow widths | Live fonts, CDN, YouTube playback, actual authentication or upload |
| Schema-upgrade job | Pinned native Frappe schema validation and repeated isolated MariaDB conversion | Full `bench migrate` against the production database |
| Operator deployment log | Named site, exact code, migration/build, restart/readiness and HTTP checks | Full interactive or business acceptance |
| Owner UAT/operations review | Actual editorial/private/auth flows, restore and acceptance | Nothing unless cases/results are recorded |

The source snapshot workflow archives only tracked source plus the contemporaneous
canonical `main` planning revision, with hashes. It contains no runner Git credentials
or site data. Artifact retention is seven days; retain required release evidence in
your own approved release records. CI does not deploy automatically.

## Remaining production acceptance

- Confirm the release on a staging clone, record the exact Frappe/ERPNext/DB versions,
  and test a full migration before approving a live switch.
- Publish/unpublish a real event with photos and both publication types, then check
  Guest/editor behavior and private-file rejection through native Desk and API.
- Test native login/recovery/MFA, authorized versus unauthorized private playlists,
  EN/AR first paint, mobile navigation and no cross-site visual regression.
- Test actual appointment availability and verification mail only after explicitly
  approved configuration; source presence does not enable bookings.
- Perform backup restore/recovery drill; review shared-process restart impact,
  rate limiting, monitoring, data retention, legal text and image/code license rights.
- Record Search Console/indexing checks separately; do not promise search rankings.

Entities (`bedya`/`bdanexus`/`voyatours`), operational development projects, ERPNext
Project/Task linking and owner/assignee portal remain **Deferred - do not execute**.
