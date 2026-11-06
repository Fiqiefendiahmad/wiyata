# WIYATA — Professional Tools Catalog
## Research, Content Architecture & Implementation Specification

**Product:** WIYATA — Your Database Learning Center  
**Module:** Katalog Alat / Professional Tools  
**Audience:** Coding agent, technical researcher, content editor, product designer  
**Languages:** English (`en`) and Bahasa Indonesia (`id`)  
**Status:** Implementation brief; findings must be verified before publication

---

## 1. Mission

Research, design, and implement a trustworthy, searchable, bilingual catalog of tools used in database administration, database engineering, reliability, security, architecture, and data engineering. Each tool needs a meaningful detail page—not merely a logo and outbound link.

**Important product boundary:** WIYATA is an educational directory and reference. It does not claim to operate, host, endorse, resell, or integrate the listed tools. An external tool's feature must never be presented as a built-in WIYATA feature.

**Do not stop at mockups or generated seed content.** Inspect the existing application, implement the catalog using its architecture, populate a carefully verified starter collection, test it, and document any gaps.

## 2. Mandatory Repository Discovery

Before coding:

1. Inspect repository structure, framework, backend, database/ORM, migrations, API conventions, authentication, localization, content management, UI components, and tests.
2. Locate the existing **Katalog Alat** navigation, routes, tool records, cards, filters, and detail pages.
3. Identify existing entities for Knowledge Center, Career Paths, competencies, learning paths, Studio & Lab, and SQL Challenges.
4. Reuse existing patterns and components; **do not create parallel systems or duplicate tables** if suitable models already exist.
5. Determine whether tools are currently static, database-backed, CMS-managed, or generated.
6. Produce a brief gap analysis and phased implementation plan before changing files.
7. Preserve Studio & Lab as WIYATA's central experience. Do not convert the site to a dashboard-first product.

## 3. Research Standards and Source Hierarchy

For **each tool**, research and document:

- Official product name, owner/vendor, canonical URL, category, product type, short and long description.
- Official documentation, official downloads, source repository (if applicable), licensing and pricing pages.
- Current supported operating systems, deployment types, relevant database engines, integration protocols, and version constraints.
- Key capabilities, limitations, security implications, maintenance status, and typical professional use cases.
- Installation prerequisites, configuration workflows, tutorials, troubleshooting references, and alternatives.
- Related roles, competencies, Knowledge Center articles, and exercises.

**Source priority:** (1) vendor/project documentation and release notes; (2) official repositories and licensing terms; (3) authoritative standards or platform docs; (4) credible independent technical evaluations. Community commentary may provide context but must not replace primary evidence for compatibility, pricing, security, or support claims.

For every significant factual claim, store a source URL, page title, `verified_at` date, and the exact feature/claim it supports. Distinguish **verified**, **partially verified**, **unverified**, and **deprecated** claims. Do not invent release numbers, prices, product capabilities, compatibility, or screenshots. Never scrape or republish copyrighted manuals wholesale; author original WIYATA explanations and short properly attributed quotations only when appropriate.

If browsing/network access is unavailable, implement the source and verification workflow, populate only facts established by available evidence, mark remaining fields `needs_review`, and report what requires manual research.

## 4. Initial Taxonomy

A tool may belong to multiple categories. Make categories configurable, not hardcoded.

| Category | Candidate tools to research (not preverified) |
|---|---|
| Database management and SQL clients | DBeaver, DataGrip, pgAdmin, SQL Server Management Studio, Oracle SQL Developer |
| Monitoring and observability | Prometheus, Grafana, Zabbix, Datadog, Percona Monitoring and Management |
| Migration and schema change | Flyway, Liquibase, Alembic, pgloader |
| Backup and recovery | RMAN, pgBackRest, Barman, Percona XtraBackup |
| Infrastructure and automation | Ansible, Terraform, Docker, Kubernetes |
| Data engineering and orchestration | Apache Airflow, dbt, Apache Kafka, Apache Spark |
| Database modeling and design | dbdiagram.io, ER/Studio, SQLDBM |
| Security and secrets | HashiCorp Vault, OpenSSL, database-native auditing utilities |
| Performance and diagnostics | pg_stat_statements, EXPLAIN/EXPLAIN ANALYZE, Oracle AWR/ASH, SQL Server Query Store |
| Command-line and native administration | psql, sqlcmd, SQL*Plus, MySQL client, Db2 CLP |

Classify native database features/utilities separately from standalone third-party applications. Do not imply all tools are free, universally compatible, or equally suitable for every platform.

## 5. Tool Detail Page — Required Content

### A. Identity and quick facts
- Name, verified logo/brand assets and attribution as required, vendor/project, official website.
- Category, tags, product type, open-source/commercial/hybrid designation when verified.
- Supported OS/deployment and supported database engines (with evidence).
- License model, official download/documentation links, review date and content status.

### B. What it does
- Beginner-friendly summary (2–3 sentences).
- Technical overview, primary jobs-to-be-done, typical users, common environments.
- Explicit boundaries: what it **does not** do or when it is a poor fit.

### C. Capabilities and constraints
- Grouped features, edition-dependent differences, prerequisites, known limitations.
- Support/compatibility matrix with evidence, version scope, and last-checked date.
- Security considerations: credentials, network access, permissions, TLS, least privilege, auditing.

### D. Getting started
- Prerequisites and installation links, platform-specific setup, initial configuration.
- A safe first workflow with expected outcome and troubleshooting checkpoints.
- Use demo/local/test environments; never require production credentials.

### E. Practical professional scenarios
- At least two realistic workflows per priority tool.
- State goal, role, environment, steps, validation, expected result, common errors, and rollback where relevant.
- Include safe commands only where verified and label engine/version-specific syntax.

### F. Learning connections
- Related career roles and competency IDs, expected proficiency, Knowledge Center articles, learning paths, Studio & Lab exercises, SQL Challenges where applicable.
- Explain **why** the tool is relevant to the competency rather than only attaching a tag.

### G. Alternatives and comparisons
- Comparable tools, use-case differences, tradeoffs, platform fit, licensing considerations.
- Neutral language; avoid unsupported rankings or promotional claims.

### H. References and freshness
- Official documentation, downloads, releases, license, security guidance, and cited supporting pages.
- `last_verified_at`, `last_content_reviewed_at`, maintainer, source status, and change log.

## 6. Catalog Discovery UX

Implement:

- Search by name, purpose, capability, category, database engine, role, and tags.
- Filters for category, database compatibility, OS/platform, licensing model, deployment, and verified status.
- Sort by relevance, alphabetical name, and recently reviewed (avoid popularity without defensible metrics).
- Clear tool cards with logo, name, short description, categories, and verified metadata only.
- Tool detail routes with stable slugs, SEO metadata, canonical links, structured navigation, and breadcrumbs.
- Related tools, related knowledge, related roles, and related exercises.
- Responsive desktop/mobile layouts, keyboard navigation, accessible contrast, screen reader labels, loading/empty/error states.
- English/Indonesian content and UI strings; clearly flag untranslated content rather than silently fabricating translations.

Suggested detail-page tabs: **Overview · Features · Getting Started · Tutorials · Compatibility · Careers & Learning · Alternatives · Resources**. Reuse the existing design system; adapt tab structure if it conflicts with established navigation.

## 7. Shared Competency-Based Integration

Use a **many-to-many** graph; do not duplicate Knowledge Center articles inside tool profiles.

```text
Tool ── ToolCompetency ── Competency ── CareerRoleCompetency ── CareerRole
  │                             │
  ├── ToolKnowledge ───────── KnowledgeArticle
  ├── ToolExercise ────────── StudioLabExercise
  ├── ToolLearningPath ────── LearningPath
  └── ToolAlternative ─────── Tool
```

Required behaviors:

1. Tool page shows relevant roles, competency level, learning articles, and exercises.
2. Career role page shows recommended tools for each competency and why they matter.
3. Knowledge article page links to related tools and practical workflows.
4. Learning paths can recommend a tool without requiring installation or external integration.
5. Distinguish reading an article, completing an exercise, passing an assessment, and demonstrating competency; **viewing a tool page does not establish proficiency**.
6. Maintain relationship provenance and editorial approval.

Example mappings to **verify and refine**:

| Tool | Example role | Example competency |
|---|---|---|
| DBeaver | DBA / SQL Developer | SQL client workflow and schema exploration |
| pgAdmin | PostgreSQL DBA | PostgreSQL administration interface |
| Grafana | Database Reliability Engineer | Operational dashboard interpretation |
| Prometheus | Database Reliability Engineer | Metrics collection and alerting concepts |
| Flyway | Database Engineer | Controlled schema migrations |
| Ansible | DBA / Infrastructure Engineer | Repeatable automation |
| Apache Airflow | Data Engineer | Workflow orchestration |

## 8. Data Model — Adapt to Existing Schema

Proposed logical entities (rename/reuse to fit current conventions):

```text
tools
  id, slug, canonical_name, vendor_name, official_url, product_type,
  short_description_en, short_description_id,
  overview_en, overview_id, license_model, publication_status,
  last_verified_at, last_content_reviewed_at, created_at, updated_at

tool_categories
  id, slug, name_en, name_id, description_en, description_id

tool_category_links
  tool_id, category_id

tool_features
  id, tool_id, name_en, name_id, description_en, description_id,
  edition_scope, verification_status

tool_compatibility
  id, tool_id, target_type, target_name, target_version_range,
  support_level, notes, verification_status, verified_at

tool_resources
  id, tool_id, resource_type, title, url, official, verified_at

tool_claim_sources
  id, tool_id, claim_entity_type, claim_entity_id, claim_text,
  source_url, source_title, verified_at, verification_status

tool_guides
  id, tool_id, slug, locale, guide_type, content,
  prerequisite_notes, safety_notes, publication_status, reviewed_at

tool_role_links
  tool_id, career_role_id, relevance_note, priority

tool_competency_links
  tool_id, competency_id, expected_proficiency, relevance_note

tool_knowledge_links
  tool_id, knowledge_article_id, relationship_type

tool_exercise_links
  tool_id, exercise_id, relationship_type

tool_alternatives
  tool_id, alternative_tool_id, comparison_note, comparison_source

tool_revision_history
  id, tool_id, revision_type, editor_id, summary, created_at
```

Add appropriate unique constraints, foreign keys, indexes, and soft-delete/archive semantics. Prefer locale-specific translation tables if that matches existing CMS design. Ensure no user-generated HTML is rendered unsanitized. Avoid storing secrets, binaries, or copyrighted vendor assets without appropriate rights.

## 9. API and Content Management

Reuse existing backend/API conventions. Suggested logical operations:

```text
GET    /api/tools
GET    /api/tools/{slug}
GET    /api/tools/{slug}/related
GET    /api/tool-categories
GET    /api/tools/filters

Admin-only, authenticated, authorized:
POST   /api/admin/tools
PATCH  /api/admin/tools/{id}
POST   /api/admin/tools/{id}/sources
POST   /api/admin/tools/{id}/review
POST   /api/admin/tools/{id}/publish
```

Requirements:

- Pagination and bounded page size; server-side filtering/search where appropriate.
- Stable slugs and localization-aware responses.
- Validated URLs and input fields; sanitize rich text.
- Authorization for editorial operations; audit trail for changes.
- Draft → in review → approved → published → archived workflow.
- Prevent publication of mandatory high-risk claims lacking source evidence.
- Cache invalidation after edits and periodic verification reminders.
- No client-side exposure of internal administrative tokens.

## 10. Editorial Research Workflow

For each candidate tool:

1. Confirm official identity and canonical domain.
2. Classify category and product type.
3. Research capabilities and verify each material claim.
4. Check supported platforms/engines, editions, licensing, and version scope.
5. Draft original overview and getting-started guidance in English.
6. Translate and technically review Indonesian content.
7. Add professional scenarios and safe test workflows.
8. Map competencies, roles, and Knowledge Center content using existing IDs.
9. Record source links, verification dates, reviewer, and unresolved uncertainties.
10. Run editorial and technical review; publish only approved records.
11. Recheck time-sensitive claims on a defined cadence or when official releases change.

Suggested initial quality gate for a **full profile**: verified identity and official links; substantive original overview; core features with sources; compatibility notes; licensing evidence; at least one validated getting-started guide; two practical scenarios; related competencies/roles; bilingual review; review timestamp.

Do not silently turn missing facts into definitive statements. Profiles that do not meet the gate may remain unpublished or appear as explicitly limited directory entries if product policy permits.

## 11. Delivery Phases

### Phase 0 — Audit and architecture
- Existing code/data inventory, gaps, reusable components, migration plan, integration points.

### Phase 1 — Catalog foundation
- Models/migrations, public APIs, search/filter, categories, cards, detail pages, localization, source attribution, admin editorial workflow.

### Phase 2 — Verified starter catalog
- Research and publish a manageable, high-quality set (suggested initial candidates: DBeaver, pgAdmin, SSMS, Oracle SQL Developer, Grafana, Prometheus, Flyway, Liquibase, pgBackRest, Ansible, Apache Airflow, dbt).
- **Candidate list is not verified content**; research each item before publishing.

### Phase 3 — Learning graph
- Link tools to Career Paths, competencies, Knowledge Center, and practical exercises; implement reverse links and relevant recommendations.

### Phase 4 — Advanced discovery
- Side-by-side comparisons, guided selection by role/task, version-aware compatibility, richer tutorials, source freshness checks.

Each phase must ship working functionality and test evidence. Do not require all advanced features before releasing the verified catalog foundation.

## 12. Security, Accessibility, Performance, and Legal

- External URLs: validate schemes, prevent open redirects, use safe link attributes where applicable.
- Editorial admin endpoints: authenticated, authorized, rate-limited where appropriate, audited.
- Rich content: sanitize Markdown/HTML; avoid script injection.
- Source retrieval/import: prevent SSRF and restrict unsafe network targets if the backend fetches URLs.
- Logos/screenshots: use permitted official assets, attribution, or original illustrations; provide fallbacks.
- Licensing/pricing: cite current official pages; do not present estimates as contractual terms.
- Accessibility: keyboard operation, semantic headings, accessible filters, image alt text, focus visibility.
- Performance: paginate results, index search/filter columns, lazy-load noncritical media, avoid N+1 queries.
- Privacy: no mandatory third-party tracking merely to view tool profiles.
- The catalog must not require users to grant access to production databases.

## 13. Acceptance Tests

### Research quality
- Every published tool has verified official identity and documentation link.
- Material compatibility, license, and version claims have dated supporting sources.
- Unsupported or ambiguous claims are clearly labeled or withheld.

### Functional
- Directory loads and search/filter/sort work, including combined filters.
- Each published tool has a stable detail page and functional navigation.
- EN/ID rendering works; untranslated fields have deliberate fallback behavior.
- Admin can draft, review, publish, update, and archive content with authorization.
- Tool↔role, tool↔competency, and tool↔knowledge links work in both directions.
- Broken/outdated external links are flagged for editorial review.

### Quality
- Mobile and desktop responsive layouts.
- Keyboard and screen-reader basics.
- API validation, authorization, pagination, and injection protections.
- Migration and rollback tested on nonproduction data.
- Existing WIYATA Studio & Lab, Career Paths, and Knowledge Center remain functional.

### Evidence
- Provide test commands/results, screenshots of real implemented pages, sample API responses, and a matrix of completed vs pending requirements. Do not claim tests were run unless they were actually executed.

## 14. Deliverables

1. Repository audit and architecture/gap analysis.
2. Database schema/migrations and model relationships.
3. Public catalog and tool-detail UI.
4. Search, filters, and API endpoints.
5. Editorial CMS workflow and source verification fields.
6. Verified bilingual starter content and source records.
7. Career/competency/knowledge integration.
8. Tests, security checks, accessibility checks, and performance notes.
9. Screenshots of the implemented experience.
10. Implementation summary, changed files, limitations, unresolved research, and next-phase backlog.

## 15. Final Agent Instruction

**Research first, inspect existing code, then implement.** Prioritize accurate, useful, maintainable tool profiles over a large shallow directory. Never fabricate vendor facts, prices, compatibility, release versions, feature availability, or test results. Use the current WIYATA architecture and design language. Treat competencies as the central link between tools, learning content, and career paths. Finish with a working catalog and an evidence-backed implementation report—not only a specification or static design.
