"""
WIYATA Knowledge Center v2 Expanded Data Catalog
Bilingual (en/id) datasets for Glossary, Cross-Database Comparisons,
DBA Field Handbook, Incident Runbooks, 20-Engine Database Encyclopedia,
Troubleshooting Knowledge Base, and Visual Database Academy.
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
        "aliases": ["Row Versioning", "Snapshot Isolation"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "oracle", "mysql", "mssql", "sqlite"],
        "level": "Fundamental",
        "definition_en": "Concurrency control method providing point-in-time snapshots of data so readers never block writers and writers never block readers.",
        "definition_id": "Metode kontrol konkurensi berbasis snapshot waktu sehingga pembacaan data tidak pernah mengunci penulisan, dan sebaliknya.",
        "explanation_en": "In PostgreSQL, updates create new row versions (tuples) with xmin/xmax headers. In Oracle and MySQL InnoDB, updates overwrite data blocks and record previous versions in UNDO segments.",
        "explanation_id": "Pada PostgreSQL, update menyisipkan versi baris baru dengan header xmin/xmax. Pada Oracle dan MySQL, data ditimpa dan versi lama disimpan di segmen UNDO.",
        "field_slang": "Isolasi Multi-Versi Baris Data",
        "diagnostic_query": "SELECT schemaname, relname, n_dead_tup, n_live_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 5;",
        "related_slugs": ["vacuum", "undo", "session-lock"]
    },
    {
        "slug": "awr",
        "term": "Automatic Workload Repository",
        "acronym": "AWR",
        "aliases": ["Oracle AWR", "Workload Snapshot"],
        "category": "Monitoring & Telemetry",
        "category_id": "Monitoring & Telemetri",
        "engines": ["oracle"],
        "level": "Advanced",
        "definition_en": "Built-in Oracle Database repository collecting performance statistics and metrics snapshots every hour for performance triage.",
        "definition_id": "Repositori bawaan Oracle yang mengumpulkan snapshot statistik performa dan metrik tiap jam untuk analisis performa.",
        "explanation_en": "Provides Top 5 Timed Wait Events, SQL ordered by elapsed time, CPU time, and I/O buffer reads between two snapshot IDs.",
        "explanation_id": "Menyajikan Top 5 Wait Events berbobot waktu, kueri SQL terberat berdasarkan elapsed time, CPU, dan pembacaan blok memori.",
        "field_slang": "Laporan Snapshot Performa Oracle",
        "diagnostic_query": "SELECT snap_id, begin_interval_time, end_interval_time FROM dba_hist_snapshot ORDER BY snap_id DESC FETCH FIRST 5 ROWS ONLY;",
        "related_slugs": ["ash", "addm", "wait-event"]
    },
    {
        "slug": "ash",
        "term": "Active Session History",
        "acronym": "ASH",
        "aliases": ["Oracle ASH", "pg_stat_activity sampling"],
        "category": "Monitoring & Telemetry",
        "category_id": "Monitoring & Telemetri",
        "engines": ["oracle", "postgres"],
        "level": "Advanced",
        "definition_en": "High-frequency in-memory sampling (every 1 second) of active non-idle database sessions and their immediate wait events.",
        "definition_id": "Sampling frekuensi tinggi di memori (tiap 1 detik) untuk merekam sesi aktif non-idle beserta wait event spesifiknya.",
        "explanation_en": "Enables minute-by-minute forensic triage of intermittent performance spikes and transient lock contention without running full AWR reports.",
        "explanation_id": "Memungkinkan triage menit-per-menit atas lonjakan latensi kueri mendadak dan kontensi lock tanpa harus membuat laporan AWR lengkap.",
        "field_slang": "Sampling Sesi Real-Time",
        "diagnostic_query": "SELECT sample_time, session_id, event, wait_time FROM v$active_session_history ORDER BY sample_time DESC FETCH FIRST 10 ROWS ONLY;",
        "related_slugs": ["awr", "wait-event", "blocking-session"]
    },
    {
        "slug": "addm",
        "term": "Automatic Database Diagnostic Monitor",
        "acronym": "ADDM",
        "aliases": ["Oracle ADDM Engine"],
        "category": "Monitoring & Telemetry",
        "category_id": "Monitoring & Telemetri",
        "engines": ["oracle"],
        "level": "Advanced",
        "definition_en": "Self-diagnostic engine analyzing AWR snapshots to diagnose performance bottlenecks and provide actionable tuning advice.",
        "definition_id": "Mesin diagnosis mandiri Oracle yang menganalisis snapshot AWR untuk menemukan akar masalah performa dan memberi saran perbaikan.",
        "explanation_en": "Analyzes DB Time consumption, finding root causes such as missing indexes, small SGA buffer cache, CPU starvation, and lock contention.",
        "explanation_id": "Menganalisis penggunaan DB Time, mendeteksi ketiadaan indeks, buffer cache terlalu kecil, atau antrean lock.",
        "field_slang": "Penasihat Diagnostik Otomatis Oracle",
        "diagnostic_query": "SELECT task_name, status, how_created FROM dba_advisor_tasks WHERE advisor_name = 'ADDM' ORDER BY execution_end DESC FETCH FIRST 5 ROWS ONLY;",
        "related_slugs": ["awr", "ash", "execution-plan"]
    },
    {
        "slug": "buffer-pool",
        "term": "Buffer Pool / Buffer Cache",
        "acronym": "BP",
        "aliases": ["InnoDB Buffer Pool", "Shared Buffers", "Database Buffer Cache"],
        "category": "Memory & Cache",
        "category_id": "Memori & Cache",
        "engines": ["postgres", "mysql", "oracle", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "Main-memory cache area where database engine caches disk data pages (typically 8KB - 16KB blocks) for rapid read/write operations.",
        "definition_id": "Area cache memori utama di mana database menyimpan halaman data disk (umumnya 8KB - 16KB) untuk operasi baca/tulis kilat.",
        "explanation_en": "Prevents slow mechanical or NVMe disk I/O. Uses Least Recently Used (LRU) algorithms. Sized at 60-80% of RAM on dedicated MySQL servers, and 25-40% on PostgreSQL (shared_buffers).",
        "explanation_id": "Mencegah pembacaan disk fisik yang lambat. Menggunakan algoritma LRU. Disetel 70-80% RAM di MySQL, dan 25-40% RAM di PostgreSQL.",
        "field_slang": "Cache Memori Data Halaman",
        "diagnostic_query": "SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%s';",
        "related_slugs": ["sga", "checkpoint", "wal"]
    },
    {
        "slug": "tablespace",
        "term": "Tablespace & Storage Containers",
        "acronym": "TBS",
        "aliases": ["Filegroup", "Database Tablespace"],
        "category": "Storage & Architecture",
        "category_id": "Penyimpanan & Arsitektur",
        "engines": ["oracle", "postgres", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "Logical storage boundary uniting one or more physical datafiles to organize table and index segments across disks.",
        "definition_id": "Batas penyimpanan logis yang menyatukan satu atau beberapa file data fisik untuk mengorganisir tabel dan indeks.",
        "explanation_en": "Allows DBAs to place hot transactional tables on fast NVMe SSDs and historical partitions on cheaper bulk storage tiers.",
        "explanation_id": "Memungkinkan DBA menempatkan tabel transaksi bertrafik tinggi pada SSD NVMe cepat dan arsip historis pada storage ekonomis.",
        "field_slang": "Wadah Ruang Penyimpanan Database",
        "diagnostic_query": "SELECT tablespace_name, status FROM user_tablespaces;",
        "related_slugs": ["datafile", "tablespace-full"]
    },
    {
        "slug": "datafile",
        "term": "Physical Datafile & Extents",
        "acronym": "DBF",
        "aliases": ["Data File", ".dbf", ".mdf", ".ndf"],
        "category": "Storage & Architecture",
        "category_id": "Penyimpanan & Arsitektur",
        "engines": ["oracle", "sqlserver", "db2"],
        "level": "Intermediate",
        "definition_en": "OS physical filesystem file containing database extents, pages, and allocated schema object segments.",
        "definition_id": "File fisik pada filesystem OS yang menampung extent, halaman, dan segmen objek skema database.",
        "explanation_en": "Can be configured as fixed size or autoextensible up to an operating system or filesystem max size limit (e.g. 32GB per datafile in standard 8KB block Oracle smallfile tablespaces).",
        "explanation_id": "Dapat berukuran tetap atau autoextend hingga batas filesystem (misal 32GB per datafile pada Oracle smallfile).",
        "field_slang": "File Fisik Penyimpan Data di Disk",
        "diagnostic_query": "SELECT file_name, bytes/1024/1024 AS mb, autoextensible FROM dba_data_files;",
        "related_slugs": ["tablespace", "tablespace-full"]
    },
    {
        "slug": "redo-log",
        "term": "Redo Log / Transaction Log",
        "acronym": "REDO",
        "aliases": ["ib_logfile", "ldf file", "pg_wal"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["oracle", "mysql", "sqlserver", "db2", "postgres"],
        "level": "Fundamental",
        "definition_en": "Circular or sequential log recording all schema and data changes made to database blocks to support instance crash recovery.",
        "definition_id": "File log berurutan yang mencatat seluruh mutasi data dan skema untuk menjamin pemulihan instan saat server crash.",
        "explanation_en": "When an instance crashes unexpectedly, the recovery engine rolls forward redo logs to reinstate all committed transactions.",
        "explanation_id": "Saat server crash atau mati mendadak, engine me-roll forward redo log untuk memulihkan transaksi yang telah di-commit.",
        "field_slang": "Catatan Redo Pemulihan Crash",
        "diagnostic_query": "SELECT group#, sequence#, bytes/1024/1024 AS mb, status FROM v$log;",
        "related_slugs": ["wal", "undo", "checkpoint"]
    },
    {
        "slug": "undo",
        "term": "Undo Segment / Rollback Segment",
        "acronym": "UNDO",
        "aliases": ["Rollback Segment", "InnoDB Undo Tablespace"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["oracle", "mysql"],
        "level": "Intermediate",
        "definition_en": "Storage structures recording previous images of data blocks modified by active transactions.",
        "definition_id": "Struktur penyimpanan yang merekam data sebelum dimodifikasi oleh transaksi yang sedang berjalan.",
        "explanation_en": "Supports transaction ROLLBACK commands, provides Read Consistency for concurrent SELECT queries (MVCC), and crash recovery rollbacks.",
        "explanation_id": "Mendukung perintah pembatalan ROLLBACK, konsistensi pembacaan (Read Consistency) kueri lain, dan pembersihan rollback.",
        "field_slang": "Segmen Pembatalan & Versi Lama",
        "diagnostic_query": "SELECT tablespace_name, status, sum(bytes)/1024/1024 AS mb FROM dba_undo_extents GROUP BY tablespace_name, status;",
        "related_slugs": ["mvcc", "redo-log"]
    },
    {
        "slug": "lsn",
        "term": "Log Sequence Number",
        "acronym": "LSN",
        "aliases": ["PostgreSQL LSN", "SQL Server LSN"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "sqlserver", "db2"],
        "level": "Intermediate",
        "definition_en": "64-bit monotonically increasing integer representing the exact byte offset of a record in the transaction write-ahead log.",
        "definition_id": "Nilai integer 64-bit yang bertambah secara monotonik, merepresentasikan posisi offset byte pasti dalam log transaksi.",
        "explanation_en": "Used to verify streaming replication synchronization, determine page update freshness in buffer caches, and enforce WAL ordering.",
        "explanation_id": "Digunakan untuk mengukur sinkronisasi replikasi streaming dan membandingkan usia modifikasi halaman data di cache.",
        "field_slang": "Nomor Urut Posisi WAL",
        "diagnostic_query": "SELECT pg_current_wal_lsn(), pg_walfile_name(pg_current_wal_lsn());",
        "related_slugs": ["wal", "pitr"]
    },
    {
        "slug": "rac",
        "term": "Real Application Clusters",
        "acronym": "RAC",
        "aliases": ["Oracle RAC", "Cache Fusion"],
        "category": "High Availability & Clustering",
        "category_id": "Ketersediaan Tinggi & Replikasi",
        "engines": ["oracle"],
        "level": "Advanced",
        "definition_en": "Shared-everything active-active database clustering technology allowing multiple server instances to share a single shared storage.",
        "definition_id": "Teknologi cluster database aktif-aktif di mana beberapa instance server mengakses satu penyimpanan bersama (shared storage).",
        "explanation_en": "Employs Cache Fusion interconnect technology to transfer data blocks directly across server memory via high-speed InfiniBand network.",
        "explanation_id": "Menggunakan teknologi Cache Fusion untuk mentransfer blok data langsung antar RAM server melalui jaringan privat berkecepatan tinggi.",
        "field_slang": "Cluster Multi-Node Aktif-Aktif Oracle",
        "diagnostic_query": "SELECT inst_id, instance_name, status FROM gv$instance;",
        "related_slugs": ["asm", "hadr", "failover"]
    },
    {
        "slug": "asm",
        "term": "Automatic Storage Management",
        "acronym": "ASM",
        "aliases": ["Oracle ASM Disk Groups"],
        "category": "Storage & Architecture",
        "category_id": "Penyimpanan & Arsitektur",
        "engines": ["oracle"],
        "level": "Advanced",
        "definition_en": "Integrated volume manager and filesystem specifically optimized for Oracle Database datafiles and disk groups.",
        "definition_id": "Volume manager dan filesystem terintegrasi khusus untuk mendistribusikan file Oracle secara merata ke seluruh disk fisik.",
        "explanation_en": "Provides automatic stripe and mirror rebalancing across disks with zero database downtime when drives are added or removed.",
        "explanation_id": "Menyediakan fitur striping dan mirroring otomatis dengan kemampuan rebalance tanpa mematikan database saat menambah disk.",
        "field_slang": "Manajer Volume Disk Oracle Otomatis",
        "diagnostic_query": "SELECT name, total_mb, free_mb, state FROM v$asm_diskgroup;",
        "related_slugs": ["rac", "tablespace"]
    },
    {
        "slug": "blocking-session",
        "term": "Blocking Session / Wait Chain",
        "acronym": "BLOCK",
        "aliases": ["Lead Blocker", "Lock Wait"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "mysql", "oracle", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "Scenario where a database session holds an exclusive lock on a table or row, forcing other concurrent sessions into an idle wait queue.",
        "definition_id": "Situasi di mana suatu sesi menahan lock eksklusif pada tabel atau baris data, memaksa sesi lain mengantre dan tidak dapat berjalan.",
        "explanation_en": "Common root causes include uncommitted manual transactions (DML without COMMIT), batch updates locking large row sets, and missing foreign key indexes.",
        "explanation_id": "Penyebab umum meliputi transaksi manual yang lupa di-commit, update massal ribuan baris, atau ketiadaan indeks pada foreign key.",
        "field_slang": "Session Nge-Lock / Sesi Nyangkut",
        "diagnostic_query": "SELECT pid, usename, wait_event_type, wait_event, query FROM pg_stat_activity WHERE wait_event_type = 'Lock';",
        "related_slugs": ["deadlock", "mvcc"]
    },
    {
        "slug": "deadlock",
        "term": "Deadlock & Cycle Detection",
        "acronym": "DLOCK",
        "aliases": ["Deadlock Graph", "Deadlock Victim"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "mysql", "oracle", "sqlserver", "db2"],
        "level": "Intermediate",
        "definition_en": "Condition where two or more transactions hold locks on resources and each waits for the resource held by the other, forming a circular dependency.",
        "definition_id": "Kondisi jalan buntu di mana dua transaksi saling menunggu pelepasan lock yang dipegang pihak lain dalam siklus melingkar.",
        "explanation_en": "Database lock managers continuously evaluate wait-for graphs. When a cycle is detected, the engine aborts and rolls back one transaction (the victim) to resolve the freeze.",
        "explanation_id": "Lock manager otomatis mendeteksi siklus buntu dan mengorbankan salah satu transaksi (victim rollback) agar sistem tidak beku.",
        "field_slang": "Siklus Kunci Buntu / Deadlock",
        "diagnostic_query": "SELECT * FROM sys.dm_os_waiting_tasks WHERE blocking_session_id IS NOT NULL;",
        "related_slugs": ["blocking-session", "session-lock"]
    },
    {
        "slug": "session-lock",
        "term": "Session Lock Contention",
        "acronym": "LOCK",
        "aliases": ["Exclusive Lock", "Shared Lock", "Table Lock"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "mysql", "oracle", "sqlserver", "db2"],
        "level": "Intermediate",
        "definition_en": "State where a database transaction locks a row or table resource to maintain ACID Isolation, causing other queries to queue.",
        "definition_id": "Kondisi saat transaksi menahan izin akses eksklusif pada baris atau tabel data untuk menjaga isolasi ACID.",
        "explanation_en": "Uncommitted transactions holding locks cause cascading queues in production web apps, exhausting server connection pools.",
        "explanation_id": "Transaksi menggantung yang tidak di-commit menyebabkan antrean kueri menumpuk hingga menghabiskan connection pool aplikasi.",
        "field_slang": "Sesi Nge-Lock / Blocking",
        "diagnostic_query": "SELECT blocked_locks.pid AS blocked_pid, blocking_locks.pid AS blocking_pid FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype WHERE NOT blocked_locks.granted;",
        "related_slugs": ["deadlock", "blocking-session"]
    },
    {
        "slug": "tablespace-full",
        "term": "Tablespace Full Outage",
        "acronym": "TBS-FULL",
        "aliases": ["Disk Full Outage", "ORA-01653", "Space Exhaustion"],
        "category": "Storage & Architecture",
        "category_id": "Penyimpanan & Arsitektur",
        "engines": ["oracle", "db2", "sqlserver", "postgres"],
        "level": "Fundamental",
        "definition_en": "Outage condition where a tablespace exhausts all allocated datafiles and filesystem storage, rejecting all incoming INSERT and UPDATE statements.",
        "definition_id": "Insiden di mana ruang penyimpanan tablespace habis total, menolak semua operasi INSERT dan UPDATE dari aplikasi.",
        "explanation_en": "Requires immediate DBA intervention: adding a new datafile, enabling AUTOEXTEND, or purging archival tables to restore availability.",
        "explanation_id": "Memerlukan intervensi kilat DBA: menambah datafile baru, mengaktifkan autoextend, atau menghapus data arsip.",
        "field_slang": "Tablespace Penuh / Disk Mentok",
        "diagnostic_query": "SELECT tablespace_name, round(used_percent, 2) AS used_pct FROM dba_tablespace_usage_metrics WHERE used_percent > 85;",
        "related_slugs": ["tablespace", "datafile"]
    },
    {
        "slug": "pitr",
        "term": "Point-in-Time Recovery",
        "acronym": "PITR",
        "aliases": ["Database Rollforward", "Flashback Database"],
        "category": "Backup & Disaster Recovery",
        "category_id": "Cadangan & Pemulihan Bencana",
        "engines": ["postgres", "oracle", "mysql", "sqlserver", "db2"],
        "level": "Advanced",
        "definition_en": "Disaster recovery method allowing a database to be restored to any exact second or transaction ID prior to an accidental corruption or DROP TABLE.",
        "definition_id": "Metode pemulihan bencana yang memungkinkan database dikembalikan ke detik atau LSN tertentu sebelum terjadinya insiden korupsi data.",
        "explanation_en": "Combines a base physical backup with continuous archived WAL/redo logs replayed sequentially up to the target timestamp.",
        "explanation_id": "Menggabungkan backup fisik dasar dengan pemutaran berurutan file arsip WAL hingga tepat sebelum waktu insiden.",
        "field_slang": "Restore Database ke Detik Spesifik",
        "diagnostic_query": "SELECT pg_wal_replay_pause(), pg_is_wal_replay_paused();",
        "related_slugs": ["wal", "rpo-rto", "redo-log"]
    },
    {
        "slug": "hadr",
        "term": "High Availability Disaster Recovery",
        "acronym": "HADR",
        "aliases": ["IBM HADR", "AlwaysOn AG", "Data Guard"],
        "category": "High Availability & Clustering",
        "category_id": "Ketersediaan Tinggi & Replikasi",
        "engines": ["db2", "sqlserver", "oracle", "postgres"],
        "level": "Advanced",
        "definition_en": "Database replication and failover architecture maintaining one or more synchronized standby databases ready to take over primary operations.",
        "definition_id": "Arsitektur replikasi dan failover database yang memelihara standby server tersinkronisasi untuk mengambil alih tugas server primary.",
        "explanation_en": "Supports synchronous replication (zero data loss, RPO=0) or asynchronous replication (low network latency impact) across datacenters.",
        "explanation_id": "Mendukung sinkronisasi murni (RPO=0) maupun asinkronus (tahan latensi jaringan jarak jauh) lintas pusat data.",
        "field_slang": "Cluster Failover Standby Otomatis",
        "diagnostic_query": "SELECT hadr_role, hadr_state, hadr_syncmode FROM TABLE(MON_GET_HADR(NULL));",
        "related_slugs": ["failover", "switchover", "rpo-rto"]
    },
    {
        "slug": "rpo-rto",
        "term": "RPO & RTO Objectives",
        "acronym": "RPO/RTO",
        "aliases": ["Recovery Objectives", "SLA Metrics"],
        "category": "Backup & Disaster Recovery",
        "category_id": "Cadangan & Pemulihan Bencana",
        "engines": ["universal", "postgres", "oracle", "mysql", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "The two foundational metrics governing database disaster recovery SLAs: Recovery Point Objective (data loss) and Recovery Time Objective (downtime).",
        "definition_id": "Dua metrik fundamental penentu SLA pemulihan bencana: RPO (toleransi kehilangan data) dan RTO (kecepatan sistem kembali online).",
        "explanation_en": "RPO measures maximum acceptable data loss in seconds/hours. RTO measures maximum allowable downtime before business operations resume.",
        "explanation_id": "RPO mengukur batas toleransi data hilang dalam durasi waktu. RTO mengukur durasi maksimal server boleh mati sebelum harus online.",
        "field_slang": "Target Maksimal Data Hilang & Downtime",
        "diagnostic_query": "SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag_seconds;",
        "related_slugs": ["pitr", "hadr", "failover"]
    },
    {
        "slug": "cardinality",
        "term": "Cardinality Estimation",
        "acronym": "CARD",
        "aliases": ["Row Count Estimate", "Optimizer Cardinality"],
        "category": "Performance & Optimizer",
        "category_id": "Performa & Pengoptimal",
        "engines": ["postgres", "oracle", "sqlserver", "mysql", "db2"],
        "level": "Intermediate",
        "definition_en": "The query optimizer's estimation of the number of rows that will be returned by a query operator or predicate.",
        "definition_id": "Perkiraan jumlah baris data yang akan dihasilkan oleh suatu operator atau filter query yang dihitung oleh optimizer.",
        "explanation_en": "Bad cardinality estimates (e.g. optimizer expects 1 row but receives 1,000,000 rows) cause catastrophic join algorithm choices (Nested Loop instead of Hash Join).",
        "explanation_id": "Estimasi kardinalitas yang meleset menyebabkan optimizer salah memilih strategi join (memilih Nested Loop alih-alih Hash Join).",
        "field_slang": "Estimasi Jumlah Baris Optimizer",
        "diagnostic_query": "EXPLAIN ANALYZE SELECT * FROM customers WHERE city = 'Jakarta';",
        "related_slugs": ["selectivity", "execution-plan"]
    },
    {
        "slug": "selectivity",
        "term": "Predicate Selectivity",
        "acronym": "SEL",
        "aliases": ["Filter Selectivity", "Index Density"],
        "category": "Performance & Optimizer",
        "category_id": "Performa & Pengoptimal",
        "engines": ["postgres", "oracle", "sqlserver", "mysql", "db2"],
        "level": "Intermediate",
        "definition_en": "Ratio of rows matching a query predicate relative to total rows in the table (ranging from 0.0 to 1.0).",
        "definition_id": "Rasio baris data yang lolos filter dibandingkan total baris tabel (antara 0.0 sampai 1.0).",
        "explanation_en": "High selectivity (matching < 5% of rows) makes B-Tree index lookup optimal. Low selectivity (matching > 20% of rows) favors a sequential table scan.",
        "explanation_id": "Selektivitas tinggi (< 5% baris) menjadikan pencarian indeks B-Tree efisien. Selektivitas rendah (> 20%) lebih efisien dibaca dengan full table scan.",
        "field_slang": "Tingkat Ketajaman Saringan Filter",
        "diagnostic_query": "SELECT attname, n_distinct, correlation FROM pg_stats WHERE tablename = 'orders';",
        "related_slugs": ["cardinality", "execution-plan"]
    },
    {
        "slug": "vacuum",
        "term": "VACUUM & Autovacuum Maintenance",
        "acronym": "VAC",
        "aliases": ["PostgreSQL VACUUM", "Space Reclamation"],
        "category": "Storage & Architecture",
        "category_id": "Penyimpanan & Arsitektur",
        "engines": ["postgres"],
        "level": "Fundamental",
        "definition_en": "Essential PostgreSQL engine maintenance process that marks dead row versions (tuples) as reusable space and freezes transaction IDs.",
        "definition_id": "Proses pemeliharaan esensial PostgreSQL untuk menandai baris mati (dead tuple) agar ruangnya bisa dipakai kembali serta membekukan Transaction ID.",
        "explanation_en": "Without autovacuum, tables suffer severe bloat, sequential scans degrade, and the instance risks transaction ID wraparound shutdown.",
        "explanation_id": "Tanpa autovacuum, tabel akan membengkak parah (bloat) dan database terancam mati mendadak akibat transaction ID wraparound.",
        "field_slang": "Pembersihan Sampah Data PostgreSQL",
        "diagnostic_query": "SELECT relname, last_vacuum, last_autovacuum, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 5;",
        "related_slugs": ["mvcc", "index-bloat"]
    },
    {
        "slug": "checkpoint",
        "term": "Checkpoint & Buffer Flushing",
        "acronym": "CHKPT",
        "aliases": ["Dirty Buffer Flush", "Database Checkpoint"],
        "category": "Transactions & Concurrency",
        "category_id": "Transaksi & Konkurensi",
        "engines": ["postgres", "mysql", "oracle", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "Synchronization event where all modified dirty pages cached in memory are flushed and written safely to physical disk.",
        "definition_id": "Peristiwa sinkronisasi di mana seluruh halaman data yang dimodifikasi di memori di-flush dan ditulis aman ke disk fisik.",
        "explanation_en": "Advances the recovery point: during crash recovery, only WAL/redo records generated after the last checkpoint need to be replayed.",
        "explanation_id": "Memajukan titik pemulihan: saat server crash, hanya log setelah checkpoint terakhir yang perlu di-replay.",
        "field_slang": "Titik Sinkronisasi Memori ke Disk",
        "diagnostic_query": "SELECT checkpoints_timed, checkpoints_req, checkpoint_write_time FROM pg_stat_bgwriter;",
        "related_slugs": ["wal", "buffer-pool", "redo-log"]
    },
    {
        "slug": "connection-pool",
        "term": "Database Connection Pooling",
        "acronym": "POOL",
        "aliases": ["PgBouncer", "HikariCP", "ProxySQL"],
        "category": "Performance & Architecture",
        "category_id": "Performa & Arsitektur",
        "engines": ["postgres", "mysql", "oracle", "sqlserver"],
        "level": "Fundamental",
        "definition_en": "Cache of pre-established database physical connections maintained so connections can be reused across incoming HTTP requests.",
        "definition_id": "Cache koneksi database yang sudah terbentuk sebelumnya agar dapat dipakai berulang kali tanpa beban handshake koneksi baru.",
        "explanation_en": "Prevents database backend process exhaustion, avoids fork() overhead, and protects servers from connection spikes.",
        "explanation_id": "Mencegah ledakan proses backend, menghilangkan beban fork(), dan melindungi database dari lonjakan trafik tiba-tiba.",
        "field_slang": "Kolam Penggunaan Bersama Koneksi",
        "diagnostic_query": "SELECT count(*), state FROM pg_stat_activity GROUP BY state;",
        "related_slugs": ["session-lock", "blocking-session"]
    },
    {
        "slug": "failover",
        "term": "Failover (Unplanned Disaster Recovery)",
        "acronym": "FAILOVER",
        "aliases": ["Primary Failover", "Emergency Takeover"],
        "category": "High Availability & Clustering",
        "category_id": "Ketersediaan Tinggi & Replikasi",
        "engines": ["postgres", "oracle", "mysql", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "Automatic or emergency manual process of promoting a standby replica to become the primary active database after a primary node crash.",
        "definition_id": "Proses otomatis atau darurat untuk mempromosikan standby replica menjadi server utama (primary) saat server utama mati.",
        "explanation_en": "Carried out automatically by clustering orchestrators (Patroni, Data Guard Fast-Start Failover, Always On WSFC, Galera).",
        "explanation_id": "Dijalankan secara otomatis oleh orkestrator cluster (Patroni, Data Guard FSFO, Always On, Galera).",
        "field_slang": "Pengalihan Darurat ke Server Cadangan",
        "diagnostic_query": "SELECT pg_is_in_recovery();",
        "related_slugs": ["switchover", "hadr", "rpo-rto"]
    },
    {
        "slug": "switchover",
        "term": "Switchover (Planned Role Transition)",
        "acronym": "SWITCHOVER",
        "aliases": ["Graceful Role Swap", "Maintenance Switch"],
        "category": "High Availability & Clustering",
        "category_id": "Ketersediaan Tinggi & Replikasi",
        "engines": ["postgres", "oracle", "mysql", "sqlserver", "db2"],
        "level": "Fundamental",
        "definition_en": "Planned zero-loss operational role reversal between a primary database and standby replica for server maintenance or OS upgrades.",
        "definition_id": "Pertukaran peran terencana tanpa kehilangan data (zero-loss) antara server utama dan replika untuk pemeliharaan hardware/OS.",
        "explanation_en": "Unlike emergency failovers, a switchover guarantees zero data loss (RPO=0) because all pending logs are fully applied before roles flip.",
        "explanation_id": "Berbeda dengan failover darurat, switchover menjamin nol data hilang (RPO=0) karena seluruh log disinkronkan tuntas sebelum peran ditukar.",
        "field_slang": "Tukar Peran Server Terencana",
        "diagnostic_query": "SELECT database_role FROM v$database;",
        "related_slugs": ["failover", "hadr"]
    }
]

CROSS_COMPARISONS = [
    {
        "topic": "Memory Architecture & Caching",
        "topic_id": "Arsitektur Memori & Mekanisme Cache",
        "dimension": "Memory Management",
        "summary": "Comparison of global shared caching areas, process-private work memory, and page eviction algorithms across 6 enterprise engines.",
        "summary_id": "Perbandingan alokasi cache global, memori kerja privat sesi, dan algoritma pembebasan blok memori di 6 mesin database.",
        "engines": {
            "postgres": {
                "name": "PostgreSQL 17",
                "shared_pool": "shared_buffers (typical: 25-40% of RAM; relies heavily on OS kernel page cache)",
                "private_memory": "work_mem (per sort/hash operation per query) + maintenance_work_mem",
                "diagnostics": "pg_buffercache extension, pg_stat_database (blks_hit vs blks_read)"
            },
            "mysql": {
                "name": "MariaDB 11.3 / MySQL 8.4",
                "shared_pool": "innodb_buffer_pool_size (typical: 70-80% of dedicated RAM, divided into instances)",
                "private_memory": "sort_buffer_size, join_buffer_size, read_rnd_buffer_size",
                "diagnostics": "SHOW ENGINE INNODB STATUS, information_schema.innodb_buffer_pool_stats"
            },
            "oracle": {
                "name": "Oracle 23ai",
                "shared_pool": "SGA (System Global Area): Database Buffer Cache, Shared Pool, Large Pool, Redo Buffer",
                "private_memory": "PGA (Program Global Area): sort work area, hash area, private SQL areas",
                "diagnostics": "V$SGASTAT, V$PGASTAT, V$BUFFER_POOL_STATISTICS, AWR Memory Advisory"
            },
            "mssql": {
                "name": "SQL Server 2022",
                "shared_pool": "Buffer Pool: caches 8KB data/index pages; dynamic memory governed by max server memory",
                "private_memory": "Workspace memory grants for sorting and hash joins",
                "diagnostics": "sys.dm_os_buffer_descriptors, sys.dm_os_memory_clerks, sys.dm_os_wait_stats"
            },
            "db2": {
                "name": "IBM Db2 11.5",
                "shared_pool": "Database Bufferpools (custom page sizes: 4K, 8K, 16K, 32K) + Package Cache",
                "private_memory": "Sortheap, sheapthres_shr (shared sort memory threshold)",
                "diagnostics": "MON_GET_BUFFERPOOL, db2pd -mempool, db2pd -bufferpools"
            },
            "sqlite": {
                "name": "SQLite 3.45",
                "shared_pool": "Process-local page cache governed by PRAGMA cache_size (default: -2000 KiB)",
                "private_memory": "Embedded within application host process heap; no inter-process shared memory",
                "diagnostics": "PRAGMA cache_size, PRAGMA page_count, PRAGMA freelist_count"
            }
        }
    },
    {
        "topic": "Concurrency Control & MVCC Mechanism",
        "topic_id": "Kontrol Konkurensi & Mekanisme MVCC",
        "dimension": "Transactions & Locking",
        "summary": "How each engine enforces ACID Isolation, generates row versions, and reclaims dead tuples or undo blocks.",
        "summary_id": "Cara tiap mesin menerapkan Isolasi ACID, menghasilkan versi baris data, dan membersihkan dead tuple atau blok undo.",
        "engines": {
            "postgres": {
                "name": "PostgreSQL 17",
                "shared_pool": "In-place page versioning: updates insert new tuples with xmin/xmax markers; requires VACUUM to reclaim space",
                "private_memory": "Lock Manager shared memory table; row locks recorded directly in tuple Infomask bits",
                "diagnostics": "pg_locks, pg_stat_user_tables (n_dead_tup), txid_current_snapshot()"
            },
            "mysql": {
                "name": "MariaDB 11.3 / MySQL 8.4",
                "shared_pool": "Rollback segments in Undo Tablespace; updates overwrite data block and record previous state in undo log",
                "private_memory": "Record locks, Gap locks, and Next-Key locks in InnoDB lock table",
                "diagnostics": "performance_schema.data_locks, performance_schema.data_lock_waits"
            },
            "oracle": {
                "name": "Oracle 23ai",
                "shared_pool": "Undo Tablespace rollback: readers reconstruct historical block images from undo segments (CR blocks)",
                "private_memory": "Enqueue lock manager; TX (Transaction) locks and TM (DML) table locks",
                "diagnostics": "V$LOCK, V$LOCKED_OBJECT, V$TRANSACTION, V$UNDOSTAT"
            },
            "mssql": {
                "name": "SQL Server 2022",
                "shared_pool": "Pessimistic 2PL locking by default; Read Committed Snapshot Isolation (RCSI) stores row versions in TempDB",
                "private_memory": "Lock manager tracks database, table, page, key, and extent locks in memory",
                "diagnostics": "sys.dm_tran_locks, sys.dm_os_waiting_tasks, sys.dm_tran_version_store"
            },
            "db2": {
                "name": "IBM Db2 11.5",
                "shared_pool": "Currently Committed semantics: readers read last committed data image without waiting for uncommitted locks",
                "private_memory": "Locklist shared memory; automatically escalates row locks to table locks if locklist fills",
                "diagnostics": "MON_GET_LOCKS, db2pd -locks, db2pd -wlocks, DIA8300E lock escalation events"
            },
            "sqlite": {
                "name": "SQLite 3.45",
                "shared_pool": "WAL Mode (Write-Ahead Log): readers read committed snapshot while single writer appends to -wal file",
                "private_memory": "File-level locking (SHARED, RESERVED, PENDING, EXCLUSIVE) via OS fcntl / LockFileEx",
                "diagnostics": "PRAGMA journal_mode=WAL, PRAGMA wal_checkpoint(PASSIVE)"
            }
        }
    },
    {
        "topic": "High Availability & Clustering Architecture",
        "topic_id": "Arsitektur Ketersediaan Tinggi (HA) & Clustering",
        "dimension": "High Availability",
        "summary": "Clustering models, consensus orchestration, replication transports, and automated failover mechanics across engines.",
        "summary_id": "Model klaster, orkestrasi konsensus, protokol replikasi, dan mekanisme failover otomatis lintas mesin.",
        "engines": {
            "postgres": {
                "name": "PostgreSQL 17",
                "shared_pool": "Physical Streaming Replication (Sync/Async) via walsender/walreceiver; orchestrated via Patroni with etcd/Raft",
                "private_memory": "Hot Standby read queries; replication slots prevent WAL recycling before standby consumption",
                "diagnostics": "pg_stat_replication, pg_stat_wal_receiver, pg_replication_slots"
            },
            "mysql": {
                "name": "MariaDB 11.3 / MySQL 8.4",
                "shared_pool": "GTID-based replication, Galera Cluster multi-master (MariaDB), or MySQL Group Replication / InnoDB Cluster",
                "private_memory": "Relay log receiver thread and applier SQL worker threads",
                "diagnostics": "SHOW REPLICA STATUS, performance_schema.replication_applier_status"
            },
            "oracle": {
                "name": "Oracle 23ai",
                "shared_pool": "Oracle Data Guard (Physical/Logical Standby) with Fast-Start Failover (FSFO); Oracle RAC active-active clustering",
                "private_memory": "Data Guard Broker, Log Writer (LGWR) Network Server (NSS)",
                "diagnostics": "V$ARCHIVE_DEST_STATUS, V$DATAGUARD_STATS, dgmgrl CLI status"
            },
            "mssql": {
                "name": "SQL Server 2022",
                "shared_pool": "Always On Availability Groups (Synchronous/Asynchronous Commit) with Windows Server Failover Cluster (WSFC)",
                "private_memory": "Log capture and log redo queue workers on secondary replicas",
                "diagnostics": "sys.dm_hadr_availability_replica_states, sys.dm_hadr_database_replica_states"
            },
            "db2": {
                "name": "IBM Db2 11.5",
                "shared_pool": "High Availability Disaster Recovery (HADR) with TSA / Pacemaker automated takeover; pureScale active-active",
                "private_memory": "HADR log shipping engine with SYNC, NEARSYNC, ASYNC, SUPERASYNC modes",
                "diagnostics": "TABLE(MON_GET_HADR(NULL)), db2pd -hadr, db2 TAKEOVER HADR"
            },
            "sqlite": {
                "name": "SQLite 3.45",
                "shared_pool": "Single-node embedded; replicated distributed extensions exist via Litestream / LiteFS (FUSE-based Raft)",
                "private_memory": "Local process handle; no native distributed cluster transport built-in",
                "diagnostics": "PRAGMA integrity_check, Litestream replication status daemon"
            }
        }
    }
]

INCIDENT_RUNBOOKS = [
    {
        "slug": "high-cpu-runaway-queries",
        "title": "High CPU Saturation & Query Regression",
        "title_id": "Saturasi CPU Ekstrem & Regresi Kueri",
        "severity": "CRITICAL",
        "category": "Performance Degradation",
        "symptoms": [
            "Server CPU utilization sustained at > 95% across all cores",
            "Application HTTP response latency degrades from < 50ms to > 5000ms",
            "Connection pool exhaustion as query processing queues expand"
        ],
        "first_checks": [
            "Run top / htop to verify if CPU time is in user space (database queries) or system/kernel (paging/context switching)",
            "Check active database session count: SELECT count(*) FROM pg_stat_activity WHERE state = 'active'",
            "Identify top 3 CPU consuming queries executing longer than 30 seconds"
        ],
        "diagnostic_commands": [
            {
                "engine": "PostgreSQL",
                "risk": "read_only",
                "label": "Top Running Long Queries",
                "sql": "SELECT pid, now() - query_start AS duration, usename, query FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '10 seconds' ORDER BY duration DESC LIMIT 5;"
            },
            {
                "engine": "Oracle",
                "risk": "read_only",
                "label": "Top Active Sessions by CPU Time",
                "sql": "SELECT s.sid, s.serial#, s.username, s.status, q.sql_text FROM v$session s JOIN v$sql q ON s.sql_id = q.sql_id WHERE s.status = 'ACTIVE' ORDER BY s.last_call_et DESC FETCH FIRST 5 ROWS ONLY;"
            },
            {
                "engine": "MySQL",
                "risk": "read_only",
                "label": "Slow Running Processlist",
                "sql": "SELECT id, user, host, db, command, time, state, info FROM information_schema.processlist WHERE command != 'Sleep' AND time > 10 ORDER BY time DESC LIMIT 5;"
            },
            {
                "engine": "SQL Server",
                "risk": "read_only",
                "label": "Top Active CPU Demanding Requests",
                "sql": "SELECT r.session_id, r.cpu_time, r.total_elapsed_time, t.text FROM sys.dm_exec_requests r CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t ORDER BY r.cpu_time DESC;"
            }
        ],
        "remediation_steps": [
            "Terminate rogue runaway analytical query or un-indexed loop with graceful statement cancel: SELECT pg_cancel_backend(pid)",
            "If query refuses to cancel, terminate backend connection: SELECT pg_terminate_backend(pid)",
            "Inject query plan baseline or create missing composite index in production"
        ],
        "rollback_plan": "If terminating the session causes an uncommitted transaction rollback storm, monitor server I/O and wait for rollback completion."
    },
    {
        "slug": "cascading-lock-blocking",
        "title": "Cascading Lock Contention & Deadlocks",
        "title_id": "Kontensi Kunci Beruntun & Deadlock Sesi",
        "severity": "CRITICAL",
        "category": "Concurrency & Locking",
        "symptoms": [
            "Connection pool count spikes rapidly toward max_connections",
            "Dozens of application threads enter waiting status with zero CPU activity",
            "Database error logs show SQLSTATE 40P01 / ORA-00060 (Deadlock detected)"
        ],
        "first_checks": [
            "Locate root blocker SPID whose blocked_by_spid IS NULL",
            "Inspect transaction start time: how long has the root blocker held the lock?",
            "Identify application endpoint and client host that spawned the uncommitted transaction"
        ],
        "diagnostic_commands": [
            {
                "engine": "PostgreSQL",
                "risk": "read_only",
                "label": "Lock Dependency Tree",
                "sql": "SELECT blocked_locks.pid AS blocked_pid, blocking_locks.pid AS blocking_pid, blocked_activity.query AS blocked_statement, blocking_activity.query AS current_statement_in_blocking_process FROM pg_catalog.pg_locks blocked_locks JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype WHERE NOT blocked_locks.granted;"
            },
            {
                "engine": "Oracle",
                "risk": "read_only",
                "label": "Root Blocker Sessions",
                "sql": "SELECT s1.sid AS blocking_sid, s2.sid AS blocked_sid, s1.username, s1.program FROM v$lock l1, v$session s1, v$lock l2, v$session s2 WHERE l1.id1 = l2.id1 AND l1.id2 = l2.id2 AND l1.block = 1 AND l2.request > 0 AND l1.sid = s1.sid AND l2.sid = s2.sid;"
            }
        ],
        "remediation_steps": [
            "Contact application owner or verify if session is an orphaned developer client tool",
            "Kill the root blocker session to immediately free the entire queue of waiting transactions",
            "In PostgreSQL: SELECT pg_terminate_backend(blocking_pid);",
            "In Oracle: ALTER SYSTEM KILL SESSION 'sid,serial#' IMMEDIATE;"
        ],
        "rollback_plan": "The database will cleanly roll back only the root blocker uncommitted transaction. All waiting sessions will immediately resume."
    },
    {
        "slug": "tablespace-capacity-exhaustion",
        "title": "Tablespace / Storage Exhaustion Outage",
        "title_id": "Kehabisan Ruang Disk / Tablespace Penuh",
        "severity": "HIGH",
        "category": "Storage & Capacity",
        "symptoms": [
            "Applications receive immediate errors on writes: ORA-01653 / No space left on device",
            "Database engine crashes or drops into Emergency Read-Only status",
            "Write-Ahead Log (WAL) archiving fails because disk directory is 100% full"
        ],
        "first_checks": [
            "Execute df -h on database host to identify filled filesystem mount point (/u01, /var/lib/postgresql)",
            "Verify if datafiles are configured with AUTOEXTEND and check max_mb ceiling"
        ],
        "diagnostic_commands": [
            {
                "engine": "Oracle",
                "risk": "read_only",
                "label": "Tablespace Capacity Metrics",
                "sql": "SELECT tablespace_name, round(used_percent, 2) AS used_pct, round(tablespace_size*8192/1024/1024, 0) AS total_mb FROM dba_tablespace_usage_metrics ORDER BY used_percent DESC;"
            },
            {
                "engine": "PostgreSQL",
                "risk": "read_only",
                "label": "Database Disk Size",
                "sql": "SELECT datname, pg_size_pretty(pg_database_size(datname)) AS db_size FROM pg_database ORDER BY pg_database_size(datname) DESC;"
            }
        ],
        "remediation_steps": [
            "Add a secondary datafile to tablespace: ALTER TABLESPACE USERS ADD DATAFILE '/u01/app/oracle/oradata/users02.dbf' SIZE 10G AUTOEXTEND ON NEXT 512M MAXSIZE 32G;",
            "Resize existing datafile if underlying filesystem has headroom: ALTER DATABASE DATAFILE '/u01/app/oracle/oradata/users01.dbf' RESIZE 30G;",
            "Clean up stale archived logs or temporary spill directories"
        ],
        "rollback_plan": "Dropping newly added datafiles is destructive. Never delete a datafile while database is online."
    }
]

VISUAL_LESSONS = [
    {
        "slug": "sql-execution-lifecycle",
        "title": "SQL Query Execution Lifecycle",
        "title_id": "Siklus Hidup Eksekusi Kueri SQL",
        "category": "Internals",
        "estimated_minutes": 5,
        "description_en": "Step-by-step architectural breakdown of what happens when a client sends an SQL query to an enterprise database engine.",
        "description_id": "Simulasi tahapan arsitektur internal saat kueri SQL dikirimkan oleh klien ke mesin database enterprise.",
        "steps": [
            {
                "step": 1,
                "stage": "Client Connection",
                "stage_id": "Koneksi Klien & Autentikasi",
                "active_node": "client",
                "text_en": "Client connects via TCP/IP. Postmaster/Listener authenticates credentials and assigns a dedicated backend server process.",
                "text_id": "Klien terhubung melalui TCP/IP. Listener memverifikasi kredensial dan mengalokasikan proses server backend khusus.",
                "sql_state": "TCP Handshake -> TLS Handshake -> Auth Success"
            },
            {
                "step": 2,
                "stage": "SQL Parser & AST",
                "stage_id": "Parser SQL & Pembuatan Pohon AST",
                "active_node": "parser",
                "text_en": "Engine performs lexical analysis and syntax checking, generating an Abstract Syntax Tree (AST).",
                "text_id": "Mesin membedah sintaks kueri dan membuat Abstract Syntax Tree (AST) untuk memastikan validitas struktur SQL.",
                "sql_state": "SELECT * FROM orders WHERE total > 1000; [PARSED]"
            },
            {
                "step": 3,
                "stage": "Semantic Catalog Resolution",
                "stage_id": "Resolusi Semantik Katalog Database",
                "active_node": "catalog",
                "text_en": "Engine consults system catalogs (pg_class, sys.tables) to verify table existence, column types, and user permissions.",
                "text_id": "Mesin memeriksa katalog sistem untuk memverifikasi keberadaan tabel, tipe data kolom, dan izin akses pengguna.",
                "sql_state": "Validating table 'orders' & column 'total' permissions: OK"
            },
            {
                "step": 4,
                "stage": "Cost-Based Query Optimizer",
                "stage_id": "Pengoptimal Kueri Berbasis Biaya (CBO)",
                "active_node": "optimizer",
                "text_en": "Optimizer evaluates multiple execution candidate paths using table statistics to choose lowest cost plan.",
                "text_id": "Optimizer mengevaluasi kandidat jalur eksekusi menggunakan statistik data dan memilih rencana berbiaya terendah.",
                "sql_state": "Cost Comparison: Seq Scan (Cost 2400) vs Index Scan (Cost 18.4) -> Index Scan Selected"
            },
            {
                "step": 5,
                "stage": "Plan Execution Engine",
                "stage_id": "Mesin Eksekusi Rencana Kueri",
                "active_node": "executor",
                "text_en": "Execution engine processes plan nodes step-by-step using Volcano iterator model (Init -> Next -> Close).",
                "text_id": "Engine menjalankan simpul rencana secara bertahap menggunakan model iterator Volcano.",
                "sql_state": "Executor Pipeline: Index Scan -> Filter -> Materialize"
            },
            {
                "step": 6,
                "stage": "Buffer Cache & Disk I/O",
                "stage_id": "Pencarian di Buffer Cache & I/O Disk",
                "active_node": "buffer",
                "text_en": "Executor checks Buffer Pool for requested 8KB pages. Cache Hit: Read immediately from RAM. Cache Miss: Read page from disk into buffer.",
                "text_id": "Executor memeriksa halaman data di Buffer Cache RAM. Jika Miss, blok data dibaca dari disk fisik ke RAM.",
                "sql_state": "Buffer Hit Ratio: 99.4% (Direct RAM Access)"
            },
            {
                "step": 7,
                "stage": "Result Streaming to Client",
                "stage_id": "Pengiriman Baris Hasil ke Klien",
                "active_node": "network",
                "text_en": "Executor serializes matching row tuples into wire protocol packets and streams them to the client socket.",
                "text_id": "Executor membungkus baris data ke dalam paket protokol jaringan dan mengirimkannya ke socket klien.",
                "sql_state": "24 rows streamed (0.42 ms total elapsed time)"
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

TROUBLESHOOTING_KB = [
    {
        "slug": "ora-01555-snapshot-too-old",
        "title": "ORA-01555: Snapshot Too Old (Rollback / Undo Sizing)",
        "title_id": "ORA-01555: Snapshot Terlalu Lama (Kapasitas Undo / Rollback)",
        "error_code": "ORA-01555",
        "engines": ["Oracle"],
        "severity": "HIGH",
        "symptoms": [
            "Long-running report fails after running for 20-45 minutes",
            "Error stack ORA-01555: snapshot too old: rollback segment number with name string too small",
            "Frequent occurrence during daytime business hours with concurrent heavy batch processing"
        ],
        "root_cause": "A long-running read query required historical images of data blocks that were updated and committed by concurrent writers, but the required UNDO records were overwritten before the reader could finish.",
        "investigation_sql": "SELECT begin_time, end_time, undoblks, maxquerylen, tuned_undoretention, ssolderrcnt FROM v$undostat WHERE ssolderrcnt > 0 ORDER BY begin_time DESC;",
        "remediation": [
            "Increase UNDO_RETENTION parameter to exceed the longest query duration: ALTER SYSTEM SET UNDO_RETENTION = 14400 SCOPE=BOTH;",
            "Add storage to the UNDO tablespace or enable AUTOEXTEND on undo datafiles",
            "Avoid commit-in-a-loop patterns in concurrent batch application jobs"
        ],
        "rollback": "Revert UNDO_RETENTION to original value if memory or storage becomes constrained: ALTER SYSTEM SET UNDO_RETENTION = 3600 SCOPE=BOTH;"
    },
    {
        "slug": "pg-53300-too-many-connections",
        "title": "PostgreSQL 53300: FATAL: sorry, too many clients already",
        "title_id": "PostgreSQL 53300: FATAL: Sambungan Klien Mencapai Batas Maksimal",
        "error_code": "53300",
        "engines": ["PostgreSQL"],
        "severity": "CRITICAL",
        "symptoms": [
            "Microservices fail to acquire database connections with 53300 error",
            "Web APIs return HTTP 500 / 503 Internal Server Error",
            "Connection count reaches max_connections (e.g. 100 or 200)"
        ],
        "root_cause": "Client services opened more physical database backends than max_connections permits, usually due to lack of a connection pooler or client connection leaks.",
        "investigation_sql": "SELECT count(*), state, usename, client_addr FROM pg_stat_activity GROUP BY state, usename, client_addr ORDER BY count(*) DESC;",
        "remediation": [
            "Deploy or scale PgBouncer connection pooler in transaction pooling mode",
            "Terminate idle connections: SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND state_change < now() - interval '15 minutes';",
            "Temporarily increase max_connections in postgresql.conf and restart if RAM allows"
        ],
        "rollback": "Lower max_connections back to safe baseline once PgBouncer is routing connections."
    },
    {
        "slug": "mysql-1205-lock-wait-timeout",
        "title": "MySQL Error 1205: Lock wait timeout exceeded",
        "title_id": "MySQL Error 1205: Batas Waktu Menunggu Lock Terlampaui",
        "error_code": "1205 (HY000)",
        "engines": ["MySQL", "MariaDB"],
        "severity": "HIGH",
        "symptoms": [
            "Applications throw java.sql.SQLException / pymysql.err.OperationalError: (1205, 'Lock wait timeout exceeded; try restarting transaction')",
            "Transactions stall for 50 seconds (default innodb_lock_wait_timeout) before failing"
        ],
        "root_cause": "A transaction waited longer than innodb_lock_wait_timeout for another transaction to release an exclusive row lock.",
        "investigation_sql": "SELECT * FROM performance_schema.data_lock_waits;",
        "remediation": [
            "Identify blocking transaction via performance_schema.data_locks",
            "Kill the blocking connection using KILL [thread_id];",
            "Ensure application transactions commit quickly and queries access rows in consistent order"
        ],
        "rollback": "None required; failed transaction is cleanly rolled back by InnoDB."
    },
    {
        "slug": "mssql-1205-deadlock-victim",
        "title": "SQL Server Error 1205: Transaction Deadlock Victim",
        "title_id": "SQL Server Error 1205: Transaksi Menjadi Korban Deadlock",
        "error_code": "1205",
        "engines": ["SQL Server"],
        "severity": "HIGH",
        "symptoms": [
            "Application receives SqlException: Transaction (Process ID) was deadlocked on lock resources with another process and has been chosen as the deadlock victim",
            "Periodic transaction aborts during high-concurrency batch updates"
        ],
        "root_cause": "Two or more concurrent sessions held exclusive or shared locks on distinct resources and each requested a lock on the other's resource in cyclic dependency.",
        "investigation_sql": "SELECT XEventData.XEvent.value('(data/value)[1]', 'varchar(max)') AS DeadlockGraph FROM (SELECT CAST(target_data AS xml) AS TargetData FROM sys.dm_xe_session_targets st JOIN sys.dm_xe_sessions s ON s.address = st.event_session_address WHERE s.name = 'system_health' AND st.target_name = 'ring_buffer') AS Data CROSS APPLY TargetData.nodes('//RingBufferTarget/event[@name=\"xml_deadlock_report\"]') AS XEventData(XEvent);",
        "remediation": [
            "Access database tables and indexes in a strictly identical sequence across all application procedures",
            "Create covering non-clustered indexes to avoid bookmark lookups that escalate shared locks",
            "Implement resilient exponential backoff retry logic in client applications on SQL error 1205"
        ],
        "rollback": "Revert index or schema changes if execution plans degrade."
    },
    {
        "slug": "db2-sql0911n-deadlock-locktimeout",
        "title": "IBM Db2 SQL0911N: Lock Timeout or Deadlock Rolled Back",
        "title_id": "IBM Db2 SQL0911N: Transaksi Dibatalkan Karena Deadlock atau Lock Timeout",
        "error_code": "SQL0911N",
        "engines": ["IBM Db2"],
        "severity": "HIGH",
        "symptoms": [
            "DB21034E / SQL0911N The current transaction has been rolled back because of a deadlock or timeout (Reason code 2 or 68)",
            "Application batches aborted during heavy end-of-month reconciliations"
        ],
        "root_cause": "Reason code 2 indicates a mutual deadlock; Reason code 68 indicates lock wait duration exceeded the configured LOCKTIMEOUT database parameter.",
        "investigation_sql": "SELECT application_handle, lock_name, lock_mode, lock_status, lock_wait_elapsed_time FROM TABLE(MON_GET_APPL_LOCKWAIT(NULL, -2)) AS T;",
        "remediation": [
            "Enable Currently Committed semantics (CUR_COMMIT = ON) so readers access the last committed version instead of waiting for exclusive row locks",
            "Audit db2diag.log with 'db2diag -rc -911' to pinpoint holding application handle and SQL statement",
            "Tune LOCKTIMEOUT (default -1 wait indefinitely, recommended 30-60s) and index foreign key columns"
        ],
        "rollback": "Reset CUR_COMMIT or LOCKTIMEOUT via 'db2 update db cfg for <dbname> using LOCKTIMEOUT 30'."
    }
]
