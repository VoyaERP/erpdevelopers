# Application-wide refactor audit - 2026-11-14

Baseline: `3cddab9beb2d4b49427458befc1421bf7e8bcf71` (source, not confirmed deployment).
User scope: refactor current app, production branch and documentation; record new
entity/project/task/portal ideas without implementing them.

| Area reviewed | Decision / change |
| --- | --- |
| Brand, hooks, site setup, SEO, guides | Preserve exact logo, native authentication, explicit site guard, fingerprinted assets and non-deceptive metadata; rewrite stale architecture/README claims |
| Playlist/resource catalogs | Share schema probing and public/private playlist URL projection; retain compatibility imports and support plain dictionary resource/Web Page rows |
| Events and publications | Share page parsing while retaining different caps; move publication normalization to pure rules and editorial topics to neutral taxonomy |
| Public image security | Extract one shared native File/path/image-byte boundary; event galleries retain parent limits and publication covers reuse it directly |
| Schemas and URL normalization | No DocType/schema changes; retain Small Text fix, 1500-character URL limit and validation tests |
| Guest APIs and legacy intake | Preserve endpoints, feature gates, native ERPNext booking and permission checks; no new scheduling, CRM or auth engine |
| Frontend styles/scripts | Consolidate cascade-equivalent playlist overrides and remove dead external-link/loading-overlay selectors; retain modal, navigation and mobile behavior |
| Deployment | Shared pure branch policy, exact pins, explicit one-way production switch, existing backup-first updater and shared source-check runner |
| CI | Apply existing validation to refactor and production branches; check every app JS file, all shell scripts and compiled Arabic catalog |
| Documentation | Replace accumulated README recovery notes with current capabilities and operating guidance; canonical roadmap/status remain on main |

Compatibility aliases point at the same function objects, not duplicated logic.
Existing externally referenced module paths and native DocTypes remain intact.
No operational entity/project/task/portal feature, demo data, publication, credentials,
privacy setting, source-provider connection or server deployment is added.

## Evidence and limits

Local baseline: 185 Python tests passed before changes. Refactored local source:
199 Python tests and 14 Node tests passed, with shell/JavaScript syntax and Arabic
catalog compilation. The local interpreter is Python 3.13; declared runtime remains
3.14 and the CI Python 3.14 run is required before promotion. Browser/schema CI and
live Bench acceptance are separate gates; do not infer a live deployment from Git.

Prior operator evidence ended at `c8cb0de` with successful HTTP and Arabic-login
verification. The earlier event URL schema failure is retained as a regression;
source-only tests had missed an existing-table constraint. A rollback or restore is
not performed automatically by this refactor.

See [PRODUCTION_RELEASE.md](PRODUCTION_RELEASE.md) for the pending acceptance gates.
