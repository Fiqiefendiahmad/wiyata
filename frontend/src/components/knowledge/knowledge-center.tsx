"use client";

import React, { useState, useEffect, useMemo } from "react";
import {
  BookOpen,
  Search,
  ArrowRight,
  Tag,
  Database,
  ArrowLeft,
  Server,
  Layers,
  Activity,
  CheckCircle,
  Play,
  ArrowRightLeft,
  ShieldAlert,
  Sparkles,
} from "lucide-react";
import { api } from "@/lib/api";
import { VisualDatabaseAcademy } from "./visual-player";
import { GlossaryExplorer } from "./glossary-explorer";
import { CrossComparisonMatrix } from "./cross-comparison-matrix";
import { DbaHandbookIncidents } from "./dba-handbook-incidents";
import { ArticleMarkdown } from "./article-markdown";

interface ArticleItem {
  id?: string;
  slug: string;
  title: string;
  titleId?: string;
  category?: string;
  engine: string;
  summary: string;
  summaryId?: string;
  readTime?: string;
  body_markdown?: string;
  body?: string;
  bodyId?: string;
}

const FALLBACK_ARTICLES: ArticleItem[] = [
  {
    slug: "postgresql-17-architecture-internals",
    title: "PostgreSQL 17 Architecture & Internals: MVCC, VACUUM, and WAL",
    titleId: "Arsitektur & Internal PostgreSQL 17: MVCC, VACUUM, dan WAL",
    category: "Architecture",
    engine: "PostgreSQL",
    readTime: "8 min read",
    summary:
      "Mastering PostgreSQL 17 multi-version concurrency control, autovacuum memory tuning, shared buffers, and streaming replication.",
    summaryId:
      "Memahami kontrol konkurensi MVCC pada PostgreSQL 17, optimasi autovacuum, shared buffers, dan replikasi streaming.",
    body: `### PostgreSQL 17 Core Architecture
PostgreSQL uses a process-based client-server architecture (\`postmaster\` forks a dedicated backend process per client connection).

### 1. Multi-Version Concurrency Control (MVCC)
In PostgreSQL, an \`UPDATE\` does not overwrite the row in place; it inserts a new tuple with updated \`xmin\`/\`xmax\` system columns while marking the older tuple dead.
- \`xmin\`: Transaction ID that created the tuple.
- \`xmax\`: Transaction ID that deleted/superseded the tuple (0 if active).
- **Benefit**: Readers never block writers, and writers never block readers.

### 2. The Role of VACUUM and Autovacuum
Because dead tuples accumulate (table bloat), \`VACUUM\` reclaims dead space and updates the Free Space Map (FSM) and Visibility Map (VM).
Key PostgreSQL 17 tuning:
\`\`\`ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_scale_factor = 0.05
maintenance_work_mem = 512MB
\`\`\`

### 3. Memory Hierarchy: Shared Buffers & Work Mem
- \`shared_buffers\`: Dedicated buffer cache (typically set to 25% of total server RAM).
- \`work_mem\`: Memory allocated per sort/hash operation per query. Set carefully to prevent OOM.
- \`effective_cache_size\`: Informs the planner how much filesystem cache is available (typically 50-75% of RAM).

### 4. Streaming Replication & WAL
Transactions append changes sequentially to Write-Ahead Log (WAL) files in \`pg_wal/\`.
- Synchronous or asynchronous standby nodes stream WAL records via \`walsender\` and \`walreceiver\`.
- Use \`pg_stat_replication\` to monitor replication lag in bytes and time.`,
    bodyId: `### Arsitektur Inti PostgreSQL 17
PostgreSQL menggunakan model proses berbasis client-server (proses \`postmaster\` melakukan \`fork\` untuk membuat proses backend per koneksi client).

### 1. Multi-Version Concurrency Control (MVCC)
Pada PostgreSQL, perintah \`UPDATE\` tidak menimpa data lama di disk, melainkan menyisipkan baris (tuple) baru dengan mencatat ID transaksi pada \`xmin\`/\`xmax\`, sementara baris lama ditandai sebagai dead tuple.
- \`xmin\`: ID transaksi pembuat baris.
- \`xmax\`: ID transaksi yang menghapus/memperbarui baris.
- **Keuntungan**: Operasi baca tidak pernah mengunci operasi tulis, dan sebaliknya.

### 2. Peran VACUUM dan Autovacuum
Dead tuple yang menumpuk menyebabkan bloat (pembengkakan ukuran tabel). \`VACUUM\` membebaskan ruang kosong untuk dipakai kembali dan memperbarui Free Space Map (FSM).
Konfigurasi penting pada PostgreSQL 17:
\`\`\`ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_scale_factor = 0.05
maintenance_work_mem = 512MB
\`\`\`

### 3. Hirarki Memori: Shared Buffers & Work Mem
- \`shared_buffers\`: Alokasi cache tabel di RAM (umumnya disetel pada 25% total RAM server).
- \`work_mem\`: Memori per operasi sorting/hashing per kueri.
- \`effective_cache_size\`: Estimasi cache filesystem untuk optimizer (50-75% total RAM).

### 4. Streaming Replication & WAL
Setiap mutasi data dicatat berurutan pada file Write-Ahead Log (WAL) di direktori \`pg_wal/\`.
- Server standby mereplikasi WAL secara real-time via proses \`walsender\` dan \`walreceiver\`.
- Pantau keterlambatan data melalui view \`pg_stat_replication\`.`,
  },
  {
    slug: "mysql-11-innodb-replication-guide",
    title: "MySQL & MariaDB 11 Deep Dive: InnoDB Engine, Buffer Pool & GTID Replication",
    titleId: "Panduan Mendalam MySQL & MariaDB 11: Mesin InnoDB, Buffer Pool & Replikasi GTID",
    category: "Architecture",
    engine: "MySQL / MariaDB",
    readTime: "7 min read",
    summary:
      "Anatomy of the InnoDB storage engine, doublewrite buffers, redo logs, and production GTID replication topologies.",
    summaryId:
      "Anatomi mesin penyimpanan InnoDB, doublewrite buffer, redo log, dan konfigurasi replikasi berbasis GTID.",
    body: `### The InnoDB Storage Engine
InnoDB is the ACID-compliant default storage engine for MySQL and MariaDB, organizing tables in clustered B+tree indexes ordered by Primary Key.

### 1. The InnoDB Buffer Pool
The single most critical memory structure in MySQL. Caches data pages, index pages, undo pages, and change buffers.
\`\`\`ini
# my.cnf
innodb_buffer_pool_size = 8G      # 60-75% of dedicated server RAM
innodb_buffer_pool_instances = 8  # Reduces thread concurrency contention
innodb_log_file_size = 2G         # Redo log capacity
innodb_flush_log_at_trx_commit = 1 # 1 = Full ACID compliance
\`\`\`

### 2. Durability Mechanisms: Redo Log & Doublewrite Buffer
- **Redo Log (\`ib_logfile\`)**: Sequential circular log recording physical page changes before memory pages flush.
- **Doublewrite Buffer**: Prevents page corruption from torn writes by writing pages to a contiguous disk buffer before writing to \`.ibd\` tablespace files.

### 3. Global Transaction Identifier (GTID) Replication
GTID assigns a unique 128-bit UUID and sequence number to every committed transaction (\`source_id:transaction_id\`).
- Eliminates tracking binlog file coordinates (\`mysql-bin.000123:456\`).
- Enables automated topology failovers via tools like Orchestrator and ProxySQL.`,
    bodyId: `### Mesin Penyimpanan InnoDB
InnoDB adalah mesin penyimpanan default berbasis ACID untuk MySQL dan MariaDB. Semua tabel disimpan dengan clustered B+tree berurutan berdasarkan Primary Key.

### 1. InnoDB Buffer Pool
Struktur memori paling vital di MySQL. Berfungsi meng-cache halaman data, indeks, undo log, dan change buffer di RAM.
\`\`\`ini
# my.cnf
innodb_buffer_pool_size = 8G      # 60-75% dari total RAM server khusus database
innodb_buffer_pool_instances = 8  # Membagi buffer pool untuk mencegah thread contention
innodb_log_file_size = 2G         # Kapasitas Redo Log
innodb_flush_log_at_trx_commit = 1 # 1 = Jaminan penuh ACID Durability
\`\`\`

### 2. Menjaga Integritas Data: Redo Log & Doublewrite Buffer
- **Redo Log**: Mencatat perubahan fisik halaman disk secara sekuensial sebelum data di-flush ke disk.
- **Doublewrite Buffer**: Mencegah kerusakan halaman data akibat torn write (listrik mati saat menulis halaman 16KB).

### 3. Replikasi Modern Berbasis GTID
GTID (Global Transaction Identifier) memberikan pengenal unik pada setiap transaksi (\`UUID:sequence_number\`).
- Menghapus kerumitan pelacakan koordinat file binlog manual (\`file:position\`).
- Mempermudah failover klaster otomatis menggunakan tools seperti Orchestrator dan ProxySQL.`,
  },
  {
    slug: "oracle-23ai-enterprise-architecture",
    title: "Oracle 23ai Architecture: Multitenant CDB/PDB, SGA/PGA & AWR Telemetry",
    titleId: "Arsitektur Oracle 23ai: Multitenant CDB/PDB, Memori SGA/PGA & Telemetri AWR",
    category: "Architecture",
    engine: "Oracle",
    readTime: "8 min read",
    summary:
      "Exploring Oracle 23ai multitenant architecture, System Global Area memory allocation, and Automatic Workload Repository (AWR) diagnostics.",
    summaryId:
      "Memahami arsitektur multitenant Oracle 23ai, alokasi memori SGA/PGA, serta diagnostik Automatic Workload Repository (AWR).",
    body: `### Oracle 23ai Multitenant Architecture
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
- **ASH (Active Session History)**: Samples active sessions once every second in memory, enabling micro-level bottleneck triage.`,
    bodyId: `### Arsitektur Multitenant Oracle 23ai
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
- **ASH (Active Session History)**: Merekam aktivitas sesi aktif setiap 1 detik di memori untuk diagnosis insiden performa secara real-time.`,
  },
  {
    slug: "sql-server-2022-internals-query-store",
    title: "SQL Server 2022 Architecture: Storage Engine, Query Store & Extended Events",
    titleId: "Arsitektur SQL Server 2022: Mesin Penyimpanan, Query Store & Extended Events",
    category: "Architecture",
    engine: "SQL Server",
    readTime: "7 min read",
    summary:
      "Deep dive into Microsoft SQL Server 2022 extents, clustered index storage, Query Store plan forcing, and Extended Events telemetry.",
    summaryId:
      "Memahami organisasi halaman 8KB, indeks clustered, Query Store untuk stabilisasi rencana kueri, dan telemetri Extended Events.",
    body: `### Storage Engine Organization
SQL Server stores database data in 8 KB pages grouped into 64 KB extents (8 contiguous pages).
- **Clustered Index**: The leaf level of the index *is* the actual table data itself, physically sorted by cluster key.
- **Non-Clustered Index**: Separate B-tree structure holding key columns and a row locator (pointer to clustered key).

### 1. Query Store: The Database Flight Recorder
Query Store continuously captures history of queries, execution plans, and runtime statistics:
- Automatically detects plan regressions where a query suddenly consumes 10x more CPU.
- Allows DBAs to force good execution plans with a single command without altering application code.

### 2. Telemetry: Extended Events (XEvents) vs. SQL Profiler
- **SQL Profiler**: Deprecated; heavy client overhead that can degrade production throughput.
- **Extended Events**: High-performance, lightweight event-handling engine built directly into the SQL Server kernel with minimal CPU impact (< 1%).`,
    bodyId: `### Organisasi Mesin Penyimpanan SQL Server
SQL Server menyimpan data dalam halaman (page) berukuran 8 KB yang dikelompokkan ke dalam extent 64 KB (8 halaman berurutan).
- **Clustered Index**: Daun (leaf level) dari pohon indeks merupakan data baris fisik tabel itu sendiri yang terurut berdasarkan cluster key.
- **Non-Clustered Index**: Struktur B-tree terpisah yang menampung kolom kunci dan pointer ke clustered key.

### 1. Query Store: Flight Recorder Database
Query Store merekam riwayat eksekusi kueri, rencana eksekusi (execution plan), dan statistik latensi:
- Mendeteksi regresi performa kueri secara otomatis.
- Mengizinkan DBA memaksa (force) execution plan yang efisien tanpa mengubah kode aplikasi.

### 2. Telemetri: Extended Events (XEvents) Menggantikan SQL Profiler
- **SQL Profiler**: Bersifat usang (deprecated) dan membebani server secara signifikan.
- **Extended Events**: Sistem pelacakan event terintegrasi langsung pada kernel SQL Server dengan overhead sangat rendah (< 1% CPU).`,
  },
  {
    slug: "ibm-db2-11-5-hadr-tablespaces-wlm",
    title: "IBM Db2 11.5 Architecture: HADR Replication, Tablespaces & Workload Manager",
    titleId: "Arsitektur IBM Db2 11.5: Replikasi HADR, Tablespace & Workload Manager (WLM)",
    category: "Architecture",
    engine: "IBM Db2",
    readTime: "7 min read",
    summary:
      "Enterprise deep dive into IBM Db2 11.5: High Availability Disaster Recovery (HADR), SMS/DMS tablespace management, and Workload Manager (WLM) prioritization.",
    summaryId:
      "Panduan arsitektur enterprise IBM Db2 11.5: Replikasi High Availability Disaster Recovery (HADR), alokasi tablespace SMS/DMS, dan Workload Manager (WLM).",
    body: `### Core Storage Architecture: Tablespaces & Bufferpools
IBM Db2 structures relational persistence across decoupled logical layers:
- **Bufferpools**: Dedicated memory regions caching 4KB, 8KB, 16KB, or 32KB pages from disk.
- **SMS (System-Managed Space)**: Operating system directories where files expand automatically (often used for temp tables).
- **DMS (Database-Managed Space) & Automatic Storage**: Raw containers or dynamic filesystem paths allocated directly by Db2 with pre-allocated extents for high OLTP throughput.

### 1. High Availability Disaster Recovery (HADR)
HADR provides real-time transaction replication between Primary and Standby databases:
- **Sync Modes**: \`SYNC\` (zero data loss), \`NEARSYNC\` (low latency), \`ASYNC\` (network friendly), and \`SUPERASYNC\` (WAN tolerance without impacting Primary write throughput).
- **Read on Standby (RoS)**: Offloads read-only analytics queries to Standby nodes while the Primary processes high-concurrency writes.

### 2. Workload Manager (WLM) & Resource Governance
Db2 Workload Manager allows DBAs to enforce service level agreements (SLAs):
- Categorizes database requests into service classes (e.g., Fast OLTP vs. Heavy Analytical Reporting).
- Restricts runaway queries from monopolizing CPU cores or memory bufferpools using thresholds and execution timeouts.`,
    bodyId: `### Arsitektur Penyimpanan IBM Db2: Tablespace & Bufferpool
IBM Db2 memisahkan penyimpanan data dalam lapisan logis yang terstruktur:
- **Bufferpool**: Alokasi RAM khusus yang men-cache halaman berukuran 4KB, 8KB, 16KB, atau 32KB dari disk.
- **SMS (System-Managed Space)**: Direktori filesystem sistem operasi yang ukurannya bertambah dinamis.
- **DMS (Database-Managed Space) & Automatic Storage**: Kontainer penyimpanan terkelola dengan alokasi extent berurutan untuk memaksimalkan throughput transaksi tinggi (OLTP).

### 1. High Availability Disaster Recovery (HADR)
HADR mereplikasi log transaksi secara real-time dari database Primary ke Standby:
- **Mode Sinkronisasi**: \`SYNC\` (jaminan zero data loss), \`NEARSYNC\` (latensi rendah), \`ASYNC\`, dan \`SUPERASYNC\` (tahan latensi WAN).
- **Read on Standby (RoS)**: Mengalihkan kueri pelaporan analitik ke server Standby sehingga server Primary tetap optimal memproses transaksi tulis.

### 2. Workload Manager (WLM) & Regulasi Resource
Db2 Workload Manager mengelompokkan kueri ke dalam kelas layanan (Service Class):
- Memisahkan prioritas kueri OLTP kasir/perbankan dengan pelaporan analitik bulanan.
- Mencegah kueri berat yang tidak efisien menghabiskan kapasitas CPU atau RAM melalui ambang batas (thresholds) otomatis.`,
  },
  {
    slug: "database-monitoring-golden-signals",
    title: "Database Observability Guide: The 4 Golden Signals, Exporters & PMM Runbooks",
    titleId: "Panduan Observabilitas Database: 4 Golden Signals, Exporter & Runbook PMM",
    category: "Performance",
    engine: "Universal",
    readTime: "6 min read",
    summary:
      "Actionable monitoring architecture for production databases: Latency, Traffic, Errors, and Saturation with PromQL and Grafana.",
    summaryId:
      "Arsitektur monitoring database produksi: Latency, Traffic, Errors, dan Saturation menggunakan PromQL dan dashboard Grafana.",
    body: `### The 4 Golden Signals for Database Observability
Google's Site Reliability Engineering framework applied to relational databases:

### 1. Latency
Time taken to service read and write queries.
- **Target**: p95 < 20ms, p99 < 50ms.
- **Metric**: \`rate(pg_stat_statements_total_time_ms[5m]) / rate(pg_stat_statements_calls[5m])\`.

### 2. Traffic (Throughput)
Volume of transactions demanded by clients.
- **Metric**: Transactions per Second (TPS), Queries per Second (QPS).
- **PromQL**: \`rate(pg_stat_database_xact_commit[1m]) + rate(pg_stat_database_xact_rollback[1m])\`.

### 3. Errors
Failure rate of database operations.
- **Metric**: Transaction abort rate, Deadlock counts, Connection authorization rejections.
- **PromQL**: \`increase(mysql_global_status_innodb_deadlocks[1h])\`.

### 4. Saturation
Fraction of database resource capacity utilized.
- **Buffer Pool / Shared Buffer Hit Ratio**: Must stay > 99%.
- **Active Connections**: Alert when \`active_connections / max_connections > 0.85\`.
- **Replication Lag**: Alert when standby replication lag exceeds 30 seconds.`,
    bodyId: `### 4 Golden Signals untuk Observabilitas Database
Penerapan standar Google SRE untuk memantau kesehatan database relasional:

### 1. Latensi (Latency)
Waktu yang dibutuhkan untuk mengeksekusi kueri baca dan tulis.
- **Target**: p95 < 20ms, p99 < 50ms.
- **Metrik**: Rata-rata waktu eksekusi kueri melalui \`pg_stat_statements\` atau InnoDB Query Analytics (QAN).

### 2. Trafik (Throughput)
Beban transaksi yang diproses database dari aplikasi.
- **Metrik**: Transactions per Second (TPS) dan Queries per Second (QPS).
- **PromQL**: \`rate(pg_stat_database_xact_commit[1m]) + rate(pg_stat_database_xact_rollback[1m])\`.

### 3. Kesalahan (Errors)
Tingkat kegagalan operasi database.
- **Metrik**: Rollback paksa, frekuensi deadlock per jam, dan penolakan koneksi akibat penuh.
- **PromQL**: \`increase(mysql_global_status_innodb_deadlocks[1h])\`.

### 4. Saturasi (Saturation)
Persentase pemanfaatan kapasitas sumber daya database.
- **Buffer Cache Hit Ratio**: Harus bertahan di atas 99%.
- **Utilisasi Koneksi**: Berikan peringatan jika \`koneksi aktif / max_connections > 85%\`.
- **Replication Lag**: Berikan alert jika keterlambatan replikasi melebihi 30 detik.`,
  },
  {
    slug: "sqlite-wal-mode-explained",
    title: "SQLite Write-Ahead Logging (WAL) Mode Explained",
    titleId: "Penjelasan Mode Write-Ahead Logging (WAL) pada SQLite",
    category: "Internals",
    engine: "SQLite",
    readTime: "4 min read",
    summary:
      "How WAL mode unlocks concurrent readers alongside a writer in SQLite environments.",
    summaryId:
      "Bagaimana mode WAL membuka kemampuan pembacaan bersamaan (concurrent readers) tanpa terblokir penulis pada SQLite.",
    body: `### The Default Journal vs. WAL
In classic rollback journal mode, writing locks the whole database from readers.
In **WAL mode** (\`PRAGMA journal_mode=WAL;\`):
- Readers never block writers.
- Writers never block readers.
- Commits are appended to a \`-wal\` file and periodically checkpointed back to the main database file.`,
    bodyId: `### Perbedaan Rollback Journal vs. Mode WAL
Pada mode rollback journal standar, operasi penulisan akan mengunci seluruh database dari proses pembacaan.
Pada **mode WAL** (\`PRAGMA journal_mode=WAL;\`):
- Pembaca (readers) tidak pernah memblokir penulis (writers).
- Penulis (writers) tidak pernah memblokir pembaca (readers).
- Operasi commit ditulis ke file \`-wal\` tambahan dan secara berkala dikonsolidasikan (checkpointing) ke file database utama.`,
  },
  {
    slug: "understanding-acid-properties",
    title: "Understanding ACID Properties in Modern Relational Databases",
    titleId: "Memahami Prinsip ACID pada Database Relasional Modern",
    category: "Architecture",
    engine: "Universal",
    readTime: "5 min read",
    summary:
      "A deep dive into Atomicity, Consistency, Isolation, and Durability and why they matter in production workloads.",
    summaryId:
      "Penjelasan mendalam mengenai Atomicity, Consistency, Isolation, dan Durability dalam beban kerja produksi.",
    body: `### What is ACID?
ACID represents the four key guarantees of reliable database transactions:
- **Atomicity**: An operation succeeds entirely or is rolled back completely. Never partial states.
- **Consistency**: Data transitions strictly from one valid state to another according to constraints and triggers.
- **Isolation**: Concurrent transactions do not interfere or observe uncommitted intermediate mutations.
- **Durability**: Once committed, changes survive unexpected crashes, hardware failures, or power loss.`,
    bodyId: `### Apa itu ACID?
ACID adalah empat pilar jaminan keandalan transaksi database relasional:
- **Atomicity (Keutuhan)**: Transaksi sukses seluruhnya atau dibatalkan total. Tidak ada status setengah jalan.
- **Consistency (Konsistensi)**: Data hanya berpindah dari satu status valid ke status valid lainnya sesuai aturan skema dan integritas.
- **Isolation (Isolasi)**: Transaksi bersamaan tidak saling mengganggu atau melihat mutasi yang belum di-commit.
- **Durability (Ketahanan)**: Sekali transaksi di-commit, data dijamin bertahan walau sistem atau server mati mendadak.`,
  },
  {
    slug: "mongodb-architecture-wiredtiger-sharding",
    title: "MongoDB Architecture: WiredTiger Engine, Replica Sets, and Sharding",
    titleId: "Arsitektur MongoDB: WiredTiger Engine, Replica Set, dan Sharding",
    category: "NoSQL",
    engine: "MongoDB",
    readTime: "7 min read",
    summary: "Deep dive into MongoDB WiredTiger cache evictions, write concerns, Raft-like replica set elections, and distributed sharded cluster balancing.",
    summaryId: "Analisis mendalam mesin penyimpanan WiredTiger MongoDB, write concerns, pemilihan replica set, dan partisi klaster sharding terdistribusi.",
    body: `### MongoDB Core Architecture
MongoDB is a distributed document database using BSON serialization.
- **WiredTiger Engine**: Document-level concurrency, Snappy compression, checkpoints every 60s.
- **Replica Sets**: Raft-like elections with 10s timeout, idempotent oplog replication.
- **Sharded Clusters**: mongos query routers, Config Replica Set metadata, background chunk balancing.`,
    bodyId: `### Arsitektur Inti MongoDB
MongoDB adalah database dokumen terdistribusi yang menyimpan data dalam format serialisasi BSON.
- **Mesin WiredTiger**: Kontrol konkurensi tingkat dokumen, kompresi Snappy, dan checkpoint berkala tiap 60 detik.
- **Replica Set**: Pemilihan pemimpin berbasis Raft, replikasi oplog idempoten ke node Secondary.
- **Klaster Sharding**: Router mongos stateless, metadata Config Replica Set, dan balancing chunk otomatis.`,
  },
  {
    slug: "redis-internals-persistence-cluster",
    title: "Redis Architecture & Internals: In-Memory Data Structures, Persistence, and Cluster",
    titleId: "Arsitektur & Internal Redis: Struktur Data Memori, Persistensi RDB/AOF, dan Klaster",
    category: "NoSQL",
    engine: "Redis",
    readTime: "6 min read",
    summary: "Understanding Redis single-threaded event loop, RDB vs AOF persistence trade-offs, Sentinel failovers, and 16,384-slot Cluster partitioning.",
    summaryId: "Memahami event loop single-threaded Redis, kompromi persistensi RDB vs AOF, failover otomatis Sentinel, dan partisi 16.384 slot Redis Cluster.",
    body: `### Redis Architecture Overview
- **Event Loop**: Single-threaded non-blocking epoll loop eliminates locking overhead.
- **Persistence**: RDB point-in-time binary snapshots vs. AOF append-only log with configurable fsync policies.
- **Cluster**: Keyspace partitioned across exactly 16,384 hash slots (\`CRC16(key) MOD 16384\`).`,
    bodyId: `### Ikhtisar Arsitektur Redis
- **Event Loop**: Loop epoll non-blocking single-threaded meniadakan perebutan kunci (lock contention).
- **Persistensi Ganda**: Snapshot biner RDB fork copy-on-write vs log mutasi sekuensial AOF.
- **Redis Cluster**: Ruang kunci dipartisi rata ke dalam 16.384 hash slot (\`CRC16(key) MOD 16384\`).`,
  },
  {
    slug: "cassandra-lsm-architecture-ring",
    title: "Apache Cassandra Architecture: LSM-Tree Storage, Ring Topology, and Tunable Consistency",
    titleId: "Arsitektur Apache Cassandra: Penyimpanan LSM-Tree, Topologi Ring, dan Konsistensi Fleksibel",
    category: "NoSQL",
    engine: "Apache Cassandra",
    readTime: "8 min read",
    summary: "Mastering Cassandra masterless architecture, Memtable/SSTable compaction, Bloom filters, and tunable CAP theorem consistency levels.",
    summaryId: "Menguasai arsitektur masterless Cassandra, komparasi pemadatan Memtable/SSTable, filter Bloom, dan tingkat konsistensi CAP theorem yang dapat dikonfigurasi.",
    body: `### Apache Cassandra Core Architecture
- **Masterless Ring**: Peer-to-peer ring topology with Murmur3Partitioner and Gossip protocol.
- **LSM-Tree Write Path**: Sequential CommitLog append + Memtable write flushed to immutable SSTables.
- **Tunable Consistency**: R + W > N ensures strong consistency across distributed nodes.`,
    bodyId: `### Arsitektur Inti Apache Cassandra
- **Ring Masterless**: Topologi peer-to-peer terdistribusi tanpa Single Point of Failure (SPOF).
- **Alur Tulis LSM**: Penulisan sekuensial ke CommitLog dan Memtable tanpa random I/O disk, di-flush ke SSTable.
- **Konsistensi Fleksibel**: Rumus R + W > N menjamin pembacaan konsistensi kuat lintas node.`,
  },
  {
    slug: "cockroachdb-distributed-sql-raft",
    title: "CockroachDB & YugabyteDB: Distributed SQL, Multi-Raft Consensus, and HLC",
    titleId: "CockroachDB & YugabyteDB: SQL Terdistribusi, Konsensus Multi-Raft, dan HLC",
    category: "Distributed SQL",
    engine: "CockroachDB & YugabyteDB",
    readTime: "7 min read",
    summary: "How next-generation distributed SQL databases provide full ACID serializability, Raft range replication, and Hybrid Logical Clocks.",
    summaryId: "Bagaimana database Distributed SQL modern menghadirkan serializability ACID penuh, replikasi range berbasis Multi-Raft, dan Hybrid Logical Clocks (HLC).",
    body: `### Distributed SQL Paradigm
- **Multi-Raft Consensus**: Keyspace divided into 64 MB ranges, each managed by independent Raft groups.
- **Hybrid Logical Clocks**: Combines physical wall-clock time with logical counters to coordinate serializable ordering without atomic GPS hardware.
- **Inline Intent MVCC**: Non-blocking lock-free transaction resolution.`,
    bodyId: `### Paradigma Distributed SQL
- **Konsensus Multi-Raft**: Ruang kunci dibagi menjadi rentang 64 MB (Ranges) yang direplikasi via Raft.
- **Hybrid Logical Clocks (HLC)**: Sinkronisasi waktu konsisten tanpa memerlukan jam atomik GPS khusus.
- **Intent MVCC**: Transaksi terdistribusi aman tanpa memicu deadlock atau lock berkepanjangan.`,
  },
  {
    slug: "snowflake-cloud-data-warehouse-internals",
    title: "Snowflake Architecture: Multi-Cluster Shared Data, Micro-Partitions, and Zero-Copy Cloning",
    titleId: "Arsitektur Snowflake: Multi-Cluster Shared Data, Micro-Partition, dan Zero-Copy Cloning",
    category: "Analytics",
    engine: "Snowflake",
    readTime: "7 min read",
    summary: "An architectural exploration of Snowflake tri-layer separation of storage, compute virtual warehouses, and cloud services metadata.",
    summaryId: "Eksplorasi arsitektur pemisahan tiga lapis Snowflake: penyimpanan data terpusat, komputasi virtual warehouse, dan layanan metadata cloud.",
    body: `### Snowflake Tri-Layer Architecture
- **Separation of Concerns**: Centralized object storage, elastic Virtual Warehouses for compute, and Cloud Services metadata brain.
- **Immutable Micro-Partitions**: 50-500 MB columnar partitions with metadata min/max pruning.
- **Zero-Copy Cloning**: Metadata-only duplication enables instant table copies with zero initial storage cost.`,
    bodyId: `### Arsitektur Tiga Lapis Snowflake
- **Pemisahan Storage & Compute**: Penyimpanan cloud terpusat, Virtual Warehouse elastis, dan Cloud Services koordinator.
- **Micro-Partition Kolumnar**: File 50-500 MB immutable dengan optimasi partition pruning otomatis.
- **Zero-Copy Cloning**: Duplikasi instan dalam hitungan detik berbasis pointer metadata.`,
  },
  {
    slug: "clickhouse-duckdb-columnar-vectorized",
    title: "ClickHouse & DuckDB: Column-Oriented Storage and Vectorized Query Execution",
    titleId: "ClickHouse & DuckDB: Penyimpanan Kolumnar dan Eksekusi Kueri Tervektorisasi (SIMD)",
    category: "Analytics",
    engine: "ClickHouse & DuckDB",
    readTime: "6 min read",
    summary: "High-performance analytical engines demystified: MergeTree storage family, SIMD vectorized processing, and embedded columnar analytics with DuckDB.",
    summaryId: "Membedah mesin analitik performa tinggi: arsitektur MergeTree, eksekusi tervektorisasi SIMD pada CPU, dan analisis kolumnar embedded dengan DuckDB.",
    body: `### Columnar Analytical Engines
- **Column-Oriented Storage**: Reading only required columns slashes disk I/O by 90-95% with high compression.
- **SIMD Vectorized Execution**: Operates on arrays of values using CPU vector registers for massive throughput.
- **ClickHouse MergeTree & DuckDB**: High-throughput parts merging and embedded in-process OLAP.`,
    bodyId: `### Mesin Analitik Berorientasi Kolom
- **Penyimpanan Kolumnar**: Membaca kolom yang dibutuhkan saja memangkas I/O disk hingga 90%+.
- **Eksekusi Tervektorisasi (SIMD)**: Memanfaatkan register vektor CPU modern untuk memproses ribuan baris per siklus clock.
- **ClickHouse MergeTree & DuckDB**: Arsitektur merge parts berkinerja tinggi serta analitik kolumnar in-process.`,
  },
];

type KnowledgeSection = "articles" | "visual" | "glossary" | "comparison" | "handbook";

interface KnowledgeCenterProps {
  language: "en" | "id";
  onOpenLab: () => void;
}

export function KnowledgeCenter({ language, onOpenLab }: KnowledgeCenterProps) {
  const isId = language === "id";
  const [activeSection, setActiveSection] = useState<KnowledgeSection>("articles");
  const [articles, setArticles] = useState<ArticleItem[]>(FALLBACK_ARTICLES);
  const [selectedArticle, setSelectedArticle] = useState<ArticleItem | null>(FALLBACK_ARTICLES[0]);
  const [activeEngineFilter, setActiveEngineFilter] = useState<string>("ALL");
  const [searchTerm, setSearchTerm] = useState("");
  const [mobileViewingArticle, setMobileViewingArticle] = useState(false);
  const [fullArticleDetail, setFullArticleDetail] = useState<string | null>(null);

  const subSections: {
    id: KnowledgeSection;
    labelEn: string;
    labelId: string;
    icon: React.ElementType;
  }[] = [
    {
      id: "articles",
      labelEn: "Architecture Articles",
      labelId: "Ensiklopedia & Artikel",
      icon: BookOpen,
    },
    {
      id: "visual",
      labelEn: "Visual Academy (Simulations)",
      labelId: "Akademi Visual (Simulasi)",
      icon: Activity,
    },
    {
      id: "glossary",
      labelEn: "Glossary & Field Terms",
      labelId: "Glosarium & Istilah",
      icon: Tag,
    },
    {
      id: "comparison",
      labelEn: "Cross-Database Matrix",
      labelId: "Matriks Komparasi",
      icon: ArrowRightLeft,
    },
    {
      id: "handbook",
      labelEn: "DBA Incident Runbooks",
      labelId: "Buku Saku Insiden",
      icon: ShieldAlert,
    },
  ];

  // Fetch live articles from API
  useEffect(() => {
    api
      .get(`/knowledge/articles?language=${language}`)
      .then((res) => {
        if (Array.isArray(res.data) && res.data.length > 0) {
          const apiMapped: ArticleItem[] = res.data.map((a: any) => ({
            id: a.id,
            slug: a.slug,
            title: a.title,
            titleId: a.title,
            category: "Database Architecture",
            engine: a.engine || "Universal",
            summary: a.summary || "",
            summaryId: a.summary || "",
            readTime: "6 min read",
          }));
          setArticles(apiMapped);
          if (apiMapped.length > 0) setSelectedArticle(apiMapped[0]);
        }
      })
      .catch((err) => console.error("Error loading articles from API:", err));
  }, [language]);

  // Fetch complete article body when selected
  useEffect(() => {
    if (!selectedArticle) return;
    setFullArticleDetail(null);
    api
      .get(`/knowledge/articles/${selectedArticle.slug}?language=${language}`)
      .then((res) => {
        if (res.data?.body_markdown) {
          setFullArticleDetail(res.data.body_markdown);
        }
      })
      .catch(() => {
        // Fallback to static body
        const fb = FALLBACK_ARTICLES.find((f) => f.slug === selectedArticle.slug);
        if (fb) {
          setFullArticleDetail(isId ? fb.bodyId || fb.body || "" : fb.body || "");
        }
      });
  }, [selectedArticle?.slug, language, isId]);

  const filteredArticles = useMemo(() => {
    return articles.filter((a) => {
      if (activeEngineFilter !== "ALL") {
        const eng = a.engine.toLowerCase();
        const cat = (a.category || "").toLowerCase();
        const filt = activeEngineFilter.toLowerCase();
        if (filt === "nosql") {
          if (
            !eng.includes("mongo") &&
            !eng.includes("redis") &&
            !eng.includes("cassandra") &&
            !eng.includes("cockroach") &&
            !cat.includes("nosql")
          ) {
            return false;
          }
        } else if (filt === "analytics") {
          if (
            !eng.includes("snow") &&
            !eng.includes("click") &&
            !eng.includes("duck") &&
            !eng.includes("bigquery") &&
            !eng.includes("redshift") &&
            !cat.includes("analytics")
          ) {
            return false;
          }
        } else if (!eng.includes(filt)) {
          return false;
        }
      }
      if (searchTerm.trim()) {
        const q = searchTerm.toLowerCase();
        return (
          a.title.toLowerCase().includes(q) ||
          (a.summary && a.summary.toLowerCase().includes(q)) ||
          a.engine.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [articles, activeEngineFilter, searchTerm]);

  const handleSelect = (art: ArticleItem) => {
    setSelectedArticle(art);
    setMobileViewingArticle(true);
  };

  const articleBodyToRender =
    fullArticleDetail ||
    (selectedArticle
      ? isId
        ? selectedArticle.bodyId || selectedArticle.body || selectedArticle.body_markdown || ""
        : selectedArticle.body || selectedArticle.body_markdown || ""
      : "");

  return (
    <div className="flex flex-col h-auto lg:h-[calc(100dvh-3.5rem)] w-full overflow-hidden bg-[#071A3A] text-slate-200">
      {/* Top Knowledge Sub-Navigation Header */}
      <header className="flex-none border-b border-slate-800 bg-[#091b36] px-3 py-2 z-10 shadow-sm">
        <div className="flex items-center gap-1.5 overflow-x-auto no-scrollbar touch-scroll">
          {subSections.map((sec) => {
            const Icon = sec.icon;
            const isActive = activeSection === sec.id;
            return (
              <button
                key={sec.id}
                onClick={() => setActiveSection(sec.id)}
                className={`flex items-center gap-2 rounded-xl px-3 py-1.5 text-xs font-semibold whitespace-nowrap transition-all ${
                  isActive
                    ? "bg-gradient-to-r from-[#F2B84B] to-[#E5A838] text-[#071A3A] shadow-md font-bold"
                    : "bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800/80"
                }`}
              >
                <Icon className={`h-3.5 w-3.5 ${isActive ? "text-[#071A3A]" : "text-[#F2B84B]"}`} />
                <span>{isId ? sec.labelId : sec.labelEn}</span>
              </button>
            );
          })}
        </div>
      </header>

      {/* Main Content Area */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {activeSection === "articles" && (
          <div className="flex flex-col lg:flex-row flex-1 overflow-hidden">
            {/* Sidebar Article List */}
            <aside
              className={`${
                mobileViewingArticle ? "hidden" : "flex"
              } lg:flex w-full lg:w-84 xl:w-96 flex-col border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#071A3A]/95 overflow-hidden`}
            >
              <div className="p-3.5 border-b border-slate-800 bg-[#10264A]/30">
                <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#F2B84B] mb-1.5">
                  <BookOpen className="h-4 w-4" />
                  <span>{isId ? "Ensiklopedia Mesin Database" : "Database Engine Encyclopedia"}</span>
                </div>

                {/* Search Box */}
                <div className="relative mb-2.5">
                  <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-slate-400" />
                  <input
                    type="text"
                    placeholder={
                      isId ? "Cari panduan arsitektur..." : "Search engine architecture..."
                    }
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full rounded-lg bg-slate-900 border border-slate-700/80 pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#F2B84B]"
                  />
                </div>

                {/* Engine Filter Chips */}
                <div className="flex items-center gap-1 overflow-x-auto no-scrollbar touch-scroll pb-1">
                  {[
                    { id: "ALL", label: isId ? "Semua" : "All" },
                    { id: "postgres", label: "Postgres" },
                    { id: "mysql", label: "MySQL" },
                    { id: "oracle", label: "Oracle" },
                    { id: "sql server", label: "SQL Server" },
                    { id: "ibm db2", label: "IBM Db2" },
                    { id: "sqlite", label: "SQLite" },
                    { id: "nosql", label: isId ? "NoSQL & Terdistribusi" : "NoSQL & Distributed" },
                    { id: "analytics", label: isId ? "Analitik & Cloud" : "Analytics & Cloud" },
                    { id: "universal", label: isId ? "Infrastruktur & APM" : "Infra & APM" },
                  ].map((chip) => (
                    <button
                      key={chip.id}
                      onClick={() => setActiveEngineFilter(chip.id)}
                      className={`rounded-md px-2 py-0.5 text-[10px] font-semibold whitespace-nowrap transition-colors ${
                        activeEngineFilter === chip.id
                          ? "bg-[#F2B84B] text-[#071A3A] font-bold"
                          : "bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800"
                      }`}
                    >
                      {chip.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Article Cards List */}
              <div className="flex-1 overflow-y-auto p-2 space-y-2">
                {filteredArticles.length === 0 ? (
                  <div className="p-6 text-center text-xs text-slate-500">
                    {isId ? "Tidak ada artikel yang cocok." : "No articles found."}
                  </div>
                ) : (
                  filteredArticles.map((art) => {
                    const isSelected = selectedArticle?.slug === art.slug;
                    return (
                      <div
                        key={art.slug}
                        onClick={() => handleSelect(art)}
                        className={`p-3 rounded-xl border cursor-pointer transition-all ${
                          isSelected
                            ? "border-[#F2B84B] bg-[#10264A] shadow-md ring-1 ring-[#F2B84B]/20"
                            : "border-slate-800/80 bg-slate-900/40 hover:border-slate-700 hover:bg-slate-800/40"
                        }`}
                      >
                        <div className="flex items-center justify-between text-[10px] mb-1">
                          <span className="rounded bg-slate-800 px-1.5 py-0.5 text-[#F2B84B] font-mono font-semibold">
                            {art.engine}
                          </span>
                          <span className="text-slate-500">{art.readTime || "5 min read"}</span>
                        </div>
                        <h3 className="text-xs font-bold text-white leading-snug line-clamp-2">
                          {art.title}
                        </h3>
                        <p className="mt-1 text-[11px] text-slate-400 line-clamp-2 leading-relaxed">
                          {art.summary}
                        </p>
                      </div>
                    );
                  })
                )}
              </div>
            </aside>

            {/* Reader Pane */}
            <main
              className={`${
                mobileViewingArticle ? "flex" : "hidden"
              } lg:flex flex-1 flex-col overflow-y-auto bg-[#071A3A]`}
            >
              {selectedArticle ? (
                <div className="mx-auto w-full max-w-4xl p-4 sm:p-8">
                  {/* Mobile Back Button */}
                  <button
                    onClick={() => setMobileViewingArticle(false)}
                    className="lg:hidden mb-4 flex items-center gap-1.5 text-xs text-[#F2B84B] font-semibold"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    <span>{isId ? "Kembali ke Daftar Artikel" : "Back to Article List"}</span>
                  </button>

                  {/* Article Header */}
                  <div className="border-b border-slate-800 pb-5 mb-6">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <span className="rounded-lg bg-[#F2B84B]/20 border border-[#F2B84B]/40 px-2.5 py-0.5 text-xs font-bold text-[#F2B84B]">
                        {selectedArticle.engine}
                      </span>
                      <span className="text-xs text-slate-400">
                        {selectedArticle.readTime || "6 min read"}
                      </span>
                    </div>

                    <h1 className="text-xl sm:text-2xl font-bold text-white mb-3 leading-snug">
                      {selectedArticle.title}
                    </h1>

                    <p className="text-sm text-slate-300 leading-relaxed bg-[#10264A]/30 p-3 rounded-xl border border-slate-800">
                      {selectedArticle.summary}
                    </p>
                  </div>

                  {/* Markdown Body */}
                  <div className="my-4">
                    <ArticleMarkdown content={articleBodyToRender} />
                  </div>

                  {/* Quick Action Footer */}
                  <div className="mt-8 border-t border-slate-800 pt-5 flex items-center justify-between flex-wrap gap-3">
                    <span className="text-xs text-slate-400">
                      {isId
                        ? "Ingin menguji kueri pada mesin ini secara langsung?"
                        : "Ready to test queries on this engine?"}
                    </span>
                    <button
                      onClick={onOpenLab}
                      className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#F2B84B] to-[#D99A32] px-4 py-2 text-xs font-bold text-[#071A3A] hover:opacity-95 shadow-md transition-all"
                    >
                      <Database className="h-4 w-4" />
                      <span>{isId ? "Buka di Query Studio" : "Open in Query Studio"}</span>
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center text-slate-500">
                  {isId ? "Pilih artikel dari daftar." : "Select an article from the list."}
                </div>
              )}
            </main>
          </div>
        )}

        {activeSection === "visual" && (
          <div className="flex-1 overflow-y-auto">
            <VisualDatabaseAcademy language={language} onOpenLab={onOpenLab} />
          </div>
        )}

        {activeSection === "glossary" && (
          <div className="flex-1 overflow-y-auto">
            <GlossaryExplorer language={language} />
          </div>
        )}

        {activeSection === "comparison" && (
          <div className="flex-1 overflow-y-auto">
            <CrossComparisonMatrix language={language} />
          </div>
        )}

        {activeSection === "handbook" && (
          <div className="flex-1 overflow-y-auto">
            <DbaHandbookIncidents language={language} />
          </div>
        )}
      </div>
    </div>
  );
}
