# Roadmap and Recommended Build Order

Estimates are planning ranges for a focused small team and should be revised after technical spikes.

## Phase 0 — Foundation
- Confirm repo and contribution model.
- Establish CI, lint, tests, environment management.
- Create Next.js and FastAPI skeleton.
- Create PostgreSQL schema and migrations.
- Implement authentication and language preferences.
- Establish design system.

## Phase 1 — Query Studio foundation
- Monaco editor.
- Manual SQL workflow.
- SQLGlot integration.
- PostgreSQL/MySQL/SQLite dialect selection.
- Parse and conversion endpoints.
- Query library.
- AI provider abstraction.
- Query explanation with explicit review.

## Phase 2 — SQLite Database Lab
- Sandbox lifecycle API.
- Isolated SQLite worker.
- Resource and result limits.
- Templates and sample datasets.
- Expiration and cleanup worker.
- Reset and export.

## Phase 3 — Knowledge Center and Professional Tools
- Content schema and publishing workflow.
- Article pages and search.
- Engine/version filters.
- Tool catalog and licensing metadata.
- Monitoring and observability catalog.
- English and Indonesian content workflow.

## Phase 4 — PostgreSQL and MySQL sandboxes
- Worker pools or isolated containers.
- Engine-specific drivers.
- Metadata discovery.
- Test datasets.
- Secure query gateway.
- Quotas and cleanup.

## Phase 5 — Professional database integrations
- External database connections.
- Oracle, SQL Server, Db2 adapter foundations.
- Explain-plan integrations.
- DBA workflows and diagnostics.
- Local connection agent design and implementation.

## Phase 6 — Ecosystem expansion
- NoSQL and warehouse support.
- Community contributions.
- Advanced learning paths.
- Team workspaces.
- Optional monitoring integrations.

## Recommended first release

Ship a small but coherent product:
- SQL editor
- SQLite sandbox
- query conversion
- basic AI provider interface
- knowledge article system
- professional tools directory
- English/Indonesian UI
- Docker self-hosting

Do not delay the first usable release until every database engine is supported.
