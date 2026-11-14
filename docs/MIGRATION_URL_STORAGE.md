# Recovery: existing Event table rejects 1500-character Data fields

## Observed state

The 2026-11-14 12:10 deployment log backed up the site and fast-forwarded the
checkout from c1c08ca to 99156e9. All 156 Python and 14 Node tests passed. Migration
then stopped on ERP Developers Event with `Length of event_url should be between
1 and 1000`. Build, web restart and frontend verification were not reached.
This was a release schema defect, not an invalid URL entered by the operator.
Do not describe this run as deployed or assume a complete database rollback.

## Cause and correction

Both event_url and source_url were Data fields with length=1500. Frappe's
DBTable.validate enforces 1..1000 on varchar-backed fields for existing tables.
The early return for new tables explains why initial creation alone cannot prove
that a subsequent update will work. This behavior is confirmed in v16.56.0:
frappe/database/schema.py and frappe/database/mariadb/mysqlclient.py.

Both fields now use native Small Text (MariaDB TEXT) without a varchar length or
URL Data-control option. Existing server-side event URL validation still applies,
including HTTPS normalization, unsafe/private-link restrictions and the maximum
1500-character normalized URL. Required/optional behavior, names, permissions,
publication rules and public rendering are unchanged. No URL slicing, SQL data
rewrite, truncation, Frappe core change, permission override or manual alteration
of tabDocField is introduced. Field layout stays in its existing two-column group.

## Regression coverage

Offline tests scan every application DocType for the existing-table varchar
limit, valid field order and child-table targets. Boundary tests retain 1001..1500
character links and reject over-limit/unsafe inputs. These run in the existing
pre-migration unittest discovery as well as CI.

A separate CI-only MariaDB fixture downloads Git-blob-pinned Frappe v16.56.0
sources and executes the native DBTable.validate, type-map and SQL-type-definition
functions against synthetic existing-table metadata. It reproduces the old
failure independently for both URL fields, checks all app schemas, and verifies
that converting synthetic VARCHAR(1500) URL columns to TEXT preserves stored
values and NULLs on two passes. This is a focused schema/SQL upgrade regression,
not a full Frappe install, bench migrate or production database test. It never
connects to the user's server or uses production credentials.

## Recovery

Keep the successful backup from 2026-11-14 12:10. Fetch the corrected version-16
release and use the existing pinned scripts/deploy_erptest_lightnode.sh saved
outside the checkout. It reuses the backup-first updater and retries the full
migration before compiling assets/translations or restarting the specified web
process. Do not use --skip-failing, bypass schema checks, drop tables, manually
edit database field definitions or restore a backup solely for this error.

The previous event-photo and Arabic-login changes remain included. An Arabic
logo is still awaiting explicit name approval and is not changed by this fix.
