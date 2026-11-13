"""Cross-links from WIYATA (database learning) to LADANG (server platform) knowledge.

LADANG base: https://ladang.sadeyan.my.id
Provides related server/platform articles and actions per WIYATA DB topic/slug.
"""

LADANG_BASE = "https://ladang.sadeyan.my.id"


def _a(slug: str, title: str, why: str) -> dict:
    return {
        "kind": "article",
        "title": title,
        "url": f"{LADANG_BASE}/knowledge/{slug}",
        "why": why,
    }


def _page(path: str, title: str, why: str, kind: str = "action") -> dict:
    return {"kind": kind, "title": title, "url": f"{LADANG_BASE}{path}", "why": why}


SLUG_LINKS: dict[str, list[dict]] = {
    "postgresql-17-architecture-internals": [
        _a("postgresql-administration-basics", "PostgreSQL Administration Basics", "Server-side administration, WAL internals, vacuuming, and connection pooling."),
        _a("backup-restore-strategies", "Backup & Restore Strategies", "pg_dump, WAL archiving, PITR, and restore workflows on servers."),
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Storage layout and tuning that underpin database performance."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Host and service metrics for database observability."),
        _page("/lab", "LADANG Server Lab", "Practice Linux/server commands in an isolated sandbox."),
    ],
    "b-tree-indexes-deep-dive": [
        _a("postgresql-administration-basics", "PostgreSQL Administration Basics", "Operational tuning and maintenance context for indexes."),
        _a("troubleshooting-methodology", "Production Troubleshooting Methodology", "Systematic diagnosis for slow queries and resource issues."),
        _page("/lab", "LADANG Server Lab", "Run diagnostics and inspection commands."),
    ],
    "database-isolation-levels": [
        _a("postgresql-administration-basics", "PostgreSQL Administration Basics", "How PostgreSQL manages concurrency and connections in production."),
        _a("troubleshooting-methodology", "Production Troubleshooting Methodology", "Diagnose locking/contention symptoms at system level."),
    ],
    "understanding-acid-properties": [
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Durability in practice: backups, WAL, and recovery."),
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Reliable storage foundations for durable systems."),
    ],
    "mysql-11-innodb-replication-guide": [
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Backup and recovery practices for production data services."),
        _a("linux-networking-basics", "Linux Networking Basics", "Network fundamentals affecting replication and connectivity."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Monitor replication lag and host metrics."),
        _page("/lab", "LADANG Server Lab", "Practice server/network diagnostics."),
    ],
    "sql-server-2022-internals-query-store": [
        _a("windows-server-overview", "Windows Server Architecture & Editions", "Platform foundations for SQL Server deployments."),
        _a("windows-monitoring-performance", "Windows Performance Monitoring", "Counters and event tracing for host-level diagnosis."),
        _a("iis-web-server", "IIS Web Server Architecture", "Common Windows application stack alongside SQL Server."),
        _page("/command", "LADANG Command Studio", "Generate service/config snippets for Windows and Linux."),
    ],
    "oracle-23ai-enterprise-architecture": [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Storage planning for enterprise database workloads."),
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Operational backup/restore discipline."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Observability for hosts running database workloads."),
    ],
    "ibm-db2-11-5-hadr-tablespaces-wlm": [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Tablespaces and storage performance considerations."),
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Disaster recovery and restore readiness."),
    ],
    "database-monitoring-golden-signals": [
        _a("prometheus-grafana", "Prometheus & Grafana", "Metrics architecture, PromQL, and dashboards."),
        _a("centralized-logging", "Centralized Log Aggregation", "Loki/Promtail/Vector for correlated incident analysis."),
        _a("distributed-tracing", "Distributed Tracing & OpenTelemetry", "Trace request paths across services and databases."),
        _page("/observability", "LADANG Observability", "Observability concepts and references on LADANG."),
        _page("/lab", "LADANG Server Lab", "Run host checks during incident triage."),
    ],
    "enterprise-monitoring-apps-oem-manageengine-dmc-ssms-pem": [
        _a("prometheus-grafana", "Prometheus & Grafana", "Open-source metrics and dashboards stack."),
        _a("windows-monitoring-performance", "Windows Performance Monitoring", "Performance counters and ETW for Windows hosts."),
        _a("centralized-logging", "Centralized Log Aggregation", "Log pipelines for operational visibility."),
        _page("/observability", "LADANG Observability", "Observability learning path and resources."),
    ],
    "tablespaces-blocking-locks-and-mirroring-guide": [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Physical storage, RAID, and filesystem choices."),
        _a("troubleshooting-methodology", "Production Troubleshooting Methodology", "Structured approach to lock/contention incidents."),
        _page("/resources", "LADANG Incident Resources", "Runbooks and troubleshooting references."),
    ],
    "sqlite-wal-mode-explained": [
        _a("backup-restore-strategies", "Backup & Restore Strategies", "WAL, checkpoints, and recovery concepts in practice."),
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Filesystem behavior affecting WAL performance."),
    ],
    "kubernetes-and-docker-for-enterprise-databases": [
        _a("docker-networking", "Container Networking Architecture", "Bridge, host, overlay networking for stateful services."),
        _a("docker-storage-volumes", "Container Storage Drivers & Volumes", "Persistent storage choices for containers."),
        _a("docker-security", "Container Hardening", "Rootless, capabilities, seccomp for safer workloads."),
        _a("kubernetes-storage", "Kubernetes Storage Architecture", "CSI, PV/PVC, and dynamic provisioning."),
        _a("kubernetes-services-ingress", "Kubernetes Services & Ingress", "Expose and route traffic to database-backed services."),
        _page("/lab", "LADANG Server Lab", "Practice container and Linux commands."),
    ],
    "mongodb-architecture-wiredtiger-sharding": [
        _a("docker-networking", "Container Networking Architecture", "Networking considerations for distributed data stores."),
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Backup/restore planning for stateful systems."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Monitor cluster health and host metrics."),
    ],
    "redis-internals-persistence-cluster": [
        _a("redis-administration-basics", "Redis Administration Basics", "Persistence (RDB/AOF), eviction, and operational practices."),
        _a("linux-networking-basics", "Linux Networking Basics", "Latency and connectivity for in-memory stores."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Observe memory, latency, and saturation."),
    ],
    "cassandra-lsm-architecture-ring": [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Disk/IO characteristics for LSM-tree workloads."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Monitor node and cluster metrics."),
    ],
    "cockroachdb-distributed-sql-raft": [
        _a("docker-networking", "Container Networking Architecture", "Networking for distributed clusters."),
        _a("kubernetes-deployments", "Kubernetes Deployments & Rollouts", "Run and update distributed services reliably."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Cluster observability and alerting."),
    ],
    "snowflake-cloud-data-warehouse-internals": [
        _a("terraform-iac-basics", "Terraform / OpenTofu Basics", "Provision and manage cloud infrastructure declaratively."),
        _a("ci-security", "Supply Chain Security in CI", "Secure pipelines and credentials for data platforms."),
    ],
    "clickhouse-duckdb-columnar-vectorized": [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Storage throughput for analytical workloads."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Monitor query and host performance."),
    ],
}

KEYWORD_RULES: list[tuple[list[str], list[dict]]] = [
    (["postgres"], [
        _a("postgresql-administration-basics", "PostgreSQL Administration Basics", "Server-side PostgreSQL operations."),
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Backups and PITR."),
        _page("/lab", "LADANG Server Lab", "Practice server commands."),
    ]),
    (["mysql", "mariadb", "innodb"], [
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Backup/recovery discipline."),
        _a("linux-networking-basics", "Linux Networking Basics", "Replication and connectivity."),
        _page("/lab", "LADANG Server Lab", "Practice diagnostics."),
    ]),
    (["redis"], [
        _a("redis-administration-basics", "Redis Administration Basics", "Persistence and operations."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Monitoring in-memory stores."),
    ]),
    (["oracle"], [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Storage for enterprise DBs."),
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Recovery planning."),
    ]),
    (["sql server", "mssql"], [
        _a("windows-server-overview", "Windows Server Architecture & Editions", "Windows platform basics."),
        _a("windows-monitoring-performance", "Windows Performance Monitoring", "Host performance analysis."),
    ]),
    (["monitor", "observ", "pmm", "prometheus", "grafana", "oem"], [
        _a("prometheus-grafana", "Prometheus & Grafana", "Metrics and dashboards."),
        _a("centralized-logging", "Centralized Log Aggregation", "Log pipelines."),
        _a("distributed-tracing", "Distributed Tracing & OpenTelemetry", "Tracing across services."),
        _page("/observability", "LADANG Observability", "Observability resources."),
    ]),
    (["backup", "restore", "recovery", "pitr", "rman", "pgbackrest", "xtrabackup"], [
        _a("backup-restore-strategies", "Backup & Restore Strategies", "Server-side backup and restore practices."),
        _page("/resources", "LADANG Incident Resources", "Runbooks and recovery guidance."),
    ]),
    (["kubernetes", "docker", "container"], [
        _a("docker-networking", "Container Networking Architecture", "Networking for containers."),
        _a("docker-storage-volumes", "Container Storage & Volumes", "Persistent storage."),
        _a("kubernetes-storage", "Kubernetes Storage Architecture", "CSI and PV/PVC."),
        _page("/lab", "LADANG Server Lab", "Hands-on sandbox."),
    ]),
    (["storage", "tablespace", "disk", "raid", "lvm"], [
        _a("linux-storage-lvm-raid", "Linux Storage: LVM2, RAID, XFS/ext4", "Storage architecture and tuning."),
    ]),
    (["replication", "hadr", "failover", "cluster", "distributed"], [
        _a("linux-networking-basics", "Linux Networking Basics", "Networking for replicated systems."),
        _a("prometheus-grafana", "Prometheus & Grafana", "Monitor health and lag."),
    ]),
]


def _dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for it in items:
        key = (it.get("kind"), it.get("url"))
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out


def get_ladang_links(slug: str, title: str = "") -> dict:
    links: list[dict] = []
    links.extend(SLUG_LINKS.get(slug, []))
    hay = f"{slug} {title}".lower()
    for keywords, items in KEYWORD_RULES:
        if any(k in hay for k in keywords):
            links.extend(items)
    links = _dedupe(links)
    if not links:
        links = [
            _page("/knowledge", "LADANG Knowledge Center", "Server platform, Linux, networking, containers, and ops."),
            _page("/lab", "LADANG Server Lab", "Practice commands in an isolated sandbox."),
            _page("/resources", "LADANG Resources", "Runbooks, troubleshooting, and visual lessons."),
        ]
    return {
        "base_url": LADANG_BASE,
        "description": "Related server platform knowledge and actions on LADANG (ladang.sadeyan.my.id).",
        "links": links[:12],
    }
