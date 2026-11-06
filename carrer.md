# WIYATA — Career Academy: Comprehensive Role Investigation & Implementation Specification

**Product:** WIYATA — Your Database Learning Center  
**Module:** Career Paths / Jalur Profesi  
**Languages:** English (`en`) and Bahasa Indonesia (`id`)  
**Purpose:** Build a technically accurate, practical, measurable career-development system for database and data professionals.

---

## 1. Mission and Product Vision

Transform WIYATA's Career Paths module into a comprehensive **Database & Data Engineering Career Academy**.

The module must help learners:

1. Understand what a professional role actually does.
2. Distinguish similar or overlapping job titles.
3. Identify the technical and professional competencies required.
4. Understand junior, intermediate, senior, lead, principal, architect, and management expectations.
5. Follow a structured learning roadmap.
6. Practice realistic technical and production scenarios.
7. Assess demonstrated skills and identify gaps.
8. Build evidence of their capabilities through portfolio projects.

This must be more than a job-title directory or a collection of generic skill cards. It should connect career information to WIYATA's Knowledge Center, Database Glossary, Visual Database Academy, SQL Challenges, Studio & Lab, Professional Tools, and DBA Field Handbook.

**Core learning model:** Understand → Learn → Visualize → Practice → Simulate → Assess → Build Portfolio.

## 2. Non-Negotiable Implementation Instructions

Before modifying the application:

1. Inspect the complete repository and current deployed application.
2. Identify the framework, routing, components, API conventions, state management, authentication, database schema, migrations, and content architecture.
3. Inventory all existing career pages, roles, learning paths, skills, assessments, and user progress features.
4. Test existing functionality.
5. Identify what is complete, incomplete, duplicated, inaccurate, or missing.
6. Produce an audit report before implementation.

Preserve existing working features and conventions. Extend the current application instead of replacing it with an unrelated template.

Do not:

- Assume that a role has identical responsibilities in every company.
- Present suggested career levels as universal industry standards.
- Reuse generic descriptions across different roles.
- Treat reading an article as proof of technical proficiency.
- Claim that a user is job-ready based only on a quiz.
- Claim that WIYATA provides accredited certifications unless that is actually established.
- Promise employment, salary, promotion, or hiring outcomes.
- Copy large sections from external job descriptions or documentation.
- Invent employer requirements, certifications, salary ranges, or job-market statistics.
- Hardcode all career content into UI components.
- Remove existing functionality without documenting and justifying the change.

When information cannot be verified, label it as an example, recommendation, or organization-dependent practice.

## 3. Career Academy Information Architecture

Organize the module into these primary areas:

1. Career Academy landing page.
2. Career family directory.
3. Career role catalog.
4. Role detail pages.
5. Career level framework.
6. Competency and skills framework.
7. Engine-specific specializations.
8. Role comparison.
9. Career assessment.
10. Personalized career roadmap.
11. Practical scenario library.
12. Portfolio project catalog.
13. Learning progress.
14. References and further reading.

Suggested navigation:

- Overview
- Explore Careers
- Compare Roles
- Skills & Competencies
- Learning Roadmaps
- Practical Scenarios
- Portfolio Projects
- My Career Plan

Use the existing WIYATA navigation and visual language. Do not create unnecessary top-level navigation if the current information architecture supports a nested Career Academy.

## 4. Career Family Taxonomy

Create six career families. A role may be associated with more than one family through explicit relationships and tags, but should not be duplicated in the database.

### Family A — Database Administration & Operations

- Database Support Engineer
- Junior Database Administrator
- Database Administrator (DBA)
- Senior Database Administrator
- Lead Database Administrator
- Oracle Database Administrator
- PostgreSQL Database Administrator
- MySQL Database Administrator
- MariaDB Database Administrator
- Microsoft SQL Server Database Administrator
- IBM Db2 Database Administrator
- Database Operations Manager

Core focus: database availability, installation and configuration, maintenance, backup and recovery, security and access control, monitoring, performance troubleshooting, replication and high availability, disaster recovery, capacity planning, production support and incident response.

### Family B — Database Engineering & Performance

- SQL Developer
- Database Developer
- Database Engineer
- Senior Database Engineer
- Principal Database Engineer
- Database Performance Engineer
- Database Migration Engineer
- Database Automation Engineer

Core focus: application/database integration, data and schema design, advanced SQL, query optimization, index design, database code quality, schema migration, testing, performance benchmarking, and database development tooling.

### Family C — Database Reliability & Platform Engineering

- Infrastructure Engineer
- Database Reliability Engineer (DBRE)
- Database Site Reliability Engineer (Database SRE)
- Senior Database SRE
- Lead Database SRE
- Database Platform Engineer
- Database Platform Architect

Core focus: reliability engineering, availability and resilience, SLI/SLO and error budgets, monitoring and observability, incident response, automation, Infrastructure as Code, database platform operations, capacity and performance, cloud and distributed systems.

### Family D — Data Engineering & Analytics

- Junior Data Engineer
- Data Engineer
- Senior Data Engineer
- Lead Data Engineer
- Analytics Engineer
- Data Platform Engineer
- Data Warehouse Engineer
- Data Architect

Core focus: ETL and ELT, data pipelines, data modeling, batch and streaming processing, data warehouses and lakes, data quality, orchestration, integration, governance, and pipeline observability.

### Family E — Database Architecture & Strategy

- Database Designer
- Database Architect
- Senior Database Architect
- Enterprise Database Architect
- Cloud Database Architect
- Enterprise Data Architect

Core focus: enterprise data architecture, conceptual/logical/physical data models, platform selection, distributed architecture, high availability, disaster recovery, security and governance, scalability, capacity and cost modeling, architecture standards and technical strategy.

### Family F — Specialist Database Professions

- Database Security Engineer
- Database Backup & Recovery Specialist
- Database Performance Engineer
- Cloud Database Engineer
- NoSQL Database Engineer
- Database Migration Specialist
- Database Automation Engineer
- Database Observability Engineer

Core focus: deep expertise in a specific technical domain, advanced troubleshooting, specialist tooling, domain-specific solution design and implementation, and technical standards.

## 5. Detailed Role Profile Standard

Every role must have a substantive profile. Do not publish a role with only a title and a short generic paragraph.

Required role fields:

1. Role title and alternative job titles.
2. Canonical role name and career family.
3. Role summary and purpose.
4. Business value.
5. Typical organizational placement.
6. Reporting and collaboration relationships, where applicable.
7. Core responsibilities.
8. Daily, weekly, and monthly/periodic activities.
9. Production responsibilities.
10. Required and preferred technical competencies.
11. Professional and communication skills.
12. Tools and technologies.
13. Database engine and cloud/platform applicability.
14. Common workplace terminology.
15. Typical incidents and problems.
16. Expected work products and deliverables.
17. Example performance indicators.
18. Entry expectations.
19. Career progression.
20. Related and adjacent roles.
21. Learning roadmap.
22. Practical exercises and portfolio projects.
23. Assessment criteria.
24. Relevant certifications, with current status verified.
25. Official references and further reading.
26. Last technical review date, content status, and reviewer.

Explain what the role does in a real organization. Include concrete examples of decisions, tasks, collaboration, risks, and deliverables.

Distinguish common professional responsibilities from those that depend on company size, industry, engine, deployment model, or team design.

## 6. Career Levels and Professional Expectations

Use this flexible WIYATA framework, not a universal title standard:

1. Foundation / Awareness
2. Junior
3. Intermediate / Practitioner
4. Senior
5. Lead / Principal
6. Architect / Manager

Not every role needs every level. Technical leadership and people management must be represented as different progression directions.

For each level, define technical knowledge, practical execution, independence, problem complexity, production responsibility, risk assessment, decision-making authority, communication, documentation, collaboration, mentoring, and architecture/strategic scope.

### Example: DBA progression

| Dimension | Junior DBA | DBA | Senior DBA | Lead DBA |
|---|---|---|---|---|
| Routine monitoring | Performs guided checks | Owns routine monitoring | Improves monitoring strategy | Establishes team standards |
| Backup and recovery | Runs documented procedures | Performs and verifies recovery tasks | Designs and tests recovery plans | Owns recovery standards and risk |
| Performance | Identifies basic symptoms | Investigates common problems | Resolves complex bottlenecks | Guides optimization strategy |
| Incidents | Escalates with evidence | Handles standard incidents | Leads complex investigations | Coordinates technical response |
| Automation | Uses existing scripts | Writes basic automation | Builds reliable workflows | Sets automation direction |
| Architecture | Understands current design | Contributes to changes | Designs components | Reviews and governs architecture |

Define equivalent expectations for each role rather than copying this table.

## 7. Competency Framework

Create a reusable competency taxonomy mapped to multiple roles.

### Competency categories

**Database foundations:** DBMS/RDBMS, relational theory, SQL, data types, constraints, normalization, data modeling, transactions, ACID, isolation levels.

**Database internals:** query parsing and planning, query execution, optimizers, index structures, B-tree and other index types, buffer pools and caches, memory management, storage architecture, WAL and transaction logs, MVCC, locking and concurrency, checkpoints.

**Administration and operations:** installation, configuration, users and roles, backup and recovery, maintenance, patching and upgrades, replication, high availability, disaster recovery, capacity planning, production support.

**Performance engineering:** query plans, cardinality and selectivity, index selection, statistics, wait events, slow query analysis, I/O diagnosis, memory diagnosis, benchmarking, workload analysis.

**Infrastructure:** Linux, Windows Server, processes and services, filesystems, storage, CPU and memory, networking, DNS, TCP/IP, TLS, firewalls, load balancing.

**Reliability and automation:** monitoring, observability, SLI/SLO, incident management, root cause analysis, runbooks, Python/Go/Shell, Terraform, Ansible, Docker, Kubernetes, CI/CD.

**Data engineering:** ETL/ELT, batch processing, streaming, CDC, warehouses, lakes, dimensional modeling, data quality, orchestration, Airflow, Kafka, Spark, dbt.

**Professional skills:** technical communication, documentation, incident reporting, change management, risk analysis, collaboration, stakeholder management, mentoring, prioritization, problem solving.

### Four proficiency levels

| Level | Label | Definition |
|---|---|---|
| 1 | Awareness | Can explain the concept and recognize its use |
| 2 | Working | Can perform a guided or routine task |
| 3 | Practitioner | Can independently complete realistic tasks and troubleshoot common failures |
| 4 | Expert | Can design complex solutions, handle ambiguity, establish standards, and mentor others |

Each level must have observable evidence criteria. Do not infer proficiency from page views, time spent, or course completion alone.

Possible evidence: knowledge assessment, SQL challenge, sandbox exercise, practical scenario, project submission, architecture diagram, troubleshooting report, runbook, or reviewed portfolio project.

Clearly label self-assessed skills separately from skills demonstrated through WIYATA assessments.

## 8. Engine-Specific Career Specializations

Universal database competencies and engine-specific competencies must be separated.

### Oracle Database Administrator

Cover Oracle architecture; instance and database; SGA and PGA; background processes; control files; datafiles; tablespaces; redo and undo; archived redo logs; RMAN; Data Guard; RAC; ASM; AWR; ASH; ADDM; wait events; V$/GV$ views; alert logs and ADR; performance tuning; security; backup and recovery; patching and upgrades.

Explain licensing restrictions and prerequisites for features such as AWR, ASH, and ADDM. Never imply that every feature is available under every Oracle edition or license.

### PostgreSQL Database Administrator

Cover PostgreSQL architecture; processes and shared memory; MVCC; WAL; checkpoints; VACUUM and autovacuum; index types; EXPLAIN and EXPLAIN ANALYZE; pg_stat_activity; pg_stat_database; pg_stat_statements; pg_locks; pg_stat_replication; replication slots; streaming and logical replication; backup and PITR; high availability; extensions; security and roles; configuration and maintenance.

### MySQL and MariaDB Administrator

Cover server architecture; InnoDB; buffer pool; redo and undo logs; binary logs; transaction isolation; indexes; Performance Schema; sys schema; slow query log; EXPLAIN; replication; Group Replication where applicable; backup and recovery; high availability; security; configuration and maintenance.

Identify MySQL/MariaDB differences rather than assuming complete compatibility.

### Microsoft SQL Server Administrator

Cover SQL Server architecture; database files; transaction logs; TempDB; buffer pool; query optimizer; execution plans; DMVs; Query Store; Extended Events; SQL Server Agent; backup and restore; Always On availability groups; replication; security; performance tuning; maintenance.

Verify the current lifecycle and status of tools such as Azure Data Studio before recommending them.

### IBM Db2 Administrator

Cover Db2 architecture; instances and databases; buffer pools; tablespaces; containers and storage groups as applicable; logging; transaction management; MON_GET functions; db2pd; event monitors; db2diag.log; HADR; backup and recovery; performance monitoring; security; configuration and maintenance.

### Cloud Database Engineer

Cover relevant services and concepts across Amazon RDS and Aurora, DynamoDB, Google Cloud SQL, AlloyDB, BigQuery, Azure SQL Database, and Azure Database for PostgreSQL. Include managed database operations, cloud networking, IAM, encryption and key management, backups and recovery, multi-zone/multi-region architecture, cost and performance management.

Verify product names, availability, capabilities, and lifecycle information against current official documentation.

### NoSQL Database Engineer

Cover document databases, key-value stores, wide-column databases, graph databases, data modeling, partition keys, replication, consistency models, distributed transactions, scaling, monitoring, backup and recovery, and security. Include MongoDB, Redis, Cassandra, HBase, Elasticsearch, and DynamoDB where relevant.

## 9. Six Flagship Career Paths

The first release must contain six complete flagship career paths:

1. Database Administrator.
2. Oracle Database Administrator.
3. PostgreSQL Database Administrator.
4. Database Engineer.
5. Database Reliability Engineer.
6. Data Engineer.

For each flagship path, deliver:

- Detailed role profile.
- Role-specific career levels.
- Competency matrix.
- Universal and specialized skill mapping.
- Learning roadmap.
- Engine/tool references.
- Practical exercises.
- At least three realistic scenario-based assessments.
- At least two portfolio project specifications.
- Role-specific assessment rubric.
- Related career comparisons.

Expand the remaining roles after the flagship paths have meaningful, reviewed content. Do not create dozens of empty role pages merely to claim coverage.

## 10. Practical Scenario and Simulation System

Every scenario must contain: title, target role and level, learning objectives, prerequisites, environment and engine, background context, symptoms, business impact, initial evidence, tasks, hints, expected findings, recommended resolution, verification steps, rollback/recovery considerations, evaluation rubric, explanation, and related resources.

### DBA scenarios

- Database unavailable.
- High CPU or memory usage.
- Disk or tablespace full.
- Slow SQL.
- Blocking sessions and deadlocks.
- Failed backup.
- Restore and recovery.
- Replication lag.
- Authentication failures and permission errors.
- Long-running transactions.
- Connection exhaustion.
- Database startup failure.
- Unexpected execution plan changes.
- High I/O wait.
- Database growth and capacity issues.

### Database Engineer scenarios

- Optimize a slow application query.
- Redesign an inefficient schema.
- Implement a safe schema migration.
- Investigate a connection storm.
- Improve transaction handling.
- Benchmark alternative index strategies.
- Diagnose an ORM-generated query problem.

### DBRE scenarios

- Define database SLOs.
- Build a monitoring dashboard.
- Create replication-lag alerts.
- Automate backup verification.
- Provision a database platform.
- Conduct an incident review.
- Execute a failover exercise.
- Design a capacity alerting strategy.

### Data Engineer scenarios

- Build an ETL pipeline.
- Diagnose a failed pipeline.
- Implement CDC.
- Create a dimensional warehouse.
- Validate data quality.
- Handle late-arriving data.
- Monitor pipeline freshness and reliability.

### Architect scenarios

- Design an enterprise database platform.
- Compare database technologies.
- Design multi-region availability.
- Create a disaster recovery strategy.
- Model data growth and capacity.
- Assess migration risk.
- Evaluate security and governance requirements.

Clearly distinguish synthetic educational environments from real production systems. Never present simulated output as real production evidence.

## 11. Role Comparison Engine

Implement comparison between two or more roles.

Comparison dimensions:

- Role purpose and business responsibilities.
- Daily activities.
- SQL depth and database internals.
- Database administration.
- Programming.
- Linux and operating systems.
- Networking.
- Storage and infrastructure.
- Monitoring and observability.
- Automation.
- Cloud platforms.
- Data pipelines.
- Performance engineering.
- Backup and recovery.
- Security.
- Incident response.
- Architecture ownership.
- Stakeholder responsibilities.
- Typical deliverables.
- Career progression.

Required comparisons:

- DBA vs Database Engineer.
- DBA vs System Administrator.
- DBA vs Database SRE.
- Database Engineer vs Data Engineer.
- Data Engineer vs Analytics Engineer.
- Database Architect vs Data Architect.
- Cloud DBA vs Traditional DBA.
- Database Performance Engineer vs DBA.
- Database Security Engineer vs DBA.

Show focus levels as indicative, not universal. Explain that job boundaries depend on organization size, industry, team design, and platform.

## 12. Career Assessment and Personalized Development Plan

Create an assessment flow where users:

1. Select a target role.
2. Select their current experience level.
3. Evaluate relevant competencies.
4. Complete selected knowledge and practical assessments.
5. Review identified skill gaps.
6. Generate a learning sequence.
7. Set a next milestone.
8. Record evidence and project outcomes.

Show current self-assessed proficiency, demonstrated proficiency, missing competencies, recommended learning resources, challenges, scenarios, portfolio requirements, and suggested next milestone.

Do not combine self-assessment and demonstrated proficiency into one unexplained score. Do not label users as certified, accredited, or guaranteed job-ready.

Allow users to maintain a career plan with target role, current and target level, skill goals, learning tasks, project milestones, assessment results, evidence links/uploads, notes, completion status, and review dates.

Persist progress using the application's existing supported user/account architecture.

## 13. Portfolio Project System

Create practical portfolio specifications.

**DBA:** database health monitoring environment; backup and recovery implementation; performance investigation report; high availability lab; security review; capacity planning report.

**Database Engineer:** SQL optimization case study; schema design and migration; query benchmarking; connection-pooling implementation; database testing workflow.

**DBRE:** observability platform; automated provisioning; backup verification automation; database SLO implementation; incident runbook; failover exercise report.

**Data Engineer:** ETL/ELT pipeline; data warehouse; CDC pipeline; data-quality framework; pipeline observability dashboard.

**Architect:** enterprise database architecture; multi-region database design; platform selection analysis; disaster recovery architecture; modernization roadmap.

Each project specification must contain business scenario, objectives, prerequisites, required tools, architecture requirements, tasks, deliverables, evaluation rubric, security requirements, documentation requirements, and extension ideas.

Allow users to record project descriptions, architecture, technologies, outcomes, and evidence.

## 14. Integration With Other WIYATA Modules

Career Paths must connect to existing resources:

| Career learning stage | WIYATA module |
|---|---|
| Understand a concept | Pusat Pengetahuan |
| Learn terminology | Database Glossary |
| See how it works | Visual Database Academy |
| Practice SQL | Tantangan SQL |
| Experiment | Studio & Lab |
| Learn professional tools | Katalog Alat |
| Practice operations | DBA Field Handbook |
| Investigate failures | Troubleshooting Library |
| Demonstrate ability | Career Assessment |
| Record achievements | My Library / Portfolio |

Use real existing content identifiers and routes. Do not create broken or fabricated links. Where a required resource does not exist, record the dependency and prioritize its creation.

## 15. Bilingual Content Requirements

Support English (`en`) and Bahasa Indonesia (`id`).

Translate explanations, role summaries, responsibilities, learning objectives, instructions, assessment content, and UI labels.

Preserve canonical English technical terms with Indonesian explanations. Examples:

- Blocking Session — sesi yang tertahan karena menunggu resource atau lock.
- Wait Event — peristiwa ketika proses database menunggu resource atau aktivitas tertentu.
- Recovery Point Objective (RPO) — batas toleransi kehilangan data yang dinyatakan dalam waktu.
- Recovery Time Objective (RTO) — target waktu pemulihan layanan.

Use consistent terminology. Do not use machine translation without technical review.

## 16. Content Sources and Editorial Governance

Use authoritative references.

### Database vendors

- Oracle Database Documentation: https://docs.oracle.com/en/database/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
- MySQL Documentation: https://dev.mysql.com/doc/
- MariaDB Knowledge Base: https://mariadb.com/kb/en/
- Microsoft SQL Server Documentation: https://learn.microsoft.com/sql/
- IBM Db2 Documentation: https://www.ibm.com/docs/en/db2
- SQLite Documentation: https://www.sqlite.org/docs.html
- MongoDB Documentation: https://www.mongodb.com/docs/
- Redis Documentation: https://redis.io/docs/
- Apache Cassandra Documentation: https://cassandra.apache.org/doc/latest/

### Engineering role and competency references

- GitLab Database Engineer role: https://handbook.gitlab.com/job-description-library/engineering/database-engineer/
- GitLab Database Reliability Engineer role: https://handbook.gitlab.com/job-description-library/engineering/infrastructure/database-reliability-engineer/
- UK Government Data Engineer role framework: https://understand-digital-data-roles-skills.service.gov.uk/role/data-engineer/
- UK Government Digital and Data skills framework: https://understand-digital-data-roles-skills.service.gov.uk/skills/

Use these as reference material, not as content to copy.

Every role and technical article must have source references, version/applicability notes where relevant, content owner or reviewer, last reviewed date, review status, and change history.

Differentiate official documentation, industry examples, WIYATA guidance, and illustrative scenarios.

Verify current certification names, availability, prerequisites, and retirement status before publishing certification recommendations.

## 17. Data Architecture

Inspect the existing database and content model first. Reuse current conventions where possible.

If additional entities are required, consider these logical models:

### Career family

- id
- slug
- title_en
- title_id
- description_en
- description_id
- display_order
- status

### Career role

- id
- slug
- canonical_title
- title_en
- title_id
- summary_en
- summary_id
- family_relationships
- alternative_titles
- role_purpose
- business_value
- responsibilities
- daily_activities
- periodic_activities
- production_responsibilities
- expected_deliverables
- performance_indicators
- entry_expectations
- progression
- related_roles
- tools
- engine_applicability
- references
- review_status
- reviewer
- last_reviewed_at

### Career level

- id
- role_id
- level_code
- title_en
- title_id
- expectations
- independence
- technical_depth
- problem_complexity
- production_scope
- decision_scope
- communication_expectations
- mentoring_expectations

### Competency

- id
- slug
- category_id
- title_en
- title_id
- description_en
- description_id
- competency_type
- references

### Role competency

- id
- role_id
- competency_id
- required_level
- priority
- applicability
- evidence_requirements

### Proficiency level

- id
- level_number
- label_en
- label_id
- definition_en
- definition_id
- observable_criteria

### Learning path and step

- learning_paths: id, role_id, level_id, title_en, title_id, description, estimated_effort, prerequisites, status
- learning_path_steps: id, learning_path_id, order, resource_type, resource_id, objective, completion_criteria

### Practical scenario

- id
- slug
- title_en
- title_id
- role_id
- level_id
- engine
- scenario_type
- prerequisites
- scenario_context
- symptoms
- business_impact
- diagnostic_evidence
- tasks
- hints
- expected_findings
- resolution
- verification
- rollback
- evaluation_rubric
- references

### Portfolio project

- id
- slug
- role_id
- title_en
- title_id
- business_scenario
- objectives
- prerequisites
- tools
- requirements
- deliverables
- evaluation_rubric
- references

### User career plan

- id
- user_id
- target_role_id
- current_level
- target_level
- status
- created_at
- updated_at

### User skill evidence

- id
- user_id
- competency_id
- self_assessed_level
- demonstrated_level
- evidence_type
- evidence_reference
- assessment_id
- reviewed_at

### User learning progress

- id
- user_id
- learning_path_step_id
- status
- completed_at
- evidence_reference

These are logical suggestions, not a requirement to create duplicate tables. Normalize and adapt to the existing application. Use appropriate authorization, validation, migrations, and indexes.

## 18. UI and UX Requirements

Build or improve:

### Career Academy landing page

- Overview of career families.
- Featured career paths.
- Role search.
- Career exploration guidance.
- Recently updated roles.
- Entry-level and specialist pathways.

### Career directory

- Search.
- Family filters.
- Experience-level filters.
- Engine specialization filters.
- Skill filters.
- Role comparison selection.

### Role detail page

- Role overview.
- Responsibilities.
- Career levels.
- Competency matrix.
- Tools.
- Engine specializations.
- Learning roadmap.
- Scenarios.
- Portfolio projects.
- References.
- Related roles.

### Comparison interface

- Compare two or more roles.
- Show differences by responsibility and competency.
- Explain organizational variation.

### Assessment interface

- Clear assessment instructions.
- Save and resume where supported.
- Separate self-assessment from practical evidence.
- Show transparent scoring and rubrics.

### Personal career dashboard

- Target role.
- Current goals.
- Skill gaps.
- Learning progress.
- Pending assessments.
- Portfolio projects.
- Next recommended milestone.

Design principles: preserve WIYATA's identity; readable technical content; responsive layouts; accessible controls and contrast; avoid excessive decorative cards; avoid overwhelming users; progressive disclosure; consistent bilingual support.

## 19. Implementation Phases

### Phase 1 — Audit

Deliver current route inventory, existing role inventory, content inventory, data model review, feature status matrix, technical/editorial gap analysis, and prioritized implementation plan.

### Phase 2 — Core architecture

Implement or improve career family data, role data, career level model, competency taxonomy, references/review metadata, and bilingual content support.

### Phase 3 — Six flagship career paths

Complete DBA, Oracle DBA, PostgreSQL DBA, Database Engineer, DBRE, and Data Engineer. Each must include detailed profiles, competencies, roadmaps, scenarios, projects, and assessments.

### Phase 4 — Comparison and assessment

Implement role comparison, skill self-assessment, demonstrated competency tracking, skill gap analysis, and personalized career plan.

### Phase 5 — Scenario and portfolio system

Implement practical scenario library, evaluation rubrics, portfolio projects, evidence recording, and learning resource integration.

### Phase 6 — Additional roles

Expand remaining roles using the same quality standard.

### Phase 7 — Quality assurance

Run build, type checking, linting, unit tests, integration tests, API tests, authorization tests, responsive tests, accessibility checks, link validation, bilingual content validation, and content completeness checks.

## 20. Acceptance Criteria

The work is complete only when:

- Six career families are represented.
- Six flagship roles have substantive, reviewed content.
- Role responsibilities are distinct and realistic.
- Career levels have measurable expectations.
- Universal and engine-specific competencies are separated.
- Competencies have observable proficiency criteria.
- Role comparison works.
- Self-assessment and demonstrated evidence are distinguished.
- Career roadmaps link to actual WIYATA resources.
- Practical scenarios have usable tasks and evaluation rubrics.
- Portfolio projects have clear deliverables.
- User progress persists through the existing supported architecture.
- English and Indonesian are supported.
- References are verified and attributable.
- No unsupported certification or employment guarantees are made.
- No broken links or empty placeholder role pages remain in the delivered scope.
- Build and tests pass.
- Deployment and migration instructions are complete.

## 21. Final Deliverables

Produce:

1. Career module audit report.
2. Career family and role taxonomy.
3. Role inventory and prioritization.
4. Competency framework.
5. Career level framework.
6. Six complete flagship role profiles.
7. Engine-specific learning roadmaps.
8. Role comparison feature.
9. Career assessment feature.
10. Personalized career plan.
11. Practical scenario library.
12. Portfolio project specifications.
13. Bilingual content.
14. Updated application source.
15. Database migrations, if required.
16. Automated tests.
17. Deployment documentation.
18. Final implementation report.

The final report must distinguish completed and tested, implemented but not fully tested, partially implemented, not implemented, and blocked by missing dependencies or access. Include files created, modified, and removed.

## 22. Final Instruction

Begin by inspecting the actual WIYATA repository and deployed application. Do not assume previous audits describe the current version.

Implement this module systematically, preserving existing functionality and architecture.

Prioritize depth and technical accuracy over the number of role pages.

The goal is to make WIYATA's Career Academy a credible professional learning system where users can understand real database careers, develop relevant competencies, practice realistic work, and build evidence of their progress.
