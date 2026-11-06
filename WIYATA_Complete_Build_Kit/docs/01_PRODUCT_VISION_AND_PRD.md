# WIYATA Product Vision and PRD

## 1. Product definition

WIYATA — Your Database Learning Center — is a universal database learning, development, and professional knowledge platform. It combines practical database environments, query intelligence, a database encyclopedia, professional software guides, operational workflows, and career learning paths.

It is not only an AI SQL generator and not a replacement claim for every commercial database IDE or monitoring suite. It is a unified learning and workbench ecosystem.

## 2. Mission

Make database technologies easier to learn, practice, develop, understand, and operate — from a first SQL statement to professional DBA workflows.

## 3. Primary user groups

- Developers and software engineers
- Database administrators (DBAs)
- Database developers
- Data analysts and data engineers
- Database reliability and performance engineers
- Database architects
- Students and career changers

## 4. Product pillars

### A. Database Lab
Temporary and longer-lived isolated database environments:
- Create an environment by engine and version.
- Start from empty or a prepared template.
- Run SQL or native database operations.
- Browse schemas and results.
- Reset, export, snapshot, and restore where supported.
- Expire automatically according to environment policy.
- Use resource quotas and execution limits.

### B. Query Studio
- Natural-language-to-query generation.
- Manual SQL editor.
- Visual query builder.
- SQL dialect conversion.
- Query explanation.
- Syntax parsing and validation.
- Query rewrite and optimization suggestions.
- Query library and history.
- Native NoSQL operation support where implemented.

### C. Database Workspace
- Optional user-managed external database connections.
- Schema and metadata discovery.
- Query execution with explicit user approval.
- Read-only defaults.
- Results grid, export, and execution history.
- DBA diagnostics where permissions and engine capabilities allow.

### D. Knowledge Center
- General database encyclopedia.
- Database-engine-specific documentation.
- SQL learning and reference.
- Architecture, performance, security, backup/recovery, HA, replication, distributed systems, and troubleshooting.
- Version-aware articles.
- Search and related content.
- Practical links into Database Lab.

### E. Professional Tools Directory
- Catalog professional database, monitoring, backup, migration, security, infrastructure, and development applications.
- Explain purpose, supported engines, editions, licensing, operating systems, deployment modes, installation, configuration, usage, limitations, alternatives, and references.
- Clearly distinguish open source, free tier, proprietary, and commercial products.

### F. Professional Workflows and Learning Paths
- Realistic DBA runbooks and troubleshooting workflows.
- Role-based skills matrix.
- Learning paths, exercises, quizzes, and progress.
- No claim of official vendor certification unless an authorized certification is actually provided.

## 5. Product principles

1. One consistent experience across multiple database engines.
2. Database-specific correctness over false universality.
3. AI assists; deterministic tools and human review remain essential.
4. Execution is optional and explicit.
5. Read-only is the default.
6. Local/self-hosted options are first-class.
7. Basic platform functionality remains free.
8. English and Bahasa Indonesia are the only supported interface/content languages at launch.
9. Professional knowledge must be sourced, version-aware, and maintained.
10. Open interfaces and adapters should make future engines extensible.

## 6. Supported database roadmap

### Initial
- SQLite
- PostgreSQL
- MySQL

### Next
- MariaDB
- Oracle Database
- Microsoft SQL Server
- IBM Db2

### Later
- MongoDB
- Redis
- Cassandra
- BigQuery
- Snowflake
- ClickHouse
- Additional engines based on demand and implementation feasibility

No database is considered supported merely because it appears in a dropdown. Each engine must pass adapter capability and compatibility tests.

## 7. Free product model

The intended product is free. Sustainability options:
- Self-hosting
- Local AI through Ollama or compatible local inference
- Bring-your-own-key for cloud AI
- Optional donations or sponsorships
- Community contributions

Do not introduce mandatory paid tiers or paid query quotas into the product definition without an explicit product decision. Hosted infrastructure may have fair-use limits and must disclose them.

## 8. Success measures

- Users can create and use a sandbox without installing a database locally.
- Users can import schema and generate schema-aware queries.
- Users can learn from articles and practice in linked labs.
- Users can discover professional tools and understand their real-world purpose.
- Database adapters expose their actual capabilities.
- Unsafe SQL is blocked or requires an explicit, policy-controlled workflow.
- Self-hosted deployment can be reproduced from documentation.
- English and Indonesian interfaces are complete and consistent.
