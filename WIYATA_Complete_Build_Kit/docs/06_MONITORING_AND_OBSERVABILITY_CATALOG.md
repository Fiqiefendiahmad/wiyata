# Monitoring and Observability Knowledge Catalog

## Purpose

This is a knowledge and professional application directory, not a promise that WIYATA itself initially provides a complete monitoring product.

## A. Database-specific monitoring

### Oracle
- Oracle Enterprise Manager
- SQL*Plus / SQLcl for diagnostic queries
- AWR, ASH, ADDM where licensing permits
- Dynamic performance views
- Data Guard monitoring tools and views

### PostgreSQL
- pg_stat_activity
- pg_stat_database
- pg_stat_statements
- EXPLAIN / EXPLAIN ANALYZE
- pgBadger
- pgwatch
- Percona Monitoring and Management

### MySQL and MariaDB
- Performance Schema
- sys schema
- SHOW GLOBAL STATUS
- MySQL Enterprise Monitor (commercial)
- Percona Monitoring and Management
- MySQL Workbench server status features

### Microsoft SQL Server
- SQL Server Management Studio Activity Monitor
- Query Store
- Extended Events
- Dynamic Management Views (DMVs)
- SQL Server Agent monitoring
- Azure Monitor for applicable hosted services

### IBM Db2
- IBM Data Management Console
- Db2 command line and monitoring functions
- MON_GET_* table functions
- Event monitors
- Explain facility
- HADR monitoring

## B. Infrastructure monitoring

- Prometheus
- Grafana
- Zabbix
- Nagios
- Checkmk
- Icinga
- Netdata
- OpenTelemetry
- Alertmanager

## C. Enterprise observability/APM/log analytics

- Datadog
- Dynatrace
- New Relic
- Elastic Observability
- Splunk
- AppDynamics

## D. Linux and operating-system diagnostics

| Tool | Typical use |
|---|---|
| top / htop | Process and CPU activity |
| iostat | Disk I/O statistics |
| vmstat | Memory and system activity |
| free | Memory summary |
| sar | Historical system metrics |
| iotop | Process-level I/O |
| pidstat | Per-process resource metrics |
| ss | Socket and network inspection |
| nmon | System performance view |
| journalctl | System service logs |
| dmesg | Kernel messages |

## E. Monitoring learning paths

- Oracle DBA monitoring
- PostgreSQL monitoring
- MySQL monitoring
- Db2 monitoring
- SQL Server monitoring
- Linux server monitoring
- Enterprise observability
- Monitoring automation

## F. Professional workflow template

For every monitoring workflow include:
1. Scenario and symptoms
2. Impact and severity
3. Required permissions
4. Tools and metrics
5. Collection steps
6. Diagnosis steps
7. Root-cause hypotheses
8. Remediation options
9. Rollback and risk
10. Verification
11. Evidence to retain
12. Related references

## G. Metrics to teach

- Availability and connection failures
- CPU utilization and run queue
- Memory pressure and cache/buffer hit behavior
- Disk latency, throughput, IOPS, and queue depth
- Database storage and tablespace capacity
- Active sessions and connection saturation
- Locks, blocking, and deadlocks
- Query latency and throughput
- Slow statements and plan changes
- Replication lag and standby health
- Backup freshness and restore-test status
- Error rates and database logs

Explain that metric definitions differ by engine. Do not compare similarly named metrics without explaining their semantics.

## H. Licensing and safety

- Oracle diagnostic/tuning packs have licensing restrictions; explain these before teaching their use.
- Commercial observability products must be labeled correctly.
- Do not imply a monitoring dashboard alone proves database health.
- Monitoring queries should be read-only and low impact where possible.
- Teach sampling, retention, cardinality, and monitoring overhead.
