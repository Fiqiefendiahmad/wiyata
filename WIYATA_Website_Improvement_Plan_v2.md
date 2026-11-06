# WIYATA --- Revised Website Review & Improvement Specification

**Revision:** 2.0 --- Homepage re-examination\
**Website:** https://wiyata.sadeyan.my.id/\
**Product:** WIYATA --- Your Database Learning Center\
**Languages:** English (`en`) and Bahasa Indonesia (`id`)\
**Purpose:** Evidence-based improvements to the existing WIYATA website
and product.\
**Implementation rule:** Preserve working features; audit before
refactoring or replacing.

------------------------------------------------------------------------

## 1. Executive Summary

WIYATA's current public homepage is already centered on a database
workspace. It presents a SQL Studio / sandbox experience and navigation
to SQL challenges, career paths, Knowledge Center, and a tools catalog.
The visible workspace includes an engine selector, schema/table area,
query collection, AI SQL prompt, SQL editor,
execution/format/explain/audit/plan actions, dialect conversion, export,
read-only mode, and result-related tabs.

The right next step is **not to replace the existing website with a
generic dashboard-first application**. Keep the current SQL Studio as a
primary entry point and improve the product around it.

The recommended product direction is:

-   Keep **Studio & Lab** as the main hands-on workspace.
-   Make the other visible navigation areas real, coherent product
    destinations.
-   Clarify the difference between SQL generation, SQL explanation,
    database execution plans, auditing, conversion, and optimization.
-   Make engine support and sandbox status truthful and testable.
-   Improve the current workspace's loading, empty, error, and execution
    states.
-   Build Knowledge Center and Tools Catalog as structured knowledge
    systems, not link collections.
-   Add professional DBA workflows and learning paths that connect
    articles, tools, and exercises.
-   Introduce a dashboard or home overview as an optional landing
    destination, without removing or hiding the existing Studio.

**Product promise:** Learn, build, explore, and master database
technologies --- all in one place.

## 2. What Was Actually Reviewed

The public homepage was re-opened for this revision. The page snapshot
exposed the following content:

### 2.1 Visible identity and navigation

-   Brand: WIYATA.
-   Product subtitle currently displayed: "Pusat Pembelajaran Database".
-   Navigation: Studio & Lab, Tantangan SQL, Jalur Profesi, Pusat
    Pengetahuan, Katalog Alat.
-   Language controls: EN and ID.

### 2.2 Visible workspace

-   Schema & Tables with a count of 0.
-   Selected engine label: SQLite 3.45.
-   Sandbox engine selector: SQLite 3.45, Postgres 17, MySQL 11, Oracle
    23ai, SQL Server 2022.
-   Sandbox dataset indicator.
-   Structure Tables count of 0 and "Memuat tabel..." loading text.
-   Query collection and Save.
-   AI SQL prompt with a banking/customer balance example.
-   Actions: Run, Format, Explain, Audit, Plan.
-   Conversion selector and Export.
-   Read-only indicator.
-   SQL editor with a sample Core Banking query joining `accounts`,
    `customers`, and `branches`.
-   Result-related tabs: Query Results, Logic Flow, Audit,
    Transpilation, Plan.
-   Visible result metadata includes "12 baris".
-   A message also instructs the user to press Run to execute the query.

### 2.3 Limitations of this review

This is a public-page review, not a browser-driven functional test,
source-code inspection, API test, database connection test, security
assessment, or penetration test. The public page snapshot does not
establish that every button works, that the sample result is live, or
that each engine is available for sandbox execution.

The review also could not verify the deeper navigation destinations
through the public page snapshot. Those routes must be checked directly
in the running application and repository.

**Do not interpret a visible label as proof of implementation.** All
items below that require backend or runtime verification are marked as
verification tasks.

------------------------------------------------------------------------

## 3. Updated Assessment: What to Keep, Fix, and Build

### Keep

1.  The SQL Studio as a prominent core feature.
2.  The engine selector and engine-aware workflow.
3.  The AI-to-SQL prompt.
4.  Query collection and save workflow.
5.  SQL formatting, explanation, auditing, and plan concepts.
6.  Conversion and export controls.
7.  The five visible product navigation destinations.
8.  English and Indonesian language controls.

### Fix or verify first

1.  The schema panel shows zero tables while displaying "Memuat
    tabel...". Verify whether loading is stuck, the sandbox is empty,
    the API failed, or the schema has not been initialized.
2.  The result area shows "12 baris" while also showing a prompt to
    press Run. Verify whether those rows are sample/static data, stale
    results, or a live execution result. The interface must distinguish
    them.
3.  Verify the engine/version labels, especially "MySQL 11". MySQL and
    MariaDB are distinct products with separate version schemes. Do not
    silently relabel one as the other.
4.  Verify that SQLite 3.45 and PostgreSQL 17 correspond to the actual
    sandbox/runtime images.
5.  Verify whether Oracle 23ai and SQL Server 2022 are real runnable
    sandboxes, external-connection-only options, or currently UI
    placeholders.
6.  Clarify what "Read-only" means: a visual mode, backend policy, or
    native database permission.
7.  Clarify the difference between Explain, Audit, and Plan.
8.  Verify all language strings and persistence of the language choice.
9.  Verify Save, Export, Convert, and each result tab through real
    interaction.

### Build next

-   Robust schema explorer and connection state.
-   Engine capability registry.
-   Reliable sandbox lifecycle.
-   Clear query execution state and history.
-   Knowledge Center content model and search.
-   Tools Catalog with licensing and version information.
-   Learning paths and SQL challenge progression.
-   Career role pages and guided DBA workflows.
-   User library for saved queries, notes, bookmarks, and progress.

------------------------------------------------------------------------

## 4. Product Architecture: Evolve the Existing Navigation

Do not force a new navigation model before inspecting current routes and
user behavior. First map the current five destinations and keep their
names recognizable.

  -----------------------------------------------------------------------
  Existing navigation     Recommended product     Important additions
                          responsibility          
  ----------------------- ----------------------- -----------------------
  Studio & Lab            Main hands-on SQL       Schema explorer, engine
                          workspace and sandbox   status, query history,
                          learning                safe execution, lab
                                                  exercises

  Tantangan SQL           SQL challenge and       Difficulty, engine,
                          practice center         topic, hints,
                                                  validation,
                                                  explanation, progress

  Jalur Profesi           Career paths and        Role profiles, skills,
                          role-based development  tools, workflows,
                                                  learning sequences

  Pusat Pengetahuan       Knowledge Center /      Articles,
                          database encyclopedia   engine/version filters,
                                                  references, search,
                                                  diagrams, exercises

  Katalog Alat            Professional Tools      Categories, supported
                          catalog                 engines, platform,
                                                  license, setup guides,
                                                  alternatives
  -----------------------------------------------------------------------

### 4.1 Optional Dashboard / Home

Add a separate dashboard only if it improves discovery and return
visits. It should not displace Studio & Lab or require an extra click
for users who want to work with SQL.

Dashboard sections: - Continue where you left off. - Open Studio &
Lab. - Recent queries and saved work. - Active sandbox status. -
Continue a learning path. - Recommended articles. - Featured
professional tools. - Recently updated content.

Consider a user preference for the default landing page: Dashboard or
Studio & Lab.

### 4.2 Suggested secondary structure

**Studio & Lab** - Query Studio - Quick Sandbox - Learning Labs - Saved
Queries - Query History

**Tantangan SQL** - Beginner - Intermediate - Advanced - Engine-specific
challenges - Daily or curated challenges

**Jalur Profesi** - Database Administrator - Database Developer -
Performance Engineer - Database Reliability Engineer - Database
Architect - Data Engineer - Database Security Engineer - Cloud DBA

**Pusat Pengetahuan** - Fundamentals - SQL - Database Engines -
Architecture & Internals - Administration - Performance - Backup &
Recovery - High Availability - Security - NoSQL & Distributed
Databases - Data Engineering - Monitoring & Troubleshooting

**Katalog Alat** - Database Clients - Administration - Performance &
Diagnostics - Backup & Recovery - Migration - Monitoring &
Observability - Schema & Modeling - Infrastructure & Automation -
Security - Data Engineering

------------------------------------------------------------------------

## 5. Homepage and Studio UX Improvements

### 5.1 Resolve the current loading/empty-state ambiguity

The visible page currently reports zero tables and "Memuat tabel...".
Treat this as the highest-priority UX defect to investigate.

Expected state model:

  -----------------------------------------------------------------------
  State                               UI behavior
  ----------------------------------- -----------------------------------
  Initializing                        Show "Starting sandbox..." with
                                      progress or spinner

  Loading schema                      Show "Loading schema..." and
                                      skeleton rows

  Ready with tables                   Show actual schemas and tables

  Ready but empty                     Explain that the selected database
                                      has no tables; offer dataset
                                      initialization

  Failed                              Show a human-readable error and
                                      Retry

  Unauthorized                        Explain that metadata permission is
                                      missing

  Disconnected                        Show connection state and reconnect
                                      action

  Expired                             Explain sandbox expiry and offer a
                                      new environment
  -----------------------------------------------------------------------

Do not leave "Loading..." indefinitely. Add request timeout, retry,
cancellation, and structured backend errors.

### 5.2 Make result provenance obvious

The current snapshot displays "12 baris" and also tells the user to
press Run. Verify the data source and make it impossible to confuse demo
output with real execution.

Show one of: - `Example result` --- fixed demonstration data. -
`Previous execution` --- result from a prior run, with timestamp. -
`Live execution` --- result from the current run, with duration and
environment. - `No execution yet` --- no results exist. -
`Execution failed` --- error and diagnostic reference.

Clear or mark stale results when the SQL text changes. Never imply a
query has executed when it has not.

### 5.3 Query editor behavior

Add: - SQL syntax highlighting by selected engine. - Engine-aware
autocomplete. - Schema/table/column suggestions. - Format-on-demand and
configurable formatting. - Multiple query tabs, if the current
architecture supports it. - Unsaved-change warning. - Keyboard shortcuts
and shortcut help. - Line numbers and error location. - Query selection
execution only when safely supported. - Clear distinction between
current SQL and generated SQL.

Avoid losing editor content when switching result tabs, changing
language, or opening supporting panels.

### 5.4 Schema explorer

Show authorized metadata: - Database and schema. - Tables and views. -
Columns and data types. - Primary/foreign keys. - Indexes and
constraints. - Sequences, triggers, and routines where supported.

Requirements: - Lazy loading. - Refresh control. - Search/filter. -
Expand/collapse. - Loading, empty, permission-denied, disconnected, and
error states. - Do not infer "no objects" from a failed metadata
request. - Display the active connection/environment clearly.

### 5.5 Query execution controls

Show a compact execution toolbar: - Run. - Stop/Cancel. - Format. -
Validate. - Explain SQL. - Explain Plan. - Audit SQL. - Optimize SQL. -
Convert.

Only show actions supported by the selected engine and environment. If
an action is unavailable, explain why rather than presenting a
nonfunctional control.

### 5.6 Result area

Tabs should be consistent and meaningful: - Results - Messages - Explain
SQL - Execution Plan - Audit Findings - Conversion - Logic Flow (only if
a real representation exists)

For results: - Row count. - Duration. - Engine/version. - Execution
timestamp. - Pagination. - Bounded export. - Copy cell/row/result. -
Error messages. - Truncation indicator when row/byte limits apply.

Do not show "Logic Flow" or "Transpilation" panels as if they are native
database outputs if they are generated approximations. Label their
origin.

------------------------------------------------------------------------

## 6. Clarify the Query Studio Concepts

The current labels Explain, Audit, and Plan are useful but ambiguous.
Standardize their definitions.

  ------------------------------------------------------------------------------
  Feature                 Definition              Data required
  ----------------------- ----------------------- ------------------------------
  Explain SQL             Human-readable          SQL text; schema context
                          explanation of SQL      improves quality
                          intent and clauses      

  Explain Plan            Native or               Connected engine and plan
                          engine-generated        privileges/support
                          execution plan          

  Audit SQL               Static/policy           SQL AST and policy rules
                          inspection of SQL risks 

  Optimize SQL            Recommendations for     SQL;
                          potential performance   schema/index/statistics/plan
                          improvement             context improves confidence

  Validate SQL            Syntax and policy       Parser/dialect and execution
                          validation              policy

  Convert SQL             Dialect translation     Source and target dialects
  ------------------------------------------------------------------------------

Do not call static SQL risk analysis a database audit trail. Do not
claim an execution plan is real unless it came from the selected engine
or is explicitly labeled as an estimate.

### 6.1 Audit SQL findings

Potential findings: - Destructive statement. - Unbounded
update/delete. - Missing or suspicious filter. - `SELECT *` where
discouraged. - Potentially expensive pattern. - Unparameterized user
input. - Unsupported or nonportable syntax. - Multiple statements. -
Privileged or administrative operation.

Findings must include severity, explanation, evidence/location, and a
suggested safer approach. Avoid claiming that a static scan proves a
query is safe.

### 6.2 Optimize SQL

Separate deterministic facts from suggestions: - Observed execution-plan
evidence. - Schema/index metadata. - General heuristic. - AI-generated
hypothesis.

For every recommendation, explain the expected benefit, trade-off, and
how to measure it. Never promise a performance improvement without
measurement.

------------------------------------------------------------------------

## 7. Engine Support and Capability Registry

The engine selector currently lists SQLite, PostgreSQL, MySQL, Oracle,
and SQL Server. That is a good visible roadmap, but each option must
accurately describe its current capability.

### 7.1 Required capability fields

For each engine and tested version, track:

-   SQL generation.
-   SQL parsing.
-   SQL formatting.
-   SQL conversion.
-   Sandbox execution.
-   External connection.
-   Metadata introspection.
-   Native explain plan.
-   Read-only enforcement.
-   Cancellation.
-   Export.
-   Supported authentication.
-   Known limitations.

Status values: - `available` - `limited` - `planned` - `unavailable`

Show the status in the UI. Distinguish "SQL dialect supported" from
"database execution supported".

### 7.2 Engine/version corrections

-   MySQL and MariaDB are different database products.
-   Verify the meaning of the current "MySQL 11" selector entry. If it
    is MariaDB 11.x, label it MariaDB and keep it separate from MySQL.
-   Verify SQLite 3.45 against the actual runtime.
-   Verify PostgreSQL 17 against the actual sandbox image.
-   Verify Oracle 23ai naming and the actual supported image/connection
    mode.
-   Verify SQL Server 2022 connection and execution support.
-   Store exact tested patch/minor versions and adapter version.
-   Show "Last verified" information in admin documentation.

Never imply every listed engine has an isolated sandbox. A product may
support SQL generation without supporting sandbox execution.

### 7.3 Recommended implementation sequence

1.  SQLite: complete, tested sandbox and learning flow.
2.  PostgreSQL: isolated sandbox, metadata, read-only execution,
    explain.
3.  MySQL: isolated sandbox and tested adapter.
4.  MariaDB: separate dialect and test matrix.
5.  Oracle, SQL Server, and Db2: start with validated SQL/documentation
    capabilities; add sandbox or external connections only after
    infrastructure and licensing/security review.
6.  MongoDB, Redis, Cassandra, and analytics engines: separate
    non-relational capability models rather than forcing them into a
    relational SQL interface.

------------------------------------------------------------------------

## 8. Database Lab and Sandbox

Make the difference between the current sandbox and persistent database
connections explicit.

### Quick Sandbox

-   Disposable.
-   Created from a known dataset.
-   Expires automatically.
-   Resettable.
-   Resource-limited.
-   Intended for challenges and experimentation.

### Persistent Learning Environment

-   Longer-lived.
-   User-controlled lifecycle.
-   Quotas for CPU, memory, storage, and duration.
-   Can pause, reset, or delete.
-   Intended for projects and longer courses.

### Sandbox safety requirements

-   No privileged containers.
-   No Docker socket mounted into application containers.
-   No broad host filesystem mounts.
-   No public database ports.
-   Block outbound network by default.
-   Block cloud metadata endpoints.
-   CPU, memory, process, disk, and execution-time limits.
-   Query cancellation.
-   Per-user quotas.
-   Automatic cleanup.
-   Secrets excluded from logs.
-   Isolation tests before public release.

Start with SQLite if that is the current implemented path. Do not add
multiple containerized engines until the lifecycle and isolation are
proven.

------------------------------------------------------------------------

## 9. Tantangan SQL --- SQL Challenges

The current navigation already has a dedicated SQL challenge
destination. Give it a clear progression and connect it to the existing
Studio & Lab.

### Challenge page requirements

-   Title and learning objective.
-   Difficulty.
-   Topic tags.
-   Engine and version.
-   Dataset and schema.
-   Problem statement.
-   Expected output description.
-   Starter query or schema explorer.
-   Hints.
-   Submit/validate.
-   Result feedback.
-   Explanation and reference lesson.
-   Next challenge.
-   Progress state.

### Challenge categories

Beginner: - SELECT and WHERE. - ORDER BY and LIMIT. - Aggregation. -
GROUP BY and HAVING. - Basic joins.

Intermediate: - Subqueries. - CTEs. - CASE. - Window functions. -
Views. - Index awareness.

Advanced: - Query plans. - Multi-step analysis. - Transactions and
concurrency. - Performance diagnosis. - Data modeling.

### Validation

Prefer result-based validation over exact SQL string comparison.
Multiple semantically equivalent queries should pass unless the exercise
explicitly teaches a required construct.

------------------------------------------------------------------------

## 10. Jalur Profesi --- Career Paths

The current career-path navigation should become role-based, practical
learning plans rather than generic job descriptions.

Initial roles: - Database Administrator. - Database Developer. -
Database Performance Engineer. - Database Reliability Engineer. -
Database Architect. - Data Engineer. - Database Security Engineer. -
Cloud Database Administrator.

Each role page should contain: - Role overview. - Responsibilities. -
Core knowledge. - Useful tools. - Engine-specific skills. - Practical
workflows. - Learning sequence. - Projects and exercises. - Related
Knowledge Center articles. - Self-assessment.

Avoid presenting one vendor or tool as mandatory for every company. Make
clear that career paths are educational guidance, not official
certification.

------------------------------------------------------------------------

## 11. Pusat Pengetahuan --- Knowledge Center

Build an original, searchable, version-aware database encyclopedia.

### 11.1 Main categories

1.  Database Fundamentals.
2.  Relational Database Concepts.
3.  SQL Fundamentals.
4.  Advanced SQL.
5.  Database Design and Modeling.
6.  Database Architecture and Internals.
7.  Database Administration.
8.  Performance Engineering.
9.  Query Optimization.
10. Transactions and Concurrency.
11. Backup and Recovery.
12. High Availability and Disaster Recovery.
13. Database Security.
14. NoSQL and Distributed Databases.
15. Data Engineering and Warehousing.
16. Database Migration and Integration.
17. Monitoring and Observability.
18. Troubleshooting and Incident Response.
19. Cloud Databases.
20. Professional Practices.

### 11.2 Article format

Every article: - Title and summary. - Learning objectives. - Category
and tags. - Skill level. - Prerequisites. - Engine/version scope. -
Explanation. - Diagrams where useful. - SQL/command examples. - Use
cases. - Limitations and trade-offs. - Common mistakes. -
Troubleshooting. - Exercise or quiz. - Related articles. - Official
references. - Author/reviewer. - Publication and review dates. -
English/Indonesian translation status.

### 11.3 Editorial workflow

`Draft → Technical Review → Language Review → Approved → Published → Review Due`

Official documentation is the primary authority for product-specific
behavior. University material supports fundamentals and internals.
Educational sites inspire lesson design. GitHub projects support
implementation study and exercises only after license review.

### 11.4 Knowledge search

Search must work without AI. Filters: - Keyword. - Category. - Engine. -
Engine version. - Difficulty. - Language. - Content type. - Last
reviewed. - Source type.

AI knowledge answers must cite actual retrieved sources, distinguish
facts from suggestions, and abstain when evidence is insufficient.

------------------------------------------------------------------------

## 12. Katalog Alat --- Professional Tools

Make this a curated professional tool directory, not a simple list of
names.

Categories: - Database Clients. - Database Administration. - Performance
and Diagnostics. - Backup and Recovery. - Migration. - Monitoring and
Observability. - Schema and Modeling. - SQL Quality. - Infrastructure
and Automation. - Security and Secrets. - Data Engineering.

Example tools to evaluate: - DBeaver, SQL Developer, SQLcl, SQL\*Plus,
pgAdmin, psql, MySQL Workbench, HeidiSQL, SSMS, IBM Data Management
Console, Db2 CLP, DataGrip. - Oracle Enterprise Manager, PostgreSQL
EXPLAIN, pg_stat_statements, pgBadger, MySQL Performance Schema, SQL
Server Query Store, Extended Events, Db2 monitoring functions, PMM. -
RMAN, pgBackRest, Barman, pg_dump, Percona XtraBackup, native SQL Server
backup, Db2 utilities, Flyway, Liquibase. - Prometheus, Grafana, Zabbix,
Nagios, Checkmk, Icinga, Netdata, OpenTelemetry, Datadog, Dynatrace, New
Relic, Elastic Observability, Splunk. - Docker, Kubernetes, Ansible,
Terraform, Jenkins, GitHub Actions, GitLab CI/CD. - Airflow, dbt, Spark,
Kafka, Trino, Debezium.

Each tool page must show: - Purpose and category. - Official website and
docs. - Supported engines and versions. - OS and deployment. - Editions
and license. - Installation/configuration. - Use cases and
limitations. - Permissions and security. - Resource requirements. -
Troubleshooting. - Alternatives. - Practical exercise. - Last verified
date.

Do not call a tool free solely because it has a free trial or limited
edition.

------------------------------------------------------------------------

## 13. Monitoring and Observability

Monitoring and observability should be a **subcategory of Katalog Alat
and Pusat Pengetahuan**, not a separate WIYATA monitoring product.

Teach engine-native monitoring alongside infrastructure tools.

### Engine-specific

-   Oracle: Enterprise Manager, dynamic performance views, Data Guard
    monitoring, AWR/ASH/ADDM where licensed.
-   PostgreSQL: `pg_stat_activity`, `pg_stat_database`,
    `pg_stat_statements`, EXPLAIN, pgBadger, pgwatch.
-   MySQL/MariaDB: Performance Schema, sys schema, `SHOW GLOBAL STATUS`,
    PMM.
-   SQL Server: Activity Monitor, Query Store, Extended Events, DMVs,
    SQL Server Agent.
-   Db2: Data Management Console, CLP, `MON_GET_*`, event monitors,
    explain, HADR monitoring.

### Infrastructure

Prometheus, Grafana, Zabbix, Nagios, Checkmk, Icinga, Netdata,
OpenTelemetry, Alertmanager, Datadog, Dynatrace, New Relic, Elastic
Observability, Splunk, AppDynamics.

### Metrics

Availability, CPU/run queue, memory/cache/buffer, disk
latency/IOPS/throughput/queue, storage, sessions, locks, blocking,
deadlocks, query latency, throughput, slow SQL, plan changes,
replication lag, backup freshness, restore testing, errors, and logs.

Explain metric semantics per engine. Teach sampling, collection
overhead, retention, cardinality, and alert fatigue.

------------------------------------------------------------------------

## 14. Professional DBA Workflows

Create guided, repeatable workflows. Each one should include scenario,
impact, required permission, tools, evidence collection, diagnosis,
hypotheses, remediation, rollback, verification, and references.

Initial workflows: 1. Investigate slow Oracle database. 2. Diagnose
PostgreSQL connection exhaustion. 3. Troubleshoot MySQL replication lag.
4. Monitor Db2 tablespace utilization. 5. Investigate SQL Server
blocking and deadlocks. 6. Validate backup freshness and restore. 7.
Investigate high Linux disk I/O. 8. Review database privileges. 9. Plan
a database migration. 10. Diagnose CPU and memory saturation.

For Oracle, explain licensing restrictions around diagnostic/tuning
packs. Monitoring queries should be read-only and low-impact by default.

------------------------------------------------------------------------

## 15. My Library and User Continuity

Add a personal area when the current authentication model supports it: -
Saved queries. - Query folders and tags. - Query history. - Bookmarked
articles. - Saved tools. - Notes. - Learning progress. - Completed
challenges. - Recent sandbox environments. - Exportable notes.

Apply ownership checks on every API. Provide delete and export controls.
If authentication is not yet ready, do not build fake persistent user
data in browser-only state and present it as account storage.

------------------------------------------------------------------------

## 16. Visual Design and Language

Keep WIYATA's existing identity and refine consistency rather than
redesigning without evidence.

Suggested direction: - Modern developer-oriented interface. - Deep navy
foundation. - Restrained gold accent. - Neutral technical surfaces. -
Clear separation between editor, schema, results, and assistant
panels. - Subtle heritage influence; avoid heavy decoration.

Suggested palette: - Navy `#071A3A` - Navy surface `#10264A` - Gold
`#F2B84B` - Warm white `#F7F8FA` - Text `#172033` - Muted `#64748B` -
Border `#DCE2EA`

Check WCAG contrast, particularly gold on white and muted text on dark
backgrounds.

### Language

The current public page shows the Indonesian product subtitle and
language controls. Make the EN/ID experience consistent: - Support
English and Bahasa Indonesia only. - Persist user language choice. -
Translate navigation, buttons, empty/error states, and content. - Avoid
mixing languages in one state. - Preserve SQL syntax, identifiers, and
product names. - Ensure dates and numbers use locale-aware formatting.

Decide whether the tagline should remain "Your Database Learning Center"
in both languages or use a consistent localized version.

------------------------------------------------------------------------

## 17. Technical Architecture Recommendations

These are target recommendations. First inspect the current stack and
reuse what works.

Potential stack: - Frontend: Next.js + TypeScript. - UI: Tailwind CSS
and component library. - SQL editor: Monaco Editor. - Client data:
TanStack Query. - Validation: Zod. - Backend: FastAPI. - Backend
validation: Pydantic. - ORM: SQLAlchemy. - Migrations: Alembic. - SQL
parser/converter: SQLGlot plus engine-specific validation. - Platform
DB: PostgreSQL. - Optional queue/cache: Redis. - Sandbox: isolated
workers/containers.

Use a modular monolith initially. Do not introduce microservices without
demonstrated need.

### Engine adapter contract

Possible operations: - `connect` - `disconnect` - `get_capabilities` -
`list_databases` - `list_schemas` - `list_tables` -
`get_table_metadata` - `validate_sql` - `execute_read_only` -
`explain` - `cancel_query`

Adapters must report unsupported features honestly.

### API areas

``` text
/api/v1/query/generate
/api/v1/query/convert
/api/v1/query/explain
/api/v1/query/validate
/api/v1/query/optimize
/api/v1/query/execute
/api/v1/sandboxes
/api/v1/connections
/api/v1/challenges
/api/v1/career-paths
/api/v1/knowledge
/api/v1/tools
/api/v1/library
```

Do not create duplicate endpoints if the existing API already provides
equivalent functionality. Document and extend the current API.

------------------------------------------------------------------------

## 18. Security and Execution Policy

Database execution is security-critical.

### Safe defaults

-   Read-only by default.
-   AI-generated SQL never executes automatically.
-   Explicit user action before execution.
-   No multi-statement execution by default.
-   Backend-enforced authorization.
-   Native database roles and grants.
-   Parameterized values.
-   Statement timeout and cancellation.
-   Row and byte limits.
-   Rate limits and per-user quotas.
-   Secrets never sent to frontend, logs, analytics, or AI prompts.

### SQL policy

Use AST-aware parsing and policy checks. Do not rely on regex alone.
Restrict by default: - `DROP` - `TRUNCATE` - Unapproved `DELETE` and
`UPDATE` - Privilege/role changes. - Administrative operations. -
External file operations. - Server-side program execution. - Unapproved
stored procedures. - Multiple statements. - Engine-specific dangerous
commands.

A parser is not a security boundary by itself. Combine it with native
permissions, isolation, quotas, network restrictions, and timeouts.

------------------------------------------------------------------------

## 19. Testing and Acceptance Criteria

### Homepage and Studio

-   All visible navigation destinations resolve correctly.
-   Schema loading reaches a terminal state.
-   Empty database differs from loading and failure.
-   Demo results are labeled as demo.
-   Previous results are timestamped and marked stale when appropriate.
-   Run, Stop, Format, Explain, Audit, Plan, Convert, Save, and Export
    are tested.
-   Editor content survives navigation and panel changes.
-   Language switching is complete and persistent.

### Engine support

For every engine/version advertised: - Verify actual
runtime/connection. - Verify metadata. - Verify parsing and
validation. - Verify read-only enforcement. - Verify
timeout/cancellation. - Verify row/byte limits. - Verify plan support. -
Verify failure and unsupported capability handling.

### Knowledge and tools

-   Search works without AI.
-   Articles have references, reviewers, and review dates.
-   Version-specific articles show scope.
-   Tool license and edition information is checked.
-   Draft/unreviewed content is not public.
-   External content is not republished without rights.

### Security

-   Users cannot access another user's data.
-   Secrets never appear in API responses.
-   Sandbox cannot access host resources or cloud metadata.
-   SQL policy is enforced server-side.
-   Unapproved outbound network is blocked.
-   Rate limits and quotas work.
-   Error messages do not disclose secrets.

------------------------------------------------------------------------

## 20. Prioritized Implementation Roadmap

### Phase 0 --- Repository and runtime audit

Before redesigning anything: - Inspect repository and deployment. - Map
current routes and components. - Map backend APIs and data models. -
Test all visible homepage controls. - Check loading and empty states. -
Verify the result panel's "12 rows" provenance. - Verify engine versions
and capabilities. - Inspect auth and read-only enforcement. - Inspect
sandbox isolation. - Produce a feature matrix and risk register.

Deliverable: `WIYATA_CURRENT_STATE_AUDIT.md`.

### Phase 1 --- Stabilize current Studio & Lab

-   Fix schema loading and error states.
-   Clarify sample vs live results.
-   Verify engine selector.
-   Implement capability registry.
-   Separate Explain SQL / Explain Plan / Audit SQL / Optimize SQL.
-   Implement server-side read-only policy.
-   Add cancellation, pagination, and execution metadata.
-   Add query history and reliable save/export.

### Phase 2 --- Complete SQL Challenges

-   Challenge model and authoring.
-   Engine/version and dataset association.
-   Result-based validation.
-   Hints and explanations.
-   Progress tracking.
-   Deep link from challenge to Studio & Lab.

### Phase 3 --- Knowledge Center foundation

-   Source registry and license status.
-   Article taxonomy and translations.
-   Section-level references.
-   Editorial workflow.
-   Search and filters.
-   Initial reviewed content collection.

### Phase 4 --- Professional Tools and DBA workflows

-   Tool catalog and tool detail pages.
-   Monitoring/observability category.
-   Edition/licensing checks.
-   DBA workflows with risk/rollback.
-   Role-specific learning paths.

### Phase 5 --- Career paths and My Library

-   Role explorer.
-   Skill map and recommended sequence.
-   Saved queries, bookmarks, notes, progress.
-   Export and deletion controls.

### Phase 6 --- Quality and scale

-   Accessibility and responsive refinement.
-   Performance/load tests.
-   Content freshness checks.
-   Broken-link checks.
-   Security regression tests.
-   Operational runbooks and backups.

------------------------------------------------------------------------

## 21. Definition of Done

The improvement is complete when: - Existing Studio & Lab functionality
is preserved and verified. - Navigation destinations are implemented and
coherent. - Schema loading and result provenance are unambiguous. -
Engine/version claims match tested capabilities. - SQL actions have
precise definitions and correct outputs. - Database Lab is safely
isolated. - SQL Challenges have meaningful validation. - Knowledge
Center is searchable, sourced, and version-aware. - Professional Tools
shows accurate licensing and support. - Career paths connect roles to
practical skills and learning. - Monitoring/observability is part of
professional knowledge, not a falsely implied WIYATA monitoring
service. - English and Indonesian are consistent. - Tests cover
functionality, engines, and security. - Documentation matches actual
runtime behavior.

------------------------------------------------------------------------

## 22. Development Team / AI Coding Agent Instruction

> You are improving the existing WIYATA website and application. Do not
> create an unrelated replacement.
>
> Begin by inspecting the repository, deployed routes, frontend
> components, backend APIs, database schema, authentication, engine
> adapters, sandbox implementation, and deployment configuration.
>
> Reproduce and test the existing homepage behavior. In particular,
> investigate the schema area that displays zero tables and "Memuat
> tabel...", the result panel that displays "12 baris" while asking the
> user to press Run, the engine/version labels, and the read-only
> indicator.
>
> Preserve existing working features. Do not replace Studio & Lab with a
> new dashboard or remove the existing navigation. Improve the current
> product incrementally and keep backward compatibility where possible.
>
> Build a current-state inventory with each feature marked implemented,
> partial, placeholder, planned, or unverified. Record the route,
> component, API, data model, test evidence, and known limitation for
> each feature.
>
> Stabilize Studio & Lab before adding new engine integrations. Verify
> the actual engine and version behind every selector option.
> Distinguish SQL generation, parsing, formatting, conversion, sandbox
> execution, external connection, metadata introspection, and native
> explain-plan support.
>
> AI-generated SQL must never execute automatically. Enforce read-only
> behavior on the backend and through native database permissions. Use
> AST-aware SQL policy, parameterized values, timeouts, cancellation,
> row/byte limits, and isolated sandbox environments.
>
> Implement the existing navigation destinations as coherent products:
> SQL Challenges, Career Paths, Knowledge Center, and Professional
> Tools. Connect them to Studio & Lab rather than building disconnected
> pages.
>
> Build Knowledge Center with original, reviewed, version-aware articles
> and traceable references. Build Professional Tools with accurate
> edition/licensing and official documentation. Monitoring and
> observability should be a category within professional knowledge and
> tools.
>
> Support English and Bahasa Indonesia. Keep the interface terminology
> consistent.
>
> For every phase, report changed files, architecture decisions,
> migrations, API changes, tests, security review, UI evidence, known
> limitations, and rollback steps.
>
> Do not claim completion based only on a successful build. Test actual
> runtime behavior and all user-facing controls.

------------------------------------------------------------------------

## 23. Immediate Action List

1.  Run a complete repository and deployed-runtime audit.
2.  Reproduce the homepage schema loading behavior.
3.  Determine whether "12 baris" is demo, stale, or live output.
4.  Verify the engine/version selector and classify actual capabilities.
5.  Verify backend enforcement of read-only mode.
6.  Test all visible Studio controls.
7.  Preserve Studio & Lab and stabilize it.
8.  Map the current routes for Tantangan SQL, Jalur Profesi, Pusat
    Pengetahuan, and Katalog Alat.
9.  Implement content/source governance.
10. Deliver a phased backlog with tests and evidence.

**Final direction:** WIYATA should evolve from its current SQL Studio
and sandbox foundation into a connected database learning and
professional development platform. Keep the workspace as the heart of
the product, and make every other module strengthen it.
