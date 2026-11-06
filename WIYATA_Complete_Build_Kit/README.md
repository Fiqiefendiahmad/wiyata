# WIYATA — Your Database Learning Center

**WIYATA** is a free, open-source-oriented Universal Database Learning, Development, and Professional Knowledge Platform.

**Brand promise:** Learn, build, explore, and master database technologies — all in one place.

This package is a build-ready product and engineering blueprint. It includes product requirements, architecture, UX direction, database and API contracts, sandbox security requirements, Knowledge Center structure, professional application catalog, monitoring/observability catalog, deployment guidance, testing strategy, and the generated app icon.

> This ZIP is a specification and starter kit, not a completed or deployable application. The frontend, backend, database adapters, sandbox orchestrator, and content must still be implemented and tested.

## Product decisions

- Product name: **WIYATA**
- Tagline: **Your Database Learning Center**
- Languages: English and Bahasa Indonesia only
- Default language: English; user-selectable Bahasa Indonesia
- Audience: developers, DBAs, data analysts, data engineers, students, and database professionals
- Business model: free
- Source direction: open source
- Deployment: hosted service and self-hosted Docker deployment
- Authentication: optional for basic learning and quick sandbox; account for saved workspaces and longer-lived environments
- AI: hybrid provider model — local models, user-provided cloud API keys, and non-AI/manual workflows
- Database execution: optional, isolated, and read-only by default
- Temporary databases: disposable quick sandboxes and longer-lived development/learning environments
- Core engines: SQLite, PostgreSQL, MySQL first; Oracle, SQL Server, IBM Db2 and others progressively

## Package map

- `docs/` — product, requirements, security, localization, and implementation instructions
- `architecture/` — system architecture, adapter contract, sandbox architecture, and query pipeline
- `database/` — platform data model and starter SQL
- `design/` — visual identity and UX specification
- `examples/` — API request examples, query IR, and sample content
- `deployment/` — Docker Compose starter and environment template
- `assets/` — WIYATA app icon

## Recommended reading order

1. `docs/01_PRODUCT_VISION_AND_PRD.md`
2. `docs/02_SCOPE_AND_ACCEPTANCE_CRITERIA.md`
3. `architecture/01_SYSTEM_ARCHITECTURE.md`
4. `architecture/02_DATABASE_ADAPTER_CONTRACT.md`
5. `architecture/03_SANDBOX_ARCHITECTURE.md`
6. `docs/03_UX_AND_PAGE_SPECIFICATION.md`
7. `docs/04_KNOWLEDGE_CENTER_SPECIFICATION.md`
8. `docs/05_PROFESSIONAL_TOOLS_CATALOG.md`
9. `docs/06_MONITORING_AND_OBSERVABILITY_CATALOG.md`
10. `docs/07_API_SPECIFICATION.md`
11. `database/01_PLATFORM_DATA_MODEL.md`
12. `docs/08_SECURITY_AND_PRIVACY.md`
13. `docs/09_I18N_AND_CONTENT_POLICY.md`
14. `docs/10_TESTING_AND_QUALITY_PLAN.md`
15. `docs/11_ROADMAP_AND_BUILD_ORDER.md`
16. `deployment/README.md`

## Suggested implementation stack

- Frontend: Next.js + TypeScript
- UI: Tailwind CSS + shadcn/ui
- Editor: Monaco Editor
- Backend: Python + FastAPI
- SQL parsing/transpilation: SQLGlot, with database-native validation where possible
- Metadata/persistence: PostgreSQL + SQLAlchemy + Alembic
- Optional cache/job coordination: Redis
- Database drivers: engine-specific Python drivers
- Deployment: Docker Compose initially; Kubernetes only when justified
- AI: provider abstraction; Ollama/local models and BYO cloud API keys

## Non-negotiable engineering rules

- Do not execute AI-generated SQL automatically.
- Do not treat parser-valid SQL as proof that it is valid on a target database.
- Do not expose database ports publicly for sandbox instances.
- Do not rely on regex alone for SQL safety classification.
- Use parameterized execution and database-native permissions.
- Never put secrets in frontend code, logs, or prompts.
- Keep sandbox workloads isolated and resource-limited.
- Clearly disclose licensing, edition, version, and compatibility limitations for professional tools.
- Knowledge articles must have sources, version applicability, and a last-verified date.
