"""
WIYATA Knowledge Center v2 Data Catalog
Bilingual (en/id) datasets for Glossary, Cross-Database Comparisons,
DBA Field Handbook, Incident Runbooks, and Visual Database Academy.
"""

GLOSSARY_TERMS = [
    {
        "slug": "sga",
        "term": "System Global Area",
        "acronym": "SGA",
        "aliases": ["Shared Global Area", "Oracle SGA"],
        "category": "Memory & Cache",
        "category_id": "Memori & Cache",
        "engines": ["oracle"],
        "level": "Intermediate",
        "definition_en": "Shared memory region allocated when an Oracle Database instance starts, containing data and control information for the instance.",
        "definition_id": "Area memori bersama yang dialokasikan saat instance Oracle Database menyala, menampung data cache dan kontrol instansi.",
        "explanation_en": "The SGA is shared by all server and background processes. Key subcomponents include the Database Buffer Cache (stores data blocks), Shared Pool (parses SQL, package cache), Redo Log Buffer, and Large Pool.",
        "explanation_id": "SGA diakses bersama oleh seluruh proses server dan background. Komponen utamanya meliputi Buffer Cache (cache blok data), Shared Pool (cache SQL dan eksekusi), Redo Log Buffer, dan Large Pool.",
        "field_slang": "Memori Instance Oracle / Pool Bersama",
        "diagnostic_query": "SELECT pool, name, bytes/1024/1024 AS mb FROM v$sgastat ORDER BY bytes DESC FETCH FIRST 10 ROWS ONLY;",
        "related_slugs": ["pga", "buffer-pool", "redo-log"]
    },
    {
        "slug": "pga",
        "term": "Program Global Area",
        "acronym": "PGA",
        "aliases": ["Process Global Area", "Private Global Area"],
        "category": "Memory & Cache",
        "category_id": "Memori & Cache",
        "engines": ["oracle"],
        "level": "Intermediate",
        "definition_en": "Private non-shared memory region allocated when a dedicated server process starts in Oracle.",
        "definition_id": "Area memori privat yang dialokasikan khusus untuk tiap proses server klien di Oracle, tidak dibagi dengan sesi lain.",
        "explanation_en": "Stores session variables, sort work areas, hash join areas, and cursor state. Unlike the SGA, PGA is private to each server process and is deallocated upon disconnect.",
        "explanation_id": "Menyimpan variabel sesi, area kerja pengurutan (sort work area), hash join, dan status kursor. Dibebaskan saat klien disconnect.",
        "field_slang": "Memori Privat Sesi",
        "diagnostic_query": "SELECT program, pga_used_mem/1024/1024 AS pga_used_mb, pga_alloc_mem/1024/1024 AS pga_alloc_mb FROM v$process ORDER BY pga_used_mem DESC FETCH FIRST 10 ROWS ONLY;",
        "related_slugs": ["sga", "work-mem"]
    },
    {
        "slug": "wal",
        "term": "Write-Ahead Logging",
        "acronym": "WAL",
        "aliases": ["Transaction Log", "XLOG", "Redo Log"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "sqlite", "mysql", "oracle", "mssql", "db2"],
        "level": "Fundamental",
        "definition_en": "Core durability technique where state changes must be appended to disk storage before data pages are written.",
        "definition_id": "Teknik durabilitas fundamental di mana log perubahan harus ditulis dan di-flush ke disk sebelum halaman data dimodifikasi.",
        "explanation_en": "Ensures ACID Atomicity and Durability without requiring the database engine to flush random dirty pages on every transaction commit.",
        "explanation_id": "Menjamin sifat ACID Durability tanpa harus mem-flush halaman data acak ke disk setiap kali ada commit transaksi.",
        "field_slang": "Buku Catatan Transaksi / Jurnal WAL",
        "diagnostic_query": "SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());",
        "related_slugs": ["checkpoint", "pitr", "redo-log"]
    },
    {
        "slug": "mvcc",
        "term": "Multi-Version Concurrency Control",
        "acronym": "MVCC",
        "aliases": ["Snapshot Isolation", "Row Versioning"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "mysql", "oracle", "mssql", "db2"],
        "level": "Advanced",
        "definition_en": "Concurrency paradigm allowing readers not to block writers and writers not to block readers by keeping multiple row versions.",
        "definition_id": "Mekanisme konkurensi di mana pembaca data (SELECT) tidak mengunci penulis (UPDATE) dan sebaliknya melalui riwayat versi baris.",
        "explanation_en": "Postgres writes new tuple versions into heap tables, requiring VACUUM. InnoDB and Oracle keep rollback undo segments. SQL Server utilizes TempDB version stores.",
        "explanation_id": "Postgres menyimpan versi baru langsung di tabel fisik (butuh VACUUM). InnoDB dan Oracle menggunakan segmen UNDO. SQL Server memakai TempDB.",
        "field_slang": "Versi Snapshot Data",
        "diagnostic_query": "SELECT relname, n_dead_tup, n_live_tup, last_vacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;",
        "related_slugs": ["vacuum", "undo-log", "dirty-read"]
    },
    {
        "slug": "session-lock",
        "term": "Blocking Session",
        "acronym": "LOCK",
        "aliases": ["Sesi Terblokir", "Session Nge-lock", "Contention"],
        "category": "Operational Incidents",
        "category_id": "Insiden Operasional",
        "engines": ["oracle", "postgres", "mysql", "mssql", "db2"],
        "level": "Intermediate",
        "definition_en": "Occurs when a database session holds an exclusive lock on a row or table that another session requests, forcing the second session to wait.",
        "definition_id": "Kondisi di mana sebuah sesi memegang lock eksklusif pada baris/tabel yang diminta sesi lain, menyebabkan sesi kedua tertahan antre.",
        "explanation_en": "If unresolved, blocking cascades into application connection pool exhaustion and HTTP 504 gateway timeouts.",
        "explanation_id": "Bila dibiarkan, antrean blocking menjalar ke antrean koneksi aplikasi hingga pool habis dan memicu HTTP 504 Gateway Timeout.",
        "field_slang": "Session Nge-lock / Antrean Gantung",
        "diagnostic_query": "SELECT blocked_locks.pid AS blocked_pid, blocking_locks.pid AS blocking_pid, blocked_activity.query AS blocked_statement FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid AND blocking_locks.pid != blocked_locks.pid JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid WHERE NOT blocked_locks.granted;",
        "related_slugs": ["deadlock", "connection-pool"]
    },
    {
        "slug": "deadlock",
        "term": "Deadlock",
        "acronym": "DLK",
        "aliases": ["Saling Mengunci", "Circular Wait"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "mysql", "oracle", "mssql", "db2"],
        "level": "Intermediate",
        "definition_en": "A circular dependency between two or more transactions where each holds a lock the other needs to proceed.",
        "definition_id": "Kondisi siklus buntu antara dua atau lebih transaksi di mana masing-masing memegang kunci yang dibutuhkan pihak lain.",
        "explanation_en": "Neither transaction can continue without external intervention. The database lock manager detects the cycle via a wait-for graph and terminates one transaction (the victim) with a rollback.",
        "explanation_id": "Tidak ada transaksi yang bisa lanjut. Mesin database mendeteksi siklus graf ketergantungan dan mengorbankan (rollback) salah satu transaksi korban.",
        "field_slang": "Saling Kunci Mati / Tabrakan Lock",
        "diagnostic_query": "SHOW ENGINE INNODB STATUS; -- Cek bagian LATEST DETECTED DEADLOCK",
        "related_slugs": ["session-lock", "mvcc"]
    },
    {
        "slug": "tablespace-full",
        "term": "Tablespace Saturation",
        "acronym": "TS_FULL",
        "aliases": ["Tablespace Penuh", "Datafile Maxsize", "Disk Exhaustion"],
        "category": "Storage & Capacity",
        "category_id": "Penyimpanan & Kapasitas",
        "engines": ["oracle", "db2", "postgres", "mssql"],
        "level": "Fundamental",
        "definition_en": "Critical storage incident where a tablespace or filesystem reaches 100% capacity and cannot allocate new extents.",
        "definition_id": "Insiden kapasitas di mana tablespace mencapai 100% dan gagal mengalokasikan extent baru untuk INSERT/UPDATE.",
        "explanation_en": "Throws error ORA-01653 / SQL0289N / MSSQL 1105. Write transactions fail immediately. Remedy requires adding datafiles, extending autoextend limits, or purging tables.",
        "explanation_id": "Menghasilkan error ORA-01653 / SQL0289N. Transaksi tulis gagal seketika. Solusi meliputi penambahan datafile atau pembersihan data usang.",
        "field_slang": "Storage / Kuota Disk Jebol",
        "diagnostic_query": "SELECT tablespace_name, round(used_percent, 2) AS pct_used FROM dba_tablespace_usage_metrics WHERE used_percent > 85;",
        "related_slugs": ["datafile", "autoextend"]
    },
    {
        "slug": "pitr",
        "term": "Point-in-Time Recovery",
        "acronym": "PITR",
        "aliases": ["Roll-Forward Recovery", "Pemulihan Berdasarkan Waktu"],
        "category": "Backup & Disaster Recovery",
        "category_id": "Backup & Pemulihan Bencana",
        "engines": ["postgres", "oracle", "mysql", "mssql", "db2"],
        "level": "Advanced",
        "definition_en": "Recovery procedure restoring a full baseline backup and rolling forward continuous transaction logs up to an exact microsecond before an incident.",
        "definition_id": "Prosedur restore backup dasar kemudian menerapkan log transaksi secara berurutan hingga tepat sebelum insiden terjadi.",
        "explanation_en": "Crucial for accidental data corruption, human error (e.g. DROP TABLE without WHERE), or ransomware attacks. Requires continuous archival of WAL/archive logs.",
        "explanation_id": "Sangat vital jika terjadi kecelakaan manusia (seperti UPDATE tanpa WHERE). Membutuhkan pengarsipan log transaksi yang berkesinambungan.",
        "field_slang": "Restore Titik Waktu / Roll Forward",
        "diagnostic_query": "SELECT pg_wal_replay_pause_state(), pg_last_wal_replay_lsn();",
        "related_slugs": ["wal", "rpo-rto"]
    },
    {
        "slug": "hadr",
        "term": "High Availability Disaster Recovery",
        "acronym": "HADR",
        "aliases": ["Db2 HADR", "Replikasi Siaga"],
        "category": "High Availability",
        "category_id": "Ketersediaan Tinggi",
        "engines": ["db2"],
        "level": "Advanced",
        "definition_en": "IBM Db2 continuous database replication feature that streams transaction logs to one or more standby databases.",
        "definition_id": "Fitur replikasi berkelanjutan IBM Db2 yang mengalirkan log transaksi ke satu atau lebih database siaga (standby).",
        "explanation_en": "Supports SYNC, NEARSYNC, ASYNC, and SUPERASYNC modes. Features Read on Standby (RoS) to offload reporting workloads.",
        "explanation_id": "Mendukung mode SYNC, NEARSYNC, ASYNC, dan SUPERASYNC, serta fitur Read on Standby (RoS) untuk mengalihkan kueri laporan.",
        "field_slang": "Replikasi Standby Db2",
        "diagnostic_query": "SELECT HADR_ROLE, HADR_STATE, HADR_LOG_GAP FROM TABLE(MON_GET_HADR(NULL));",
        "related_slugs": ["streaming-replication", "always-on"]
    },
    {
        "slug": "rpo-rto",
        "term": "Recovery Point & Time Objectives",
        "acronym": "RPO / RTO",
        "aliases": ["Target Pemulihan Bencana", "Toleransi Kehilangan Data"],
        "category": "Backup & Disaster Recovery",
        "category_id": "Backup & Pemulihan Bencana",
        "engines": ["oracle", "postgres", "mysql", "mssql", "db2", "sqlite"],
        "level": "Fundamental",
        "definition_en": "RPO defines the maximum acceptable data loss in time; RTO defines the maximum acceptable duration to restore operational service.",
        "definition_id": "RPO adalah batas toleransi kehilangan data dalam satuan waktu; RTO adalah target durasi maksimum untuk memulihkan layanan.",
        "explanation_en": "A zero-RPO requires synchronous replication (e.g., Oracle Data Guard SYNC, Postgres Synchronous Streaming). Lower RTO requires automated cluster failover.",
        "explanation_id": "Target zero-RPO mewajibkan replikasi sinkron. RTO yang rendah menuntut failover otomatis tanpa intervensi manual yang panjang.",
        "field_slang": "SLA Pemulihan / Batas Hilang Data",
        "diagnostic_query": "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag_rpo;",
        "related_slugs": ["pitr", "hadr"]
    }
]

CROSS_COMPARISONS = [
    {
        "topic": "Memory Architecture & Caching",
        "topic_id": "Arsitektur Memori & Mekanisme Cache",
        "dimension": "memory",
        "summary": "Comparison of memory pool allocation, buffer management, and thread working memory across enterprise engines.",
        "summary_id": "Komparasi alokasi pool memori, manajemen cache buffer, dan memori kerja sesi antar mesin database enterprise.",
        "engines": {
            "postgres": {
                "name": "PostgreSQL 17",
                "shared_pool": "Shared Buffers (typically 25% of RAM), relies heavily on Linux OS Page Cache for double buffering.",
                "private_memory": "work_mem per sort/hash operation, maintenance_work_mem for VACUUM/DDL.",
                "diagnostics": "pg_stat_database, pg_buffercache extension, pg_stat_io."
            },
            "mysql": {
                "name": "MariaDB 11.3 (MySQL)",
                "shared_pool": "InnoDB Buffer Pool (often 70-80% RAM), stores data pages, indexes, adaptive hash indexes.",
                "private_memory": "join_buffer_size, sort_buffer_size, read_buffer_size allocated per thread.",
                "diagnostics": "SHOW ENGINE INNODB STATUS, information_schema.INNODB_BUFFER_POOL_STATS."
            },
            "oracle": {
                "name": "Oracle 23ai",
                "shared_pool": "SGA (System Global Area): Database Buffer Cache, Shared Pool (SQL library cache), Redo Log Buffer.",
                "private_memory": "PGA (Program Global Area): Private memory per server process (sort areas, hash joins).",
                "diagnostics": "V$SGASTAT, V$PGASTAT, V$BUFFER_POOL_STATISTICS."
            },
            "mssql": {
                "name": "SQL Server 2022",
                "shared_pool": "Buffer Pool with memory clerks allocating 8KB pages for tables and index B-trees.",
                "private_memory": "Memory Grants allocated by Resource Governor for sorting and hash joins.",
                "diagnostics": "sys.dm_os_memory_clerks, sys.dm_os_buffer_descriptors, sys.dm_exec_query_memory_grants."
            },
            "db2": {
                "name": "IBM Db2 11.5",
                "shared_pool": "Multiple Bufferpools assigned per tablespace page size (4KB, 8KB, 16KB, 32KB) and Package Cache.",
                "private_memory": "SORTHEAP and Private Sort Memory managed via Workload Manager (WLM).",
                "diagnostics": "MON_GET_BUFFERPOOL, MON_GET_WORKLOAD_DETAILS."
            },
            "sqlite": {
                "name": "SQLite 3.45",
                "shared_pool": "Process-local in-memory page cache configured via PRAGMA cache_size (default 2MB).",
                "private_memory": "Embedded inside host application memory footprint; no background processes.",
                "diagnostics": "PRAGMA cache_size, PRAGMA page_count, sqlite3_status()."
            }
        }
    },
    {
        "topic": "Concurrency & MVCC Implementation",
        "topic_id": "Konkurensi & Implementasi MVCC",
        "dimension": "concurrency",
        "summary": "How each database isolates transactions, handles snapshot views, and purges superseded row versions.",
        "summary_id": "Bagaimana tiap database mengisolasi transaksi, menyajikan snapshot data, dan membersihkan versi baris usang.",
        "engines": {
            "postgres": {
                "name": "PostgreSQL 17",
                "shared_pool": "Append-only tuple versioning directly inside heap table pages. Requires autovacuum to reclaim dead tuples.",
                "private_memory": "xmin and xmax transaction IDs on every physical row header.",
                "diagnostics": "pg_stat_user_tables (n_dead_tup), pg_locks, pg_stat_activity."
            },
            "mysql": {
                "name": "MariaDB 11.3 (MySQL)",
                "shared_pool": "In-place page update; old row versions are recorded in InnoDB Undo Segments forming a rollback pointer chain.",
                "private_memory": "Purge threads clean undo records once oldest active transaction snapshot finishes.",
                "diagnostics": "INNODB_TRX, INNODB_LOCKS, SHOW ENGINE INNODB STATUS."
            },
            "oracle": {
                "name": "Oracle 23ai",
                "shared_pool": "In-place data modification; historical before-images written to Undo Tablespace extents.",
                "private_memory": "Provides statement-level and transaction-level read consistency without deadlocks on SELECT.",
                "diagnostics": "V$TRANSACTION, V$UNDOSTAT, V$LOCK."
            },
            "mssql": {
                "name": "SQL Server 2022",
                "shared_pool": "Pessimistic locking by default. When RCSI (Read Committed Snapshot) is active, versions go to TempDB or Accelerated Database Recovery (ADR).",
                "private_memory": "Row version store in TempDB or Persistent Version Store (PVS) inside user database.",
                "diagnostics": "sys.dm_tran_version_store, sys.dm_tran_active_transactions."
            },
            "db2": {
                "name": "IBM Db2 11.5",
                "shared_pool": "Currently Committed (CC) semantics return the last committed version directly from transaction log buffers without waiting for lock release.",
                "private_memory": "Strikes balance between lock-based concurrency and undo snapshot space.",
                "diagnostics": "MON_GET_APPL_LOCKWAIT, db2pd -locks."
            },
            "sqlite": {
                "name": "SQLite 3.45",
                "shared_pool": "In WAL mode, readers access unchanged pages while writers append new frames to the .wal file. Readers never block writer.",
                "private_memory": "Single writer lock at any time. Rollback journal mode locks entire database during writes.",
                "diagnostics": "PRAGMA journal_mode = WAL, PRAGMA wal_checkpoint."
            }
        }
    },
    {
        "topic": "High Availability & Failover Models",
        "topic_id": "Ketersediaan Tinggi & Mekanisme Failover",
        "dimension": "ha",
        "summary": "Clustering, log shipping, synchronous replication, and automated failover capabilities.",
        "summary_id": "Model clustering, streaming log transaksi, replikasi sinkron, dan mekanisme failover otomatis.",
        "engines": {
            "postgres": {
                "name": "PostgreSQL 17",
                "shared_pool": "Physical Streaming Replication via WAL with replication slots. Synchronous and asynchronous modes.",
                "private_memory": "Requires Patroni, pg_auto_failover, or Corosync/Pacemaker for automated leader election.",
                "diagnostics": "pg_stat_replication, pg_stat_wal_receiver, pg_replication_slots."
            },
            "mysql": {
                "name": "MariaDB 11.3 (MySQL)",
                "shared_pool": "Binary Log (binlog) replication (row-based/statement). Group Replication & Galera Cluster provide multi-primary quorum.",
                "private_memory": "MySQL InnoDB Cluster with MySQL Router, or Galera wsrep provider.",
                "diagnostics": "SHOW REPLICA STATUS, SHOW STATUS LIKE 'wsrep_%'."
            },
            "oracle": {
                "name": "Oracle 23ai",
                "shared_pool": "Oracle Data Guard (Active Data Guard with Read on Standby) and Oracle RAC (Real Application Clusters shared disk).",
                "private_memory": "Fast-Start Failover (FSFO) with observer process for zero data loss automatic failover.",
                "diagnostics": "V$ARCHIVE_DEST_STATUS, V$DATAGUARD_STATS, dgmgrl."
            },
            "mssql": {
                "name": "SQL Server 2022",
                "shared_pool": "Always On Availability Groups (AG) streaming transaction log blocks to up to 8 secondary replicas.",
                "private_memory": "Windows Server Failover Clustering (WSFC) or Pacemaker on Linux manage cluster quorum.",
                "diagnostics": "sys.dm_hadr_availability_group_states, sys.dm_hadr_database_replica_states."
            },
            "db2": {
                "name": "IBM Db2 11.5",
                "shared_pool": "HADR (High Availability Disaster Recovery) with SYNC, NEARSYNC, ASYNC, SUPERASYNC log modes.",
                "private_memory": "TSA (Tivoli System Automation) or Pacemaker for automated virtual IP failover.",
                "diagnostics": "MON_GET_HADR, db2pd -hadr."
            },
            "sqlite": {
                "name": "SQLite 3.45",
                "shared_pool": "No native network replication. Replicated via third-party extensions like Litestream or rqlite.",
                "private_memory": "Best suited for single-node edge or read-heavy embedded deployments.",
                "diagnostics": "Litestream status, WAL file monitoring."
            }
        }
    }
]

INCIDENT_RUNBOOKS = [
    {
        "slug": "high-cpu-runaway-queries",
        "title": "High CPU Saturation & Query Regression",
        "title_id": "Saturasi CPU Tinggi & Regresi Kueri Berat",
        "severity": "HIGH",
        "category": "Performance Incidents",
        "symptoms": [
            "Server CPU usage exceeds 95% sustained for > 3 minutes",
            "Application response latency spikes from 15ms to > 1500ms",
            "Database connection count climbs towards pool maximum"
        ],
        "first_checks": [
            "Check OS load average and top processes (pidstat, top -c)",
            "Identify top 5 SQL statements currently consuming CPU active time",
            "Verify whether a sudden index drop, stale statistics, or schema change occurred"
        ],
        "diagnostic_commands": [
            {
                "engine": "postgres",
                "risk": "read_only",
                "label": "Inspect Active CPU-Heavy Queries",
                "sql": "SELECT pid, now() - query_start AS duration, query, state FROM pg_stat_activity WHERE state != 'idle' AND query NOT ILIKE '%pg_stat_activity%' ORDER BY duration DESC LIMIT 5;"
            },
            {
                "engine": "mysql",
                "risk": "read_only",
                "label": "List Long-Running Executing Threads",
                "sql": "SELECT id, user, host, db, command, time, state, left(info, 120) AS sql_preview FROM information_schema.processlist WHERE command != 'Sleep' ORDER BY time DESC LIMIT 10;"
            },
            {
                "engine": "oracle",
                "risk": "read_only",
                "label": "Top Active Sessions by CPU Wait",
                "sql": "SELECT sid, serial#, username, status, sql_id, event, seconds_in_wait FROM v$session WHERE status = 'ACTIVE' AND type != 'BACKGROUND' ORDER BY seconds_in_wait DESC FETCH FIRST 10 ROWS ONLY;"
            }
        ],
        "remediation_steps": [
            "If an unintended runaway query is scanning millions of rows without a limit, cancel the individual query (pg_cancel_backend / KILL QUERY).",
            "If execution plan regressed due to stale statistics, run targeted statistics update (ANALYZE / DBMS_STATS.GATHER_TABLE_STATS).",
            "Deploy query kill only as last resort with evidence captured beforehand."
        ],
        "rollback_plan": "Revert recent application deployment if newly introduced code generated unindexed queries."
    },
    {
        "slug": "cascading-lock-blocking",
        "title": "Cascading Lock Contention & Queue Jam",
        "title_id": "Antrean Kunci Bertingkat (Cascading Blocking)",
        "severity": "CRITICAL",
        "symptoms": [
            "Dozens of application threads stuck in 'idle in transaction' or lock wait",
            "HTTP 504 Gateway Timeouts on checkout or payment endpoints",
            "Transactions per second (TPS) drops toward zero"
        ],
        "first_checks": [
            "Identify the root blocker session holding locks at the head of the wait-for tree",
            "Inspect the blocker's current transaction age and last query",
            "Determine if the blocker is active, hanging, or waiting on client socket network I/O"
        ],
        "diagnostic_commands": [
            {
                "engine": "postgres",
                "risk": "read_only",
                "label": "Find Blocker and Blocked PIDs",
                "sql": "SELECT blocked.pid AS blocked_pid, blocking.pid AS blocker_pid, now() - blocked.query_start AS blocked_duration, blocked.query AS waiting_query FROM pg_stat_activity blocked JOIN pg_locks bl ON bl.pid = blocked.pid AND NOT bl.granted JOIN pg_locks kl ON kl.locktype = bl.locktype AND kl.relation = bl.relation AND kl.granted JOIN pg_stat_activity blocking ON blocking.pid = kl.pid WHERE NOT bl.granted;"
            },
            {
                "engine": "oracle",
                "risk": "read_only",
                "label": "Find Blocking Tree in Oracle",
                "sql": "SELECT s1.username || '@' || s1.machine || ' (SID=' || s1.sid || ') is blocking ' || s2.username || '@' || s2.machine || ' (SID=' || s2.sid || ')' AS blocking_status FROM v$lock l1, v$session s1, v$lock l2, v$session s2 WHERE s1.sid = l1.sid AND s2.sid = l2.sid AND l1.BLOCK = 1 AND l2.request > 0 AND l1.id1 = l2.id1 AND l1.id2 = l2.id2;"
            }
        ],
        "remediation_steps": [
            "Attempt to gracefully terminate the root blocker session (SELECT pg_terminate_backend(blocker_pid);).",
            "Confirm whether downstream blocked sessions immediately resolve and drain.",
            "Verify application connection pool timeout configuration (enforce query_timeout and idle_in_transaction_session_timeout)."
        ],
        "rollback_plan": "None applicable; termination is irreversible. Document blocker query and trace in postmortem."
    },
    {
        "slug": "tablespace-capacity-exhaustion",
        "title": "Tablespace & Disk Capacity Full",
        "title_id": "Kapasitas Tablespace & Disk Penuh (100% Saturation)",
        "severity": "CRITICAL",
        "symptoms": [
            "INSERT, UPDATE, and CREATE statements fail with ORA-01653 / SQL0289N / Disk Full",
            "Database switches to read-only mode or panics due to failed WAL/archive log write",
            "Alert monitor triggers > 98% filesystem warning"
        ],
        "first_checks": [
            "Check df -h to determine if OS mount is full or database tablespace limit reached",
            "Inspect archive log destination and temporary tablespace (TempDB / pg_tblspc)",
            "Identify the largest tables and recent partition creation"
        ],
        "diagnostic_commands": [
            {
                "engine": "oracle",
                "risk": "read_only",
                "label": "Inspect Tablespace Free Space",
                "sql": "SELECT tablespace_name, round(used_percent, 2) AS pct_used, round(used_space*8/1024, 2) AS used_mb FROM dba_tablespace_usage_metrics ORDER BY used_percent DESC;"
            },
            {
                "engine": "postgres",
                "risk": "read_only",
                "label": "Top 10 Largest Tables with Indexes",
                "sql": "SELECT relname AS table_name, pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE n.nspname = 'public' AND c.relkind = 'r' ORDER BY pg_total_relation_size(c.oid) DESC LIMIT 10;"
            }
        ],
        "remediation_steps": [
            "Add a new datafile or resize existing datafile with autoextend on (e.g. ALTER TABLESPACE ... ADD DATAFILE).",
            "Clean up unneeded archive logs that have already been backed up.",
            "Truncate temporary staging tables if non-production."
        ],
        "rollback_plan": "Datafile addition cannot be undone easily; verify mount points have sufficient underlying LVM space."
    }
]

VISUAL_LESSONS = [
    {
        "slug": "sql-execution-lifecycle",
        "title": "SQL Query Execution Lifecycle",
        "title_id": "Siklus Hidup Eksekusi Kueri SQL",
        "category": "Internals",
        "estimated_minutes": 5,
        "description_en": "Interactive step-by-step journey of how an SQL string is parsed, planned by the cost-based optimizer, and executed across RAM buffer pools.",
        "description_id": "Visualisasi interaktif tahap demi tahap bagaimana teks SQL diparsing, dioptimasi oleh query planner, dan dieksekusi di RAM buffer pool.",
        "steps": [
            {
                "step": 1,
                "stage": "Client Submission",
                "stage_id": "Pengiriman dari Klien",
                "active_node": "client",
                "text_en": "Client sends raw SQL query text over TLS socket connection to the database listener or backend process.",
                "text_id": "Aplikasi klien mengirim string kueri SQL mentah melalui koneksi socket TCP/TLS ke listener database.",
                "sql_state": "SELECT full_name, balance FROM accounts WHERE balance > 50000000;"
            },
            {
                "step": 2,
                "stage": "Parser & Lexer",
                "stage_id": "Parser & Analisis Leksikal",
                "active_node": "parser",
                "text_en": "Lexer breaks query into tokens. Parser validates SQL grammar and constructs an Abstract Syntax Tree (AST). Syntax errors fail immediately here.",
                "text_id": "Lexer memecah teks menjadi token. Parser memvalidasi tata bahasa SQL dan membentuk Abstract Syntax Tree (AST). Kesalahan sintaks gagal di sini.",
                "sql_state": "AST Tree: [SelectStmt -> TargetList(full_name, balance) -> From(accounts) -> Where(balance > 50M)]"
            },
            {
                "step": 3,
                "stage": "Semantic Analyzer & Catalog",
                "stage_id": "Analisis Semantik & Katalog",
                "active_node": "catalog",
                "text_en": "Validates table and column names against the system catalog (data dictionary). Verifies user authorization and access privileges.",
                "text_id": "Memvalidasi keberadaan nama tabel dan kolom di sistem katalog. Memverifikasi hak akses pengguna (privileges).",
                "sql_state": "Catalog Check: Table 'accounts' [EXISTS], Column 'balance' [TYPE: DECIMAL], Grant [OK]"
            },
            {
                "step": 4,
                "stage": "Cost-Based Optimizer (CBO)",
                "stage_id": "Optimizer Berbasis Biaya (CBO)",
                "active_node": "optimizer",
                "text_en": "Evaluates possible execution paths using column statistics & histograms: Full Table Scan vs Index Scan. Chooses lowest calculated cost plan.",
                "text_id": "Mengevaluasi jalur eksekusi berdasar statistik: Scan Penuh vs Scan Indeks. Memilih rencana dengan estimasi biaya (cost) paling hemat.",
                "sql_state": "Plan Choice: Index Scan on idx_accounts_balance (Cost: 8.24) vs Seq Scan (Cost: 142.00)"
            },
            {
                "step": 5,
                "stage": "Executor & Buffer Pool Cache",
                "stage_id": "Eksekutor & Cache Buffer Pool",
                "active_node": "buffer",
                "text_en": "Executor requests required 8KB pages. If found in RAM Buffer Pool (Cache Hit), loads directly. If Cache Miss, triggers asynchronous disk read.",
                "text_id": "Eksekutor meminta halaman data 8KB. Bila ada di Buffer Pool RAM (Cache Hit), langsung dibaca. Bila belum, dibaca dari disk.",
                "sql_state": "Buffer Hit Ratio: 99.4% (Page #1042 in RAM Buffer Cache)"
            },
            {
                "step": 6,
                "stage": "Result Delivery",
                "stage_id": "Pengembalian Hasil ke Klien",
                "active_node": "result",
                "text_en": "Executor formats qualified rows into wire protocol packets and streams results back to the client application.",
                "text_id": "Eksekutor memformat baris yang cocok ke dalam paket protokol jaringan dan mengirimkannya kembali ke aplikasi klien.",
                "sql_state": "Completed in 1.42ms. 6 rows returned to client socket."
            }
        ]
    },
    {
        "slug": "btree-vs-tablescan",
        "title": "B-Tree Index Lookup vs. Full Table Scan",
        "title_id": "Pencarian Indeks B-Tree vs. Scan Tabel Penuh",
        "category": "Performance",
        "estimated_minutes": 6,
        "description_en": "Interactive visualization demonstrating how B-Tree logarithmic search (O(log N)) compares against sequential I/O page scanning based on selectivity.",
        "description_id": "Visualisasi interaktif membandingkan pencarian logaritmik B-Tree (O(log N)) melawan pembacaan seluruh halaman disk berdasarkan selektivitas.",
        "steps": [
            {
                "step": 1,
                "stage": "Query Predicate",
                "stage_id": "Kondisi Filter Kueri",
                "active_node": "predicate",
                "text_en": "Query filters for customer_id = 4502 out of 100,000 total records in the database.",
                "text_id": "Kueri memfilter customer_id = 4502 dari total 100.000 baris data di dalam database.",
                "sql_state": "SELECT * FROM customers WHERE customer_id = 4502;"
            },
            {
                "step": 2,
                "stage": "Sequential Scan Mode",
                "stage_id": "Mode Scan Berurutan (Tanpa Indeks)",
                "active_node": "seq_scan",
                "text_en": "Without an index, the engine must read every 8KB disk block sequentially from page 1 to page 12,500. Consumes high disk I/O.",
                "text_id": "Tanpa indeks, mesin database wajib membaca tiap blok halaman disk dari awal sampai akhir. Menghabiskan I/O disk tinggi.",
                "sql_state": "Pages Visited: 12,500 | IO Latency: ~180ms"
            },
            {
                "step": 3,
                "stage": "B-Tree Root Node",
                "stage_id": "Node Akar (Root) B-Tree",
                "active_node": "btree_root",
                "text_en": "With a B-Tree index, execution begins at the Root Node. Compares 4502 against branch keys [1000 | 5000 | 10000] and navigates to Branch 1.",
                "text_id": "Dengan indeks B-Tree, pencarian dimulai di Node Root. Membandingkan 4502 dengan kunci cabang dan menuju ke Cabang yang sesuai.",
                "sql_state": "Traversing Root Node -> Follow Pointer [1000 - 5000]"
            },
            {
                "step": 4,
                "stage": "B-Tree Leaf Node & Row Pointer",
                "stage_id": "Node Daun (Leaf) & Pointer Baris",
                "active_node": "btree_leaf",
                "text_en": "Leaf node holds the sorted customer_id and the physical RowID/TID (Page #48, Slot #12). Pinpoints exact record in only 3 page reads.",
                "text_id": "Node daun menampung kunci terurut dan pointer fisik baris (Page #48, Slot #12). Menemukan baris hanya dalam 3 pembacaan halaman.",
                "sql_state": "Pages Visited: 3 | IO Latency: ~0.8ms (225x faster)"
            }
        ]
    },
    {
        "slug": "concurrency-locks-deadlocks",
        "title": "Concurrency, Row Locks & Deadlock Cycle",
        "title_id": "Konkurensi, Kunci Baris & Siklus Deadlock",
        "category": "Concurrency",
        "estimated_minutes": 7,
        "description_en": "Step through two concurrent sessions acquiring conflicting row locks that produce a circular wait-for deadlock graph.",
        "description_id": "Simulasi interaktif dua sesi yang saling berebut lock eksklusif hingga menghasilkan siklus ketergantungan deadlock.",
        "steps": [
            {
                "step": 1,
                "stage": "Session 1 Acquires Lock A",
                "stage_id": "Sesi 1 Mengunci Baris A",
                "active_node": "s1_lock_a",
                "text_en": "Session 1 begins transaction and updates Account #101. Acquires Exclusive Row Lock (X-Lock) on Row A.",
                "text_id": "Sesi 1 memulai transaksi dan mengupdate Akun #101. Memperoleh Exclusive Row Lock pada Baris A.",
                "sql_state": "Session 1: UPDATE accounts SET balance = balance - 100 WHERE id = 101; [LOCK A GRANTED]"
            },
            {
                "step": 2,
                "stage": "Session 2 Acquires Lock B",
                "stage_id": "Sesi 2 Mengunci Baris B",
                "active_node": "s2_lock_b",
                "text_en": "Session 2 begins transaction and updates Account #102. Acquires Exclusive Row Lock on Row B.",
                "text_id": "Sesi 2 memulai transaksi dan mengupdate Akun #102. Memperoleh Exclusive Row Lock pada Baris B.",
                "sql_state": "Session 2: UPDATE accounts SET balance = balance - 50 WHERE id = 102; [LOCK B GRANTED]"
            },
            {
                "step": 3,
                "stage": "Session 1 Requests Lock B (Blocked)",
                "stage_id": "Sesi 1 Meminta Kunci B (Tertahan)",
                "active_node": "s1_waits_b",
                "text_en": "Session 1 attempts to update Account #102. Since Session 2 holds Lock B, Session 1 is placed into WAIT queue.",
                "text_id": "Sesi 1 mencoba mengupdate Akun #102. Karena Sesi 2 memegang Lock B, Sesi 1 tertahan dalam antrean tunggu (BLOCKED).",
                "sql_state": "Session 1: UPDATE accounts SET balance = balance + 100 WHERE id = 102; [WAITING ON LOCK B]"
            },
            {
                "step": 4,
                "stage": "Session 2 Requests Lock A (Deadlock Cycle)",
                "stage_id": "Sesi 2 Meminta Kunci A (Siklus Deadlock)",
                "active_node": "deadlock_detected",
                "text_en": "Session 2 attempts to update Account #101. Creates circular dependency: S1 waits for S2, and S2 waits for S1. Deadlock cycle detected by lock manager.",
                "text_id": "Sesi 2 mencoba mengupdate Akun #101. Terjadi siklus buntu: S1 menunggu S2, dan S2 menunggu S1. Lock manager mendeteksi siklus buntu.",
                "sql_state": "Deadlock Graph: (S1 -> S2 -> S1) Detected!"
            },
            {
                "step": 5,
                "stage": "Victim Rollback & Recovery",
                "stage_id": "Pemilihan Korban (Victim) & Rollback",
                "active_node": "victim_rollback",
                "text_en": "Lock manager terminates Session 2 with SQLSTATE 40P01 / ORA-00060 (Deadlock victim). Session 1 immediately unblocks and completes.",
                "text_id": "Lock manager membatalkan transaksi Sesi 2 (korban). Sesi 1 otomatis terbebas dari antrean dan berhasil commit.",
                "sql_state": "Session 2 aborted with ERROR: deadlock detected. Session 1 unblocked and committed."
            }
        ]
    }
]
