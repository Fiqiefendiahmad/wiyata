import asyncio
import json
from pathlib import Path
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory
from app.models.tools import ProfessionalTool, ToolCategory
from app.models.user import User, Workspace

SEED_TOOLS = [
    # Clients & Administration
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "DBeaver Community",
        "slug": "dbeaver",
        "vendor": "DBeaver Corp",
        "summary": "Universal database tool for developers and DBAs supporting any database with a JDBC driver.",
        "official_url": "https://dbeaver.io/",
        "documentation_url": "https://dbeaver.com/docs/dbeaver/",
        "license_model": "Open Source",
        "supported_engines": ["SQLite", "PostgreSQL", "MySQL", "Oracle", "SQL Server", "MariaDB"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "pgAdmin 4",
        "slug": "pgadmin",
        "vendor": "PostgreSQL Global Development Group",
        "summary": "The leading open-source graphical management and development platform for PostgreSQL.",
        "official_url": "https://www.pgadmin.org/",
        "documentation_url": "https://www.pgadmin.org/docs/",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "MySQL Workbench",
        "slug": "mysql-workbench",
        "vendor": "Oracle Corporation",
        "summary": "Unified visual tool for database architects, developers, and DBAs working with MySQL.",
        "official_url": "https://www.mysql.com/products/workbench/",
        "documentation_url": "https://dev.mysql.com/doc/workbench/en/",
        "license_model": "Open Source",
        "supported_engines": ["MySQL"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "Oracle SQL Developer",
        "slug": "oracle-sql-developer",
        "vendor": "Oracle Corporation",
        "summary": "Free graphical user interface designed for database tasks in Oracle Database.",
        "official_url": "https://www.oracle.com/database/sqldeveloper/",
        "documentation_url": "https://docs.oracle.com/en/database/oracle/sql-developer/",
        "license_model": "Free Proprietary",
        "supported_engines": ["Oracle"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "SQL Server Management Studio (SSMS)",
        "slug": "ssms",
        "vendor": "Microsoft",
        "summary": "Integrated environment for managing any SQL infrastructure from SQL Server to Azure SQL.",
        "official_url": "https://learn.microsoft.com/en-us/ssms/",
        "documentation_url": "https://learn.microsoft.com/en-us/ssms/",
        "license_model": "Free Proprietary",
        "supported_engines": ["SQL Server"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "LiteCLI",
        "slug": "litecli",
        "vendor": "DBCLI Community",
        "summary": "CLI for SQLite with auto-completion and syntax highlighting in the terminal.",
        "official_url": "https://litecli.com/",
        "documentation_url": "https://litecli.com/",
        "license_model": "Open Source",
        "supported_engines": ["SQLite"],
    },

    # Monitoring & Observability
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Percona Monitoring and Management (PMM)",
        "slug": "pmm",
        "vendor": "Percona",
        "summary": "Best-of-breed open-source database monitoring, query analytics, and metrics visualization platform.",
        "official_url": "https://www.percona.com/software/pmm",
        "documentation_url": "https://docs.percona.com/percona-monitoring-and-management/",
        "license_model": "Open Source",
        "supported_engines": ["MySQL", "PostgreSQL", "MongoDB"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Prometheus",
        "slug": "prometheus",
        "vendor": "Cloud Native Computing Foundation",
        "summary": "Open-source systems monitoring and alerting toolkit with dimensional data model and PromQL.",
        "official_url": "https://prometheus.io/",
        "documentation_url": "https://prometheus.io/docs/",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL", "MySQL", "Oracle", "Universal"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Grafana",
        "slug": "grafana",
        "vendor": "Grafana Labs",
        "summary": "Open-source platform for query, visualization, alerting, and metrics dashboards across any data source.",
        "official_url": "https://grafana.com/",
        "documentation_url": "https://grafana.com/docs/",
        "license_model": "Open Source / AGPL",
        "supported_engines": ["PostgreSQL", "MySQL", "Oracle", "ClickHouse", "Universal"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "pgMustard",
        "slug": "pgmustard",
        "vendor": "pgMustard",
        "summary": "Visual EXPLAIN ANALYZE query plan inspector that pinpoints performance bottlenecks and suggests index fixes.",
        "official_url": "https://www.pgmustard.com/",
        "documentation_url": "https://www.pgmustard.com/docs",
        "license_model": "Commercial",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "pgwatch",
        "slug": "pgwatch",
        "vendor": "Cybertec",
        "summary": "Flexible, non-invasive PostgreSQL monitoring tool with ready-made Grafana dashboards.",
        "official_url": "https://pgwatch.org/",
        "documentation_url": "https://github.com/cybertec-postgresql/pgwatch",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Oracle Enterprise Manager (OEM)",
        "slug": "oracle-enterprise-manager",
        "vendor": "Oracle Corporation",
        "summary": "Enterprise-grade complete lifecycle management, Active Session History (ASH), AWR diagnostics, and automated patching for Oracle Database and Exadata.",
        "official_url": "https://www.oracle.com/enterprise-manager/",
        "documentation_url": "https://docs.oracle.com/en/enterprise-manager/",
        "license_model": "Commercial / Enterprise",
        "supported_engines": ["Oracle"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "ManageEngine Applications Manager",
        "slug": "manageengine-db-manager",
        "vendor": "Zoho Corporation",
        "summary": "Full-stack enterprise database APM supporting Oracle, SQL Server, PostgreSQL, MySQL, and DB2 with anomaly detection and automated alert runbooks.",
        "official_url": "https://www.manageengine.com/products/applications_manager/database-monitoring.html",
        "documentation_url": "https://www.manageengine.com/products/applications_manager/help/",
        "license_model": "Commercial",
        "supported_engines": ["Oracle", "SQL Server", "PostgreSQL", "MySQL", "DB2"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "IBM Db2 Data Management Console (DMC)",
        "slug": "ibm-dmc",
        "vendor": "IBM",
        "summary": "Unified web console for IBM Db2 monitoring, lock contention visualization, statement cache metrics, and workload management (WLM).",
        "official_url": "https://www.ibm.com/products/db2-data-management-console",
        "documentation_url": "https://www.ibm.com/docs/en/db2-data-mgmt-console",
        "license_model": "Enterprise / Included with Db2",
        "supported_engines": ["IBM Db2"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "EDB Postgres Enterprise Manager (PEM)",
        "slug": "edb-pem",
        "vendor": "EnterpriseDB",
        "summary": "Comprehensive enterprise management and monitoring suite for PostgreSQL with SQL Profiler, capacity planning, and streaming replication topology monitors.",
        "official_url": "https://www.enterprisedb.com/products/edb-postgres-enterprise-manager-pem",
        "documentation_url": "https://www.enterprisedb.com/docs/pem/latest/",
        "license_model": "Commercial / Enterprise",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Prometheus Node Exporter & Host Monitor",
        "slug": "node-exporter",
        "vendor": "Cloud Native Computing Foundation",
        "summary": "Hardware and OS metric collector exposing host CPU steal/wait, disk IOPS queue depth, memory page faults, and filesystem inode exhaustion for DB hosts.",
        "official_url": "https://github.com/prometheus/node_exporter",
        "documentation_url": "https://prometheus.io/docs/guides/node-exporter/",
        "license_model": "Open Source",
        "supported_engines": ["Linux", "Host Server", "Universal"],
    },

    # Backup & Migration
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "pgBackRest",
        "slug": "pgbackrest",
        "vendor": "pgBackRest Community",
        "summary": "High-performance backup and restore solution for PostgreSQL with compression and parallel streaming.",
        "official_url": "https://pgbackrest.org/",
        "documentation_url": "https://pgbackrest.org/user-guide.html",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "Percona XtraBackup",
        "slug": "xtrabackup",
        "vendor": "Percona",
        "summary": "Non-blocking physical backup utility for MySQL and Percona Server without locking databases.",
        "official_url": "https://www.percona.com/software/mysql-database/percona-xtrabackup",
        "documentation_url": "https://docs.percona.com/percona-xtrabackup/",
        "license_model": "Open Source",
        "supported_engines": ["MySQL"],
    },
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "Flyway",
        "slug": "flyway",
        "vendor": "Redgate",
        "summary": "Database version control tool supporting evolutionary migrations across 25+ relational engines.",
        "official_url": "https://www.red-gate.com/products/flyway/",
        "documentation_url": "https://documentation.red-gate.com/flyway",
        "license_model": "Open Source / Commercial",
        "supported_engines": ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "SQLite"],
    },
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "Bytebase",
        "slug": "bytebase",
        "vendor": "Bytebase Inc",
        "summary": "Database CI/CD and GitOps schema change management platform with automated SQL review and rollouts.",
        "official_url": "https://www.bytebase.com/",
        "documentation_url": "https://www.bytebase.com/docs/",
        "license_model": "Freemium",
        "supported_engines": ["PostgreSQL", "MySQL", "Snowflake", "ClickHouse", "Oracle"],
    },
]

SEED_ARTICLES = [
    {
        "slug": "understanding-acid-properties",
        "category_slug": "architecture",
        "engine": "Universal",
        "en": {
            "title": "Understanding ACID Properties in Modern Relational Databases",
            "summary": "A deep dive into Atomicity, Consistency, Isolation, and Durability and why they matter in production workloads.",
            "body": """### What is ACID?
ACID represents the four key guarantees of reliable database transactions:
- **Atomicity**: An operation succeeds entirely or is rolled back completely. Never partial states.
- **Consistency**: Data transitions strictly from one valid state to another according to constraints and triggers.
- **Isolation**: Concurrent transactions do not interfere or observe uncommitted intermediate mutations.
- **Durability**: Once committed, changes survive unexpected crashes, hardware failures, or power loss.

### SQLite Implementation
SQLite guarantees ACID through its Write-Ahead Log (WAL) or Rollback Journal mechanisms.

### PostgreSQL Implementation
PostgreSQL achieves ACID via Multi-Version Concurrency Control (MVCC) and Write-Ahead Logging (WAL).""",
        },
        "id": {
            "title": "Memahami Prinsip ACID pada Database Relasional Modern",
            "summary": "Penjelasan mendalam mengenai Atomicity, Consistency, Isolation, dan Durability dalam beban kerja produksi.",
            "body": """### Apa itu ACID?
ACID adalah empat pilar jaminan keandalan transaksi database relasional:
- **Atomicity (Keutuhan)**: Transaksi sukses seluruhnya atau dibatalkan total. Tidak ada status setengah jalan.
- **Consistency (Konsistensi)**: Data hanya berpindah dari satu status valid ke status valid lainnya sesuai aturan skema dan integritas.
- **Isolation (Isolasi)**: Transaksi bersamaan tidak saling mengganggu atau melihat mutasi yang belum di-commit.
- **Durability (Ketahanan)**: Sekali transaksi di-commit, data dijamin bertahan walau sistem atau server mati mendadak.

### Implementasi pada SQLite
SQLite menjamin ACID melalui mekanisme Write-Ahead Log (WAL) atau Rollback Journal.

### Implementasi pada PostgreSQL
PostgreSQL mengimplementasikan ACID melalui Multi-Version Concurrency Control (MVCC) dan Write-Ahead Logging (WAL).""",
        },
    },
    {
        "slug": "b-tree-indexes-deep-dive",
        "category_slug": "performance",
        "engine": "PostgreSQL & SQLite",
        "en": {
            "title": "B-Tree Indexes: How They Work and When to Use Them",
            "summary": "Demystifying balanced trees, range queries, composite indexes, and index selectivity.",
            "body": """### The B-Tree Data Structure
B-Trees keep data sorted and allow searches, sequential access, insertions, and deletions in logarithmic time: **O(log N)**.

### Best Practices for Indexes:
1. Index columns frequently used in `WHERE`, `JOIN`, and `ORDER BY` clauses.
2. Put the most selective column first in composite indexes.
3. Avoid over-indexing tables with high write volume (every index adds write penalty).
4. Prefer covering indexes when index-only scans can satisfy queries without table lookups.""",
        },
        "id": {
            "title": "B-Tree Index: Cara Kerja dan Kapan Harus Digunakan",
            "summary": "Memahami struktur balanced tree, pencarian rentang (range query), composite index, dan selektivitas index.",
            "body": """### Struktur Data B-Tree
B-Tree menjaga data tetap terurut dan memungkinkan pencarian, akses berurutan, penambahan, serta penghapusan data dalam kompleksitas waktu logaritmik: **O(log N)**.

### Praktik Terbaik Pembuatan Indeks:
1. Berikan indeks pada kolom yang sering muncul di klausa `WHERE`, `JOIN`, dan `ORDER BY`.
2. Letakkan kolom dengan selektivitas tertinggi di urutan pertama pada composite index.
3. Hindari pembuatan indeks berlebih pada tabel yang intensif operasi penulisan (write-heavy).
4. Gunakan covering index bila index-only scan cukup menjawab kueri tanpa perlu membaca heap tabel.""",
        },
    },
    {
        "slug": "sqlite-wal-mode-explained",
        "category_slug": "internals",
        "engine": "SQLite",
        "en": {
            "title": "SQLite Write-Ahead Logging (WAL) Mode Explained",
            "summary": "How WAL mode unlocks concurrent readers alongside a writer in SQLite environments.",
            "body": """### The Default Journal vs. WAL
In classic rollback journal mode, writing locks the whole database from readers.
In **WAL mode** (`PRAGMA journal_mode=WAL;`):
- Readers never block writers.
- Writers never block readers.
- Commits are appended to a `-wal` file and periodically checkpointed back to the main database file.
- Significantly faster in most concurrency workloads.""",
        },
        "id": {
            "title": "Penjelasan Mode Write-Ahead Logging (WAL) pada SQLite",
            "summary": "Bagaimana mode WAL membuka kemampuan pembacaan bersamaan (concurrent readers) tanpa terblokir penulis pada SQLite.",
            "body": """### Perbedaan Rollback Journal vs. Mode WAL
Pada mode rollback journal standar, operasi penulisan akan mengunci seluruh database dari proses pembacaan.
Pada **mode WAL** (`PRAGMA journal_mode=WAL;`):
- Pembaca (readers) tidak pernah memblokir penulis (writers).
- Penulis (writers) tidak pernah memblokir pembaca (readers).
- Operasi commit ditulis ke file `-wal` tambahan dan secara berkala dikonsolidasikan (checkpointing) ke file database utama.
- Meningkatkan performa transaksi berkali-kali lipat pada beban kerja konkuren.""",
        },
    },
    {
        "slug": "database-isolation-levels",
        "category_slug": "architecture",
        "engine": "Universal",
        "en": {
            "title": "SQL Transaction Isolation Levels & Concurrency Phenomena",
            "summary": "Understanding Dirty Reads, Non-repeatable Reads, and Phantom Reads across ANSI SQL isolation levels.",
            "body": """### The 4 ANSI SQL Isolation Levels
1. **Read Uncommitted**: Allows dirty reads (reading uncommitted rows).
2. **Read Committed**: Prevents dirty reads; guarantees reading only committed rows. Default in PostgreSQL.
3. **Repeatable Read**: Prevents dirty and non-repeatable reads. Guarantees consistent snapshot throughout transaction.
4. **Serializable**: Strictest level; guarantees transactions execute as if strictly serial.""",
        },
        "id": {
            "title": "Tingkat Isolasi Transaksi SQL & Fenomena Konkurensi",
            "summary": "Memahami Dirty Reads, Non-repeatable Reads, dan Phantom Reads pada 4 tingkatan isolasi ANSI SQL.",
            "body": """### 4 Tingkat Isolasi Standar ANSI SQL
1. **Read Uncommitted**: Mengizinkan dirty read (membaca baris yang belum di-commit transaksi lain).
2. **Read Committed**: Mencegah dirty read; hanya membaca baris yang sudah di-commit. Merupakan default di PostgreSQL.
3. **Repeatable Read**: Menjamin baris yang dibaca tidak berubah selama transaksi berjalan.
4. **Serializable**: Tingkat terketat; menjamin urutan eksekusi setara dengan eksekusi satu-per-satu tanpa anomali.""",
        },
    },
    {
        "slug": "postgresql-17-architecture-internals",
        "category_slug": "architecture",
        "engine": "PostgreSQL",
        "en": {
            "title": "PostgreSQL 17 Architecture & Internals: MVCC, VACUUM, and WAL",
            "summary": "Mastering PostgreSQL 17 multi-version concurrency control, autovacuum memory tuning, shared buffers, and streaming replication.",
            "body": """### PostgreSQL 17 Core Architecture
PostgreSQL uses a process-based client-server architecture (`postmaster` forks a dedicated backend process per client connection).

### 1. Multi-Version Concurrency Control (MVCC)
In PostgreSQL, an `UPDATE` does not overwrite the row in place; it inserts a new tuple with updated `xmin`/`xmax` system columns while marking the older tuple dead.
- `xmin`: Transaction ID that created the tuple.
- `xmax`: Transaction ID that deleted/superseded the tuple (0 if active).
- **Benefit**: Readers never block writers, and writers never block readers.

### 2. The Role of VACUUM and Autovacuum
Because dead tuples accumulate (table bloat), `VACUUM` reclaims dead space and updates the Free Space Map (FSM) and Visibility Map (VM).
Key PostgreSQL 17 tuning:
```ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_scale_factor = 0.05
maintenance_work_mem = 512MB
```

### 3. Memory Hierarchy: Shared Buffers & Work Mem
- `shared_buffers`: Dedicated buffer cache (typically set to 25% of total server RAM).
- `work_mem`: Memory allocated per sort/hash operation per query. Set carefully to prevent OOM.
- `effective_cache_size`: Informs the planner how much filesystem cache is available (typically 50-75% of RAM).

### 4. Streaming Replication & WAL
Transactions append changes sequentially to Write-Ahead Log (WAL) files in `pg_wal/`.
- Synchronous or asynchronous standby nodes stream WAL records via `walsender` and `walreceiver`.
- Use `pg_stat_replication` to monitor replication lag in bytes and time.""",
        },
        "id": {
            "title": "Arsitektur & Internal PostgreSQL 17: MVCC, VACUUM, dan WAL",
            "summary": "Memahami kontrol konkurensi MVCC pada PostgreSQL 17, optimasi autovacuum, shared buffers, dan replikasi streaming.",
            "body": """### Arsitektur Inti PostgreSQL 17
PostgreSQL menggunakan model proses berbasis client-server (proses `postmaster` melakukan `fork` untuk membuat proses backend per koneksi client).

### 1. Multi-Version Concurrency Control (MVCC)
Pada PostgreSQL, perintah `UPDATE` tidak menimpa data lama di disk, melainkan menyisipkan baris (tuple) baru dengan mencatat ID transaksi pada `xmin`/`xmax`, sementara baris lama ditandai sebagai dead tuple.
- `xmin`: ID transaksi pembuat baris.
- `xmax`: ID transaksi yang menghapus/memperbarui baris.
- **Keuntungan**: Operasi baca tidak pernah mengunci operasi tulis, dan sebaliknya.

### 2. Peran VACUUM dan Autovacuum
Dead tuple yang menumpuk menyebabkan bloat (pembengkakan ukuran tabel). `VACUUM` membebaskan ruang kosong untuk dipakai kembali dan memperbarui Free Space Map (FSM).
Konfigurasi penting pada PostgreSQL 17:
```ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_scale_factor = 0.05
maintenance_work_mem = 512MB
```

### 3. Hirarki Memori: Shared Buffers & Work Mem
- `shared_buffers`: Alokasi cache tabel di RAM (umumnya disetel pada 25% total RAM server).
- `work_mem`: Memori per operasi sorting/hashing per kueri.
- `effective_cache_size`: Estimasi cache filesystem untuk optimizer (50-75% total RAM).

### 4. Streaming Replication & WAL
Setiap mutasi data dicatat berurutan pada file Write-Ahead Log (WAL) di direktori `pg_wal/`.
- Server standby mereplikasi WAL secara real-time via proses `walsender` dan `walreceiver`.
- Pantau keterlambatan data melalui view `pg_stat_replication`.""",
        },
    },
    {
        "slug": "mysql-11-innodb-replication-guide",
        "category_slug": "architecture",
        "engine": "MySQL / MariaDB",
        "en": {
            "title": "MySQL & MariaDB 11 Deep Dive: InnoDB Engine, Buffer Pool & GTID Replication",
            "summary": "Anatomy of the InnoDB storage engine, doublewrite buffers, redo logs, and production GTID replication topologies.",
            "body": """### The InnoDB Storage Engine
InnoDB is the ACID-compliant default storage engine for MySQL and MariaDB, organizing tables in clustered B+tree indexes ordered by Primary Key.

### 1. The InnoDB Buffer Pool
The single most critical memory structure in MySQL. Caches data pages, index pages, undo pages, and change buffers.
```ini
# my.cnf
innodb_buffer_pool_size = 8G      # 60-75% of dedicated server RAM
innodb_buffer_pool_instances = 8  # Reduces thread concurrency contention
innodb_log_file_size = 2G         # Redo log capacity
innodb_flush_log_at_trx_commit = 1 # 1 = Full ACID compliance
```

### 2. Durability Mechanisms: Redo Log & Doublewrite Buffer
- **Redo Log (`ib_logfile`)**: Sequential circular log recording physical page changes before memory pages flush.
- **Doublewrite Buffer**: Prevents page corruption from torn writes by writing pages to a contiguous disk buffer before writing to `.ibd` tablespace files.

### 3. Global Transaction Identifier (GTID) Replication
GTID assigns a unique 128-bit UUID and sequence number to every committed transaction (`source_id:transaction_id`).
- Eliminates tracking binlog file coordinates (`mysql-bin.000123:456`).
- Enables automated topology failovers via tools like Orchestrator and ProxySQL.""",
        },
        "id": {
            "title": "Panduan Mendalam MySQL & MariaDB 11: Mesin InnoDB, Buffer Pool & Replikasi GTID",
            "summary": "Anatomi mesin penyimpanan InnoDB, doublewrite buffer, redo log, dan konfigurasi replikasi berbasis GTID.",
            "body": """### Mesin Penyimpanan InnoDB
InnoDB adalah mesin penyimpanan default berbasis ACID untuk MySQL dan MariaDB. Semua tabel disimpan dengan clustered B+tree berurutan berdasarkan Primary Key.

### 1. InnoDB Buffer Pool
Struktur memori paling vital di MySQL. Berfungsi meng-cache halaman data, indeks, undo log, dan change buffer di RAM.
```ini
# my.cnf
innodb_buffer_pool_size = 8G      # 60-75% dari total RAM server khusus database
innodb_buffer_pool_instances = 8  # Membagi buffer pool untuk mencegah thread contention
innodb_log_file_size = 2G         # Kapasitas Redo Log
innodb_flush_log_at_trx_commit = 1 # 1 = Jaminan penuh ACID Durability
```

### 2. Menjaga Integritas Data: Redo Log & Doublewrite Buffer
- **Redo Log**: Mencatat perubahan fisik halaman disk secara sekuensial sebelum data di-flush ke disk.
- **Doublewrite Buffer**: Mencegah kerusakan halaman data akibat torn write (listrik mati saat menulis halaman 16KB).

### 3. Replikasi Modern Berbasis GTID
GTID (Global Transaction Identifier) memberikan pengenal unik pada setiap transaksi (`UUID:sequence_number`).
- Menghapus kerumitan pelacakan koordinat file binlog manual (`file:position`).
- Mempermudah failover klaster otomatis menggunakan tools seperti Orchestrator dan ProxySQL.""",
        },
    },
    {
        "slug": "oracle-23ai-enterprise-architecture",
        "category_slug": "architecture",
        "engine": "Oracle",
        "en": {
            "title": "Oracle 23ai Architecture: Multitenant CDB/PDB, SGA/PGA & AWR Telemetry",
            "summary": "Exploring Oracle 23ai multitenant architecture, System Global Area memory allocation, and Automatic Workload Repository (AWR) diagnostics.",
            "body": """### Oracle 23ai Multitenant Architecture
Oracle Database 23ai enforces the Container Database (CDB) and Pluggable Database (PDB) paradigm:
- **CDB$ROOT**: Stores Oracle-supplied metadata and common administrative users.
- **PDBs**: Self-contained, portable tenant databases holding user schemas and data.

### 1. Memory Structure: SGA vs. PGA
- **SGA (System Global Area)**: Shared memory region allocated at instance startup.
  - *Database Buffer Cache*: Caches blocks read from datafiles.
  - *Shared Pool*: Caches parsed SQL execution plans (Library Cache) and data dictionary metadata (Row Cache).
  - *Redo Log Buffer*: Circular buffer recording database mutations.
- **PGA (Program Global Area)**: Dedicated private memory per server process (used for sorting, hashing, and cursor state).

### 2. Telemetry & Diagnostics: AWR and ASH
- **AWR (Automatic Workload Repository)**: Captures snapshots every 60 minutes, recording top SQL by elapsed time, wait events, and I/O profiles.
- **ASH (Active Session History)**: Samples active sessions once every second in memory, enabling micro-level bottleneck triage.""",
        },
        "id": {
            "title": "Arsitektur Oracle 23ai: Multitenant CDB/PDB, Memori SGA/PGA & Telemetri AWR",
            "summary": "Memahami arsitektur multitenant Oracle 23ai, alokasi memori SGA/PGA, serta diagnostik Automatic Workload Repository (AWR).",
            "body": """### Arsitektur Multitenant Oracle 23ai
Oracle Database 23ai menggunakan paradigma Container Database (CDB) dan Pluggable Database (PDB):
- **CDB$ROOT**: Menyimpan metadata internal sistem Oracle dan user administratif bersama.
- **PDB**: Database mandiri dan portabel yang menampung skema dan data aplikasi pengguna.

### 1. Struktur Memori: SGA vs. PGA
- **SGA (System Global Area)**: Memori bersama yang dialokasikan saat instance Oracle dinyalakan.
  - *Database Buffer Cache*: Menyimpan blok data tabel dan indeks.
  - *Shared Pool*: Menyimpan rencana eksekusi SQL (Library Cache) dan kamus data skema.
  - *Redo Log Buffer*: Buffer sirkular penampung mutasi data sebelum ditulis ke disk.
- **PGA (Program Global Area)**: Memori privat per proses koneksi pengguna (digunakan untuk sort dan hash join).

### 2. Diagnostik & Analisis Performa: AWR dan ASH
- **AWR (Automatic Workload Repository)**: Mengambil snapshot metrik setiap 60 menit untuk menganalisis SQL terberat, konsumsi I/O, dan wait event.
- **ASH (Active Session History)**: Merekam aktivitas sesi aktif setiap 1 detik di memori untuk diagnosis insiden performa secara real-time.""",
        },
    },
    {
        "slug": "sql-server-2022-internals-query-store",
        "category_slug": "architecture",
        "engine": "SQL Server",
        "en": {
            "title": "SQL Server 2022 Architecture: Storage Engine, Query Store & Extended Events",
            "summary": "Deep dive into Microsoft SQL Server 2022 extents, clustered index storage, Query Store plan forcing, and Extended Events telemetry.",
            "body": """### Storage Engine Organization
SQL Server stores database data in 8 KB pages grouped into 64 KB extents (8 contiguous pages).
- **Clustered Index**: The leaf level of the index *is* the actual table data itself, physically sorted by cluster key.
- **Non-Clustered Index**: Separate B-tree structure holding key columns and a row locator (pointer to clustered key).

### 1. Query Store: The Database Flight Recorder
Query Store continuously captures history of queries, execution plans, and runtime statistics:
- Automatically detects plan regressions where a query suddenly consumes 10x more CPU.
- Allows DBAs to force good execution plans with a single command without altering application code.

### 2. Telemetry: Extended Events (XEvents) vs. SQL Profiler
- **SQL Profiler**: Deprecated; heavy client overhead that can degrade production throughput.
- **Extended Events**: High-performance, lightweight event-handling engine built directly into the SQL Server kernel with minimal CPU impact (< 1%).""",
        },
        "id": {
            "title": "Arsitektur SQL Server 2022: Mesin Penyimpanan, Query Store & Extended Events",
            "summary": "Memahami organisasi halaman 8KB, indeks clustered, Query Store untuk stabilisasi rencana kueri, dan telemetri Extended Events.",
            "body": """### Organisasi Mesin Penyimpanan SQL Server
SQL Server menyimpan data dalam halaman (page) berukuran 8 KB yang dikelompokkan ke dalam extent 64 KB (8 halaman berurutan).
- **Clustered Index**: Daun (leaf level) dari pohon indeks merupakan data baris fisik tabel itu sendiri yang terurut berdasarkan cluster key.
- **Non-Clustered Index**: Struktur B-tree terpisah yang menampung kolom kunci dan pointer ke clustered key.

### 1. Query Store: Flight Recorder Database
Query Store merekam riwayat eksekusi kueri, rencana eksekusi (execution plan), dan statistik latensi:
- Mendeteksi regresi performa kueri secara otomatis.
- Mengizinkan DBA memaksa (force) execution plan yang efisien tanpa mengubah kode aplikasi.

### 2. Telemetri: Extended Events (XEvents) Menggantikan SQL Profiler
- **SQL Profiler**: Bersifat usang (deprecated) dan membebani server secara signifikan.
- **Extended Events**: Sistem pelacakan event terintegrasi langsung pada kernel SQL Server dengan overhead sangat rendah (< 1% CPU).""",
        },
    },
    {
        "slug": "database-monitoring-golden-signals",
        "category_slug": "performance",
        "engine": "Universal",
        "en": {
            "title": "Database Observability Guide: The 4 Golden Signals, Exporters & PMM Runbooks",
            "summary": "Actionable monitoring architecture for production databases: Latency, Traffic, Errors, and Saturation with PromQL and Grafana.",
            "body": """### The 4 Golden Signals for Database Observability
Google's Site Reliability Engineering framework applied to relational databases:

### 1. Latency
Time taken to service read and write queries.
- **Target**: p95 < 20ms, p99 < 50ms.
- **Metric**: `rate(pg_stat_statements_total_time_ms[5m]) / rate(pg_stat_statements_calls[5m])`.

### 2. Traffic (Throughput)
Volume of transactions demanded by clients.
- **Metric**: Transactions per Second (TPS), Queries per Second (QPS).
- **PromQL**: `rate(pg_stat_database_xact_commit[1m]) + rate(pg_stat_database_xact_rollback[1m])`.

### 3. Errors
Failure rate of database operations.
- **Metric**: Transaction abort rate, Deadlock counts, Connection authorization rejections.
- **PromQL**: `increase(mysql_global_status_innodb_deadlocks[1h])`.

### 4. Saturation
Fraction of database resource capacity utilized.
- **Buffer Pool / Shared Buffer Hit Ratio**: Must stay > 99%.
- **Active Connections**: Alert when `active_connections / max_connections > 0.85`.
- **Replication Lag**: Alert when standby replication lag exceeds 30 seconds.""",
        },
        "id": {
            "title": "Panduan Observabilitas Database: 4 Golden Signals, Exporter & Runbook PMM",
            "summary": "Arsitektur monitoring database produksi: Latency, Traffic, Errors, dan Saturation menggunakan PromQL dan dashboard Grafana.",
            "body": """### 4 Golden Signals untuk Observabilitas Database
Penerapan standar Google SRE untuk memantau kesehatan database relasional:

### 1. Latensi (Latency)
Waktu yang dibutuhkan untuk mengeksekusi kueri baca dan tulis.
- **Target**: p95 < 20ms, p99 < 50ms.
- **Metrik**: Rata-rata waktu eksekusi kueri melalui `pg_stat_statements` atau InnoDB Query Analytics (QAN).

### 2. Trafik (Throughput)
Beban transaksi yang diproses database dari aplikasi.
- **Metrik**: Transactions per Second (TPS) dan Queries per Second (QPS).
- **PromQL**: `rate(pg_stat_database_xact_commit[1m]) + rate(pg_stat_database_xact_rollback[1m])`.

### 3. Kesalahan (Errors)
Tingkat kegagalan operasi database.
- **Metrik**: Rollback paksa, frekuensi deadlock per jam, dan penolakan koneksi akibat penuh.
- **PromQL**: `increase(mysql_global_status_innodb_deadlocks[1h])`.

### 4. Saturasi (Saturation)
Persentase pemanfaatan kapasitas sumber daya database.
- **Buffer Cache Hit Ratio**: Harus bertahan di atas 99%.
- **Utilisasi Koneksi**: Berikan peringatan jika `koneksi aktif / max_connections > 85%`.
- **Replication Lag**: Berikan alert jika keterlambatan replikasi melebihi 30 detik.""",
        },
    },
    {
        "slug": "enterprise-monitoring-apps-oem-manageengine-dmc-ssms-pem",
        "category_slug": "monitoring",
        "engine": "Universal",
        "en": {
            "title": "Enterprise Database Monitoring Suites: OEM, ManageEngine, IBM DMC, SSMS, PEM & Server Telemetry",
            "summary": "Deep architectural analysis of industry-standard database management and APM suites: OEM, ManageEngine, IBM DMC, SSMS, PEM, and Linux host server telemetry.",
            "body": """### Enterprise Database APM & Monitoring Suites
Modern enterprises manage heterogeneous database fleets spanning Oracle, SQL Server, PostgreSQL, MySQL, and IBM Db2. Dedicated monitoring suites provide deep internal instrumentation beyond basic black-box ping checks.

---

### 1. Oracle Enterprise Manager (OEM Cloud Control)
The gold standard for mission-critical Oracle Exadata and Database fleets.
- **Core Architecture**:
  - **Oracle Management Agent (OMA)**: Light agent running on each database host collecting internal SGA/PGA metrics.
  - **Oracle Management Service (OMS)**: WebLogic-based middleware orchestrating telemetry ingestion.
  - **Oracle Management Repository (OMR)**: Dedicated Oracle database storing historical metrics and performance baselines.
- **Key Capabilities**:
  - **Active Session History (ASH)**: 1-second sample of non-idle sessions waiting on CPU or wait events.
  - **Automatic Workload Repository (AWR)**: 60-minute automated snapshots of top SQL, system waits, and latch contention.
  - **ADDM (Automatic Database Diagnostic Monitor)**: AI-driven diagnostic engine identifying performance bottlenecks and root causes.
  - **Tablespace Capacity Alerts**: Threshold warnings for data file autoextend limits and high water mark expansion.

---

### 2. ManageEngine Applications Manager & OpManager
Widely adopted enterprise APM for heterogeneous database environments.
- **Architecture**:
  - Centralized collector utilizing agentless JDBC/WMI/SSH or lightweight local monitoring agents.
- **Key Capabilities**:
  - **Multi-Engine Dashboard**: Unified monitoring across Oracle, SQL Server, PostgreSQL, MySQL, DB2, and SAP HANA.
  - **Anomaly Detection**: Machine learning baselines triggering alerts when query latency or active connection count deviates from historic patterns.
  - **Automated Remediation Runbooks**: Configurable webhooks to execute shell scripts, restart services, or notify PagerDuty/ServiceNow.

---

### 3. IBM Db2 Data Management Console (DMC)
Unified browser-based console designed specifically for IBM Db2 on-premises and hybrid cloud.
- **Core Features**:
  - **Real-Time Lock & Blocker Graphs**: Interactive topology showing waiting transactions, lock escalations, and deadlocks.
  - **Statement Cache Analysis**: Real-time inspection of dynamic and static SQL statements with execution count and CPU consumption.
  - **Workload Management (WLM)**: Monitoring service classes, thresholds, and priority queuing to protect OLTP from rogue analytical queries.

---

### 4. SQL Server Management Studio (SSMS) & Diagnostic Tooling
The native administrative and diagnostic cockpit for Microsoft SQL Server and Azure SQL.
- **Key Monitoring Components**:
  - **Activity Monitor**: Real-time pane displaying Processor Time, Waiting Tasks, Database I/O (MB/sec), and Batch Requests/sec.
  - **Extended Events (XEvents)**: High-performance, lightweight event tracing replacing deprecated SQL Profiler with minimal CPU overhead.
  - **Query Store**: Flight recorder inside the database capturing execution plan changes, runtime stats, and plan regression detection with one-click Plan Forcing.

---

### 5. EDB Postgres Enterprise Manager (PEM)
Enterprise-grade management platform for high-scale PostgreSQL and EDB Postgres Advanced Server.
- **Architecture**:
  - **PEM Server**: Centralized PostgreSQL instance hosting monitoring metadata and alert definitions.
  - **PEM Agent**: Deployed on database nodes to inspect Postgres server logs and collect low-level metrics.
- **Key Features**:
  - **Postgres Expert Rules**: Static and dynamic analyzer auditing security compliance and configuration parameters (`shared_buffers`, `work_mem`, `wal_buffers`).
  - **SQL Profiler**: Integrated trace engine capturing problematic queries directly within PEM.
  - **Streaming Replication Monitor**: Topology map showing primary and standby lag in bytes and time.

---

### 6. Host & Server Infrastructure Telemetry (Prometheus Node Exporter)
Database performance is directly bounded by the host OS. A healthy DBA dashboard must monitor:
- **Disk I/O Saturation (`%util` & IOPS)**: Sustained 100% disk utilization indicates disk queue bottleneck.
- **CPU I/O Wait (`%iowait`)**: CPU idle cycles spent waiting on disk reads or synchronous WAL/Redo writes.
- **Memory Paging / Swap Thrashing**: Paging database memory to swap destroys query latency; `vm.swappiness` should be tuned to 1 or 10.
- **Filesystem Inodes (`df -i`)**: Databases creating thousands of temp files or WAL archives can fail with "Disk full" errors if inode capacity is exhausted, even with gigabytes of free disk space remaining.""",
        },
        "id": {
            "title": "Aplikasi Monitoring Database Enterprise: OEM, ManageEngine, IBM DMC, SSMS, PEM & Telemetri Server",
            "summary": "Analisis arsitektural mendalam aplikasi APM dan manajemen database standar industri: OEM, ManageEngine, IBM DMC, SSMS, PEM, dan telemetri server Linux.",
            "body": """### Aplikasi Monitoring & APM Database Enterprise
Perusahaan modern mengelola cluster database heterogen yang mencakup Oracle, SQL Server, PostgreSQL, MySQL, dan IBM Db2. Aplikasi pemantau khusus memberikan instrumentasi internal mendalam jauh melampaui sekadar ping uptime jaringan.

---

### 1. Oracle Enterprise Manager (OEM Cloud Control)
Standar tertinggi untuk memantau cluster database Oracle Exadata dan database mission-critical.
- **Arsitektur Inti**:
  - **Oracle Management Agent (OMA)**: Agen ringan pada server database untuk membaca telemetri SGA/PGA secara real-time.
  - **Oracle Management Service (OMS)**: Middleware berbasis WebLogic yang memproses dan menganalisis aliran metrik.
  - **Oracle Management Repository (OMR)**: Database Oracle khusus untuk menyimpan riwayat metrik dan baseline performa.
- **Fitur Kunci**:
  - **Active Session History (ASH)**: Sampel 1-detik sesi aktif yang sedang menunggu antrean event atau CPU.
  - **Automatic Workload Repository (AWR)**: Snapshot otomatis per 60 menit berisi kueri terberat, latensi I/O, dan latch contention.
  - **ADDM**: Mesin diagnostik otomatis yang mengidentifikasi bottleneck dan akar masalah performa kueri.
  - **Alert Kapasitas Tablespace**: Peringatan batas autoextend datafile dan High Water Mark (HWM).

---

### 2. ManageEngine Applications Manager & OpManager
Solusi APM enterprise populer untuk monitoring database multi-vendor terpusat.
- **Arsitektur**:
  - Collector terpusat yang menggunakan koneksi agentless JDBC/WMI/SSH atau agent lokal.
- **Fitur Kunci**:
  - **Dashboard Terintegrasi**: Satu layar untuk memantau Oracle, SQL Server, PostgreSQL, MySQL, DB2, dan SAP HANA.
  - **Deteksi Anomali Berbasis AI**: Mempelajari pola normal latensi dan koneksi aktif untuk membunyikan alert sebelum sistem tumbang.
  - **Runbook Remediasi Otomatis**: Menjalankan skrip bash/powershell otomatis saat terjadi kegagalan layanan.

---

### 3. IBM Db2 Data Management Console (DMC)
Konsol berbasis browser resmi untuk pengelolaan dan pemantauan IBM Db2 on-premise maupun cloud.
- **Fitur Kunci**:
  - **Grafik Antrean Lock & Blocker Real-Time**: Visualisasi interaktif rantai sesi yang terkunci dan terblokir.
  - **Analisis Statement Cache**: Menampilkan kueri SQL dinamis/statis terberat beserta konsumsi CPU dan durasi eksekusi.
  - **Workload Management (WLM)**: Mengatur kelas prioritas transaksi agar kueri analitik berat tidak melumpuhkan transaksi kasir/OLTP.

---

### 4. SQL Server Management Studio (SSMS) & Diagnostik
Pusat kendali administratif dan diagnostik resmi Microsoft SQL Server dan Azure SQL.
- **Komponen Diagnostik Utama**:
  - **Activity Monitor**: Panel real-time menampilkan beban CPU, task yang menunggu antrean, volume I/O data file (MB/s), dan Batch Requests/sec.
  - **Extended Events (XEvents)**: Mekanisme logging event berkecepatan tinggi yang menggantikan SQL Profiler lama tanpa membebani performa CPU server.
  - **Query Store**: Kotak hitam internal database yang merekam histori perubahan query plan, mendeteksi regresi performa, dan menyediakan fitur Plan Forcing.

---

### 5. EDB Postgres Enterprise Manager (PEM)
Platform manajemen enterprise khusus untuk database PostgreSQL dan EDB Postgres Advanced Server berskala besar.
- **Arsitektur**:
  - **PEM Server**: Instans PostgreSQL terpusat yang menyimpan metadata monitoring dan aturan alert.
  - **PEM Agent**: Terpasang di server database untuk membaca log engine dan status sistem operasi.
- **Fitur Kunci**:
  - **Postgres Expert Rules**: Menganalisis konfigurasi database (`shared_buffers`, `work_mem`) dan memeriksa kepatuhan standar keamanan secara berkala.
  - **SQL Profiler**: Melacak query bermasalah langsung dari antarmuka web.
  - **Peta Replikasi Streaming**: Diagram topologi menampilkan lag replikasi antara primary dan standby dalam satuan byte dan detik.

---

### 6. Telemetri Infrastruktur & Host Server (Node Exporter)
Performa database dibatasi langsung oleh stabilitas server fisik atau VM tempat database berjalan. Metrik wajib pada dashboard DBA:
- **Saturasi Disk I/O (`%util` & IOPS)**: Utilisasi disk 100% secara kontinu menandakan antrean disk jenuh.
- **CPU I/O Wait (`%iowait`)**: Siklus CPU terbuang sia-sia karena menunggu data dibaca dari disk atau ditulis ke WAL/Redo log.
- **Memory Swap Thrashing**: Jika OS mulai memindahkan buffer pool database ke partisi Swap, latensi query akan melonjak drastis. Disarankan menyetel `vm.swappiness = 1`.
- **Kapasitas Inode Filesystem (`df -i`)**: Jika direktori temporary atau arsip WAL menghabiskan inode, database akan gagal menulis data dengan galat 'Disk Full', meskipun sisa kapasitas gigabyte disk masih banyak.""",
        },
    },
    {
        "slug": "tablespaces-blocking-locks-and-mirroring-guide",
        "category_slug": "architecture",
        "engine": "Universal",
        "en": {
            "title": "Production Architecture: Tablespaces, Lock Blocking Trees & Database Mirroring",
            "summary": "Mastering storage allocation in tablespaces, diagnosing root-cause blocking session trees, and architecting database mirroring & replication topologies.",
            "body": """### Production Database Storage & Concurrency Architecture

---

### 1. Tablespaces & Physical Storage Hierarchy
Relational databases decouple logical data structures from physical storage using Tablespaces:
- **Logical to Physical Mapping**:
  - **Database** → Contains multiple **Tablespaces**.
  - **Tablespace** → Composed of one or more physical **Data Files** (`.dbf`, `.ibd`, `.mdf`).
  - **Segment** → An individual table or index structure.
  - **Extent** → A contiguous set of database pages/blocks (typically 64KB - 1MB).
  - **Page / Block** → Smallest unit of I/O (8KB in PostgreSQL/SQL Server, 8KB/16KB in Oracle/MySQL).
- **High Water Mark (HWM)**:
  - In Oracle and transactional databases, the HWM indicates the highest block ever formatted for data.
  - Massive `DELETE` statements do NOT lower the HWM; table scans continue reading empty blocks up to the HWM until an `ALTER TABLE ... SHRINK SPACE` or `VACUUM FULL` is executed.
- **Autoextend Best Practices**:
  - Never allow percentage-based autoextend (e.g., `AUTOEXTEND ON NEXT 10%`) as large files cause massive allocation pauses. Use fixed allocation steps (e.g., `NEXT 512M MAXSIZE 32G`).

---

### 2. Lock Blocking Chains & Deadlock Diagnostics
Concurrency control mechanisms protect ACID properties but introduce blocking under contention:
- **Lock Hierarchy**:
  - **Shared Lock (S)**: Held during read operations; allows multiple readers.
  - **Exclusive Lock (X)**: Held during write operations (`INSERT`, `UPDATE`, `DELETE`); blocks both readers and writers.
  - **Intent Locks (IS, IX)**: Indicate locking intention at lower levels (row/page) to prevent table-level locks from acquiring conflicting permissions.
- **The Blocker Tree**:
  - When Session A locks Row 1, Session B waits for Row 1 while locking Row 2, and Session C waits for Row 2.
  - **Root Blocker**: The head of the chain (Session A) is NOT waiting on any other session, but holds the lock blocking everyone downstream.
  - **Diagnostic Queries**:
    - **Oracle**: Query `v$session` checking `BLOCKING_SESSION`.
    - **PostgreSQL**: Query `pg_locks` self-joined on `locktype`, `relation`, and `tuple`.
    - **SQL Server**: Inspect `sys.dm_exec_requests` checking `blocking_session_id`.
- **Deadlock Resolution**:
  - A deadlock occurs when a cycle forms in the Wait-For Graph (Session A holds X and waits for Y; Session B holds Y and waits for X).
  - The database deadlock detection engine identifies the cycle and kills one session (the "deadlock victim"), rolling back its transaction.

---

### 3. Database Mirroring & High Availability Topologies
To protect against hardware and datacenter failures, databases synchronize transaction logs to standby instances:
- **SQL Server AlwaysOn Availability Groups (formerly Database Mirroring)**:
  - **Principal (Primary)**: Handles read-write client transactions.
  - **Secondary (Mirror)**: Replays incoming transaction log records in memory and disk.
  - **Synchronous Commit**: Primary waits for confirmation that the log block is written to disk on the secondary before returning commit success (Zero data loss, slight network latency penalty).
  - **Asynchronous Commit**: Primary commits immediately without waiting (Maximum performance, minimal RPO data loss risk).
- **Oracle Active Data Guard**:
  - **Primary**: Transmits Redo Log buffers via Log Network Server (LNS).
  - **Physical Standby**: Remote File Server (RFS) receives redo logs and applies them using Redo Apply (MRP).
  - **Fast-Start Failover (FSFO)**: Automatically promotes the standby if the primary heartbeat drops.
- **PostgreSQL Streaming Replication + Patroni**:
  - Standby nodes connect via physical replication slots and stream WAL records continuously.
  - **Patroni**: Utilizes an external consensus store (Consul, Etcd, or Raft) to manage automated leader election and split-brain prevention.""",
        },
        "id": {
            "title": "Arsitektur Produksi: Tablespace, Antrean Blocking Lock & Mirroring Database",
            "summary": "Memahami alokasi ruang pada tablespace, mendiagnosis akar masalah rantai blocking lock, dan merancang topologi mirroring database.",
            "body": """### Arsitektur Penyimpanan & Konkurensi Database Produksi

---

### 1. Tablespace & Hirarki Penyimpanan Fisik
Database enterprise memisahkan struktur data logis dari file fisik menggunakan konsep Tablespace:
- **Pemetaan Logis ke Fisik**:
  - **Database** → Terdiri dari beberapa **Tablespace**.
  - **Tablespace** → Berisi satu atau lebih file data fisik di disk (`.dbf`, `.ibd`, `.mdf`).
  - **Segment** → Satu struktur tabel atau indeks.
  - **Extent** → Sekumpulan blok halaman disk yang berurutan (biasanya 64KB - 1MB).
  - **Page / Block** → Unit I/O terkecil (8KB di PostgreSQL/SQL Server, 8KB/16KB di Oracle/MySQL).
- **High Water Mark (HWM)**:
  - Garis batas tertinggi blok data yang pernah diisi oleh database.
  - Operasi `DELETE` massal TIDAK menurunkan HWM; pemindaian tabel (full table scan) akan tetap membaca blok-blok kosong tersebut sampai dilakukan `ALTER TABLE ... SHRINK SPACE` atau `VACUUM FULL`.
- **Praktik Terbaik Autoextend**:
  - Hindari penambahan ukuran berdasarkan persentase (`AUTOEXTEND ON NEXT 10%`) karena file besar akan memicu jeda I/O panjang saat alokasi. Gunakan penambahan tetap (misal: `NEXT 512M MAXSIZE 32G`).

---

### 2. Rantai Blocking Lock & Diagnostik Deadlock
Kontrol konkurensi menjamin sifat ACID tetapi menimbulkan antrean (blocking) saat terjadi perebutan baris yang sama:
- **Hirarki Kunci (Locks)**:
  - **Shared Lock (S)**: Dimiliki saat query baca (`SELECT`); mengizinkan banyak pembaca sekaligus.
  - **Exclusive Lock (X)**: Dimiliki saat operasi tulis (`INSERT`, `UPDATE`, `DELETE`); mengunci pembaca dan penulis lain.
  - **Intent Locks (IS, IX)**: Mengindikasikan niat penguncian di level baris/halaman agar tabel tidak dikunci secara eksklusif oleh proses lain.
- **Rantai Antrean (Blocker Tree)**:
  - Saat Sesi A mengunci Baris 1, Sesi B menunggu Baris 1 sambil memegang Baris 2, dan Sesi C menunggu Baris 2.
  - **Root Blocker**: Sesi kepala (Sesi A) tidak menunggu siapa pun, namun menjadi penyebab seluruh sesi di belakangnya macet.
  - **Kueri Diagnostik**:
    - **Oracle**: Cek view `v$session` pada kolom `BLOCKING_SESSION`.
    - **PostgreSQL**: Kueri `pg_locks` yang dihubungkan ke `pg_stat_activity`.
    - **SQL Server**: Periksa `sys.dm_exec_requests` pada kolom `blocking_session_id`.
- **Penyelesaian Deadlock**:
  - Deadlock terjadi saat terbentuk siklus saling tunggu (Sesi A memegang X dan menunggu Y; Sesi B memegang Y dan menunggu X).
  - Mesin database secara otomatis mendeteksi siklus ini dan mematikan salah satu transaksi (Deadlock Victim) lalu melakukan rollback agar sistem kembali berjalan normal.

---

### 3. Mirroring & Topologi High Availability (HA)
Untuk melindungi data dari kegagalan server fisik atau bencana pusat data, transaksi disinkronkan ke replika standby:
- **SQL Server AlwaysOn Availability Groups (Database Mirroring)**:
  - **Principal**: Memproses transaksi baca dan tulis dari aplikasi.
  - **Secondary (Mirror)**: Menerima dan menuliskan catatan transaksi (transaction log) ke disk replika.
  - **Synchronous Commit**: Transaksi di primary baru dianggap sukses setelah standby mengonfirmasi catatan tersimpan di disk (Jaminan Zero Data Loss, RPO = 0).
  - **Asynchronous Commit**: Transaksi di primary langsung di-commit tanpa menunggu standby (Performa maksimal, sedikit risiko data tertinggal jika primary tiba-tiba padam).
- **Oracle Active Data Guard**:
  - **Primary**: Mengirim Redo Log buffer secara langsung melalui proses LNS (Log Network Server).
  - **Standby Fisik**: Menerima redo log dan mengaplikasikannya ke data file menggunakan proses MRP (Managed Recovery Process).
  - **Fast-Start Failover (FSFO)**: Mengalihkan peran standby menjadi primary secara otomatis saat sinyal heartbeat terputus.
- **PostgreSQL Streaming Replication + Patroni**:
  - Standby terhubung melalui physical replication slot dan mereplikasi data WAL secara streaming kontinu.
  - **Patroni**: Menggunakan konsensus terdistribusi (Etcd, Consul, atau Raft) untuk memilih leader baru secara otomatis tanpa risiko split-brain.""",
        },
    },
    {
        "slug": "kubernetes-and-docker-for-enterprise-databases",
        "category_slug": "architecture",
        "engine": "Universal",
        "en": {
            "title": "Containerized Databases: Kubernetes StatefulSets, DB Operators & Docker Runtime Optimization",
            "summary": "Production guide for running stateful databases on Kubernetes and Docker: StatefulSets, StorageClasses, CloudNativePG/CrunchyData operators, shared memory IPC, and cgroup limits.",
            "body": """### Running Stateful Databases on Containers: Kubernetes & Docker

---

### 1. Kubernetes for Databases: StatefulSets vs Deployments
Stateless web applications use `Deployments`, but relational databases require `StatefulSets`:
- **Stable Network Identity**: Pods receive predictable hostnames (`postgres-cluster-0`, `postgres-cluster-1`). Standby nodes always know the exact hostname of the primary node.
- **Ordered Deployment and Scaling**: Pod `db-0` must be healthy and running before `db-1` is launched, preventing concurrent initialization conflicts.
- **Persistent Storage Binding**: Each pod template specifies a `volumeClaimTemplates` which dynamically provisions an independent PersistentVolume (PV) that stays attached even if the pod restarts on another worker node.

---

### 2. Kubernetes StorageClasses & I/O Performance
Storage layer selection determines database transactions per second (TPS):
- **Local NVMe SSDs (Local Persistent Volumes)**:
  - Delivers direct hardware I/O performance (sub-millisecond latency, zero network hops).
  - Requires database-level replication (Patroni, InnoDB Cluster) to protect against local node disk failure.
- **Network Block Storage (AWS EBS gp3/io2, Ceph, GCP pd-ssd)**:
  - Allows easy pod migration across worker nodes.
  - Suffers from network latency penalties and IOPS bursting limits; must be provisioned with guaranteed provisioned IOPS.

---

### 3. Kubernetes Database Operators (The Modern Standard)
Never deploy raw database YAML manifests in production. Use battle-tested Kubernetes Database Operators:
- **CloudNativePG & Crunchy Data PGO (PostgreSQL)**:
  - Automated continuous WAL archiving to S3/MinIO/GCS.
  - Point-In-Time Recovery (PITR) to any second in history.
  - Automated failover within 5 seconds with zero human intervention.
  - Seamless rolling minor version upgrades (`17.0` to `17.1`).
- **Percona Kubernetes Operator for MySQL / MongoDB**:
  - Automated ProxySQL load balancing for read-write query splitting.
  - Automatic backup scheduling and physical restore verification.

---

### 4. Pod Anti-Affinity & Resource Protections
- **Pod Anti-Affinity**:
  - Always enforce `topologyKey: kubernetes.io/hostname` to ensure the Primary and Standby pods are NEVER scheduled on the same physical Kubernetes worker node.
- **cgroup Limits & OOM Killer**:
  - In Kubernetes, if a container exceeds `resources.limits.memory`, the Linux kernel OOM Killer immediately terminates the pod (`ExitCode 137`).
  - Always set DB buffer caches (`shared_buffers`, `innodb_buffer_pool_size`) to at most 60-70% of the container memory limit, leaving 30% headroom for OS threads, query work memory, and connection pools.

---

### 5. Docker Runtime Tuning for Relational Databases
When running databases in Docker containers (local development or standalone VMs):
- **Shared Memory Sizing (`/dev/shm`)**:
  - The default Docker shared memory size is only **64 MB**.
  - PostgreSQL parallel queries, hash joins, and IPC rely on shared memory. Running analytical queries in standard Docker causes immediate crashes with `could not resize shared memory segment`.
  - **Fix**: Always specify `--shm-size=1g` (or mount a `tmpfs` volume to `/dev/shm`).
- **Storage: Named Volumes vs Bind Mounts**:
  - **Named Volumes**: Docker manages files inside `/var/lib/docker/volumes/` with native Linux filesystem performance.
  - **Bind Mounts**: Mounting host directories is convenient for backups, but on macOS/Windows it incurs massive filesystem translation virtualization penalties.
- **Avoid Ephemeral Layer Writes**:
  - Never write database files to the container's overlay2 copy-on-write root filesystem; it causes severe I/O degradation and data loss when containers are recreated.""",
        },
        "id": {
            "title": "Database Kontainer: Kubernetes StatefulSet, Operator Database & Optimasi Runtime Docker",
            "summary": "Panduan produksi menjalankan database stateful di Kubernetes dan Docker: StatefulSet, StorageClass, operator CloudNativePG/CrunchyData, memori bersama IPC, dan proteksi cgroup.",
            "body": """### Menjalankan Database Stateful di Kontainer: Kubernetes & Docker

---

### 1. Kubernetes untuk Database: StatefulSet vs Deployment
Aplikasi web stateless cocok menggunakan `Deployment`, namun database relasional menuntut `StatefulSet`:
- **Identitas Jaringan yang Stabil**: Pod memiliki nama host yang konsisten (`postgres-cluster-0`, `postgres-cluster-1`). Node standby selalu tahu alamat primary tanpa bergantung pada IP dinamis.
- **Urutan Deployment & Scaling**: Pod `db-0` harus dipastikan aktif dan sehat sebelum `db-1` dibuat, mencegah konflik inisialisasi skema bersamaan.
- **Pengikatan Disk Persisten**: Setiap pod memiliki `volumeClaimTemplates` yang membuat PersistentVolume (PV) unik dan tetap terikat meskipun pod berpindah node fisik.

---

### 2. StorageClass Kubernetes & Performa I/O
Pemilihan media penyimpanan menentukan throughput transaksi (TPS) database:
- **Local NVMe SSD (Local Persistent Volume)**:
  - Menyediakan performa baca-tulis perangkat keras langsung tanpa latensi jaringan (sub-millisecond).
  - Membutuhkan replikasi level database (Patroni, InnoDB Cluster) untuk mencegah kehilangan data jika disk fisik server rusak.
- **Network Block Storage (Ceph, AWS EBS gp3, GCP pd-ssd)**:
  - Mempermudah pemindahan pod antar worker node jika satu server mati.
  - Menimbulkan penalti latensi jaringan; wajib dikonfigurasi dengan batas IOPS terjamin.

---

### 3. Operator Database Kubernetes (Standar Produksi)
Jangan pernah men-deploy database produksi menggunakan file YAML raw biasa. Gunakan Operator Database:
- **CloudNativePG & Crunchy Data PGO (PostgreSQL)**:
  - Pengarsipan otomatis file WAL ke object storage S3/GCS.
  - Point-In-Time Recovery (PITR) untuk mengembalikan database ke detik tertentu.
  - Failover otomatis dalam 5 detik saat primary padam tanpa campur tangan manusia.
  - Upgrade versi minor bergulir (rolling update) tanpa downtime.
- **Percona Kubernetes Operator untuk MySQL / MongoDB**:
  - Integrasi ProxySQL otomatis untuk memisahkan kueri baca dan tulis.
  - Penjadwalan backup rutin dan verifikasi restorasi otomatis.

---

### 4. Pod Anti-Affinity & Pencegahan OOM Killer
- **Pod Anti-Affinity**:
  - Wajib menyetel aturan `topologyKey: kubernetes.io/hostname` agar pod Primary dan Secondary TIDAK PERNAH dijadwalkan pada server fisik yang sama.
- **Batas Memori cgroup & OOM Killer**:
  - Jika kontainer melampaui `resources.limits.memory`, kernel Linux akan mengeksekusi OOM Killer yang mematikan database seketika (`ExitCode 137`).
  - Setel alokasi buffer cache (`shared_buffers`, `innodb_buffer_pool_size`) maksimal 60-70% dari batas memori kontainer, sisakan 30% untuk memori koneksi dan operasi sorting kueri.

---

### 5. Optimasi Runtime Docker untuk Database
Saat menjalankan database menggunakan Docker container:
- **Kapasitas Shared Memory (`/dev/shm`)**:
  - Default shared memory Docker hanya sebesar **64 MB**.
  - Operasi paralel kueri PostgreSQL dan hash join bergantung pada shared memory. Menjalankan kueri analitik berat pada Docker standar akan langsung memicu crash galat `could not resize shared memory segment`.
  - **Solusi**: Selalu jalankan kontainer dengan flag `--shm-size=1g` (atau pasang volume tmpfs di `/dev/shm`).
- **Penyimpanan: Named Volume vs Bind Mount**:
  - **Named Volume**: Dikelola langsung oleh Docker di `/var/lib/docker/volumes/` dengan performa I/O Linux native.
  - **Bind Mount**: Menghubungkan folder host langsung ke container; sangat lambat jika dijalankan pada host macOS/Windows karena lapisan virtualisasi filesystem.
- **Hindari Layer Ephemeral Kontainer**:
  - Jangan pernah menyimpan data database di layer root overlay2 kontainer karena kinerjanya sangat lambat dan data akan lenyap seketika saat kontainer di-recreate.""",
        },
    },
]


async def seed() -> None:
    print("Starting database seeding...")
    async with AsyncSessionLocal() as session:
        # 1. Seed Workspace & Default User if none
        res = await session.execute(select(Workspace).limit(1))
        ws = res.scalar_one_or_none()
        if not ws:
            ws = Workspace(
                id=uuid.uuid4(),
                name="Default Workspace",
            )
            session.add(ws)
            await session.commit()
            print(f"Created default workspace: {ws.id}")

        # 2. Seed Tool Categories & Tools
        category_cache: dict[str, uuid.UUID] = {}
        for tool_data in SEED_TOOLS:
            cat_slug = tool_data["category"]
            if cat_slug not in category_cache:
                cat_res = await session.execute(
                    select(ToolCategory).where(ToolCategory.slug == cat_slug)
                )
                cat = cat_res.scalar_one_or_none()
                if not cat:
                    cat = ToolCategory(
                        id=uuid.uuid4(),
                        slug=cat_slug,
                        name=tool_data["category_name"],
                    )
                    session.add(cat)
                    await session.flush()
                category_cache[cat_slug] = cat.id

            tool_res = await session.execute(
                select(ProfessionalTool).where(ProfessionalTool.slug == tool_data["slug"])
            )
            existing_tool = tool_res.scalar_one_or_none()
            if not existing_tool:
                new_tool = ProfessionalTool(
                    id=uuid.uuid4(),
                    slug=tool_data["slug"],
                    name=tool_data["name"],
                    vendor=tool_data["vendor"],
                    category_id=category_cache[cat_slug],
                    summary=tool_data["summary"],
                    official_url=tool_data["official_url"],
                    documentation_url=tool_data["documentation_url"],
                    license_model=tool_data["license_model"],
                    supported_platforms=["Linux", "macOS", "Windows"],
                    supported_engines=tool_data["supported_engines"],
                    last_verified_at=datetime.now(timezone.utc),
                )
                session.add(new_tool)
                print(f"Added tool: {tool_data['name']}")

        # 3. Seed Knowledge Categories & Articles
        k_cat_cache: dict[str, uuid.UUID] = {}
        for item in SEED_ARTICLES:
            cat_slug = item["category_slug"]
            if cat_slug not in k_cat_cache:
                cat_res = await session.execute(
                    select(KnowledgeCategory).where(KnowledgeCategory.slug == cat_slug)
                )
                k_cat = cat_res.scalar_one_or_none()
                if not k_cat:
                    k_cat = KnowledgeCategory(
                        id=uuid.uuid4(),
                        slug=cat_slug,
                        sort_order=len(k_cat_cache) + 1,
                    )
                    session.add(k_cat)
                    await session.flush()
                k_cat_cache[cat_slug] = k_cat.id

            # English Article
            en_res = await session.execute(
                select(KnowledgeArticle).where(
                    KnowledgeArticle.slug == item["slug"],
                    KnowledgeArticle.language == "en",
                )
            )
            if not en_res.scalar_one_or_none():
                session.add(
                    KnowledgeArticle(
                        id=uuid.uuid4(),
                        slug=item["slug"],
                        language="en",
                        title=item["en"]["title"],
                        summary=item["en"]["summary"],
                        body_markdown=item["en"]["body"],
                        status="published",
                        category_id=k_cat_cache[cat_slug],
                        engine=item["engine"],
                        version_scope=["Universal"],
                        references_json=[],
                        last_reviewed_at=datetime.now(timezone.utc),
                    )
                )
                print(f"Added EN article: {item['slug']}")

            # Indonesian Article
            id_res = await session.execute(
                select(KnowledgeArticle).where(
                    KnowledgeArticle.slug == item["slug"],
                    KnowledgeArticle.language == "id",
                )
            )
            if not id_res.scalar_one_or_none():
                session.add(
                    KnowledgeArticle(
                        id=uuid.uuid4(),
                        slug=item["slug"],
                        language="id",
                        title=item["id"]["title"],
                        summary=item["id"]["summary"],
                        body_markdown=item["id"]["body"],
                        status="published",
                        category_id=k_cat_cache[cat_slug],
                        engine=item["engine"],
                        version_scope=["Universal"],
                        references_json=[],
                        last_reviewed_at=datetime.now(timezone.utc),
                    )
                )
                print(f"Added ID article: {item['slug']}")

        await session.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
