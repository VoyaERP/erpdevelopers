# Deferred ideas — 2026-11-14 / أفكار مسجلة دون تنفيذ

**Status for every item below: Deferred - do not execute.**
The user explicitly said: "dont execute" and "انا بسجل افكار".
This document captures intent. It is not an approved schema, development task,
public announcement, entity registration or access grant.

## IDEA-001 — Entities

**User examples, kept as supplied:** `bedya`, `bdanexus`, `voyatours`, and others.

The future platform may represent these entities and their relationship to
projects/development. Do not assume that all are legal companies, that they have
common ownership, or that a named product is a customer or organization.
Confirm the formal/display/Arabic names, entity type, ownership, relationship,
public visibility and whether existing ERPNext Company/Customer/Supplier records
should be referenced rather than duplicated. Nothing is seeded or published now.

## IDEA-002 — Our development work as projects

Record our own development initiatives as projects in a future stage. First agree
what identifies a product versus an initiative, delivery project, release and
public portfolio story. Define ownership and lifecycle only after approval.
No actual project, task, publication or demonstration data is created by this idea.

The current `/projects` page shows explicitly reviewed `ERP Developers Publication`
records of type Project. It does not expose an operational project register.

## IDEA-003 — Native ERPNext Project and Task integration

Later link the approved project representation to native ERPNext Project and use
the existing Task/assignment facilities. Avoid a parallel task engine.
Before implementation, decide the source of truth, one-to-one or other mapping,
same-site versus cross-site integration, lifecycle/status ownership, assignment
rules, supported operations, idempotency and migration of existing records.

Any public story must remain a separately approved projection. Linking a private
Project does not authorize publishing its tasks, attachments, customer identity,
financials, internal notes or progress automatically.

## IDEA-004 — Project owner and assignee portal

A future authenticated portal should serve explicitly authorized project owners
and assignees. "Project owner" here is a business role to define, not automatically
Frappe's document creator field. Being assigned one task must not imply access to
all projects or every task within an entity.

Before coding, approve an access matrix for project visibility, task visibility,
comments, status updates, assignment/reassignment, attachments and administrative
actions. Decide the allowed user types, invitation/onboarding process, account
revocation and whether any external users can write data.

Proposed acceptance gates, not implemented functionality:
- Deny anonymous, cross-project and cross-entity access in direct routes and APIs.
- Enforce record-level permission on every read/write; UI hiding alone is insufficient.
- Keep sensitive attachments private and re-check permission when downloading.
- Define revocation behavior when assignment or ownership is removed.
- Audit allowed updates and reject unauthorized field/status changes.
- Test owner, assignee, unrelated user and administrator cases in EN/AR mobile/desktop.

## Recorded dependencies and exclusions

Suggested sequence is entity semantics -> development-project definition -> native
Project/Task mapping -> owner/assignee portal, with R2 identity/trust gates before
external access. This is a planning dependency, not authorization to begin.

The current refactor adds no entity DocType, Project/Task Link fields, assignment
batch, owner/assignee roles, portal routes, credentials or automated publications.
The new production branch is release infrastructure only. It does not activate
these ideas. Resume only after an explicit user implementation instruction.
