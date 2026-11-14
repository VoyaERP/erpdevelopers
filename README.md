# ERP Developers

**ERP = Engage. Reason. Progress.** Developers is the secondary brand signature.

A vendor-neutral technology ecosystem, starting with a bilingual public website
on Frappe/ERPNext v16. This `main` branch is the governance entry point, not the
application deployment branch.

## Source and planning

| Branch / document | Purpose |
| --- | --- |
| [production-v16](https://github.com/VoyaERP/erpdevelopers/tree/production-v16) | Reviewed, commit-pinned application release source; not proof of deployment |
| [version-16](https://github.com/VoyaERP/erpdevelopers/tree/version-16) | Ongoing integration and development |
| [Application README](https://github.com/VoyaERP/erpdevelopers/blob/production-v16/README.md) | Current capabilities, editorial operation, security and validation |
| [Master Plan](docs/MASTER_PLAN.md) | Release scope, dependencies, acceptance gates and engineering conventions |
| [Execution Status](docs/STATUS.md) | Observed source/CI/deployment evidence, separated from pending UAT |
| [Deferred Ideas](docs/DEFERRED_IDEAS.md) | Recorded ideas explicitly excluded from implementation |
| [Decision Register](docs/DECISIONS.md) | Accepted choices and open decisions |
| [Production Procedure](https://github.com/VoyaERP/erpdevelopers/blob/production-v16/docs/PRODUCTION_RELEASE.md) | Explicit promotion, backup-first deployment and remaining release gates |
| [GitHub Issues](https://github.com/VoyaERP/erpdevelopers/issues) | Existing workstream tracking; issue closure is not deployment evidence |

The current application source includes Home/Vision, Training, Insights, Events
with photos, public Projects, Team Advice, ERP development guides, native staff
login and opt-in ERPNext appointment booking. It is not a complete LMS, member
community, jobs aggregator, AI system or operational project portal.

The last supplied successful operator deployment is `c8cb0de` on
`erp-developers.com`. Projects/Team Advice and the new refactor have source/CI
status separately recorded in [STATUS.md](docs/STATUS.md). Creating the production
branch does not switch the server, configure branch protection or approve launch.

## Ideas recorded, not executed

Entities named `bedya`, `bdanexus`, `voyatours` and others; our own development as
projects; later native ERPNext Project/Task links and assignments; and a project
owner/assignee portal are **Deferred - do not execute**. No entity records,
integration fields, task automation or portal access were created. The existing
public Projects showcase remains separate from operational project delivery.

Earlier plan/status history is linked from the current documents. Keep v15
workloads untouched. Do not install this branch's old scaffold onto a live Bench.
