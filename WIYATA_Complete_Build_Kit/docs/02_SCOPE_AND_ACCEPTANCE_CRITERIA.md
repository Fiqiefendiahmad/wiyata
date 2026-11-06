# Scope and Acceptance Criteria

## MVP scope

### Included
- Responsive Next.js application shell.
- English and Bahasa Indonesia language switch.
- SQL editor with syntax highlighting.
- SQLite sandbox with isolated per-session storage.
- PostgreSQL and MySQL adapter foundations.
- Manual SQL workflow.
- Query generation interface with provider abstraction.
- SQL parsing and dialect conversion for supported SQLGlot dialects.
- DDL import and basic schema visualization.
- Query library for registered users.
- Knowledge Center content model, categories, article pages, and search.
- Professional Tools catalog and initial curated entries.
- Monitoring & Observability category.
- Docker-based local development environment.
- Automated tests and security baseline.

### Deferred
- Dedicated Oracle, SQL Server, and Db2 sandboxes.
- Full external database connection support for every engine.
- Dedicated local connection agent.
- Advanced execution-plan analysis.
- Full observability integrations.
- Community publishing workflow.
- Shared team workspaces.
- Formal learning certificates.

## Acceptance criteria

### Database Lab
- User can create a SQLite environment.
- Environment has a unique opaque identifier.
- Environment files are not web-accessible.
- SQL runs in an isolated worker with time and memory limits.
- User can reset and delete the environment.
- Expired environments are cleaned up by a background worker.
- Query results have row and byte limits.
- Sandbox cannot access arbitrary host filesystem paths or internal network services.

### Query Studio
- User can write and copy SQL manually.
- User can select a target dialect.
- Parser errors and unsupported syntax are shown clearly.
- Conversion output includes warnings for semantics that cannot be guaranteed.
- AI-generated SQL is displayed for review and never auto-executed.
- Schema context is optional and user-controlled.
- Query history and saved queries work for authenticated users.

### Knowledge Center
- Article has title, slug, language, summary, body, category, tags, applicable engines/versions, references, status, and last-reviewed date.
- Articles can link to a lab exercise.
- Search works without an AI provider.
- Content can be drafted, reviewed, published, and revised.
- English and Indonesian content can be maintained independently.

### Professional Tools
- Each catalog entry includes category, vendor, product URL, official documentation, license model, edition, supported platforms, database compatibility, and last-verified date.
- Licensing is not inferred from the existence of a free edition.
- Product details are reviewed against official sources.
- Commercial tools are not mislabeled as free/open source.

### Security
- No execution without explicit user action.
- Read-only is the default.
- Destructive statements are blocked by default.
- Secrets never appear in logs or browser storage.
- Rate limits and resource quotas are enforced.
