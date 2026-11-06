# Professional Tools Directory

## Purpose

Catalog applications commonly used by database professionals. The catalog is educational and must not imply that every organization uses the same stack.

## Required metadata per tool

- Name and vendor
- Category and subcategory
- Short purpose
- Official product URL
- Official documentation URL
- Supported database engines
- Supported operating systems
- Deployment model: desktop, web, server, container, cloud
- License model: open source, free edition, freemium, commercial, enterprise
- Edition differences
- Version and lifecycle information
- Installation guides
- Configuration guides
- Professional use cases
- Troubleshooting
- Alternatives
- Last verified date
- Sources

## Catalog categories and initial examples

### Database clients and administration
- DBeaver
- Oracle SQL Developer
- SQLcl and SQL*Plus
- pgAdmin
- psql
- MySQL Workbench
- HeidiSQL
- Microsoft SQL Server Management Studio (SSMS)
- Azure Data Studio (check current lifecycle/status before recommending)
- IBM Data Management Console
- Db2 Command Line Processor
- DataGrip
- Navicat

### Performance and query diagnostics
- Oracle Enterprise Manager
- Oracle SQL Developer execution plan tools
- Oracle AWR/ASH/ADDM (licensing and edition restrictions must be explained)
- PostgreSQL EXPLAIN/EXPLAIN ANALYZE
- pg_stat_statements
- pgBadger
- MySQL Performance Schema
- MySQL sys schema
- SQL Server Query Store
- SQL Server Extended Events
- Db2 explain and monitoring facilities
- Percona Monitoring and Management

### Backup, recovery, and migration
- Oracle RMAN
- pgBackRest
- Barman
- pg_dump and pg_basebackup
- Percona XtraBackup
- MySQL Enterprise Backup (commercial)
- SQL Server native backup/restore
- Db2 backup and restore utilities
- Flyway
- Liquibase
- AWS Database Migration Service
- Vendor-native migration tools

### Schema design and documentation
- SchemaSpy
- DBeaver ER diagrams
- DataGrip diagrams
- MySQL Workbench modeling
- Oracle SQL Developer Data Modeler
- dbdiagram.io (verify plan and licensing details)
- Mermaid ER diagrams

### SQL development quality
- SQLFluff
- SQLGlot
- SQL formatter tools
- Git
- Flyway
- Liquibase

### Infrastructure and automation
- Docker
- Kubernetes
- Ansible
- Terraform
- Jenkins
- GitHub Actions
- GitLab CI/CD
- Linux command-line tools

### Security and secrets
- HashiCorp Vault
- Wazuh
- OpenSSL
- Native database auditing
- Oracle Audit Vault and Database Firewall
- Microsoft Defender for SQL
- Cloud-native IAM and secrets services

### Data engineering
- Apache Airflow
- dbt
- Apache Spark
- Apache Kafka
- Trino
- Debezium
- Cloud data warehouse tooling

## Tool-page content

Each application page should explain:
- What the tool is
- Why a DBA/developer uses it
- When to use it
- When not to use it
- Architecture and components
- Supported engines and versions
- Installation by operating system
- Configuration and secure setup
- Common workflows
- Troubleshooting
- Performance and resource considerations
- License and edition comparison
- Alternatives
- Practical exercises
- Official sources

## Licensing rules

Do not call a tool “free” solely because it offers a free trial or limited free edition. Distinguish:
- Open-source license
- Free community edition
- Free tier with limits
- Proprietary free tool
- Commercial subscription
- Enterprise license
- Feature requiring a separately licensed database option

Check vendor terms before publishing license claims.
