# ERP Developers: diagnosing public website 500s (Frappe 16)

These checks are **read-only** and target the existing site `erp-developers.com`.
Do not disable Frappe request validation, remove DocType permissions or patch ERPNext core.

## Symptoms and likely causes

- `/insights` reads `ERP Developers Resource`. A partial Frappe migration,
  missing `tabERP Developers Resource` table, or unmigrated columns can throw
  database exceptions during initial page rendering.
- `/lets-talk` originally imported the whole appointments/CRM API even just
  to read a site flag. Its GET controller now imports only the small flag
  helper; the POST action and rate limiter remain separate and unchanged.
- A failing web page might also indicate a template exception, stale web
  workers or another server error. **The HTTP 500 screenshot alone cannot
  establish which one occurred.** Inspect traceback before assigning blame.

## Read-only diagnosis

On `erptest-lightnode`, as the existing Bench owner:

```bash
cd /data/frappe/frappe-bench
bench --site erp-developers.com list-apps
bench --site erp-developers.com execute erpdevelopers.catalog.catalog_health
```

Expected after migration: both catalog DocTypes report
`"table_present": true` and `"missing_columns": []`. If the
Resource table or a column is missing, run the approved guarded
existing-site migration/deployment process, not a manual `ALTER TABLE`.

If errors persist after a confirmed site migration and web-only reload:

```bash
cd /data/frappe/frappe-bench
grep -n -E 'insights|lets.talk|Traceback|DatabaseError|TemplateError' \
  logs/web.error.log | tail -n 60
```

Inspect the original exception and full relevant traceback on the server,
redacting secrets, email addresses and request bodies before sharing.

## Security boundaries

- The catalog returns an empty, clearly labeled pre-publication page if its
  table/required columns have not migrated. It never queries draft records
  or grants Guest DocType access. Other database failures still raise.
- Consultation requests remain disabled unless the administrator explicitly
  enables the existing `erpdev_consultation_open` site flag. The public GET
  page performs no CRM or rate-limit operations. The POST endpoint retains
  its authentication, CSRF, IP-based throttle, input validation and permissions.
- The request is not a booking: an authorized staff member must link a real
  Frappe Calendar Event before confirming.
- Because the Bench is shared, do not restart all workers or upgrade Frappe
  as part of a public-page hotfix.

## Acceptance

Verify `/training`, `/insights`, `/lets-talk`, and `/privacy`
as Guest, EN and AR, before/after adding a published resource, after
schema migration, and with public consultation submission disabled.
Only after privacy approval should consultation submission be enabled
and tested with Guest/CRM roles.
