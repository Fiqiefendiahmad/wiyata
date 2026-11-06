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
