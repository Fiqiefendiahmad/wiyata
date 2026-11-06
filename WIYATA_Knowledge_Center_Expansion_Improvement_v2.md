# WIYATA Knowledge Center Expansion & Platform Improvement Specification

**Product:** WIYATA --- Your Database Learning Center\
**Languages:** English (`en`) and Bahasa Indonesia (`id`)\
**Purpose:** Expand WIYATA into a connected database learning and
professional reference platform while preserving Studio & Lab as its
central interactive experience.

------------------------------------------------------------------------

## 1. Executive Summary

WIYATA should evolve beyond an SQL playground into a comprehensive
database learning and professional reference platform for beginners,
developers, students, DBAs, data analysts, data engineers, performance
engineers, architects, and production support teams.

This expansion adds six connected capabilities:

1.  **Database Encyclopedia** --- visual and technical profiles for each
    database engine.
2.  **Monitoring & Observability Knowledge** --- metrics, dashboards,
    monitoring products, diagnostic methods, and alerting concepts.
3.  **Database Glossary & Field Terminology** --- technical terms,
    abbreviations, and expressions used by database professionals.
4.  **DBA Field Handbook** --- commands, operational procedures, and
    maintenance checklists.
5.  **Troubleshooting & Incident Library** --- scenario-based diagnosis,
    remediation, rollback, and verification.
6.  **Cross-Database Comparison** --- explain how engines implement
    similar concepts, including their differences.

Connect these capabilities to the existing Studio & Lab, SQL Challenges,
Career Paths, Knowledge Center, and Professional Tools. Do not replace
the existing Studio & Lab with a dashboard-first design. Studio & Lab
remains a prominent entry point.

This specification is an implementation guide, not an instruction to
rewrite the application blindly. Audit the repository and deployed
behavior first, map existing features, reuse working components, and
implement incrementally.

## 2. Product Vision and Principles

### Vision

Make database knowledge understandable, searchable, comparable, and
practical --- from fundamentals to production operations.

### Principles

-   Practical before theoretical: explain why a concept matters in real
    work.
-   Engine-aware: identify the relevant database and version for
    engine-specific guidance.
-   Connected knowledge: link glossary terms, articles, tools, commands,
    metrics, labs, and incidents.
-   Evidence-based: prioritize official documentation and trustworthy
    technical references.
-   Safe practice: distinguish examples, simulations, read-only
    inspection, and destructive operations.
-   Bilingual by design: support English and Bahasa Indonesia
    consistently.
-   Progressive depth: serve beginners and experienced practitioners.
-   Version-aware: include applicability and review dates.
-   No false equivalence: compare concepts carefully; similar names do
    not mean identical implementation.
-   Preserve existing strengths and working functionality.

### Audiences

Students, beginners, application developers, junior and senior DBAs,
production support engineers, database reliability engineers, data
analysts, data engineers, performance engineers, architects, and
interview candidates.

## 3. Existing Product Context and Navigation

Preserve the five main destinations:

1.  Studio & Lab
2.  Tantangan SQL
3.  Jalur Profesi
4.  Pusat Pengetahuan
5.  Katalog Alat

Recommended structure:

-   **Studio & Lab:** Query Studio, Database Lab, Database Workspace,
    SQL editor, result explorer, engine selector, sandbox controls.
-   **Tantangan SQL:** SQL exercises, engine-specific challenges,
    optimization challenges, troubleshooting challenges.
-   **Jalur Profesi:** beginner-to-advanced paths, DBA/developer/data
    engineer/analyst/performance engineer paths, skill maps,
    assessments.
-   **Pusat Pengetahuan:** Fundamentals, Database Encyclopedia,
    Monitoring & Observability, DBA Field Handbook, Glossary & Field
    Terminology, Troubleshooting & Incident Library, Performance
    Engineering, High Availability & Disaster Recovery, Cross-Database
    Comparison.
-   **Katalog Alat:** database clients, monitoring products, performance
    tools, backup/recovery, migration/schema, infrastructure, security,
    data engineering.

A dashboard may be optional, but it must not obstruct direct access to
Studio & Lab.

## 4. Database Encyclopedia

### 4.1 Purpose and coverage

Create a dedicated profile for each database engine, from introductory
concepts to production administration.

**Initial priority:** PostgreSQL, MySQL, MariaDB, Oracle Database,
Microsoft SQL Server, IBM Db2, SQLite.

**Expansion:** MongoDB, Redis, Apache Cassandra, ClickHouse, Snowflake,
Google BigQuery, Elasticsearch, DuckDB, Apache HBase, Apache Druid,
CockroachDB, TiDB.

Do not imply that every encyclopedia engine is executable in the
sandbox. Documentation coverage and actual runtime support are separate
capabilities.

### 4.2 Standard database profile

Every profile should include:

1.  Overview, use cases, product family, editions, licensing notes, and
    deployment models.
2.  Version and lifecycle information.
3.  Architecture overview and visual component explorer.
4.  Storage, memory, transaction, and concurrency internals.
5.  Query language and dialect notes.
6.  Indexing and query optimization.
7.  Administration and configuration.
8.  Monitoring and performance diagnostics.
9.  Backup, restore, and recovery.
10. Replication, clustering, and high availability.
11. Security, authentication, authorization, and auditing.
12. Troubleshooting and common errors.
13. Hands-on labs and safe examples.
14. Interview questions and knowledge checks.
15. Official references, version scope, and last-reviewed date.

### 4.3 Visual architecture explorer

Users select a component and see its definition, responsibilities,
relationships, data flow, configuration, monitoring metrics, diagnostic
commands, common failure modes, and related glossary entries/articles.

**Oracle components:** instance/database, SGA, PGA, shared pool, buffer
cache, redo log buffer, background processes, control files, datafiles,
online redo logs, tablespaces, segments, undo, archive logs, RMAN, Data
Guard, RAC.

**PostgreSQL components:** postmaster/backend processes, shared buffers,
WAL, checkpoints, MVCC, tuple versions, vacuum/autovacuum,
catalogs/statistics, tablespaces, relation files, streaming replication,
replication slots.

**MySQL/InnoDB components:** server architecture, connection/thread
handling, InnoDB buffer pool, redo/undo logs, doublewrite buffer, binary
log, replication, tablespaces, Performance Schema, sys schema.

**MariaDB components:** server and storage engines, InnoDB/Aria
applicability by version, binary logging, replication, Galera where
applicable, monitoring tables.

**SQL Server components:** Database Engine, buffer pool, memory clerks,
transaction log, TempDB, Query Processor, execution plans, SQL Server
Agent, Query Store, Extended Events, Availability Groups.

**Db2 components:** instance/database, database manager configuration,
buffer pools, tablespaces/containers, transaction logs, package cache,
RUNSTATS, REORG, HADR, backup/recovery utilities.

**SQLite components:** embedded architecture, database file, B-tree
pages, journaling, WAL mode, locking, transactions, query planner,
application integration.

### 4.4 Version-aware content

Show product name, version scope, feature availability/deprecation,
last-reviewed date, release notes, and official documentation. Never
label a runtime with an unverified version. Keep MySQL and MariaDB
distinct; do not use ambiguous labels such as "MySQL 11" when MariaDB
11.x is intended.

## 5. Monitoring & Observability Knowledge Center

### 5.1 Purpose

Make monitoring a major knowledge category. Teach users to observe
database health, identify abnormal behavior, interpret metrics,
investigate symptoms, and verify remediation. This is a
learning/reference area, not a claim that WIYATA itself operates a
production monitoring service.

### 5.2 Monitoring taxonomy

-   **Availability and health:** instance status, uptime,
    service/listener availability, connectivity, cluster/node health,
    SLI/SLO concepts.
-   **CPU and process:** utilization, user/system CPU, CPU wait, run
    queue, process/thread counts, context switches.
-   **Memory:** Oracle SGA/PGA, PostgreSQL shared buffers and OS cache,
    MySQL InnoDB buffer pool, SQL Server buffer pool/memory clerks, Db2
    buffer pools, physical memory, swap, page faults, pressure, cache
    metrics.
-   **Storage and capacity:** database size/growth, tablespaces,
    datafiles, filegroups, disk space, table/index size, temporary
    storage, transaction/archive logs, forecasting.
-   **Disk I/O:** IOPS, throughput, read/write latency, queue depth, I/O
    wait, sequential/random I/O, saturation.
-   **Connections and sessions:** total/active/idle/blocked sessions,
    pool utilization, connection limits, churn, authentication failures,
    long-running sessions.
-   **SQL performance:** latency, duration, throughput, slow queries,
    plan changes, rows examined/returned, logical/physical reads,
    CPU/I/O time, top SQL.
-   **Locks and waits:** blocking, deadlocks, lock waits, latches,
    contention, transaction age, long-running transactions,
    engine-specific wait events.
-   **Transactions and logs:** commit/rollback rate, log generation,
    WAL, redo/undo, checkpoints, log flush latency, log space pressure.
-   **Replication and HA:** replication lag, replica health,
    apply/replay delay, slot retention, log shipping,
    synchronous/asynchronous modes, failover, quorum.
-   **Backup and recovery:** last successful backup, age, duration,
    size, throughput, failures, archive availability, restore
    validation, RPO/RTO.
-   **Network:** latency, packet loss, throughput, DNS/connectivity,
    TLS/certificates, listener/port reachability, resets/timeouts.
-   **Logs and events:** alert/error logs, audit logs, OS logs,
    agent/scheduler logs, kernel messages, application errors, event
    correlation.
-   **Capacity and trends:** growth, resource trends, storage runway,
    workload peaks, forecasts and assumptions.

### 5.3 Metric dictionary requirements

Every metric entry must include:

-   Name, aliases, definition, unit, and data type.
-   Why it matters and calculation (if applicable).
-   Collection frequency and aggregation caveats.
-   Supported engines and versions.
-   Native view/function/counter/command.
-   Example query or command and example output.
-   Interpretation and common misleading interpretations.
-   Related symptoms and metrics.
-   Suggested investigation path and alerting considerations.
-   References and review date.

Do not publish universal thresholds as if they fit every environment.
Explain baseline, workload, hardware, service objectives, and business
context.

### 5.4 Database-native monitoring references

**Oracle:** Enterprise Manager, dynamic performance views (`V$`, `GV$`),
AWR/ASH/ADDM with licensing and entitlement warnings, alert log/ADR,
RMAN, Data Guard, wait events, session diagnostics.

**PostgreSQL:** `pg_stat_activity`, `pg_stat_database`,
`pg_stat_statements`, `pg_stat_io` where supported, `pg_locks`,
`pg_stat_replication`, `pg_stat_wal`, version-specific background-writer
statistics, `EXPLAIN`, logs, extensions.

**MySQL:** Performance Schema, `sys` schema, `SHOW GLOBAL STATUS`,
`SHOW ENGINE INNODB STATUS`, InnoDB metrics, process list, slow query
log, replication status.

**MariaDB:** Information Schema/Performance Schema availability by
version, `SHOW GLOBAL STATUS`, InnoDB status, slow query log,
replication and Galera status where applicable.

**SQL Server:** DMVs/DMFs, Query Store, Extended Events, Agent history,
wait statistics, `sys.dm_exec_requests`, `sys.dm_os_wait_stats`, index
usage statistics, error log, Always On health.

**Db2:** `MON_GET` functions, database/workload metrics, buffer pool
metrics, lock/transaction monitoring, package cache, HADR, `db2pd`,
diagnostic logs.

### 5.5 External monitoring platforms

Catalog tools by purpose and support, including:

-   Metrics/visualization: Prometheus, Grafana, VictoriaMetrics,
    InfluxDB, Telegraf, OpenTelemetry.
-   Infrastructure/availability: Zabbix, Nagios, Checkmk, Icinga,
    Netdata, Centreon.
-   Database-focused: Percona Monitoring and Management (PMM), pgwatch,
    pgMonitor, Oracle Enterprise Manager, native vendor tools.
-   Commercial observability: Datadog, Dynatrace, New Relic, Elastic
    Observability, Splunk, AppDynamics.

Each tool page explains purpose, supported databases, collection method,
deployment, strengths, limitations, verified licensing/pricing category,
official docs, and alternatives. Do not imply endorsement or
affiliation.

### 5.6 Operating-system monitoring

Include Linux command references:

-   CPU/process: `top`, `htop`, `ps`, `pidstat`, `mpstat`.
-   Memory: `free`, `vmstat`, `sar`.
-   Disk: `iostat`, `iotop`, `lsblk`, `df`, `du`.
-   Network: `ss`, `ip`, `ping`, `traceroute`, `mtr`.
-   Files/processes: `lsof`, `fuser`.
-   Logs: `journalctl`, `dmesg`.
-   System activity: `sar`, `nmon`.

Document purpose, safe usage, flags, sample output, interpretation,
permissions, and caveats.

## 6. Database Glossary & Field Terminology

### 6.1 Purpose

Create a searchable bilingual dictionary of technical terms, acronyms,
abbreviations, operational phrases, and expressions commonly used by
DBAs and database engineers. Explain how terms are used in actual work,
not only their dictionary definitions.

### 6.2 Categories

Database fundamentals; SQL/query processing; architecture/internals;
memory/cache; storage/filesystems; transactions/concurrency;
locks/latches/waits; indexing/optimization; monitoring/observability;
backup/recovery; replication/HA; security/auditing;
networking/connectivity; cloud/managed databases; data
engineering/analytics; incident management/production support; capacity
planning/service management.

### 6.3 Required fields per term

-   Canonical term, acronym, abbreviation, synonyms, and aliases.
-   English definition and Bahasa Indonesia explanation.
-   Category and skill level.
-   Engines and versions where applicable.
-   Engine-specific differences.
-   Practical example and related SQL/command.
-   Related metric, incident, and terms.
-   Official/trusted references and review date.

### 6.4 Initial terminology seed

**General:** DBA, DBMS, RDBMS, OLTP, OLAP, ACID, CRUD, DDL, DML, DCL,
TCL, schema, catalog, instance, database, cluster, metadata, data
dictionary, system catalog.

**Storage/architecture:** tablespace, datafile, tempfile, filegroup,
segment, extent, page, block, buffer pool, buffer cache, shared buffers,
SGA, PGA, TempDB, WAL, redo log, undo log, transaction log, binary log,
checkpoint, archive log, journal, heap, B-tree, LSM tree, page split,
fragmentation.

**Query/performance:** execution plan, explain plan, actual plan, cost
estimate, cardinality, selectivity, full table scan, sequential scan,
index scan, index seek, nested loop, hash join, merge join, predicate
pushdown, partition pruning, statistics, histogram, stale statistics,
sargability, parameter sniffing, plan cache, logical read, physical
read, buffer hit, query latency, throughput, concurrency.

**Transactions/concurrency:** commit, rollback, savepoint, isolation
level, dirty read, non-repeatable read, phantom read, MVCC, snapshot,
row version, lock, latch, mutex, blocking, blocker, blocked session,
deadlock, lock escalation, lock timeout, long-running transaction, idle
in transaction.

**Monitoring/operations:** baseline, threshold, alert, alert fatigue,
wait event, wait class, wait statistic, bottleneck, saturation,
contention, IOPS, throughput, latency, queue depth, CPU utilization,
load average, run queue, cache hit ratio, buffer hit ratio, session,
connection, connection pool, slow query, top SQL, replication lag, apply
lag, replay lag, failover, switchover, failback, RPO, RTO, SLA, SLO,
SLI, MTTR, MTBF, RCA, postmortem.

**Backup/recovery:** full/incremental/differential backup,
physical/logical backup, PITR, restore, recover, recovery catalog,
consistency, backup validation, restore test, hot/cold/online backup,
archive retention, backup retention.

**Production field phrases:** "DB is down," "instance is up but the
application cannot connect," "tablespace is almost full," "session is
blocking other sessions," "query is hanging," "CPU is spiking," "I/O is
saturated," "replication is lagging," "backup job failed," "failover was
triggered," "check the alert log," "collect evidence before restarting,"
"change window," "maintenance window," and "rollback plan."

For field phrases, explain likely intent, what must be verified, and
which assumptions must not be made.

### 6.5 Search behavior

Support English and Indonesian, acronyms and expansions, aliases, common
misspellings, partial matches, related concepts, engine filters, and
skill-level filters. Searches such as "blocked session," "blocking,"
"session nge-lock," and "sesi terblokir" should find the canonical entry
while showing standard terminology.

## 7. DBA Field Handbook

### 7.1 Topics

Daily health checks; session/connection inspection; tablespace/storage
checks; CPU/memory/I/O investigation; slow query investigation;
blocking/deadlock investigation; backup monitoring; replication health;
user/privilege review; index/statistics maintenance; startup/shutdown
concepts; patch/upgrade preparation; capacity planning; incident
communication; change management and rollback.

### 7.2 Command reference template

Each command entry includes task/use case, supported engine/version,
required privilege, read-only/state-changing classification,
command/SQL, parameter explanation, example output, interpretation,
common errors, risks/rollback, related terms/articles, and official
references.

Clearly label: read-only inspection, administrative read,
state-changing, potentially disruptive, destructive, privileged, and
version-dependent. Never present a destructive command as routine
diagnosis.

## 8. Troubleshooting & Incident Library

### 8.1 Initial scenario catalog

-   **Performance:** high CPU, slow SQL, query regression, high disk
    latency, memory pressure, connection exhaustion, excessive parsing,
    temp-space pressure.
-   **Concurrency:** blocking, deadlocks, long transactions, lock
    escalation, latch/mutex contention.
-   **Storage:** tablespace full, datafile cannot extend, transaction
    log full, WAL/archive destination full, disk full, unexpected
    growth.
-   **Availability:** database unavailable, listener/service
    unavailable, failed startup, cluster node failure, failover failure,
    application connection failure.
-   **Replication:** replication lag, replica disconnected/stopped, log
    shipping failure, replication slot retention/log buildup.
-   **Backup/recovery:** backup failure/slowdown, missing archive logs,
    restore failure, recovery target mismatch, untested recovery.
-   **Security:** login failures, privilege errors, suspicious access,
    expired credentials/certificates, audit investigation.

### 8.2 Mandatory incident article template

Incident/severity; description; symptoms; business/technical impact;
first checks; monitoring signals; diagnostic commands/SQL; example
outputs and interpretation; possible root causes; investigation decision
tree; remediation options; risk assessment; approval/maintenance-window
considerations; rollback; post-remediation verification; evidence to
capture; prevention/alerting; related glossary terms; engine/version
scope; references and review date.

Never infer one root cause from a symptom alone. Teach hypothesis
testing and evidence collection.

## 9. Performance Engineering

Cover query lifecycle and optimizer behavior, execution-plan reading,
index design/tradeoffs, statistics/cardinality, join algorithms,
partitioning/pruning, caching, concurrency/contention, wait
events/statistics, I/O, memory pressure, workload analysis,
benchmarking, regression analysis, and capacity planning.

Use engine-specific examples and version notes. Explain why an index,
cache-hit ratio, or query plan cannot be judged in isolation from
workload and environment.

## 10. High Availability, Backup & Disaster Recovery

Cover availability architecture, replication models,
synchronous/asynchronous replication, clustering/quorum,
failover/switchover/failback, backup types/retention, logical/physical
backup, PITR, recovery testing, RPO/RTO, DR runbooks, backup
immutability, cross-region recovery, and operational readiness.

A successful backup job does not prove a database can be restored.
Include restore tests and evidence in the guidance.

## 11. Cross-Database Comparison Center

### 11.1 Comparison dimensions

Architecture/process model; memory; storage; transaction logging;
concurrency/isolation; index types; optimizer/plans; statistics;
monitoring; backup/recovery; replication/HA; security/auditing; SQL
dialect/functions; partitioning; version lifecycle/compatibility.

### 11.2 Introductory comparison

  -------------------------------------------------------------------------------------------
  Concept        Oracle      PostgreSQL       MySQL / InnoDB SQL Server         IBM Db2
  -------------- ----------- ---------------- -------------- ------------------ -------------
  Memory         SGA, PGA    Shared buffers   InnoDB buffer  Buffer pool and    Buffer pools
  concepts                   plus OS cache    pool           memory clerks      and memory
                                                                                sets

  Transaction    Redo and    WAL and MVCC     Redo, undo,    Transaction log    Transaction
  logging        undo        tuple versions   binary log                        logs

  Query          Explain     EXPLAIN,         EXPLAIN,       Actual/estimated   EXPLAIN and
  diagnostics    Plan, SQL   statistics views Performance    plans, Query Store MON_GET
                 Monitor,                     Schema                            
                 AWR/ASH                                                        
                 subject to                                                     
                 licensing                                                      

  Backup         RMAN        pg_basebackup,   Native and     Native             Db2 utilities
  ecosystem                  pgBackRest,      third-party    backup/restore     
                             Barman, logical  tools                             
                             tools                                              

  High           Data Guard, Streaming        Replication,   Always On and      HADR
  availability   RAC         replication and  Group          failover           
                             ecosystem tools  Replication,   clustering         
                                              InnoDB Cluster                    
  -------------------------------------------------------------------------------------------

This is a conceptual map, not a claim of equivalence. Each comparison
must explain differences and applicability.

### 11.3 UX

Allow users to select two to five engines and a topic, view a concise
comparison, expand technical details, see version caveats, open profile
pages, and follow related labs/glossary entries. Copyable examples must
be safe and engine-specific.

## 12. Learning Modes and Knowledge Connections

**Learn:** explanations, diagrams, terminology, examples, references,
knowledge checks.\
**Practice:** relevant Studio & Lab environment, safe SQL, query plans,
diagnostic exercises, guided challenges.\
**Work:** DBA runbooks, daily checklists, operational commands, incident
response, change/rollback plans.

Every article should link to relevant labs, challenges, glossary terms,
database profiles, metrics, tools, incidents, and career skills. Every
lab should link back to the concepts it teaches.

## 13. Professional Tools Catalog

Keep this as an educational directory, not a claim that WIYATA operates
or integrates every product.

**Database clients/admin:** DBeaver, Oracle SQL Developer,
SQLcl/SQL\*Plus, pgAdmin, psql, MySQL Workbench, HeidiSQL, SSMS, IBM Db2
tools, DataGrip, Navicat.

**Monitoring/observability:** Oracle Enterprise Manager, Prometheus,
Grafana, Zabbix, Nagios, Checkmk, Icinga, PMM, Datadog, Dynatrace, New
Relic, Elastic, Splunk, AppDynamics, OpenTelemetry.

**Backup/recovery:** RMAN, pgBackRest, Barman, `pg_dump`,
`pg_basebackup`, Percona XtraBackup, MySQL Enterprise Backup, SQL Server
backup/restore, Db2 utilities.

**Migration/schema:** Flyway, Liquibase, AWS DMS, SchemaSpy,
dbdiagram.io, Mermaid, native vendor migration tools.

**Infrastructure/automation:** Docker, Kubernetes, Ansible, Terraform,
Jenkins, GitHub Actions, GitLab CI/CD.

**Security/auditing:** HashiCorp Vault, Wazuh, OpenSSL, native database
auditing, cloud IAM/secrets, vendor security products.

**Data engineering:** Apache Airflow, dbt, Spark, Kafka, Trino,
Debezium.

Each tool page includes name/logo, category, purpose, use cases,
supported platforms, deployment, features, limitations, verified
licensing/pricing category, alternatives, official links, related WIYATA
guides, and review date. Respect trademarks, licenses, and source terms.

## 14. Search and Discovery

Global search covers articles, profiles, glossary, commands, metrics,
tools, incidents, paths, and challenges. Filters include language,
engine, version, topic, skill level, content type, command risk, and
review date.

Support exact terms, acronym expansion, English/Indonesian aliases,
common field phrases, typo tolerance where useful, and related concepts.
Rank exact title/acronym matches highly. Show why a result matches and
its engine/version scope. Track searches with no useful results to guide
content planning.

## 15. Content Model and Data Architecture

### 15.1 Suggested entities

`knowledge_categories`, `knowledge_articles`,
`knowledge_article_translations`, `knowledge_references`,
`database_engines`, `database_versions`, `database_profiles`,
`database_components`, `database_component_relations`, `glossary_terms`,
`glossary_translations`, `glossary_aliases`, `monitoring_metrics`,
`monitoring_metric_sources`, `monitoring_tools`, `dba_commands`,
`incident_scenarios`, `incident_steps`, `comparison_topics`,
`comparison_entries`, `learning_paths`, `learning_path_steps`,
`knowledge_relations`, `content_reviews`, `content_change_history`.

### 15.2 Common content fields

UUID, slug, title, summary, language, body/structured blocks, category,
engine references, version applicability, skill level, tags,
author/editor, publication status, created/updated/published timestamps,
last-reviewed date, review-due date, source references,
license/attribution notes.

### 15.3 Typed relationships

`explains`, `requires`, `compares_with`, `used_by`, `monitored_by`,
`diagnosed_by`, `practiced_in`, `related_to`, `supersedes`,
`version_specific_to`.

Use structured relationships to generate related content rather than
manually maintaining every list.

### 15.4 Example seed record

``` json
{
  "slug": "oracle-pga",
  "type": "glossary_term",
  "canonical_term": "Program Global Area",
  "acronym": "PGA",
  "translations": {
    "en": {
      "definition": "A memory area associated with an Oracle server process.",
      "explanation": "Used for process-private memory such as work areas."
    },
    "id": {
      "definition": "Area memori yang terkait dengan proses server Oracle.",
      "explanation": "Digunakan untuk memori privat proses, termasuk work area."
    }
  },
  "engines": ["oracle"],
  "skill_level": "intermediate",
  "related_slugs": ["oracle-sga", "oracle-memory-monitoring"],
  "references": [
    {
      "title": "Oracle Database Concepts",
      "url": "https://docs.oracle.com/en/database/",
      "source_type": "official_documentation"
    }
  ],
  "review_status": "needs_technical_review"
}
```

This is illustrative; validate it against the final application schema.

## 16. Sources, Accuracy, and Editorial Governance

### 16.1 Source hierarchy

Prefer official vendor documentation, release notes/manuals,
standards/specifications, maintainer documentation, peer-reviewed
books/academic material, reputable technical publications, and community
discussions only as supplementary context.

### 16.2 Editorial workflow

Identify gap → outline → gather references → draft → define
engine/version scope → add example → add risks/caveats → link related
content → technical review → language/editorial review → publish →
schedule review.

### 16.3 Content status

Draft, AI-assisted draft, technical review, editorial review, published,
needs update, archived.

AI-assisted content must not be automatically published as authoritative
technical guidance without review, especially production commands,
security, backup/recovery, and licensing.

### 16.4 Licensing and attribution

Link to official documentation instead of copying large sections.
Respect licenses and website terms. Record attribution and license
details. Do not republish code, datasets, logos, or screenshots without
checking permissions. Prefer original WIYATA explanations and examples.
Mark community content clearly if introduced later.

### 16.5 Review cadence

Fast-changing configuration/version pages: every 3--6 months. Stable
fundamentals: every 12 months. Security/licensing: when upstream changes
and at least every 3--6 months. Pricing/availability: verify before
publication and periodically. Runbooks: after relevant incidents or
major version changes. These are editorial targets, not guarantees.

## 17. UX and Interface Requirements

### Article page

Breadcrumbs; title/summary; engine/version/skill metadata; last-reviewed
date; table of contents; content; diagrams; copyable SQL/commands;
risk/permission labels; related glossary, metrics, tools, labs,
incidents; official references; feedback action.

### Database profile

Engine identity; overview/use cases; version scope; architecture;
interactive component map; topic navigation; operational references;
labs/challenges; official docs.

### Glossary

Prominent search; English/Indonesian toggle; acronym/alias support;
filters; definition and practical explanation; related terms; examples.

### Monitoring

Metric category navigation; searchable metric list; engine-specific
source; sample query/command; interpretation/caveats; related
incidents/tools.

### Accessibility and responsive behavior

Responsive desktop/tablet/mobile; keyboard-accessible search/navigation;
sufficient contrast; do not communicate status by color alone; text
alternatives for diagrams; readable code blocks; adapt dense tables for
mobile.

### Localization

Support `en` and `id` across navigation, metadata, explanations,
glossary, search, errors, learning paths, and tool descriptions.
Preserve canonical English technical terms commonly used in Indonesian
workplaces and explain them naturally in Bahasa Indonesia.

## 18. Technical Architecture Recommendations

Audit the existing stack first. Reuse it unless there is a concrete
reason to change it. Prefer a modular monolith initially; do not
introduce microservices solely for the Knowledge Center.

### Suggested modules

Identity/preferences; Studio/query services; sandbox orchestration;
knowledge content; search/indexing; glossary; monitoring reference
catalog; tools catalog; learning/progress; challenges/assessments;
editorial/admin; audit/observability.

### Technology options

These are options, not mandatory rewrites: existing frontend or
Next.js/TypeScript for greenfield; existing design system or accessible
component primitives; Monaco or existing editor; existing backend or
FastAPI for greenfield; PostgreSQL for platform data; SQLAlchemy/Alembic
or current equivalents; PostgreSQL full-text search initially; Redis
only when justified; Mermaid for diagrams and a safe diagram library for
interactive explorers.

### API outline

``` text
GET /api/v1/knowledge/categories
GET /api/v1/knowledge/articles
GET /api/v1/knowledge/articles/{slug}
GET /api/v1/knowledge/search?q=
GET /api/v1/databases
GET /api/v1/databases/{engine}
GET /api/v1/databases/{engine}/components
GET /api/v1/glossary
GET /api/v1/glossary/{slug}
GET /api/v1/monitoring/metrics
GET /api/v1/monitoring/metrics/{slug}
GET /api/v1/monitoring/tools
GET /api/v1/dba/commands
GET /api/v1/incidents
GET /api/v1/incidents/{slug}
GET /api/v1/comparisons
GET /api/v1/comparisons/{topic}
GET /api/v1/learning-paths
```

Adapt routes to existing conventions. Editorial endpoints require
authorized roles and audit history.

### Search implementation

Normalize case/whitespace; index titles, summaries, body, tags, aliases,
translations, and related terms; rank exact title/acronym matches;
filter by engine/version/language/type; add typo tolerance only if
useful; track no-result searches. Do not add vector databases or RAG
before evaluating structured search.

## 19. Security and Operational Safety

### Command classification

Every command is labeled read-only, administrative read, state-changing,
potentially disruptive, destructive, privileged, and/or
version-dependent.

### Execution policy

-   Reading an article never executes its command.
-   Generated SQL never executes automatically; require explicit user
    action.
-   Enforce read-only mode server-side and through database grants.
-   Use AST-aware SQL policy; regex alone is insufficient.
-   Parameterize values; enforce timeouts, cancellation, row/byte
    limits, and quotas.
-   Disable multi-statement execution by default.
-   Restrict destructive, privilege-changing, file, network, and
    administrative operations unless a dedicated safe lab explicitly
    supports them.
-   Use isolated disposable environments for hands-on practice.
-   Never expose credentials in frontend, prompts, logs, analytics, or
    errors.

### Production guidance

Label destructive commands. Include backup, approval,
maintenance-window, and rollback considerations where relevant.
Encourage evidence collection before restarting or terminating
processes. Never recommend killing sessions, restarting instances, or
changing memory settings based on a symptom alone. Distinguish
diagnostic examples from production-ready runbooks.

### Licensing

Some vendor features have licensing/entitlement conditions. AWR, ASH,
and ADDM content must include clear warnings and link to current
official licensing documentation. Do not imply a feature is free merely
because a view or command exists.

## 20. Quality Assurance and Acceptance Criteria

### Content acceptance

A publishable item has a clear title/summary, language/category,
engine/version scope, trustworthy references, permission/risk labels for
commands, technically reviewed examples, related links, review date, and
compliant use of third-party content.

### Functional acceptance

-   Knowledge navigation works on desktop/mobile.
-   Search finds English, Indonesian, acronym, and alias variants.
-   Filters work together.
-   Article and related-content links resolve.
-   Database components open correctly.
-   Comparisons explain differences.
-   Code copy preserves formatting.
-   Language switching preserves current page where possible.
-   Loading, empty, error, and not-found states are clear.
-   Editorial permissions are enforced; drafts are not public.
-   Search index updates when content changes.

### Technical acceptance

No secrets exposed; public endpoints appropriately cached; admin
endpoints protected; content changes auditable; migrations tested;
search performance measured; mobile/accessibility tested; engine/version
claims evidenced.

### Studio & Lab integration acceptance

Knowledge links to the correct lab; exercises state actual runtime
support; runtime versions match labels; read-only restrictions are
server-enforced; sample results are never confused with executed
results; unavailable sandboxes are clearly identified; unsupported
engines are not presented as executable.

## 21. Implementation Roadmap

### Phase 0 --- Repository and product audit

Inspect repository, frameworks, backend, database, routes, auth,
admin/editor tools, Knowledge Center, Professional Tools, Studio & Lab,
engine registry, design system, localization, and tests. Produce a gap
report. **Exit:** no blind rewrite; plan matches actual code.

### Phase 1 --- Knowledge foundation

Create structured content schemas, bilingual metadata, references,
editorial states, review dates, global search, article templates, and
related links. **Exit:** reviewed content can be published, searched,
and linked.

### Phase 2 --- Database Encyclopedia

Add initial profiles, architecture overviews, version scope, first
component explorers, and links to labs. **Exit:** users can explore
initial engines and their operational topics.

### Phase 3 --- Glossary and terminology

Build glossary schema/search, seed high-value terms, add Indonesian
explanations, aliases, engine scope, examples, and article links.
**Exit:** common terms are findable through acronym, English,
Indonesian, and field phrases.

### Phase 4 --- Monitoring & Observability

Add taxonomy, metric dictionary, native monitoring references, OS
commands, tool catalog, and incident links. **Exit:** users can move
from metric/symptom to diagnostic source and explanation.

### Phase 5 --- DBA Handbook and Incident Library

Add command reference, risk classification, operational checklists, and
initial incident runbooks. **Exit:** users can follow reviewed
troubleshooting guides.

### Phase 6 --- Comparison and learning integration

Add cross-database comparisons, Learn/Practice/Work modes,
knowledge-to-lab links, quizzes, and assessments. **Exit:** users move
from concept to comparison to practice.

### Phase 7 --- Expansion and maintenance

Add engines/tools, feedback, content gap reporting, search improvements,
review reminders, and freshness metrics. **Exit:** knowledge can grow
without losing quality.

## 22. Recommended Initial Content Backlog

**Profiles:** PostgreSQL, Oracle, MySQL/InnoDB, SQL Server, IBM Db2,
MariaDB, SQLite architecture.

**Glossary:** 100--150 high-value terms across fundamentals,
performance, monitoring, storage, concurrency, and operations; include
common abbreviations and Indonesian field phrases.

**Monitoring:** CPU, memory pressure, cache/buffer metrics and caveats,
disk latency/IOPS, active sessions, connection saturation,
blocking/deadlocks, slow queries/top SQL, replication lag,
tablespace/database growth, backup freshness/restore validation, wait
events/statistics.

**Incidents:** high CPU, slow query, blocking session, deadlock,
tablespace/disk full, connection exhaustion, replication lag, backup
failure, database unavailable, high disk latency.

**Handbook:** daily health check, session inspection, storage check,
backup verification, replication check, slow SQL investigation, blocking
investigation, change/rollback checklist.

## 23. Analytics and Content Quality Metrics

Measure usefulness, not just article count:

-   Search success and no-result rate.
-   Article engagement/completion.
-   Related-content click-through.
-   Knowledge-to-lab conversion.
-   Challenge completion after reading.
-   Glossary search success.
-   Most-used profiles and metrics.
-   Content freshness and overdue reviews.
-   User feedback and reported inaccuracies.
-   Broken reference/link rate.

Do not collect sensitive SQL, credentials, or production data as
analytics.

## 24. Complete Coding-Agent Instructions

You are improving the existing WIYATA application, not creating an
unrelated product.

### Before coding

1.  Inspect the repository and identify frontend/backend frameworks and
    versions.
2.  Identify database schemas, migrations, API routes, authentication,
    and editorial/admin capabilities.
3.  Inspect existing Knowledge Center and Professional Tools.
4.  Inspect Studio & Lab and its engine registry.
5.  Identify reusable UI components, design tokens, localization, and
    content patterns.
6.  Run existing tests and record baseline failures.
7.  Produce a gap analysis mapped to this specification.

### Implementation rules

-   Preserve brand, working features, and Studio & Lab prominence.
-   Preserve the five main navigation destinations unless a documented
    reason supports a change.
-   Do not replace architecture without evidence.
-   Prefer structured content and reusable templates over hardcoded
    article pages.
-   Support English and Bahasa Indonesia.
-   Make engine/version applicability explicit.
-   Build typed relationships and cross-links.
-   Use official references and review dates.
-   Separate editorial workflow from published content.
-   Test search, filters, localization, permissions, and relationships.
-   Technically review all engine-specific examples.
-   Label command risk and required privileges.
-   Do not claim an engine is runnable until its runtime and adapter are
    tested.
-   Do not turn the monitoring catalog into a live monitoring service
    without separate scope approval.
-   Avoid premature vector databases, microservices, and complex AI
    pipelines.
-   Never expose credentials, production data, or secrets.

### Expected deliverables

1.  Repository audit and gap report.
2.  Updated information architecture.
3.  Content schemas and migrations.
4.  Reusable Knowledge Center UI.
5.  Database profile pages.
6.  Glossary and search.
7.  Monitoring taxonomy and metric dictionary.
8.  DBA command handbook.
9.  Incident templates and initial scenarios.
10. Cross-database comparisons.
11. Bilingual seed content.
12. Tests and results.
13. Updated technical documentation.
14. Deployment and rollback instructions.
15. Known limitations and deferred work.

### Definition of done

The content model, public pages, search, cross-links, localization,
editorial controls, and tests work in the deployed application. A visual
mockup or static page alone is not complete implementation.

## 25. Final Product Direction

WIYATA should connect four kinds of knowledge:

1.  **Understand:** concepts, architecture, terminology, and internals.
2.  **Observe:** metrics, logs, monitoring tools, and performance
    signals.
3.  **Operate:** commands, checklists, maintenance, and incident
    runbooks.
4.  **Practice:** SQL Studio, database labs, challenges, and
    simulations.

Example connected journey:

A user searches **"Oracle blocking session"** → reads the definition →
explores Oracle session and lock concepts → opens a safe diagnostic
query → studies sample output → follows a troubleshooting runbook →
practices in a lab → reviews related interview questions.

That connected experience is the goal. Build it incrementally, verify
engine-specific statements, and preserve Studio & Lab as the practical
center of WIYATA.

------------------------------------------------------------------------

# 26. Visual Learning & Interactive Simulation System

## 26.1 Purpose and product direction

WIYATA should teach database concepts through a combination of written
explanations, diagrams, animations, and interactive simulations.

Many important database behaviors happen internally: query parsing,
memory allocation, transaction logging, locking, replication,
checkpointing, and recovery. Text alone can make these mechanisms
difficult to understand. Visual learning should make these processes
observable and explorable.

This capability is a core extension of the Knowledge Center, not a
decorative feature or a separate disconnected product.

The intended learning cycle is:

1.  **Read** --- understand the concept and terminology.
2.  **See** --- explore its architecture, sequence, or behavior
    visually.
3.  **Practice** --- interact with a safe simulation or Studio & Lab
    exercise.
4.  **Operate** --- learn how to observe, diagnose, and manage the
    concept in real environments.

Visual lessons must connect to database profiles, glossary terms,
monitoring metrics, DBA commands, troubleshooting guides, learning
paths, challenges, and Studio & Lab.

## 26.2 Visual learning formats

Use the visual format that best explains the subject. Do not force every
lesson into an animation.

### A. Static technical diagrams

Use for: - Database architecture. - Component relationships. - Memory
layouts. - Storage structures. - Network topology. - High-availability
architecture. - Data flows and system boundaries.

Requirements: - Clear labels and legends. - Consistent visual
notation. - Accessible text alternatives. - Responsive layout. -
Clickable components when additional explanations are useful. - A
textual explanation that remains useful when graphics cannot load.

### B. Step-by-step process animations

Use for: - SQL query lifecycle. - Transaction commit and rollback. -
WAL/redo logging. - Checkpoints. - Index lookup. - Page reads and
writes. - Replication and log application. - Backup and restore
sequences. - Lock acquisition and release. - Failover and recovery.

Requirements: - A clear beginning and end. - Visible current step. -
Explanation synchronized with the animation. - Pause, resume, previous,
next, replay, and reset. - Adjustable playback speed. - No essential
information communicated only through motion or color.

### C. Interactive architecture explorers

Users should be able to select a component and inspect: - Name and
definition. - Purpose. - Inputs and outputs. - Relationships to other
components. - Related processes or data structures. - Relevant
configuration parameters. - Monitoring metrics and diagnostic views. -
Common failure modes. - Related glossary entries and articles. -
Applicable database versions.

### D. Interactive technical simulations

Use when users benefit from changing inputs and observing outcomes.

Examples: - B-tree index traversal. - Full table scan versus index
access. - Transaction isolation and concurrent sessions. - Blocking and
deadlock. - Connection pool saturation. - Replication lag. - Cache
pressure. - Query-plan selection. - Storage growth and capacity
pressure.

A simulation must label its assumptions and must not imply that a
simplified model reproduces every detail of a production database
engine.

### E. Monitoring visualizations

Use charts and animated indicators to explain: - CPU utilization. -
Memory usage and pressure. - Disk IOPS, throughput, and latency. -
Active sessions and connection saturation. - Query latency and
throughput. - Blocking and wait duration. - Replication lag. - Backup
freshness. - Database growth and capacity trends.

Use synthetic or clearly identified sample data. Do not present
fabricated values as live measurements from a user's environment.

### F. Prepared media and narration

Optional prepared animations, Lottie assets, short videos, or narration
can supplement lessons. They must not be the only source of important
technical information.

Provide captions, transcripts, reduced-motion behavior, and a text-based
alternative.

## 26.3 Visual Database Academy

Add a dedicated subsection within the existing Knowledge Center:

**Visual Database Academy**

Initial categories and lesson ideas:

  -----------------------------------------------------------------------
  Category                            Visual lessons
  ----------------------------------- -----------------------------------
  Database Architecture               Oracle, PostgreSQL, MySQL, MariaDB,
                                      SQL Server, Db2, SQLite
                                      architecture

  SQL Internals                       Parsing, binding/analysis,
                                      optimization, execution, result
                                      delivery

  Memory Management                   SGA, PGA, shared buffers, buffer
                                      pool, memory grants

  Storage                             Datafiles, tablespaces, pages,
                                      extents, segments, files and blocks

  Indexing                            B-tree, hash, bitmap, LSM tree,
                                      index traversal and maintenance

  Transactions                        ACID, commit, rollback, isolation,
                                      MVCC and snapshots

  Concurrency                         Locks, latches, blocking, deadlocks
                                      and wait events

  Monitoring                          CPU, memory, I/O, sessions,
                                      latency, throughput and waits

  High Availability                   Replication, clustering, quorum,
                                      failover and failback

  Backup & Recovery                   Full/incremental backup, restore,
                                      PITR and recovery sequence

  Networking                          Client connection, DNS, listener,
                                      authentication, TLS and connection
                                      pool

  Performance                         Execution plans, join algorithms,
                                      caching, bottlenecks and workload
                                      behavior
  -----------------------------------------------------------------------

Start with a small number of carefully reviewed lessons rather than a
large collection of shallow animations.

## 26.4 Priority visual lessons

### Lesson 1 --- SQL query execution lifecycle

Show a simplified lifecycle:

`Client → Parser → Semantic Analysis → Optimizer → Executor → Storage/Buffer Manager → Result`

Explain that actual internal stages differ between database engines and
that some engines combine or reorder work.

Interactive elements: - Select each stage. - Show its input and
output. - Explain syntax errors versus semantic errors. - Show an
illustrative execution plan. - Connect to a safe SQL example. - Link to
engine-specific documentation.

Do not present this generic sequence as an exact internal implementation
for every engine.

### Lesson 2 --- Transactions and ACID

Animate: - BEGIN. - Read and write operations. - COMMIT. - ROLLBACK. - A
simplified failure before commit. - Recovery and durability concepts.

Provide separate explanations for atomicity, consistency, isolation, and
durability. Include a warning that transaction implementation details
differ by engine.

### Lesson 3 --- Index versus table scan

Show: - A table containing sample rows. - A full scan visiting
rows/pages. - An index structure and traversal. - The matching row
lookup. - The extra storage and write-maintenance cost of an index.

Allow users to change: - Table size. - Selectivity. - Whether an index
exists. - Illustrative data distribution.

Explain that the best access path depends on statistics, selectivity,
data distribution, table size, caching, and optimizer cost estimates. Do
not teach that an index is always faster.

### Lesson 4 --- Blocking and deadlocks

Show two or more transactions acquiring locks and waiting.

Controls: - Start transaction A. - Start transaction B. - Acquire
lock. - Request conflicting lock. - Advance time. - Trigger or resolve
the illustrative deadlock.

Explain: - Blocking versus deadlock. - Lock compatibility. - Wait-for
graph. - Deadlock detection. - Victim selection and rollback at a
conceptual level. - Engine-specific differences.

Never imply that every database detects or resolves deadlocks in exactly
the same way.

### Lesson 5 --- Replication and failover

Show: - Primary write. - Log generation. - Log transmission. - Replica
receipt. - Replay/apply. - Replication delay. - Primary failure. -
Promotion or failover. - Client reconnection.

Allow users to change network delay and apply speed in a simplified
simulation. Explain synchronous versus asynchronous replication and the
possible impact on data loss and availability.

### Lesson 6 --- Memory architecture

Create separate engine-specific diagrams: - Oracle SGA and PGA. -
PostgreSQL shared buffers and operating-system page cache. - MySQL
InnoDB buffer pool. - SQL Server buffer pool and memory clerks. - Db2
buffer pools and memory areas.

Do not imply that these components are direct one-to-one equivalents.
Link each component to relevant metrics and diagnostic views.

### Lesson 7 --- Monitoring and resource pressure

Use a synthetic workload to show: - CPU rising. - Memory pressure. -
Disk latency. - Connection saturation. - Query latency. - Queueing and
wait time.

Let the learner introduce or remove a simplified workload factor and
observe the chart. Clearly state that the simulation is educational and
not a predictive production model.

### Lesson 8 --- Backup and recovery

Show: - Backup preparation. - Data and log capture. - Backup
completion. - Failure scenario. - Restore sequence. - Recovery to a
target point. - Validation after recovery.

Explain that backup success is not proof of recoverability. A real
recovery strategy requires tested restore procedures and validated
recovery objectives.

## 26.5 Reusable Visual Lesson Player

Build one reusable player component for process animations and
simulations.

### Required controls

-   Play.
-   Pause.
-   Previous step.
-   Next step.
-   Replay.
-   Reset.
-   Playback speed.
-   Current step and total steps.
-   Progress indicator.
-   Optional timeline scrubber where seeking is valid.
-   Full-screen or expanded view where appropriate.

### Required lesson panels

-   Visualization area.
-   Current step title.
-   Step explanation.
-   Technical detail.
-   Related SQL or command example.
-   Expected output or observation.
-   Related glossary terms.
-   Related article and lab links.
-   Knowledge check.

### Player behavior

-   The learner can complete the lesson without autoplay.
-   Playback stops at the end unless looping is explicitly selected.
-   Reset returns all simulated state to its initial state.
-   Previous and next controls update the explanation and visualization
    together.
-   Speed changes do not skip required instructional states.
-   Keyboard controls are documented and accessible.
-   Reduced-motion preference is respected.
-   Mobile controls remain usable without covering important diagram
    content.

### Suggested player states

-   Idle.
-   Playing.
-   Paused.
-   Step complete.
-   Completed.
-   Error.
-   Reduced-motion/static mode.

## 26.6 Technology strategy

Choose the lightest technology that satisfies the learning requirement.

  -----------------------------------------------------------------------
  Technology              Recommended use         Guidance
  ----------------------- ----------------------- -----------------------
  SVG                     Interactive             Preferred for most
                          architecture and        technical diagrams
                          process diagrams        

  Mermaid                 Flowcharts, sequence    Good for maintainable
                          diagrams, ER diagrams   text-defined diagrams

  CSS animations          Simple transitions and  Use for lightweight
                          emphasis                effects

  React/JavaScript        Interactive simulations Preferred for
                          and synchronized lesson interactive learning
                          state                   

  D3.js                   Data-driven and complex Use only when its
                          visualizations          capabilities are needed

  Lottie                  Prepared animation      Supplementary, not the
                          assets                  default for interactive
                                                  diagrams

  Canvas/WebGL            High-volume or          Use only when SVG/DOM
                          specialized             is insufficient
                          visualization           

  Three.js                Optional 3D             Low priority; avoid
                          architecture            unnecessary complexity
                          visualization           
  -----------------------------------------------------------------------

Recommended default: - SVG + React for most interactive diagrams. -
Mermaid for authored flowcharts and sequence diagrams. - CSS for simple
motion. - Lottie for selected prepared assets. - D3.js for complex
data-driven visualizations only when justified.

Do not use GIF or video as the default format for technical lessons that
need user interaction, synchronized explanations, or selectable
components.

## 26.7 Visual lesson content schema

Visual lessons should be data-driven and reusable.

Suggested metadata:

``` json
{
  "slug": "database-deadlock",
  "type": "interactive_simulation",
  "category": "concurrency",
  "engines": ["oracle", "postgresql", "mysql", "sqlserver"],
  "languages": ["en", "id"],
  "difficulty": "intermediate",
  "visual_type": "svg_react_simulation",
  "estimated_duration_minutes": 8,
  "reduced_motion_supported": true,
  "sections": [
    "introduction",
    "visualization",
    "step_explanation",
    "sql_example",
    "diagnosis",
    "knowledge_check"
  ],
  "controls": [
    "play",
    "pause",
    "step_forward",
    "step_backward",
    "reset",
    "speed"
  ],
  "review_status": "needs_technical_review"
}
```

The example is illustrative. Validate the final schema against the
application's actual content model.

### Suggested lesson data model

-   `visual_lessons`
-   `visual_lesson_translations`
-   `visual_lesson_steps`
-   `visual_lesson_assets`
-   `visual_lesson_components`
-   `visual_lesson_interactions`
-   `visual_lesson_engine_applicability`
-   `visual_lesson_relations`
-   `visual_lesson_reviews`
-   `visual_lesson_progress`

Store authored lesson definitions separately from rendering code. Avoid
embedding large lesson-specific logic in a single generic component.

## 26.8 Visual content authoring workflow

Every visual lesson should pass through:

1.  Learning objective definition.
2.  Technical source research.
3.  Engine and version scope definition.
4.  Storyboard or process sequence.
5.  Diagram/animation design.
6.  Step explanations in English and Indonesian.
7.  Interactive behavior implementation.
8.  Technical validation.
9.  Accessibility and reduced-motion review.
10. Performance and mobile review.
11. Editorial approval.
12. Publication and scheduled review.

AI may assist with storyboards and draft explanations, but technical
reviewers must validate engine behavior and commands.

## 26.9 Accessibility and performance

-   Support reduced-motion preferences.
-   Provide a static diagram or text alternative.
-   Provide captions/transcripts for narration.
-   Use accessible labels for selectable components.
-   Ensure keyboard navigation.
-   Maintain sufficient contrast.
-   Do not rely on color alone.
-   Avoid flashing and rapid motion.
-   Lazy-load nonessential visual assets.
-   Use responsive SVG viewBox and scalable layout.
-   Optimize asset size and avoid unnecessary animation libraries.
-   Pause or reduce animation when the lesson is not visible where
    technically appropriate.
-   Test on low-memory mobile devices and slower networks.
-   Do not block article reading while visual assets load.

## 26.10 Visual learning acceptance criteria

A visual lesson is complete only when: - It has a clear learning
objective. - The diagram or animation matches the stated engine/version
scope. - Each step has synchronized explanatory text. - Controls work
correctly. - Reset returns the simulation to a valid initial state. -
Reduced-motion and static alternatives are available. - Mobile layout is
usable. - Keyboard navigation and labels are tested. - Performance is
acceptable on representative mobile devices. - Related glossary,
article, lab, and incident links work. - The lesson has technical and
editorial review status. - Sample data and simplified behavior are
clearly labelled.

------------------------------------------------------------------------

## 27. Updated Connected Learning Model

The Knowledge Center should connect four learning experiences:

### Understand

Articles, database profiles, architecture, glossary, and field
terminology.

### See

Static diagrams, interactive architecture explorers, process animations,
and simulations.

### Practice

Studio & Lab, SQL challenges, diagnostic exercises, and safe sandbox
experiments.

### Operate

DBA commands, monitoring references, checklists, troubleshooting guides,
and incident runbooks.

### Example learning journey

A user searches **"Oracle blocking session"**:

1.  Search returns the glossary definition.
2.  The glossary links to Oracle locking and session concepts.
3.  An interactive diagram shows two sessions and their lock
    relationship.
4.  The learner advances through the blocking sequence.
5.  The article provides safe diagnostic SQL and explains its output.
6.  A monitoring page explains relevant session and wait metrics.
7.  An incident guide explains investigation, evidence collection,
    remediation options, and rollback considerations.
8.  A safe lab lets the learner practice with synthetic sessions.
9.  Related interview questions and career-path skills reinforce
    learning.

This connected journey is the desired experience. It must not be a
collection of unrelated pages.

------------------------------------------------------------------------

## 28. Updated Implementation Roadmap

Add the following phases to the existing roadmap. These phases
complement the earlier Knowledge Center, glossary, monitoring, and
incident work.

### Visual Phase A --- Diagram foundation

-   Define visual design conventions and diagram notation.
-   Implement reusable SVG diagram components.
-   Implement clickable architecture components.
-   Add text alternatives and responsive behavior.
-   Deliver initial architecture diagrams for priority engines.

### Visual Phase B --- Process player

-   Implement the reusable Visual Lesson Player.
-   Add synchronized steps and explanations.
-   Add play, pause, previous, next, reset, and speed controls.
-   Add reduced-motion and static modes.
-   Add localization support.

### Visual Phase C --- Core simulations

-   SQL query lifecycle.
-   Transaction and ACID.
-   Index lookup versus table scan.
-   Blocking and deadlock.
-   Replication and failover.
-   Memory architecture.

### Visual Phase D --- Monitoring visualizations

-   Synthetic metric timelines.
-   CPU, memory, disk, sessions, latency, and replication
    visualizations.
-   Metric explanations and related diagnostic references.
-   Clear sample-data labeling.

### Visual Phase E --- Advanced interactive lessons

-   Workload and query-plan simulations.
-   Capacity pressure simulations.
-   Backup/recovery walkthroughs.
-   More engine-specific architecture explorers.
-   Optional advanced visualizations only where they provide measurable
    learning value.

Do not delay the Knowledge Center foundation or core content because
advanced animation is not yet ready. Build the system progressively.

------------------------------------------------------------------------

## 29. Additional Coding-Agent Instructions for Visual Learning

When implementing visual learning:

1.  Audit the existing frontend and design system first.
2.  Reuse current routing, localization, authentication, content models,
    and UI components.
3.  Do not introduce a separate visual-learning application.
4.  Create reusable components for diagrams, step players, simulation
    state, and explanatory panels.
5.  Keep lesson definitions data-driven where practical.
6.  Keep engine-specific simulation logic separate from generic player
    controls.
7.  Use deterministic, resettable simulations for educational examples.
8.  Clearly label simplified models and synthetic metrics.
9.  Do not present sample charts as live monitoring data.
10. Do not use animation to hide missing technical explanations.
11. Provide static and reduced-motion alternatives.
12. Test mobile performance and interaction.
13. Add automated tests for player state transitions, step
    synchronization, reset, localization, and lesson routing.
14. Ensure all visual assets have clear ownership and licensing.
15. Add technical review and version applicability to every
    engine-specific visual lesson.
16. Preserve Studio & Lab as the central practical environment.
17. Do not implement 3D visualization unless a specific lesson justifies
    its complexity.

### Expected visual-learning deliverables

-   Visual design and notation guide.
-   Reusable diagram components.
-   Reusable Visual Lesson Player.
-   Visual lesson content schema.
-   Initial architecture diagrams.
-   Initial process animations.
-   Initial interactive simulations.
-   Synthetic monitoring visualizations.
-   Bilingual lesson content.
-   Accessibility and performance tests.
-   Technical review checklist.
-   Documentation for authoring new visual lessons.

------------------------------------------------------------------------

## 30. Final Expanded Product Direction

WIYATA should combine five connected capabilities:

1.  **Read** --- understand database concepts, architecture, and
    terminology.
2.  **See** --- explore diagrams, animations, and interactive
    simulations.
3.  **Compare** --- understand differences between database engines.
4.  **Practice** --- execute SQL and interact with safe labs.
5.  **Operate** --- use monitoring references, DBA commands, and
    incident runbooks.

The visual learning system is a first-class part of the Knowledge
Center. It should make complex database behavior easier to understand
without sacrificing technical accuracy, accessibility, or performance.

The goal is not to make WIYATA visually busy. The goal is to make
invisible database processes understandable, explorable, and practical.
