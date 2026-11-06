# System Architecture

## Architecture style

Start with a modular monolith. Keep modules separated by interfaces and domain boundaries. Do not introduce microservices until operational evidence justifies them.

## Logical components

1. Web frontend
2. API and authentication
3. Query intelligence
4. SQL parser/compiler
5. Database adapter registry
6. Sandbox orchestrator
7. Execution policy gateway
8. Knowledge management and search
9. Professional tools catalog
10. Learning and career module
11. Platform PostgreSQL
12. Optional Redis for cache and jobs
13. Background workers

## Main request flow

Browser -> API -> authentication/authorization -> domain module -> policy checks -> adapter or content repository -> structured response.

## Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- Monaco Editor
- React Query or equivalent server-state library
- Zod for client-side contract validation

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- SQLGlot
- Native engine drivers
- Background worker for cleanup and asynchronous tasks

## Storage

- PostgreSQL: users, workspaces, saved queries, catalog, knowledge metadata, progress, audit metadata.
- Object storage or local private volume: imported files and sandbox artifacts where applicable.
- Redis: optional queue/cache; never the sole source of durable state.
- Sandbox storage: isolated volumes or per-environment files with lifecycle control.

## Module boundaries

- `query`: generation orchestration, parsing, conversion, explanation.
- `adapters`: engine-specific capabilities.
- `sandbox`: temporary environment lifecycle.
- `execution`: policy enforcement and result handling.
- `knowledge`: articles, references, search, version applicability.
- `tools_catalog`: professional software catalog.
- `learning`: roles, skills, courses, exercises, progress.
- `connections`: external connection metadata and secret references.
- `audit`: security and execution events.

## Reliability principles

- API instances should be stateless where possible.
- Long-running operations should be asynchronous.
- Database connections must use bounded pools.
- Sandbox cleanup must be idempotent.
- Every environment has an explicit lifecycle state.
- Adapter failures must not crash the whole API.
- Use structured logs with secrets and personal data redacted.
