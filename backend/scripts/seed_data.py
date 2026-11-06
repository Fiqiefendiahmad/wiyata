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
            "title": "SQLite Architecture: VDBE, Pager Subsystem, and Write-Ahead Logging (WAL) Internals",
            "summary": "Deep architectural dive into SQLite 3.45: parser to VDBE bytecode, B-Tree pager subsystem, rollback journal vs WAL mode, and shared memory (-shm) checkpointing.",
            "body": """## SQLite Internal Modular Architecture

SQLite is an in-process embedded database engine without external server processes. Execution flows through a layered pipeline from SQL text down to the operating system filesystem abstraction layer.

```
+---------------------------------------------------------------------------------+
|                           SQLITE ARCHITECTURAL STACK                            |
|                                                                                 |
|  +------------------------- CORE COMPILER PIPELINE --------------------------+  |
|  | Tokenizer & Lemon Parser ---> Code Generator (Bytecode Assembler)         |  |
|  +---------------------------------------------------------------------------+  |
|                                     |
|                                     v
|  +-------------------- VIRTUAL MACHINE ENGINE (VDBE) ------------------------+  |
|  | Executes compiled bytecode opcodes (e.g. OpenRead, SeekGE, Column, Result)|  |
|  +---------------------------------------------------------------------------+  |
|                                     |
|                                     v
|  +--------------------- B-TREE & PAGER SUBSYSTEM ----------------------------+  |
|  | B-Tree Layer: Manages table & index B-Trees (B-tree pages & cell payloads)|  |
|  | Pager Subsystem: Page caching, ACID transactions, lock state management   |  |
|  +---------------------------------------------------------------------------+  |
|                                     |
|                                     v
|  +---------------- OS VIRTUAL FILE SYSTEM (VFS) ABSTRACTION -----------------+  |
|  | POSIX / Windows OS system calls: open, read, write, fcntl / LockFileEx    |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
                                      | Storage
                                      v
           +------------------------------------------------------+
           | database.db  |  database.db-wal  |  database.db-shm  |
           +------------------------------------------------------+
```

---

## 1. The Pager Subsystem & Lock State Machine

In traditional Rollback Journal mode, transactions obtain escalating locks via OS file-locking interfaces:
1. `UNLOCKED`: No read or write locks held.
2. `SHARED`: Multiple readers can read simultaneously. No writer can modify data.
3. `RESERVED`: Single writer indicates intent to write in the future. Readers continue reading.
4. `PENDING`: Writer prepares to commit; no new `SHARED` locks are permitted. Existing readers finish.
5. `EXCLUSIVE`: Writer holds exclusive lock. Zero readers permitted. Pages written to disk.

---

## 2. Rollback Journal vs Write-Ahead Logging (WAL)

| Operational Dimension | Rollback Journal Mode (`PRAGMA journal_mode=DELETE`) | Write-Ahead Log Mode (`PRAGMA journal_mode=WAL`) |
| :--- | :--- | :--- |
| **Concurrency Model** | Single Writer **OR** Multiple Readers. Writer blocks readers. | Single Writer **AND** Concurrent Readers. Readers never block writers. |
| **Write Strategy** | Overwrites original pages in main database file after copying old pages to journal. | Appends new pages sequentially to separate `-wal` file. |
| **Commit Performance** | Two disk sync operations (`fsync` journal, then `fsync` db file). | Single sequential disk append; fsync deferred to checkpoint. |
| **File Footprint** | `db` + temporary `db-journal` file deleted after commit. | `db` + `db-wal` (log) + `db-shm` (shared memory index). |

---

## 3. The Shared Memory Index (`-shm`) & Checkpointing

In WAL mode, readers need to know whether the latest version of an 8KB page is in the main database file or inside the `-wal` file.
- SQLite uses a **Shared Memory file (`-shm`)** to index all frames currently stored in the WAL.
- Readers examine the `-shm` index with zero disk I/O to locate the latest frame matching their transaction snapshot.

### Checkpointing Algorithms
Checkpointing transfers modified frames from the `-wal` file back into the primary database file:
- `PASSIVE`: Checkpoints as many frames as possible without blocking readers or writers.
- `FULL`: Waits for active readers to finish their current snapshot, checkpoints all frames, and resets the WAL.
- `RESTART`: Similar to `FULL`, but blocks new readers until the WAL is completely reset to frame 1.
- `TRUNCATE`: Executes `RESTART` and truncates the `-wal` file on disk to zero bytes.

```sql
PRAGMA wal_checkpoint(PASSIVE);
```

---

## 4. Production Tuning Blueprint

```sql
-- Enforce Write-Ahead Logging
PRAGMA journal_mode = WAL;

-- Safe durability with highest write throughput
PRAGMA synchronous = NORMAL;

-- Allocate 64MB memory page cache (negative value = KiB)
PRAGMA cache_size = -64000;

-- Wait up to 5000ms if file is locked before throwing SQLITE_BUSY
PRAGMA busy_timeout = 5000;

-- Enable memory-mapped I/O up to 256MB
PRAGMA mmap_size = 268435456;
```"""
        },
        "id": {
            "title": "Arsitektur SQLite: VDBE, Subsistem Pager, dan Mekanisme Internal Write-Ahead Logging (WAL)",
            "summary": "Analisis mendalam SQLite 3.45: alur parser ke bytecode VDBE, subsistem B-Tree pager, rollback journal vs mode WAL, dan checkpointing memori terbagi (-shm).",
            "body": """## Arsitektur Modular Internal SQLite

SQLite adalah database embedded in-process tanpa proses server terpisah. Eksekusi kueri mengalir melalui pipa berlapis mulai dari parser SQL hingga lapisan abstraksi filesystem sistem operasi (OS VFS).

```
+---------------------------------------------------------------------------------+
|                           STACK ARSITEKTUR SQLITE                               |
|                                                                                 |
|  +------------------------- PIPELINE KOMPILER CORE --------------------------+  |
|  | Tokenizer & Lemon Parser ---> Code Generator (Bytecode Assembler)         |  |
|  +---------------------------------------------------------------------------+  |
|                                     |
|                                     v
|  +-------------------- VIRTUAL MACHINE ENGINE (VDBE) ------------------------+  |
|  | Mengeksekusi bytecode opcode (misal: OpenRead, SeekGE, Column, Result)    |  |
|  +---------------------------------------------------------------------------+  |
|                                     |
|                                     v
|  +--------------------- SUBSYSTEM B-TREE & PAGER ----------------------------+  |
|  | Lapisan B-Tree: Mengelola struktur B-tree tabel dan index                 |  |
|  | Subsistem Pager: Cache halaman, transaksi ACID, state lock file           |  |
|  +---------------------------------------------------------------------------+  |
|                                     |
|                                     v
|  +---------------- OS VIRTUAL FILE SYSTEM (VFS) ABSTRACTION -----------------+  |
|  | Panggilan kernel OS: open, read, write, fcntl / LockFileEx                |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
                                      | File Fisik
                                      v
           +------------------------------------------------------+
           | database.db  |  database.db-wal  |  database.db-shm  |
           +------------------------------------------------------+
```

---

## 1. Rollback Journal vs Write-Ahead Logging (WAL)

| Dimensi Operasional | Mode Rollback Journal (`DELETE`) | Mode Write-Ahead Log (`WAL`) |
| :--- | :--- | :--- |
| **Model Konkurensi** | Penulis memblokir pembaca. | Pembaca dan penulis berjalan bersamaan tanpa saling blokir. |
| **Strategi Tulis** | Menimpa halaman di file database utama setelah menyalin data lama ke journal. | Menulis halaman mutasi baru secara sekuensial ke file `-wal`. |
| **Performa Commit** | Memerlukan dua kali sinkronisasi disk (`fsync` file journal lalu file database). | Cukup satu kali append sekuensial; `fsync` utama ditunda hingga checkpoint. |
| **File di Disk** | `db` + file sementara `db-journal`. | `db` + `db-wal` (log) + `db-shm` (indeks memori terbagi). |

---

## 2. Indeks Shared Memory (`-shm`) & Checkpointing

Pada mode WAL, pembaca perlu mengetahui apakah versi terbaru suatu halaman berada di file database utama atau di file `-wal`:
- SQLite menggunakan file **Shared Memory (`-shm`)** untuk memetakan indeks frame WAL di RAM.
- Pembaca memeriksa file `-shm` secara langsung di memori tanpa I/O disk untuk menentukan snapshot transaksi yang tepat.

### Metode Checkpointing
Checkpointing memindahkan frame dari file `-wal` kembali ke file database utama:
- `PASSIVE`: Menulis sebanyak mungkin frame tanpa memblokir pembaca lain.
- `FULL`: Menunggu pembaca aktif selesai, lalu memindahkan seluruh frame.
- `RESTART`: Memblokir pembaca baru hingga pemindahan frame selesai total.
- `TRUNCATE`: Melakukan `RESTART` lalu memotong ukuran file `-wal` menjadi 0 byte.

```sql
PRAGMA wal_checkpoint(PASSIVE);
```

---

## 3. Konfigurasi Optimal Produksi

```sql
-- Mengaktifkan mode Write-Ahead Logging
PRAGMA journal_mode = WAL;

-- Keamanan data tinggi dengan performa tulis optimal
PRAGMA synchronous = NORMAL;

-- Alokasi memori cache 64MB (nilai negatif = KiB)
PRAGMA cache_size = -64000;

-- Waktu tunggu 5000ms jika database sedang terkunci
PRAGMA busy_timeout = 5000;

-- Mengaktifkan memory-mapped I/O hingga 256MB
PRAGMA mmap_size = 268435456;
```""",
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
            "title": "PostgreSQL 17 Architecture & Internals: Process Model, Shared Memory, MVCC, and Streaming Replication",
            "summary": "Deep architectural analysis of PostgreSQL 17 client backends, clock-sweep buffer eviction, tuple headers, HOT optimization, autovacuum cost delays, WAL checkpoints, and replication slots.",
            "body": """## PostgreSQL 17 Architectural Model

PostgreSQL employs a multi-process architecture rooted in a shared-memory IPC design. Each client session is handled by a dedicated backend process forked by the master coordinator process (`postmaster`).

```
+---------------------------------------------------------------------------------+
|                               POSTGRESQL INSTANCE                               |
|                                                                                 |
|  +--------------------------- SHARED MEMORY (RAM) ---------------------------+  |
|  |                                                                           |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  |  |   shared_buffers   |  |    wal_buffers     |  | Lock & Proc Array   |  |  |
|  |  |   (Clock Sweep)    |  |    (WAL Cache)     |  | (Shared & HW Locks) |  |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|         |                     |                      |                          |
|  +------+------+       +------+------+        +------+------+                   |
|  | Backend #1  |       | Backend #2  |        | Backend #N  |                   |
|  | (work_mem)  |       | (work_mem)  |        | (work_mem)  |                   |
|  +-------------+       +-------------+        +-------------+                   |
|         ^                     ^                      ^                          |
|  +----------------- BACKGROUND SYSTEM PROCESSES -----------------------------+  |
|  | checkpointer  |  bgwriter  |  walwriter  |  autovacuum  |  archiver       |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
                                      | Disk I/O
                                      v
                +-------------------------------------------+
                |  base/ (Tables/Indexes)  |  pg_wal/ (WAL) |
                +-------------------------------------------+
```

---

## 1. Process Topology & Execution Hierarchy

| Process Name | Process Role | Primary Operational Trigger |
| :--- | :--- | :--- |
| `postmaster` | Primary daemon listener; forks dedicated backend per TCP connection. | System startup / socket connection. |
| `backend` | Dedicated per-client execution thread executing SQL parser, planner, and executor. | Client query submission. |
| `checkpointer` | Flushes all dirty shared buffers to storage; updates control file with LSN checkpoint. | `checkpoint_timeout` or `max_wal_size`. |
| `bgwriter` | Proactively writes batches of dirty buffers to disk using a clean-ahead algorithm. | Continuous background loop (`bgwriter_delay`). |
| `walwriter` | Periodically writes and fsyncs WAL buffers to disk to minimize transaction commit delay. | Commit time or `wal_writer_delay`. |
| `autovacuum launcher` | Coordinates background workers to reclaim dead tuples and freeze transaction IDs. | Table dead tuple scale factor threshold. |

---

## 2. Memory Architecture & OS Interaction

### Memory Division
1. **Shared Memory Areas** (Allocated once at server startup):
   - `shared_buffers`: Central page cache. Recommended sizing is **25% of total system RAM** (up to 40% on dedicated database hosts). Page eviction uses a generalized clock-sweep algorithm tracking usage counters from 0 to 5.
   - `wal_buffers`: Memory staging buffer for unwritten WAL records (auto-tuned to 3% of `shared_buffers`, capped at 16MB).
2. **Local Backend Memory** (Allocated dynamically per query plan node):
   - `work_mem`: Memory used for individual sort operations (`ORDER BY`, `DISTINCT`) and hash tables (`Hash Join`, `Hash Aggregate`).
   - Sizing Formula to prevent Linux Out-Of-Memory (OOM) Killer crashes:

```
Safe work_mem = (Total Server RAM * 0.25) / (max_connections * Expected_Sort_Nodes_Per_Query)
```

> [!WARNING]
> A complex analytical query with 4 hash joins and 2 sorts can allocate `6 * work_mem` simultaneously within a single session. Setting `work_mem` too high with 200+ concurrent connections risks host kernel OOM termination of the primary `postmaster`.

---

## 3. Storage Subsystem & 8KB Page Layout

PostgreSQL manages data in fixed **8192-byte (8 KB)** pages on disk:

```
+-------------------------------------------------------------------+
| Page Header (24 bytes): pd_lsn, pd_checksum, pd_lower, pd_upper   |
+-------------------------------------------------------------------+
| Line Pointers (ItemIdData, 4 bytes each) ---> grows downward      |
| [ Item 1 ] [ Item 2 ] [ Item 3 ] ...                              |
+-------------------------------------------------------------------+
|                      FREE SPACE GAP                               |
+-------------------------------------------------------------------+
| <--- Tuples grow upward from bottom of page                       |
| [ Tuple 3 ] [ Tuple 2 ] [ Tuple 1 ]                               |
+-------------------------------------------------------------------+
| Special Space (Index-specific trailing metadata, e.g. B-Tree)    |
+-------------------------------------------------------------------+
```

### Tuple Header Structure (HeapTupleHeader)
Every row version contains a 23-byte header:
- `t_xmin`: 32-bit Transaction ID of the creating transaction.
- `t_xmax`: 32-bit Transaction ID of the deleting or updating transaction (0 if active).
- `t_cid`: Command identifier within the creating transaction.
- `t_infomask`: Bit flags defining commit/abort visibility (`HEAP_XMIN_COMMITTED`, `HEAP_XMIN_INVALID`, `HEAP_XMAX_COMMITTED`).
- `t_ctid`: Physical tuple ID `(block_number, offset)` pointing to itself, or to the newer tuple version if updated.

### HOT (Heap-Only Tuple) Optimization
When an `UPDATE` does not modify indexed columns and the updated tuple fits inside the existing 8KB heap page:
1. PostgreSQL writes the new tuple to the same page without adding new entries to secondary indexes.
2. The old tuple's `t_ctid` points directly to the new tuple within the page.
3. Index searches traverse the existing line pointer and follow the HOT chain in memory, eliminating secondary index write amplification.

---

## 4. MVCC, Visibility & Autovacuum

PostgreSQL uses multi-version concurrency control without in-place updates. An `UPDATE` performs a physical `INSERT` of a new row version while marking the older version dead.

### The Visibility Map (VM) and Free Space Map (FSM)
- **Visibility Map**: Tracks which 8KB pages contain only tuples visible to all current and future transactions. Allows the planner to execute **Index-Only Scans** without visiting heap pages.
- **Free Space Map**: Tracks available byte capacity across pages to accelerate target page selection during inserts.

### Autovacuum Cost-Based Throttling
To prevent vacuum operations from saturating storage I/O during business hours:

```ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_scale_factor = 0.05
autovacuum_freeze_max_age = 200000000
```

---

## 5. Write-Ahead Logging (WAL) & Checkpoints

All relational mutations are logged sequentially to 16MB WAL segment files in `pg_wal/` before corresponding dirty pages are written to disk.

### Checkpoint Mechanism
A checkpoint forces all dirty shared buffers up to a specific Log Sequence Number (LSN) to disk. Pacing parameters prevent I/O spikes:
- `checkpoint_completion_target = 0.9`: Spreads dirty page writes across 90% of `checkpoint_timeout`.
- `max_wal_size = 16GB`: Maximum WAL volume before an immediate checkpoint is triggered.

---

## 6. Physical Streaming Replication

Replication operates at the physical WAL byte level. The primary node's `walsender` transmits WAL records over TCP to the standby node's `walreceiver`, which replays them into local storage.

### Replication Slots
Physical replication slots (`pg_replication_slots`) guarantee that the primary node retains WAL segments on disk until the standby confirms reception, preventing standby desynchronization.

---

## 7. Production Diagnostic Telemetry

### Buffer Cache Hit Ratio Query
```sql
SELECT
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit)  as heap_hit,
  ROUND((sum(heap_blks_hit)::numeric / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100, 2) as hit_ratio
FROM pg_statio_user_tables;
```

### Table Bloat & Dead Tuple Monitoring
```sql
SELECT
  relname,
  n_live_tup,
  n_dead_tup,
  ROUND(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_tuple_pct,
  last_vacuum,
  last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```"""
        },
        "id": {
            "title": "Arsitektur & Internal PostgreSQL 17: Model Proses, Shared Memory, MVCC, dan Replikasi Streaming",
            "summary": "Analisis arsitektur mendalam PostgreSQL 17: proses backend, eviksi clock-sweep shared buffers, struktur header tuple, optimasi HOT, autovacuum cost delay, WAL checkpoint, dan replikasi streaming.",
            "body": """## Model Arsitektur PostgreSQL 17

PostgreSQL menerapkan arsitektur multi-proses berbasis shared-memory IPC. Setiap sesi client dikelola oleh proses backend mandiri yang di-fork oleh proses koordinator utama (`postmaster`).

```
+---------------------------------------------------------------------------------+
|                               INSTANSI POSTGRESQL                               |
|                                                                                 |
|  +--------------------------- SHARED MEMORY (RAM) ---------------------------+  |
|  |                                                                           |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  |  |   shared_buffers   |  |    wal_buffers     |  | Lock & Proc Array   |  |  |
|  |  |   (Clock Sweep)    |  |    (Cache WAL)     |  | (Shared & HW Locks) |  |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|         |                     |                      |                          |
|  +------+------+       +------+------+        +------+------+                   |
|  | Backend #1  |       | Backend #2  |        | Backend #N  |                   |
|  | (work_mem)  |       | (work_mem)  |        | (work_mem)  |                   |
|  +-------------+       +-------------+        +-------------+                   |
|         ^                     ^                      ^                          |
|  +----------------- PROSES LATAR BELAKANG SISTEM ----------------------------+  |
|  | checkpointer  |  bgwriter  |  walwriter  |  autovacuum  |  archiver       |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
                                      | Disk I/O
                                      v
                +-------------------------------------------+
                |  base/ (Tabel/Index)     |  pg_wal/ (WAL) |
                +-------------------------------------------+
```

---

## 1. Topologi Proses & Hirarki Eksekusi

| Nama Proses | Peran Operasional | Pemicu Eksekusi Utama |
| :--- | :--- | :--- |
| `postmaster` | Daemon listener utama; melakukan fork proses backend untuk tiap koneksi client. | Startup sistem / koneksi socket baru. |
| `backend` | Proses per-koneksi client yang mengeksekusi parser, optimizer/planner, dan executor. | Pengiriman kueri dari client. |
| `checkpointer` | Menulis seluruh shared buffer kotor ke disk dan memperbarui file kontrol dengan LSN. | Batas `checkpoint_timeout` atau `max_wal_size`. |
| `bgwriter` | Menulis sebagian buffer kotor ke disk secara asinkron agar buffer bersih selalu siap. | Loop latar belakang kontinu (`bgwriter_delay`). |
| `walwriter` | Melakukan flush periodik buffer WAL ke disk untuk mempercepat waktu commit. | Waktu commit atau `wal_writer_delay`. |
| `autovacuum launcher` | Mengatur worker untuk membersihkan dead tuple dan mencegah wraparound ID transaksi. | Ambang batas skala dead tuple tabel. |

---

## 2. Arsitektur Memori & Interaksi Kernel OS

### Pembagian Memori
1. **Shared Memory** (Dialokasikan saat database dijalankan):
   - `shared_buffers`: Cache data utama. Rekomendasi alokasi adalah **25% dari total RAM server** (maksimal 40% pada dedicated database host). Algoritma eviksi menggunakan *clock-sweep* dengan pencacah penggunaan 0 hingga 5.
   - `wal_buffers`: Buffer staging untuk data WAL yang belum ditulis ke disk (default 3% dari `shared_buffers`, maksimal 16MB).
2. **Local Backend Memory** (Dialokasikan per-node dalam query plan):
   - `work_mem`: Memori untuk operasi sorting (`ORDER BY`, `DISTINCT`) dan hash tables (`Hash Join`, `Hash Aggregate`).
   - Rumus keamanan agar terhindar dari Linux OOM Killer:

```
Batas Aman work_mem = (Total RAM Server * 0.25) / (max_connections * Rata2_Node_Sort_Per_Kueri)
```

> [!WARNING]
> Kueri analitik kompleks dengan 4 hash join dan 2 sort dapat mengalokasikan `6 * work_mem` secara bersamaan dalam 1 sesi. Jika `work_mem` disetel terlalu tinggi pada traffic 200+ koneksi, kernel host dapat mengeksekusi OOM killer yang mematikan `postmaster`.

---

## 3. Format Penyimpanan & Struktur Halaman 8KB

PostgreSQL mengelola data dalam halaman (page) berukuran **8192 byte (8 KB)**:

```
+-------------------------------------------------------------------+
| Page Header (24 byte): pd_lsn, pd_checksum, pd_lower, pd_upper    |
+-------------------------------------------------------------------+
| Line Pointers (ItemIdData, 4 byte per baris) ---> tumbuh ke bawah  |
| [ Item 1 ] [ Item 2 ] [ Item 3 ] ...                              |
+-------------------------------------------------------------------+
|                       RUANG KOSONG (FREE SPACE)                   |
+-------------------------------------------------------------------+
| <--- Baris Tuple tumbuh ke atas dari dasar halaman               |
| [ Tuple 3 ] [ Tuple 2 ] [ Tuple 1 ]                               |
+-------------------------------------------------------------------+
| Special Space (Metadata khusus index, misal B-Tree)               |
+-------------------------------------------------------------------+
```

### Struktur Header Tuple
Tiap versi baris memiliki header berukuran 23 byte:
- `t_xmin`: ID transaksi pembuat baris.
- `t_xmax`: ID transaksi yang menghapus atau menimpa baris (0 jika masih aktif).
- `t_cid`: Command ID dalam transaksi pembuat.
- `t_infomask`: Bit flag status commit (`HEAP_XMIN_COMMITTED`, `HEAP_XMIN_INVALID`, `HEAP_XMAX_COMMITTED`).
- `t_ctid`: Pointer fisik `(nomor_blok, offset)` yang mengarah ke versi baris baru jika baris telah diperbarui.

### Optimasi HOT (Heap-Only Tuple)
Jika perintah `UPDATE` tidak mengubah kolom yang memiliki index dan baris baru muat di halaman 8KB yang sama:
1. PostgreSQL menulis tuple baru di halaman yang sama tanpa memperbarui pointer pada index sekunder.
2. `t_ctid` tuple lama langsung mengarah ke tuple baru di halaman tersebut.
3. Kueri pencarian index langsung melintasi rantai HOT di memori tanpa memicu pembengkakan index.

---

## 4. MVCC, Dead Tuples & Autovacuum

PostgreSQL menggunakan prinsip non-overwriting. Setiap perintah `UPDATE` melakukan `INSERT` baris baru dan menandai baris lama sebagai dead tuple.

### Peran Visibility Map (VM) dan Free Space Map (FSM)
- **Visibility Map**: Mencatat halaman 8KB yang hanya berisi tuple yang telah terlihat oleh semua transaksi. Memungkinkan planner menjalankan **Index-Only Scan** tanpa membaca disk tabel.
- **Free Space Map**: Mencatat kapasitas ruang kosong pada tiap halaman agar operasi insert baru berjalan cepat.

### Konfigurasi Autovacuum Berbasis Beban
```ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_cost_delay = 2ms
autovacuum_vacuum_scale_factor = 0.05
autovacuum_freeze_max_age = 200000000
```

---

## 5. Write-Ahead Logging (WAL) & Checkpoint

Setiap mutasi dicatat berurutan pada file segmen WAL 16MB di `pg_wal/` sebelum halaman kotor ditulis ke disk.
- `checkpoint_completion_target = 0.9`: Menyebarkan penulisan halaman kotor sepanjang 90% durasi checkpoint timeout untuk mencegah lonjakan I/O disk.
- `max_wal_size = 16GB`: Volume WAL maksimal sebelum memicu checkpoint segera.

---

## 6. Kueri Diagnostik Telemetri Produksi

### Rasio Cache Hit Buffer
```sql
SELECT
  sum(heap_blks_read) as heap_read,
  sum(heap_blks_hit)  as heap_hit,
  ROUND((sum(heap_blks_hit)::numeric / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100, 2) as hit_ratio
FROM pg_statio_user_tables;
```

### Deteksi Dead Tuple & Bloat Tabel
```sql
SELECT
  relname,
  n_live_tup,
  n_dead_tup,
  ROUND(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_tuple_pct,
  last_vacuum,
  last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 10;
```""",
        },
    },
    {
        "slug": "mysql-11-innodb-replication-guide",
        "category_slug": "architecture",
        "engine": "MySQL / MariaDB",
        "en": {
            "title": "MySQL 8.4 / 11 InnoDB Architecture: Buffer Pool Internals, Redo/Undo Logs, and GTID Replication",
            "summary": "Architectural breakdown of the InnoDB storage engine: 3/8 LRU midpoint insertion, Change Buffer, Doublewrite Buffer, Redo log checkpoint age, and semi-synchronous GTID replication.",
            "body": """## MySQL / MariaDB InnoDB Architectural Model

InnoDB is an ACID-compliant transaction-safe storage engine built around a clustered index architecture (index-organized tables) and write-ahead logging.

```
+---------------------------------------------------------------------------------+
|                                INNODB STORAGE ENGINE                            |
|                                                                                 |
|  +--------------------------- INNODB BUFFER POOL ----------------------------+  |
|  |                                                                           |  |
|  |  +-------------------------- LRU LIST ---------------------------------+  |  |
|  |  | Young Sublist (Head 5/8 or ~63%) | Old Sublist (Tail 3/8 or ~37%)   |  |  |
|  |  | [ Hot Cached 16KB Pages ]        | [ Midpoint Insertion Window ]    |  |  |
|  |  +---------------------------------------------------------------------+  |  |
|  |                                                                           |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  |  |   Change Buffer    |  | Adaptive Hash (AHI)|  | Redo Log Buffer     |  |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  | Page Cleaner|       | Purge Thread|        | Master Thread|                   |
|  +-------------+       +-------------+        +-------------+                   |
+---------------------------------------------------------------------------------+
                                      | Flush Pipeline
                                      v
         +---------------------------------------------------------------+
         | Doublewrite Buffer (DWB) | ibdata1 / Undo Logs | .ibd Files   |
         +---------------------------------------------------------------+
```

---

## 1. Process & Threading Subsystem

| Thread Name | Responsibility | Critical Configuration |
| :--- | :--- | :--- |
| `master thread` | Coordinates dirty page flushing, background merges, and statistics updates. | Internal engine loop (1s / 10s intervals). |
| `page_cleaners` | Flushes dirty pages from buffer pool instances to disk asynchronously. | `innodb_page_cleaners` (matches pool instances). |
| `purge_threads` | Reclaims undo log slots and physically purges deleted records (`delete-marked` rows). | `innodb_purge_threads = 4`. |
| `io_read_threads` | Reads 16KB pages from `.ibd` datafiles into buffer pool on cache miss. | `innodb_read_io_threads = 8`. |
| `io_write_threads` | Writes pages to Doublewrite buffer and datafiles during flush operations. | `innodb_write_io_threads = 8`. |

---

## 2. Buffer Pool Internals: The 3/8 Midpoint Insertion Rule

InnoDB divides the LRU list into two sections:
- **Young Sublist** (Head, ~63%): Stores hot pages accessed repeatedly.
- **Old Sublist** (Tail, ~37%): Stores cold pages and recently read blocks.

### The Scan-Resistance Mechanism
When a query initiates a full table scan, it reads thousands of cold 16KB pages from disk. In naive LRU caches, this flushes all hot transactional data out of memory.

InnoDB prevents this via `innodb_old_blocks_time`:
1. Newly read pages enter at the **midpoint** (head of Old sublist), not at the very top of the LRU.
2. A page in the Old sublist is only promoted to the Young sublist if accessed again **after** `innodb_old_blocks_time` milliseconds (default: `1000ms`).
3. Single-pass table scans read pages within a few milliseconds, leaving them in the Old sublist where they age out and are evicted without polluting hot cache pages.

---

## 3. Storage Protection: Doublewrite Buffer & Change Buffer

### Doublewrite Buffer (DWB)
File systems typically write data in 4KB blocks, whereas InnoDB uses **16KB pages**. If the server loses power during a disk write, only part of the 16KB page may be written (a **torn page**). Redo logs cannot recover a torn page because redo entries apply delta changes rather than full images.

**Mitigation**:
- InnoDB first writes dirty pages sequentially into the contiguous Doublewrite Buffer on disk.
- Only after the DWB write is synced does InnoDB write the page to its final location in the `.ibd` file.
- On crash recovery, if a page in `.ibd` is corrupted or torn, InnoDB restores the pristine page image from the Doublewrite Buffer.

### Change Buffer
When an `INSERT` or `UPDATE` modifies a secondary index whose page is not in the Buffer Pool, reading that page from disk would incur expensive random I/O.
- InnoDB buffers the secondary index mutation in the **Change Buffer** in memory.
- When the page is eventually read into cache by another query, buffered changes are merged automatically.

---

## 4. Transaction Logging: Redo Log & Undo Tablespaces

### Redo Log Ring Buffer & Checkpoint Age
The redo log is organized as a fixed-size circular ring buffer.
- `Current LSN`: Byte offset of the latest logged transaction mutation.
- `Checkpoint LSN`: Byte offset up to which dirty pages have been flushed to disk.
- `Checkpoint Age = Current LSN - Checkpoint LSN`.
- If Checkpoint Age reaches 75% of total redo capacity, InnoDB triggers aggressive synchronous flushing, causing query latency spikes.

### Undo Tablespaces and Rollback Segments
- Every row contains hidden system columns: `DB_TRX_ID` (6 bytes, transaction ID) and `DB_ROLL_PTR` (7 bytes, pointer to undo log record).
- Undo records provide rollback capability and supply older row versions for concurrent read transactions (Consistent Non-Locking Reads).

---

## 5. GTID & High Availability Replication

Global Transaction Identifiers (`GTID`) assign a unique identity to every committed transaction across all replica nodes:
`GTID = source_id:transaction_id` (e.g., `3E11FA47-71CA-11E1-9E33-C80AA9429562:23`).

### Semi-Synchronous Replication (`AFTER_SYNC`)
- Master writes transaction to binary log and sends it to replicas.
- Master waits for at least one replica to write the transaction to its local **relay log** before committing to InnoDB locally.
- Guarantees zero data loss (RPO = 0) even if the master host suffers sudden hardware failure.

---

## 6. Production Tuning Blueprint & Diagnostics

```ini
# my.cnf
innodb_buffer_pool_size = 32G
innodb_buffer_pool_instances = 8
innodb_old_blocks_time = 1000
innodb_log_file_size = 4G
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT
innodb_doublewrite = 1
```

### Buffer Pool Hit Ratio Telemetry
```sql
SELECT
  variable_name,
  variable_value
FROM performance_schema.global_status
WHERE variable_name IN (
  'Innodb_buffer_pool_read_requests',
  'Innodb_buffer_pool_reads'
);
-- Hit Ratio = 1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)
```"""
        },
        "id": {
            "title": "Arsitektur InnoDB MySQL 8.4 / 11: Struktur Internal Buffer Pool, Redo/Undo Log, dan Replikasi GTID",
            "summary": "Bedah arsitektur mesin penyimpanan InnoDB: partisi LRU midpoint 3/8, Change Buffer, Doublewrite Buffer, checkpoint age redo log, dan replikasi semi-sinkron berbasis GTID.",
            "body": """## Model Arsitektur InnoDB MySQL / MariaDB

InnoDB adalah mesin penyimpanan transaksional ACID yang berbasis pada arsitektur clustered index (index-organized table) dan write-ahead logging.

```
+---------------------------------------------------------------------------------+
|                               MESIN STORAGE INNODB                              |
|                                                                                 |
|  +--------------------------- INNODB BUFFER POOL ----------------------------+  |
|  |                                                                           |  |
|  |  +-------------------------- LIST LRU ---------------------------------+  |  |
|  |  | Young Sublist (Head 5/8 or ~63%) | Old Sublist (Tail 3/8 or ~37%)   |  |  |
|  |  | [ Halaman Cache 16KB Aktif ]     | [ Window Midpoint Insertion ]    |  |  |
|  |  +---------------------------------------------------------------------+  |  |
|  |                                                                           |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  |  |   Change Buffer    |  | Adaptive Hash (AHI)|  | Redo Log Buffer     |  |  |
|  |  +--------------------+  +--------------------+  +---------------------+  |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  | Page Cleaner|       | Purge Thread|        | Master Thread|                   |
|  +-------------+       +-------------+        +-------------+                   |
+---------------------------------------------------------------------------------+
                                      | Flush Pipeline
                                      v
         +---------------------------------------------------------------+
         | Doublewrite Buffer (DWB) | ibdata1 / Undo Logs | File .ibd    |
         +---------------------------------------------------------------+
```

---

## 1. Subsistem Thread & Proses

| Nama Thread | Tanggung Jawab Operasional | Parameter Konfigurasi |
| :--- | :--- | :--- |
| `master thread` | Mengatur penulisan halaman kotor, merge change buffer, dan sinkronisasi metadata. | Loop interval internal (1 detik / 10 detik). |
| `page_cleaners` | Melakukan flush halaman kotor dari tiap instansi buffer pool ke disk secara asinkron. | `innodb_page_cleaners`. |
| `purge_threads` | Membersihkan slot undo log dan menghapus baris yang ditandai terhapus (`delete-marked`). | `innodb_purge_threads = 4`. |
| `io_read_threads` | Membaca halaman 16KB dari file `.ibd` ke memori saat terjadi cache miss. | `innodb_read_io_threads = 8`. |
| `io_write_threads` | Menulis halaman ke Doublewrite Buffer dan file datafile secara berkelanjutan. | `innodb_write_io_threads = 8`. |

---

## 2. Internal Buffer Pool: Aturan Midpoint Insertion 3/8

InnoDB membagi daftar LRU menjadi dua bagian:
- **Young Sublist** (Head, ~63%): Menyimpan halaman aktif yang sering diakses.
- **Old Sublist** (Tail, ~37%): Menyimpan halaman baru dibaca atau halaman dingin.

### Mekanisme Pencegahan Polusi Cache (Scan-Resistance)
Saat kueri melakukan scan tabel penuh, ribuan halaman dingin dibaca ke memori. Pada algoritma LRU biasa, hal ini akan membuang semua data transaksi penting dari RAM.

InnoDB mencegah masalah ini menggunakan `innodb_old_blocks_time`:
1. Halaman baru yang dibaca dari disk masuk di **titik tengah (midpoint)**, yaitu di posisi teratas Old Sublist.
2. Halaman di Old Sublist hanya dipromosikan ke Young Sublist jika diakses kembali **setelah** melewati durasi `innodb_old_blocks_time` milidetik (default: `1000ms`).
3. Kueri scan membaca halaman dalam hitungan milidetik saja, sehingga halaman tersebut tertahan di Old sublist lalu terbuang tanpa merusak cache transaksi utama.

---

## 3. Doublewrite Buffer (DWB) & Change Buffer

### Doublewrite Buffer (DWB)
Sistem operasi menulis data ke disk dalam blok 4KB, sedangkan InnoDB menggunakan **halaman 16KB**. Jika server mati mendadak saat menulis 16KB, hanya sebagian blok yang tersimpan di disk (kondisi **torn page**). File redo log tidak dapat memulihkan torn page karena redo log mencatat perubahan delta, bukan salinan utuh halaman data.

**Solusi**:
- InnoDB menulis halaman kotor terlebih dahulu secara sekuensial ke Doublewrite Buffer di disk.
- Setelah DWB tersimpan aman, barulah halaman ditulis ke file `.ibd` aslinya.
- Jika terjadi crash dan file `.ibd` mengalami kerusakan torn page, InnoDB memulihkan halaman dari Doublewrite Buffer.

---

## 4. Redo Log & Undo Tablespace

### Redo Log Ring Buffer & Checkpoint Age
- Redo log beroperasi sebagai circular ring buffer berukuran tetap.
- `Checkpoint Age = Current LSN - Checkpoint LSN`.
- Jika Checkpoint Age mendekati 75% dari kapasitas total file redo, InnoDB dipaksa melakukan sinkronisasi I/O agresif yang dapat membekukan latensi kueri.

---

## 5. Replikasi GTID Semi-Sinkron (`AFTER_SYNC`)

Pada mode semi-sinkron `AFTER_SYNC`:
1. Master menulis transaksi ke binary log dan mengirimkannya ke replica.
2. Master menunggu setidaknya satu replica mencatat transaksi ke **relay log** sebelum mengizinkan commit lokal di engine InnoDB.
3. Menjamin zero data loss (RPO = 0) meskipun server master mendadak terbakar atau mati total.

---

## 6. Kueri Telemetri & Diagnostik

```sql
SELECT
  variable_name,
  variable_value
FROM performance_schema.global_status
WHERE variable_name IN (
  'Innodb_buffer_pool_read_requests',
  'Innodb_buffer_pool_reads'
);
-- Hit Ratio = 1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)
```""",
        },
    },
    {
        "slug": "oracle-23ai-enterprise-architecture",
        "category_slug": "architecture",
        "engine": "Oracle",
        "en": {
            "title": "Oracle Database 23ai Architecture: Multitenant CDB/PDB, SGA/PGA Hierarchy, and Consistent Read Mechanics",
            "summary": "Comprehensive architecture of Oracle 23ai: Container & Pluggable databases, SGA components (Shared Pool, Buffer Cache), PGA work areas, SCN mechanics, and AWR wait event diagnostics.",
            "body": """## Oracle Database 23ai Multitenant Architecture

Oracle 23ai enforces a container architecture where multiple isolated Pluggable Databases (PDBs) share a single physical instance (processes and shared memory) coordinated by the Root Container (`CDB$ROOT`).

```
+---------------------------------------------------------------------------------+
|                         ORACLE INSTANCE (SGA + PROCESSES)                       |
|                                                                                 |
|  +------------------------- SYSTEM GLOBAL AREA (SGA) ------------------------+  |
|  | Database Buffer Cache | Shared Pool (Library Cache + Data Dict)           |  |
|  | Redo Log Buffer       | Large Pool (RMAN / Parallel Query)                |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  |    DBWn     |       |    LGWR     |        |    CKPT     |                   |
|  +-------------+       +-------------+        +-------------+                   |
+---------------------------------------------------------------------------------+
                                      | Storage Layers
                                      v
+---------------------------------------------------------------------------------+
|                               CONTAINER DATABASE (CDB)                          |
|                                                                                 |
|  +------------------+     +------------------+     +-------------------------+  |
|  |     CDB$ROOT     |     |     PDB$SEED     |     | PDB1 (ERP) / PDB2 (CRM) |  |
|  | System Metadata  |     | Golden Template  |     | User Tablespaces & Data |  |
|  +------------------+     +------------------+     +-------------------------+  |
+---------------------------------------------------------------------------------+
```

---

## 1. Multitenant Hierarchy: CDB vs PDB

| Container Entity | Purpose | Storage Boundary |
| :--- | :--- | :--- |
| `CDB$ROOT` | Manages instance metadata, common background processes, common users (`c##admin`), and shared control files. | System & Sysaux tablespaces for CDB. |
| `PDB$SEED` | Read-only seed template used to instantiate new pluggable databases in seconds. | Dedicated system datafiles. |
| `PDB` | Fully functional, self-contained database holding user application tablespaces, schemas, and local users. | Isolated user datafiles (`app_data01.dbf`). |

---

## 2. System Global Area (SGA) Structure

1. **Database Buffer Cache**: Caches blocks read from datafiles.
   - **Default Pool**: Standard block caching using modified LRU.
   - **KEEP Pool**: Dedicated memory for small, frequently queried reference tables to prevent them from being aged out.
   - **RECYCLE Pool**: Dedicated pool for large batch tables to prevent sequential scans from displacing OLTP cache blocks.
2. **Shared Pool**:
   - **Library Cache**: Stores parsed SQL statements, execution plans, and PL/SQL packages.
   - **Data Dictionary Cache**: Stores metadata about tables, columns, constraints, and security privileges.
3. **Redo Log Buffer**: Circular memory buffer recording row changes. Flushed to disk immediately by `LGWR` on transaction commit.
4. **Large Pool**: Sized to isolate large memory allocations such as RMAN backup buffers, parallel query execution message buffers, and shared server sessions.

---

## 3. Program Global Area (PGA) & Memory Sizing

The PGA is non-shared memory allocated to dedicated server processes servicing client connections.
- **SQL Work Areas**: `Sort Area` (ORDER BY), `Hash Area` (hash joins), and `Bitmap Merge Area`.
- Automatic memory control is governed by `PGA_AGGREGATE_TARGET` and enforced strictly by `PGA_AGGREGATE_LIMIT` to prevent host memory starvation.

---

## 4. Core Background Processes & SCN Mechanics

- **`DBWn` (Database Writer)**: Writes dirty blocks from the buffer cache to datafiles using asynchronous batched I/O.
- **`LGWR` (Log Writer)**: Flushes the Redo Log Buffer to active online redo log files on transaction commit.
- **`CKPT` (Checkpoint)**: Signals `DBWn` to write dirty blocks and updates datafile headers and control files with the current SCN.
- **`SMON` (System Monitor)**: Performs instance recovery on startup (roll-forward from redo logs, roll-back from undo).
- **`PMON` (Process Monitor)**: Cleans up failed client connections and releases locks.

### System Change Number (SCN)
The SCN is a monotonically increasing 64-bit integer that serves as Oracle's logical commit clock, establishing absolute chronological order for all transactions.

---

## 5. Consistent Read (CR) Blocks & Undo Internals

Oracle enforces read consistency without reader locks:
1. When a query begins at SCN `10500`, it must observe data strictly as it existed at SCN `10500`.
2. If another transaction modifies and commits a row at SCN `10520`, the physical block in the buffer cache now contains the newer version.
3. When the reader arrives at that block, it detects an SCN greater than `10500`.
4. The server process fetches historical before-images from the **Undo Tablespace** and reconstructs a temporary **Consistent Read (CR)** clone of the block in RAM.
5. If the required undo segments have been overwritten due to insufficient undo retention, Oracle terminates the query with:
   `ORA-01555: snapshot too old: rollback segment too small`.

---

## 6. Production Diagnostic Scripts

### Buffer Cache Advisory Analysis
```sql
SELECT
  size_for_estimate,
  size_factor,
  estd_physical_read_factor,
  estd_physical_reads
FROM v$db_cache_advice
WHERE name = 'DEFAULT';
```

### Active Session Lock & Blocking Telemetry
```sql
SELECT
  s1.username || '@' || s1.machine AS blocker,
  s1.sid AS blocker_sid,
  s2.username || '@' || s2.machine AS waiter,
  s2.sid AS waiter_sid,
  s2.seconds_in_wait
FROM v$lock l1
JOIN v$session s1 ON s1.sid = l1.sid
JOIN v$lock l2   ON l2.id1 = l1.id1 AND l2.id2 = l1.id2
JOIN v$session s2 ON s2.sid = l2.sid
WHERE l1.block = 1 AND l2.request > 0;
```"""
        },
        "id": {
            "title": "Arsitektur Oracle Database 23ai: Multitenant CDB/PDB, Hirarki SGA/PGA, dan Mekanisme Consistent Read",
            "summary": "Arsitektur mendalam Oracle 23ai: database Container dan Pluggable, komponen SGA (Shared Pool, Buffer Cache), area kerja PGA, mekanisme SCN, dan diagnostik wait event AWR.",
            "body": """## Model Arsitektur Multitenant Oracle 23ai

Oracle 23ai mewajibkan arsitektur container di mana beberapa Pluggable Database (PDB) terisolasi berbagi satu instansi fisik (proses dan shared memory) yang dikoordinasikan oleh Root Container (`CDB$ROOT`).

```
+---------------------------------------------------------------------------------+
|                         INSTANSI ORACLE (SGA + PROSES)                          |
|                                                                                 |
|  +------------------------- SYSTEM GLOBAL AREA (SGA) ------------------------+  |
|  | Database Buffer Cache | Shared Pool (Library Cache + Data Dict)           |  |
|  | Redo Log Buffer       | Large Pool (RMAN / Kueri Paralel)                 |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  |    DBWn     |       |    LGWR     |        |    CKPT     |                   |
|  +-------------+       +-------------+        +-------------+                   |
+---------------------------------------------------------------------------------+
                                      | Lapisan Penyimpanan
                                      v
+---------------------------------------------------------------------------------+
|                               CONTAINER DATABASE (CDB)                          |
|                                                                                 |
|  +------------------+     +------------------+     +-------------------------+  |
|  |     CDB$ROOT     |     |     PDB$SEED     |     | PDB1 (ERP) / PDB2 (CRM) |  |
|  | Metadata Sistem  |     | Template Master  |     | Tablespace Data Client  |  |
|  +------------------+     +------------------+     +-------------------------+  |
+---------------------------------------------------------------------------------+
```

---

## 1. Hirarki Multitenant: CDB vs PDB

| Entitas Container | Fungsi Operasional | Batas Datafile Fisik |
| :--- | :--- | :--- |
| `CDB$ROOT` | Mengelola metadata instansi, proses latar belakang bersama, user global (`c##admin`), dan file kontrol. | Tablespace System & Sysaux milik CDB. |
| `PDB$SEED` | Template read-only untuk membuat database PDB baru dalam hitungan detik. | Datafile sistem tersendiri. |
| `PDB` | Database mandiri untuk aplikasi, memiliki tablespace data dan skema lokal sendiri. | Datafile aplikasi terisolasi (`app_data01.dbf`). |

---

## 2. Struktur System Global Area (SGA)

1. **Database Buffer Cache**: Menyimpan blok data yang dibaca dari disk.
   - **Default Pool**: Cache blok standar berbasis modifikasi LRU.
   - **KEEP Pool**: Memori khusus untuk tabel referensi kecil agar tidak pernah terdepak dari RAM.
   - **RECYCLE Pool**: Memori khusus kueri batch besar agar scan tidak merusak cache transaksi OLTP.
2. **Shared Pool**:
   - **Library Cache**: Menyimpan kueri SQL terurai (parsed SQL), execution plan, dan paket PL/SQL.
   - **Data Dictionary Cache**: Menyimpan metadata definisi tabel, kolom, constraint, dan hak akses.
3. **Redo Log Buffer**: Buffer sirkular untuk mencatat perubahan baris data, ditulis ke disk oleh `LGWR` saat commit.
4. **Large Pool**: Mengisolasi alokasi memori masif seperti buffer backup RMAN dan shared server.

---

## 3. Program Global Area (PGA)

PGA adalah memori privat yang dialokasikan khusus untuk tiap proses koneksi client.
- **SQL Work Areas**: Digunakan untuk sorting (`Sort Area`), penggabungan data (`Hash Area`), dan operasi bitmap.
- Dikelola otomatis melalui parameter `PGA_AGGREGATE_TARGET` dan dibatasi ketat oleh `PGA_AGGREGATE_LIMIT`.

---

## 4. Mekanisme Consistent Read (CR) & Undo

Oracle menjamin pembacaan data konsisten tanpa mengunci baris data (readers never block writers):
1. Ketika kueri mulai berjalan pada SCN `10500`, kueri wajib membaca data persis pada kondisi SCN `10500`.
2. Jika transaksi lain mengubah dan melakukan commit baris data pada SCN `10520`, blok fisik di buffer cache telah berubah ke versi baru.
3. Saat kueri membaca blok tersebut, sistem mendeteksi bahwa SCN blok lebih besar dari `10500`.
4. Proses server secara otomatis membaca catatan before-image dari **Undo Tablespace** dan merekonstruksi klon blok sementara (**Consistent Read / CR Block**) di memori RAM.
5. Jika segmen undo telah tertimpa data lain karena kueri berjalan terlalu lama, Oracle melempar galat:
   `ORA-01555: snapshot too old: rollback segment too small`.

---

## 5. Skrip Diagnostik Produksi

### Deteksi Sesi yang Terblokir (Lock Contention)
```sql
SELECT
  s1.username || '@' || s1.machine AS blocker,
  s1.sid AS blocker_sid,
  s2.username || '@' || s2.machine AS waiter,
  s2.sid AS waiter_sid,
  s2.seconds_in_wait
FROM v$lock l1
JOIN v$session s1 ON s1.sid = l1.sid
JOIN v$lock l2   ON l2.id1 = l1.id1 AND l2.id2 = l1.id2
JOIN v$session s2 ON s2.sid = l2.sid
WHERE l1.block = 1 AND l2.request > 0;
```""",
        },
    },
    {
        "slug": "sql-server-2022-internals-query-store",
        "category_slug": "architecture",
        "engine": "SQL Server",
        "en": {
            "title": "SQL Server 2022 Architecture: SQLOS Scheduling, 8KB Page Internals, and Query Store",
            "summary": "Technical guide to SQL Server 2022 internals: cooperative SQLOS scheduling, extents, GAM/SGAM/PFS maps, VLF transaction log lifecycle, and Query Store plan forcing.",
            "body": """## SQL Server 2022 Operating System (SQLOS) Engine

Microsoft SQL Server runs on top of **SQLOS**, a specialized user-mode abstraction layer that manages thread scheduling, memory allocation, network I/O, and synchronization latches independently of the underlying Windows/Linux kernel.

```
+---------------------------------------------------------------------------------+
|                       SQL SERVER OPERATING SYSTEM (SQLOS)                       |
|                                                                                 |
|  +---------------- NUMA NODE 0 -----------------+  +--- NUMA NODE 1 --------+   |
|  |  +-----------------+   +------------------+  |  | Schedulers 2 & 3       |   |
|  |  | Scheduler 0     |   | Scheduler 1      |  |  | (Cooperative Yield)    |   |
|  |  | Worker Threads  |   | Worker Threads   |  |  +------------------------+   |
|  |  +-----------------+   +------------------+  |                               |
|  +----------------------------------------------+                               |
|                                                                                 |
|  +--------------------------- BUFFER POOL (RAM) -----------------------------+  |
|  | 8KB Data Pages | 8KB Index Pages | Free Page List | Dirty Page List       |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
                                      | Storage Engine
                                      v
         +---------------------------------------------------------------+
         | Data Files (.mdf/.ndf) Extents (64KB) | Log File (.ldf) VLFs  |
         +---------------------------------------------------------------+
```

---

## 1. SQLOS Cooperative Non-Preemptive Scheduling

Unlike standard OS preemptive schedulers, SQLOS uses **cooperative scheduling**:
- **Schedulers**: SQL Server instantiates exactly one scheduler per logical CPU core.
- **Worker Threads**: Assigned to schedulers; each thread processes tasks without being forcibly interrupted by the OS kernel.
- **Yielding**: A worker thread voluntarily yields the CPU (`SOS_SCHEDULER_YIELD`) during I/O waits, lock waits, or after executing a quantum of bytecode.
- **Thread States**:
  - `RUNNING`: Actively executing CPU instructions on the scheduler.
  - `SUSPENDED`: Waiting on a resource (lock, disk page read, network socket).
  - `RUNNABLE`: Resource acquired; sitting in queue waiting for CPU access.

---

## 2. Storage Engine: 8KB Pages & Extents

Data files (`.mdf` and `.ndf`) are partitioned into contiguous **8192-byte (8 KB)** pages:
- **Extents**: 8 contiguous 8KB pages form a **64 KB Extent**.
  - **Uniform Extents**: Dedicated exclusively to a single database object.
  - **Mixed Extents**: Shared by up to 8 small objects (SQL Server 2016+ defaults to uniform extents via trace flag 1118 behavior).

### Page Allocation Space Tracking Maps
- **GAM (Global Allocation Map)**: Tracks which extents are allocated (bit 1 = free, bit 0 = allocated).
- **SGAM (Shared Global Allocation Map)**: Tracks mixed extents with free pages.
- **PFS (Page Free Space)**: Byte flags recording allocation status and approximate free space (0%, 1-50%, 51-80%, 81-99%, 100%) for each page.

---

## 3. Transaction Log (.ldf) & Virtual Log File (VLF) Lifecycle

The transaction log writes records sequentially using Write-Ahead Logging (WAL). Internally, the log is partitioned into **Virtual Log Files (VLFs)**.

### VLF Fragmentation Hazards
- If autogrowth is configured with tiny increments (e.g., 10MB), SQL Server creates thousands of microscopic VLFs.
- **Impact**: Excessive VLFs (>1,000) severely degrade database startup time, disaster recovery roll-forward, and replication throughput.
- **Remediation**: Pre-size the log file in large chunks (e.g., 8GB or 16GB) to produce clean, well-proportioned VLFs.

---

## 4. Query Store: Plan Regression Protection

Query Store acts as a flight data recorder inside the database engine, capturing query execution plans, runtime performance metrics, and wait statistics.

### The Three Sub-Stores
1. **Plan Store**: Persists compiled execution plan XML graphs.
2. **Runtime Stats Store**: Records execution durations, CPU consumption, logical reads, and memory grants.
3. **Wait Stats Store**: Records wait types categorized per query plan.

### Plan Forcing Procedure
When parameter sniffing causes execution plan regression:
```sql
-- Force proven execution plan ID 42 for Query ID 10
EXEC sp_query_store_force_plan @query_id = 10, @plan_id = 42;
```

---

## 5. Production Diagnostic DMV Telemetry

### Scheduler Health & Runnable Queue
```sql
SELECT
  scheduler_id,
  cpu_id,
  status,
  is_online,
  current_tasks_count,
  runnable_tasks_count,
  work_queue_count,
  pending_disk_io_count
FROM sys.dm_os_schedulers
WHERE scheduler_id < 255;
```

### Top Wait Types by Cumulative Duration
```sql
SELECT TOP 10
  wait_type,
  waiting_tasks_count,
  wait_time_ms,
  max_wait_time_ms,
  signal_wait_time_ms
FROM sys.dm_os_wait_stats
WHERE wait_type NOT LIKE '%SLEEP%'
ORDER BY wait_time_ms DESC;
```"""
        },
        "id": {
            "title": "Arsitektur SQL Server 2022: Penjadwalan SQLOS, Struktur Halaman 8KB, dan Query Store",
            "summary": "Panduan teknis internal SQL Server 2022: penjadwalan kooperatif SQLOS, extents, alokasi halaman GAM/SGAM/PFS, siklus log transaksi VLF, dan pemaksaan rencana Query Store.",
            "body": """## Mesin SQL Server Operating System (SQLOS)

Microsoft SQL Server berjalan di atas **SQLOS**, lapisan abstraksi user-mode khusus yang mengelola penjadwalan thread, alokasi memori, I/O jaringan, dan sinkronisasi latch secara mandiri dari kernel Windows/Linux.

```
+---------------------------------------------------------------------------------+
|                       SQL SERVER OPERATING SYSTEM (SQLOS)                       |
|                                                                                 |
|  +---------------- NUMA NODE 0 -----------------+  +--- NUMA NODE 1 --------+   |
|  |  +-----------------+   +------------------+  |  | Schedulers 2 & 3       |   |
|  |  | Scheduler 0     |   | Scheduler 1      |  |  | (Cooperative Yield)    |   |
|  |  | Worker Threads  |   | Worker Threads   |  |  +------------------------+   |
|  |  +-----------------+   +------------------+  |                               |
|  +----------------------------------------------+                               |
|                                                                                 |
|  +--------------------------- BUFFER POOL (RAM) -----------------------------+  |
|  | Halaman Data 8KB | Halaman Index 8KB | Free Page List | Dirty Page List   |  |
|  +---------------------------------------------------------------------------+  |
+---------------------------------------------------------------------------------+
                                      | Mesin Penyimpanan
                                      v
         +---------------------------------------------------------------+
         | Data Files (.mdf/.ndf) Extents (64KB) | Log File (.ldf) VLFs  |
         +---------------------------------------------------------------+
```

---

## 1. Penjadwalan Kooperatif Non-Preemptive SQLOS

Berbeda dari scheduler sistem operasi umum, SQLOS menggunakan **penjadwalan kooperatif**:
- **Schedulers**: Satu scheduler dibuat untuk setiap inti CPU logis.
- **Worker Threads**: Thread mengeksekusi tugas tanpa diinterupsi paksa oleh kernel OS.
- **Yielding**: Worker thread secara sukarela menyerahkan giliran CPU (`SOS_SCHEDULER_YIELD`) saat menunggu I/O atau lock.

---

## 2. Struktur Penyimpanan: Halaman 8KB & Extents

File data (`.mdf` dan `.ndf`) dibagi menjadi halaman-halaman berukuran **8192 byte (8 KB)**:
- **Extents**: 8 halaman 8KB berurutan membentuk satu **64 KB Extent**.
- **Peta Alokasi Ruang**:
  - `GAM (Global Allocation Map)`: Mencatat alokasi extent secara keseluruhan.
  - `SGAM (Shared Global Allocation Map)`: Melacak mixed extent yang masih memiliki halaman kosong.
  - `PFS (Page Free Space)`: Menandai perkiraan sisa ruang kosong pada tiap halaman 8KB.

---

## 3. Log Transaksi (.ldf) & Virtual Log Files (VLF)

Log transaksi ditulis secara sekuensial dan dibagi menjadi beberapa **Virtual Log Files (VLF)**.
- Pertumbuhan otomatis (autogrowth) berukuran terlalu kecil (misal 10MB) akan menciptakan ribuan VLF mikro (**VLF Fragmentation**).
- Dampak: Memperlambat startup database, memperlambat pemulihan bencana (disaster recovery), dan membebani throughput replikasi.
- Solusi: Sediakan ukuran log file langsung dalam ukuran besar (misal 8GB atau 16GB).

---

## 4. Query Store & Pemaksaan Rencana Eksekusi (Plan Forcing)

Query Store merekam riwayat eksekusi kueri, grafik execution plan, dan metrik runtime.
Saat terjadi regresi performa akibat *parameter sniffing*:

```sql
-- Paksa optimizer menggunakan Plan ID 42 untuk Query ID 10
EXEC sp_query_store_force_plan @query_id = 10, @plan_id = 42;
```

---

## 5. Skrip Telemetri DMV Produksi

```sql
SELECT
  scheduler_id,
  cpu_id,
  status,
  is_online,
  current_tasks_count,
  runnable_tasks_count,
  work_queue_count,
  pending_disk_io_count
FROM sys.dm_os_schedulers
WHERE scheduler_id < 255;
```""",
        },
    },
    {
        "slug": "ibm-db2-11-5-hadr-tablespaces-wlm",
        "category_slug": "architecture",
        "engine": "IBM Db2",
        "en": {
            "title": "IBM Db2 11.5 Architecture: Engine Dispatchable Units, Tablespace Management, and HADR Replication",
            "summary": "In-depth architecture of IBM Db2 11.5: EDUs threading model, bufferpools, automatic storage tablespaces, Currently Committed semantics, and HADR takeover states.",
            "body": """## IBM Db2 11.5 Process & Engine Dispatchable Units (EDUs)

IBM Db2 operates on a multi-threaded process model centered on the primary database engine process (`db2sysc`). Inside `db2sysc`, concurrency is handled by specialized lightweight threads termed **Engine Dispatchable Units (EDUs)**.

```
+---------------------------------------------------------------------------------+
|                       DB2 ENGINE PROCESS INSTANCE (db2sysc)                     |
|                                                                                 |
|  +--------------------------- DATABASE BUFFERPOOLS --------------------------+  |
|  | IBMDEFAULTBP (4KB/8KB) | Dedicated Bufferpools (16KB/32KB) | Package Cache|  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  |  db2agent   |       |  db2pfchr   |        |  db2pclnr   |                   |
|  | (Coordinator|       | (Prefetcher)|        | (Page Clean)|                   |
|  +-------------+       +-------------+        +-------------+                   |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  |  db2loggw   |       |  db2hadr    |        |  db2dlock   |                   |
|  | (Log Writer)|       | (Repl Engine|        | (Deadlock)  |                   |
|  +-------------+       +-------------+        +-------------+                   |
+---------------------------------------------------------------------------------+
                                      | Storage Subsystems
                                      v
         +---------------------------------------------------------------+
         | Automatic Storage Tablespaces (.DAT) | Active Transaction Logs|
         +---------------------------------------------------------------+
```

---

## 1. Engine Dispatchable Units (EDUs) Topology

| EDU Thread | Operational Role | Sizing / Parameter Influence |
| :--- | :--- | :--- |
| `db2agent` | Coordinating agent dedicated to processing requests for an individual client connection. | Governed by `max_coordagents`. |
| `db2pfchr` | Asynchronous prefetchers reading extents ahead of execution for sequential index/table scans. | Governed by `num_ioservers`. |
| `db2pclnr` | Asynchronous page cleaners writing dirty bufferpool pages to disk before buffers run out. | Governed by `num_iocleaners` and `chngpgs_thresh`. |
| `db2loggw` | Log writer flushing active log buffers to disk on transaction commit. | Flushes `logbufsz` memory. |
| `db2hadr` | High Availability Disaster Recovery thread shipping logs across TCP sockets. | Managed by `HADR_LOCAL_HOST`/`PORT`. |
| `db2dlock` | Deadlock detection thread scanning the lock table at intervals specified by `dlchkfreq`. | Configured via `dlchkfreq` (ms). |

---

## 2. Storage Architecture: Bufferpools & Tablespaces

Db2 tablespaces are allocated with explicit page sizes matching dedicated bufferpools:
- Supported page sizes: **4 KB, 8 KB, 16 KB, and 32 KB**.
- Tablespaces can only be assigned to a bufferpool with an identical page size.
- **Automatic Storage**: Db2 dynamically allocates containers across storage paths, striping extents across disks automatically.
- **Asynchronous Cleaning Threshold (`chngpgs_thresh`)**: Specifies the percentage of dirty pages in a bufferpool (default: 60%) that triggers `db2pclnr` to start flushing pages to prevent query stalling.

---

## 3. High Availability Disaster Recovery (HADR)

HADR ships transaction logs from the Primary database to a Standby database. Db2 provides four distinct synchronization modes:

| HADR Mode | Write Acknowledged Point | RPO Guarantee | Performance Impact |
| :--- | :--- | :--- | :--- |
| `SYNC` | Acknowledged after written to disk on both Primary and Standby. | Zero (RPO = 0) | High network latency sensitivity. |
| `NEARSYNC` | Acknowledged when received in Standby main memory buffer. | Near Zero | Minimal latency impact; safe from disk failure. |
| `ASYNC` | Acknowledged when sent over Primary network socket. | Minimal (flight lag) | Very low latency impact. |
| `SUPERASYNC`| Primary never waits for Standby acknowledgments. | Potential lag | Zero latency impact on Primary transactions. |

---

## 4. Concurrency & Currently Committed Semantics

To eliminate concurrency lock waits between readers and writers:
- `CUR_COMMIT = ON`: When a transaction updates a row, concurrent `SELECT` queries do not wait for the exclusive row lock to be released.
- Instead, readers access the **currently committed version** of the data recorded in the log buffers, completely eliminating lock timeouts (`SQL0911N reason code 68`).

---

## 5. Production Diagnostics via db2pd & MON_GET

### Bufferpool Hit Ratio Telemetry
```sql
SELECT
  bp_name,
  (1.0 - (FLOAT(pool_data_p_reads + pool_index_p_reads) /
   NULLIF(FLOAT(pool_data_l_reads + pool_index_l_reads), 0))) * 100 AS hit_ratio
FROM TABLE(MON_GET_BUFFERPOOL(NULL, -2)) AS t;
```

### HADR Replication State Verification
```bash
db2pd -db SAMPLE -hadr
```"""
        },
        "id": {
            "title": "Arsitektur IBM Db2 11.5: Engine Dispatchable Units (EDUs), Manajemen Tablespace, dan Replikasi HADR",
            "summary": "Arsitektur mendalam IBM Db2 11.5: model thread EDUs, bufferpool, tablespace automatic storage, semantik Currently Committed, dan status failover HADR.",
            "body": """## Model Arsitektur Engine Dispatchable Units (EDUs) IBM Db2

IBM Db2 beroperasi menggunakan arsitektur multi-threaded berbasis proses utama `db2sysc`. Di dalam proses tersebut, konkurensi ditangani oleh unit thread ringan bernama **Engine Dispatchable Units (EDUs)**.

```
+---------------------------------------------------------------------------------+
|                       INSTANSI PROSES ENGINE DB2 (db2sysc)                      |
|                                                                                 |
|  +--------------------------- BUFFERPOOL DATABASE ---------------------------+  |
|  | IBMDEFAULTBP (4KB/8KB) | Bufferpool Khusus (16KB/32KB) | Package Cache    |  |
|  +---------------------------------------------------------------------------+  |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  |  db2agent   |       |  db2pfchr   |        |  db2pclnr   |                   |
|  | (Koordinator|       | (Prefetcher)|        | (Page Clean)|                   |
|  +-------------+       +-------------+        +-------------+                   |
|         ^                     ^                      ^                          |
|  +------+------+       +------+------+        +------+------+                   |
|  |  db2loggw   |       |  db2hadr    |        |  db2dlock   |                   |
|  | (Log Writer)|       | (Mesin HADR)|        | (Deadlock)  |                   |
|  +-------------+       +-------------+        +-------------+                   |
+---------------------------------------------------------------------------------+
                                      | Lapisan Penyimpanan
                                      v
         +---------------------------------------------------------------+
         | Tablespace Automatic Storage (.DAT)  | File Log Aktif         |
         +---------------------------------------------------------------+
```

---

## 1. Topologi Engine Dispatchable Units (EDUs)

| Nama Thread EDU | Peran Operasional | Pengaturan Terkait |
| :--- | :--- | :--- |
| `db2agent` | Agen koordinator yang melayani kueri untuk satu koneksi client tertentu. | Dibatasi oleh `max_coordagents`. |
| `db2pfchr` | Prefetcher asinkron yang membaca extent mendahului kueri saat table scan. | Dikelola via `num_ioservers`. |
| `db2pclnr` | Page cleaner yang menulis halaman kotor bufferpool ke disk sebelum memori penuh. | Dikelola via `num_iocleaners`. |
| `db2loggw` | Log writer yang melakukan flush buffer log transaksi ke disk saat commit. | Mengosongkan memori `logbufsz`. |
| `db2hadr` | Thread replikasi HADR yang mengirimkan log ke standby melalui socket TCP. | Dikonfigurasi via parameter HADR. |

---

## 2. Struktur Penyimpanan: Bufferpool & Tablespace

Tablespace pada Db2 memiliki ukuran halaman eksplisit yang harus cocok dengan bufferpool terkait:
- Pilihan ukuran halaman: **4 KB, 8 KB, 16 KB, dan 32 KB**.
- **Automatic Storage**: Db2 secara dinamis mendistribusikan container ke path storage yang tersedia.
- **`chngpgs_thresh` (Ambang Batas Halaman Kotor)**: Menentukan persentase halaman kotor di bufferpool (default: 60%) yang memicu `db2pclnr` menulis data ke disk untuk mencegah kelangkaan buffer.

---

## 3. High Availability Disaster Recovery (HADR)

Db2 menyediakan empat mode sinkronisasi log replikasi:
- **`SYNC`**: Transaksi dinyatakan selesai setelah tersimpan di disk Primary dan Standby (RPO = 0).
- **`NEARSYNC`**: Transaksi selesai setelah diterima di RAM memori Standby (kompromi terbaik RPO & kecepatan).
- **`ASYNC`**: Transaksi selesai begitu paket terkirim lewat socket Primary.
- **`SUPERASYNC`**: Primary tidak pernah menunggu konfirmasi Standby (throughput maksimal).

---

## 4. Semantik Currently Committed (`CUR_COMMIT = ON`)

Untuk menghindari transaksi pembacaan terhenti akibat menunggu lock:
- Pembaca (`SELECT`) tidak perlu menunggu transaksi tulis melepaskan lock baris.
- Pembaca langsung mengakses **versi data terakhir yang telah di-commit** dari buffer log transaksi, meniadakan error timeout lock (`SQL0911N reason code 68`).

---

## 5. Telemetri Diagnostik Produksi

```sql
SELECT
  bp_name,
  (1.0 - (FLOAT(pool_data_p_reads + pool_index_p_reads) /
   NULLIF(FLOAT(pool_data_l_reads + pool_index_l_reads), 0))) * 100 AS hit_ratio
FROM TABLE(MON_GET_BUFFERPOOL(NULL, -2)) AS t;
```""",
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
    {
        "slug": "mongodb-architecture-wiredtiger-sharding",
        "category_slug": "nosql",
        "engine": "MongoDB",
        "en": {
            "title": "MongoDB Architecture: WiredTiger Engine, Replica Sets, and Sharding",
            "summary": "Deep dive into MongoDB WiredTiger cache evictions, write concerns, Raft-like replica set elections, and distributed sharded cluster balancing.",
            "body": """### MongoDB Core Architecture
MongoDB is a distributed document database using BSON (Binary JSON) serialization.

### 1. The WiredTiger Storage Engine
Since MongoDB 3.2, WiredTiger is the default storage engine providing document-level concurrency control and compression.
- **Cache Sizing**: Defaults to `50% of (RAM - 1 GB)` or 256 MB, whichever is greater.
- **Checkpoints**: WiredTiger writes checkpoints to disk every 60 seconds or when 2 GB of dirty data accumulates.
- **Eviction Server**: Background threads continuously evict clean and dirty pages when memory usage exceeds configured thresholds (`eviction_target`: 80%, `eviction_trigger`: 95%).

### 2. High Availability: Replica Sets
A replica set consists of one Primary node and multiple Secondary nodes.
- **Election Protocol**: Modified Raft-like consensus algorithm. When heartbeats to the Primary fail for 10 seconds (`electionTimeoutMillis`), eligible Secondaries initiate an election.
- **Oplog (Operations Log)**: Capped collection in the `local` database recording write operations as idempotent transitions. Secondaries continuously tail the Primary oplog.
- **Write Concerns**:
  - `w: 1`: Acknowledged by Primary only (fast, risk of rollback on crash).
  - `w: "majority"`: Committed to a majority of replica set members before acknowledging client.

### 3. Horizontal Scalability: Sharded Clusters
For datasets exceeding single-node capacity:
- **mongos**: Stateless query routers that parse queries and direct operations to appropriate shards.
- **Config Replica Set**: Stores cluster metadata and routing table mappings for chunk ranges.
- **Shard**: Each shard is a standalone replica set containing a partition of the total dataset.
- **Balancer**: Background process that migrates data chunks across shards to ensure uniform distribution."""
        },
        "id": {
            "title": "Arsitektur MongoDB: WiredTiger Engine, Replica Set, dan Sharding",
            "summary": "Analisis mendalam mesin penyimpanan WiredTiger MongoDB, write concerns, pemilihan replica set, dan partisi klaster sharding terdistribusi.",
            "body": """### Arsitektur Inti MongoDB
MongoDB adalah database dokumen terdistribusi yang menyimpan data dalam format serialisasi BSON (Binary JSON).

### 1. Mesin Penyimpanan WiredTiger
WiredTiger menyediakan kontrol konkurensi tingkat dokumen (document-level concurrency) dan kompresi data native (Snappy/zlib).
- **Alokasi Cache**: Default ke `50% dari (RAM - 1 GB)`.
- **Checkpointing**: Menulis checkpoint ke disk setiap 60 detik atau saat data kotor mencapai 2 GB.
- **Thread Eviction**: Membersihkan halaman data dari memori RAM secara otomatis saat mencapai ambang batas batas 80%.

### 2. Ketersediaan Tinggi: Replica Set
Klaster high-availability terdiri dari satu node Primary dan beberapa node Secondary.
- **Protokol Pemilihan**: Berbasis algoritma Raft. Jika heartbeat ke Primary terputus selama 10 detik, node Secondary memulai pemilihan pemimpin baru.
- **Oplog**: Koleksi khusus berkapasitas tetap (capped collection) di database `local` yang mencatat log mutasi secara idempoten untuk direplikasi ke node Secondary.
- **Jaminan Write Concern**:
  - `w: 1`: Client mendapat konfirmasi begitu Primary menyimpan operasi.
  - `w: "majority"`: Konfirmasi hanya dikirim jika mayoritas node telah menyimpan log mutasi.

### 3. Skalabilitas Horizontal: Sharded Cluster
- **mongos**: Router kueri tanpa status (stateless) yang memetakan kueri client ke shard yang sesuai.
- **Config Replica Set**: Menyimpan katalog metadata dan batas rentang chunk (routing table).
- **Shard**: Masing-masing shard merupakan replica set mandiri yang menyimpan subset data.
- **Balancer**: Proses latar belakang yang menyeimbangkan chunk antar shard secara otomatis."""
        }
    },
    {
        "slug": "redis-internals-persistence-cluster",
        "category_slug": "nosql",
        "engine": "Redis",
        "en": {
            "title": "Redis Architecture & Internals: In-Memory Data Structures, Persistence, and Cluster",
            "summary": "Understanding Redis single-threaded event loop, RDB vs AOF persistence trade-offs, Sentinel failovers, and 16,384-slot Cluster partitioning.",
            "body": """### Redis Architecture Overview
Redis is an in-memory key-value data structure store designed for sub-millisecond latency.

### 1. The Single-Threaded Event Loop
Redis utilizes an asynchronous non-blocking event-driven loop (`ae.c` using `epoll` on Linux) to process incoming commands sequentially:
- Eliminates CPU context switching and lock contention overhead.
- Redis 6.0+ introduced multi-threaded I/O for socket reading and writing while keeping command execution single-threaded.

### 2. Dual Persistence Architecture
- **RDB (Redis Database Snapshotting)**:
  - Point-in-time binary snapshot created via `BGSAVE` using Linux `fork()` copy-on-write.
  - Minimal impact on client throughput; ultra-fast recovery time.
  - Downside: Data between the last snapshot and a crash is lost.
- **AOF (Append Only File)**:
  - Logs every write command sequentially.
  - Fsync policy configurable via `appendfsync`: `always` (slowest, safest), `everysec` (recommended default), or `no`.
  - Automatic background rewrite (`BGREWRITEAOF`) compacts log commands into minimal instructions.

### 3. High Availability: Redis Sentinel
- Three or more Sentinel instances monitor master and replica health.
- Performs automatic failover using Raft-inspired quorum election if master misses heartbeats (`down-after-milliseconds`).

### 4. Horizontal Partitioning: Redis Cluster
- Total keyspace is partitioned into exactly **16,384 hash slots**.
- Slot assignment formula: `HASH_SLOT = CRC16(key) MOD 16384`.
- Hash tags (`{user100}:profile`) guarantee related keys map to the identical slot for multi-key atomicity.
- Clients receive `MOVED` or `ASK` redirects when querying nodes that do not own the requested slot."""
        },
        "id": {
            "title": "Arsitektur & Internal Redis: Struktur Data Memori, Persistensi RDB/AOF, dan Klaster",
            "summary": "Memahami event loop single-threaded Redis, kompromi persistensi RDB vs AOF, failover otomatis Sentinel, dan partisi 16.384 slot Redis Cluster.",
            "body": """### Ikhtisar Arsitektur Redis
Redis adalah penyimpanan struktur data dalam memori (in-memory key-value store) yang dirancang untuk latensi sub-milidetik.

### 1. Event Loop Single-Threaded
Redis menggunakan event loop asinkron non-blocking (`ae.c` dengan `epoll` di Linux):
- Meniadakan overhead context switching CPU dan perebutan kunci (lock contention).
- Sejak versi 6.0, I/O jaringan (socket read/write) didukung multi-threading, namun eksekusi perintah tetap bersifat single-threaded dan atomik.

### 2. Arsitektur Persistensi Ganda
- **RDB (Snapshotting)**:
  - Snapshot biner pada titik waktu tertentu dibuat via perintah `BGSAVE` dengan memanfaatkan Linux `fork()` copy-on-write.
  - Waktu pemulihan (recovery) sangat kilat. Kekurangan: ada potensi kehilangan data beberapa menit terakhir jika terjadi crash mendadak.
- **AOF (Append Only File)**:
  - Mencatat setiap perintah mutasi penulisan secara sekuensial.
  - Kebijakan `appendfsync everysec` memberikan kompromi terbaik antara durabilitas dan kecepatan.
  - `BGREWRITEAOF` memadatkan log riwayat perintah lama agar ukuran file tidak membengkak.

### 3. Ketersediaan Tinggi: Redis Sentinel
- Minimal 3 node Sentinel memantau kesehatan node Master dan Replica.
- Melakukan failover otomatis dan mempromosikan Replica menjadi Master jika Master gagal merespons heartbeat sesuai batas kuorum.

### 4. Partisi Horizontal: Redis Cluster
- Ruang kunci dibagi rata menjadi **16.384 hash slot**.
- Rumus kalkulasi slot: `CRC16(key) MOD 16384`.
- Menggunakan hash tag (`{user:101}:orders`) untuk memastikan kumpulan kunci terkait berada pada slot yang sama.
- Client menerima redirect `MOVED` jika node yang dituju tidak memegang slot data tersebut."""
        }
    },
    {
        "slug": "cassandra-lsm-architecture-ring",
        "category_slug": "nosql",
        "engine": "Apache Cassandra",
        "en": {
            "title": "Apache Cassandra Architecture: LSM-Tree Storage, Ring Topology, and Tunable Consistency",
            "summary": "Mastering Cassandra masterless architecture, Memtable/SSTable compaction, Bloom filters, and tunable CAP theorem consistency levels.",
            "body": """### Apache Cassandra Core Architecture
Cassandra is a distributed NoSQL wide-column database based on Amazon Dynamo and Google Bigtable design principles.

### 1. Masterless Peer-to-Peer Ring
Every node in the cluster is architecturally identical; there is no primary/replica hierarchy or single point of failure (SPOF).
- **Gossip Protocol**: Nodes continuously exchange node state and cluster topology every second.
- **Partitioners**: `Murmur3Partitioner` maps partition keys to 64-bit integer tokens spanning `-2^63` to `+2^63 - 1` across the ring.

### 2. Log-Structured Merge (LSM) Storage Engine
Writes are append-only and extremely high-throughput because they avoid in-place random disk I/O:
1. **CommitLog**: Sequential append on disk for crash durability.
2. **Memtable**: In-memory sorted skiplist write buffer.
3. **SSTables (Sorted String Tables)**: Once Memtable is full, flushed sequentially to immutable on-disk SSTables.
4. **Compaction**: Background merge of overlapping SSTables discarding tombstones (deleted rows) and consolidating latest values.

### 3. Read Path Optimization
Because data blocks are immutable across multiple SSTables, Cassandra uses:
- **Bloom Filters**: Probabilistic bit arrays in RAM verifying with zero disk I/O if an SSTable definitely does not contain a partition key.
- **Partition Summary & Index**: Quickly locates the partition offset within the SSTable data file.

### 4. Tunable Consistency (CAP Theorem)
Cassandra allows client queries to tune consistency per transaction:
- **Write Consistency**: `ONE`, `QUORUM`, `LOCAL_QUORUM`, `ALL`.
- **Formula for Strong Consistency**: If `R + W > N` (where `R` = Read Consistency nodes, `W` = Write Consistency nodes, `N` = Replication Factor), the client is mathematically guaranteed to read the latest committed update."""
        },
        "id": {
            "title": "Arsitektur Apache Cassandra: Penyimpanan LSM-Tree, Topologi Ring, dan Konsistensi Fleksibel",
            "summary": "Menguasai arsitektur masterless Cassandra, komparasi pemadatan Memtable/SSTable, filter Bloom, dan tingkat konsistensi CAP theorem yang dapat dikonfigurasi.",
            "body": """### Arsitektur Inti Apache Cassandra
Cassandra adalah database terdistribusi wide-column yang menggabungkan prinsip Amazon Dynamo (distribusi masterless) dan Google Bigtable (penyimpanan LSM).

### 1. Topologi Ring Masterless P2P
Semua node dalam klaster memiliki peran yang setara tanpa adanya node master (eliminasi Single Point of Failure):
- **Gossip Protocol**: Node saling bertukar informasi kesehatan dan topologi setiap detik.
- **Partitioner**: `Murmur3Partitioner` memetakan partition key ke rentang token bilangan bulat 64-bit (`-2^63` hingga `+2^63 - 1`).

### 2. Alur Tulis LSM-Tree (Log-Structured Merge)
Operasi penulisan Cassandra tidak pernah melakukan penulisan acak (random I/O), melainkan sekuensial cepat:
1. **CommitLog**: Dicatat secara berurutan ke disk untuk ketahanan data saat crash.
2. **Memtable**: Disimpan pada memori RAM dalam struktur sorted skiplist.
3. **SSTables**: Ketika Memtable penuh, data di-flush secara sekuensial menjadi file SSTable permanen yang immutable (tidak dapat diubah).
4. **Kompaksi (Compaction)**: Proses penggabungan file SSTable untuk membersihkan tombstone (data terhapus) dan mengonsolidasikan versi terbaru.

### 3. Optimasi Alur Pembacaan
- **Bloom Filter**: Struktur data probabilistik di RAM yang menentukan apakah sebuah SSTable pasti tidak memiliki kunci yang dicari tanpa perlu membaca disk.
- **Partition Summary & Index**: Mempercepat pencarian offset baris pada file SSTable.

### 4. Konsistensi yang Dapat Dikonfigurasi (Tunable Consistency)
Client dapat menentukan tingkat konsistensi per kueri:
- Pilihan: `ONE`, `QUORUM`, `LOCAL_QUORUM`, `ALL`.
- **Prinsip Konsistensi Kuat**: Jika `R + W > N` (di mana R adalah node baca, W node tulis, dan N replication factor), client dipastikan selalu membaca data terbaru."""
        }
    },
    {
        "slug": "cockroachdb-distributed-sql-raft",
        "category_slug": "distributed-sql",
        "engine": "CockroachDB & YugabyteDB",
        "en": {
            "title": "CockroachDB & YugabyteDB: Distributed SQL, Multi-Raft Consensus, and HLC",
            "summary": "How next-generation distributed SQL databases provide full ACID serializability, Raft range replication, and Hybrid Logical Clocks.",
            "body": """### Distributed SQL Paradigm
Distributed SQL combines the relational guarantees, schemas, and ACID transactions of traditional RDBMS with the horizontal scale and high availability of NoSQL.

### 1. Multi-Raft Consensus & Range Sharding
The entire keyspace is divided into continuous **64 MB ranges**:
- Each range is replicated across multiple nodes (typically 3 or 5 replicas) forming an independent Raft consensus group.
- **Leaseholder**: One replica is elected leaseholder to coordinate client read and write operations, bypassing consensus round-trips for read-only queries.
- When ranges exceed 64 MB, CockroachDB splits the range into two 32 MB ranges and rebalances them across cluster nodes automatically.

### 2. Hybrid Logical Clocks (HLC)
Without relying on expensive proprietary atomic GPS hardware (like Google Spanner TrueTime):
- CockroachDB implements **Hybrid Logical Clocks (HLC)** combining physical wall clock time with Lamport logical counters.
- Clocks across cluster nodes must remain synchronized within a configurable maximum offset (`--max-offset`, typically 500ms). Nodes self-evict if NTP drift exceeds this threshold.

### 3. Lock-Free Distributed Transactions & MVCC
- Transactions write uncommitted row mutations as **inline intent records** pointing to a centralized transaction record in the range.
- If a concurrent transaction reads an intent, it checks the transaction status: if committed, it reads the value; if aborted, it ignores it; if pending, it waits or triggers priority resolution."""
        },
        "id": {
            "title": "CockroachDB & YugabyteDB: SQL Terdistribusi, Konsensus Multi-Raft, dan HLC",
            "summary": "Bagaimana database Distributed SQL modern menghadirkan serializability ACID penuh, replikasi range berbasis Multi-Raft, dan Hybrid Logical Clocks (HLC).",
            "body": """### Paradigma Distributed SQL
Distributed SQL menggabungkan keandalan relasional, skema SQL, dan transaksi ACID penuh dengan skalabilitas horizontal otomatis tanpa sharding manual.

### 1. Konsensus Multi-Raft & Partisi Range
Seluruh ruang data dibagi menjadi rentang byte berurutan berukuran **64 MB (Ranges)**:
- Setiap range direplikasi ke beberapa node (biasanya 3 atau 5 salinan) menggunakan grup konsensus Raft independen.
- **Leaseholder**: Salah satu replika ditunjuk sebagai koordinator kueri baca/tulis langsung untuk meniadakan latency konsensus pada pembacaan lokal.
- Ketika data melampaui 64 MB, sistem membagi range menjadi dua (range split) dan memindahkannya ke node lain yang memiliki kapasitas luang (auto-rebalancing).

### 2. Hybrid Logical Clocks (HLC)
- Menghadirkan pengurutan transaksi konsisten tanpa memerlukan jam atomik GPS mahal (seperti Google Spanner TrueTime).
- HLC menggabungkan waktu fisik sistem operasi (physical wall clock) dengan pencacah logis Lamport (logical counter).
- Toleransi selisih jam antar server dibatasi ketat (`--max-offset` maksimal 500ms); node akan mengisolasi diri jika NTP drift melampaui batas aman.

### 3. Transaksi ACID Terdistribusi Tanpa Kunci Berat
- Transaksi menulis mutasi sementara sebagai **intent record** yang mengacu pada status transaksi induk.
- Transaksi lain yang membaca intent record dapat langsung mengevaluasi status commit secara non-blocking tanpa memicu lock berkepanjangan."""
        }
    },
    {
        "slug": "snowflake-cloud-data-warehouse-internals",
        "category_slug": "analytics",
        "engine": "Snowflake",
        "en": {
            "title": "Snowflake Architecture: Multi-Cluster Shared Data, Micro-Partitions, and Zero-Copy Cloning",
            "summary": "An architectural exploration of Snowflake tri-layer separation of storage, compute virtual warehouses, and cloud services metadata.",
            "body": """### Snowflake Tri-Layer Architecture
Snowflake decouples storage and compute completely through its multi-cluster shared data model.

### 1. The Three Independent Layers
1. **Centralized Storage Layer**:
   - Resides on scalable cloud object storage (Amazon S3, Azure Blob, or Google Cloud Storage).
   - Data is stored in proprietary columnar compressed files called **Micro-Partitions** (50 to 500 MB uncompressed).
   - Micro-partitions are completely immutable; mutations create new partitions.
2. **Virtual Warehouse (Compute) Layer**:
   - Independent compute clusters of EC2/GCP instances executing query processing.
   - Warehouses can be resized (X-Small to 6X-Large) in seconds or auto-suspended when idle to minimize cloud cost.
   - Nodes feature local NVMe SSD caching for frequently queried micro-partitions.
3. **Cloud Services Layer**:
   - The brain of Snowflake managing authentication, transaction coordination, ACID metadata, query optimization, and access control.

### 2. Automatic Micro-Partitioning & Pruning
- Snowflake automatically partitions data based on natural ingestion order without requiring manual index creation or partitioning schemes.
- The Cloud Services layer records min/max metadata for every column across all micro-partitions.
- Query optimizer eliminates irrelevant micro-partitions during compilation (**partition pruning**), reading only required storage blocks.

### 3. Zero-Copy Cloning & Time Travel
- Cloning a 50-terabyte table takes seconds and zero storage cost because it only duplicates Cloud Services metadata pointers.
- Storage costs only accrue when cloned tables diverge via new mutations."""
        },
        "id": {
            "title": "Arsitektur Snowflake: Multi-Cluster Shared Data, Micro-Partition, dan Zero-Copy Cloning",
            "summary": "Eksplorasi arsitektur pemisahan tiga lapis Snowflake: penyimpanan data terpusat, komputasi virtual warehouse, dan layanan metadata cloud.",
            "body": """### Arsitektur Tiga Lapis Snowflake
Snowflake memisahkan kapasitas penyimpanan (storage) dan pemrosesan komputasi (compute) secara total.

### 1. Tiga Lapisan Mandiri
1. **Centralized Storage Layer**:
   - Menggunakan penyimpanan cloud object storage berskala masif (AWS S3, Azure Blob, atau GCP Cloud Storage).
   - Data disimpan dalam format kolumnar terkompresi yang disebut **Micro-Partition** (ukuran 50 - 500 MB). File bersifat immutable (tidak dapat ditimpa).
2. **Virtual Warehouse (Compute) Layer**:
   - Klaster komputasi mandiri (tersedia ukuran X-Small hingga 6X-Large) yang dapat di-scale up atau di-suspend seketika saat idle untuk menghemat biaya.
   - Setiap node komputasi memiliki cache NVMe SSD lokal untuk kueri berulang.
3. **Cloud Services Layer**:
   - Lapisan koordinator pusat yang mengelola autentikasi, metadata transaksi ACID, optimasi eksekusi kueri, dan keamanan.

### 2. Micro-Partitioning & Pruning Otomatis
- Data dipartisi otomatis tanpa perlu membuat index manual atau menentukan skema partisi statis.
- Lapisan metadata mencatat nilai minimum dan maksimum dari setiap kolom pada setiap micro-partition.
- Saat kueri dijalankan, optimizer langsung mengabaikan partition yang tidak relevan (**partition pruning**) sehingga meminimalisir pembacaan data.

### 3. Zero-Copy Cloning & Time Travel
- Duplikasi tabel data berukuran puluhan terabyte selesai dalam hitungan detik tanpa biaya disk tambahan karena hanya menduplikasi pointer metadata.
- Biaya penyimpanan tambahan hanya dihitung jika terjadi perubahan data baru pada tabel hasil kloning."""
        }
    },
    {
        "slug": "clickhouse-duckdb-columnar-vectorized",
        "category_slug": "analytics",
        "engine": "ClickHouse & DuckDB",
        "en": {
            "title": "ClickHouse & DuckDB: Column-Oriented Storage and Vectorized Query Execution",
            "summary": "High-performance analytical engines demystified: MergeTree storage family, SIMD vectorized processing, and embedded columnar analytics with DuckDB.",
            "body": """### Columnar Analytical Engines
Unlike OLTP row-based engines, columnar databases store entire columns contiguous on disk, maximizing aggregation speed and compression ratios.

### 1. Column-Oriented Storage Layout
- When running `SELECT AVG(revenue) FROM orders`, row-oriented databases must read every column into memory.
- Columnar engines read strictly the `revenue` column file, slashing disk I/O by 90-95%.
- Identical data types stored together achieve immense compression ratios using algorithms like LZ4, ZSTD, Gorilla, and DoubleDelta.

### 2. SIMD Vectorized Execution
- Traditional query engines process tuples one at a time using the Volcano iterator model (`next()`).
- ClickHouse and DuckDB operate on vectors of data (arrays of 1024 or 2048 values) in tight CPU loops.
- Employs CPU **SIMD (Single Instruction, Multiple Data)** registers (AVX-512, NEON) to compute arithmetic aggregations across multiple values in a single clock cycle.

### 3. ClickHouse MergeTree Engine
- Data is written in immutable parts.
- Background threads continuously merge smaller parts into larger sorted parts while updating sparse primary key indexes.
- Specialized variants: `ReplacingMergeTree` (deduplication), `AggregatingMergeTree` (pre-aggregated rollups).

### 4. DuckDB: The SQLite of Analytics
- Zero-dependency embedded analytical engine running directly inside the host process memory space (Python, Node.js, Go).
- Directly queries remote Parquet, Arrow, and CSV files with zero copy overhead."""
        },
        "id": {
            "title": "Arsitektur ClickHouse & DuckDB: Penyimpanan Kolumnar dan Eksekusi Kueri Tervektorisasi (SIMD)",
            "summary": "Membedah mesin analitik performa tinggi: arsitektur MergeTree, eksekusi tervektorisasi SIMD pada CPU, dan analisis kolumnar embedded dengan DuckDB.",
            "body": """### Mesin Analitik Berorientasi Kolom
Tidak seperti database transaksional (OLTP) yang menyimpan data per baris, database analitik menyimpan data per kolom secara berurutan pada disk.

### 1. Format Penyimpanan Kolumnar
- Pada kueri agregasi seperti `SELECT AVG(revenue) FROM orders`, database baris harus memuat seluruh kolom ke memori.
- Database kolumnar hanya membaca file kolom `revenue`, memangkas kebutuhan I/O disk hingga 90-95%.
- Data dengan tipe serupa yang tersusun berdampingan menghasilkan rasio kompresi tinggi melalui algoritma seperti LZ4, ZSTD, Gorilla, dan DoubleDelta.

### 2. Eksekusi Tervektorisasi (SIMD)
- Model iterator tradisional memproses satu baris data per panggilan fungsi (`next()`).
- ClickHouse dan DuckDB memproses data dalam bentuk vektor (vektor 1024 atau 2048 nilai) dalam satu putaran loop CPU yang ketat.
- Memanfaatkan register **SIMD (Single Instruction, Multiple Data)** modern (AVX-512 / ARM NEON) untuk mengeksekusi operasi aritmatika pada banyak nilai sekaligus dalam 1 siklus clock CPU.

### 3. Mesin MergeTree ClickHouse
- Data ditulis dalam bagian-bagian (parts) immutable.
- Thread latar belakang menggabungkan (merge) part-part kecil menjadi part besar yang terurut sambil memperbarui sparse primary key index.

### 4. DuckDB: 'SQLite' untuk Kueri Analitik
- Mesin analitik embedded tanpa ketergantungan eksternal yang berjalan langsung di dalam memori proses aplikasi (Python, Node.js).
- Mampu mengeksekusi kueri analitik langsung di atas file Parquet, Arrow, dan CSV secara efisien tanpa memerlukan server database terpisah."""
        }
    }
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
            en_art = en_res.scalar_one_or_none()
            if not en_art:
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
            else:
                en_art.title = item["en"]["title"]
                en_art.summary = item["en"]["summary"]
                en_art.body_markdown = item["en"]["body"]
                en_art.engine = item["engine"]
                en_art.category_id = k_cat_cache[cat_slug]
                en_art.last_reviewed_at = datetime.now(timezone.utc)
                print(f"Updated EN article: {item['slug']}")

            # Indonesian Article
            id_res = await session.execute(
                select(KnowledgeArticle).where(
                    KnowledgeArticle.slug == item["slug"],
                    KnowledgeArticle.language == "id",
                )
            )
            id_art = id_res.scalar_one_or_none()
            if not id_art:
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
            else:
                id_art.title = item["id"]["title"]
                id_art.summary = item["id"]["summary"]
                id_art.body_markdown = item["id"]["body"]
                id_art.engine = item["engine"]
                id_art.category_id = k_cat_cache[cat_slug]
                id_art.last_reviewed_at = datetime.now(timezone.utc)
                print(f"Updated ID article: {item['slug']}")

        await session.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
