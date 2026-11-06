import re
import secrets
import sqlite3
import time
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import psycopg
import pymysql

from app.adapters.sqlite import SQLiteAdapter
from app.adapters.oracle import OracleAdapter
from app.adapters.mssql import MSSQLAdapter
from app.config import settings
from app.templates.datasets import TEMPLATES
import sqlglot

router = APIRouter(prefix="/learning", tags=["Learning"])

CHALLENGES = [
    {
        "slug": "low-stock-alert",
        "title": "Restock Warning Alert",
        "title_id": "Peringatan Stok Barang Menipis",
        "level": "Beginner",
        "category": "Data Filtering",
        "category_id": "Penyaringan Data",
        "dataset": "ecommerce",
        "description": "Select product name, price, and stock for all products where stock is strictly less than 35 units, ordered by stock ascending.",
        "description_id": "Pilih kolom name, price, dan stock untuk semua produk dengan stok kurang dari 35 unit, diurutkan dari stok paling sedikit.",
        "expected_columns": ["name", "price", "stock"],
        "solution_sql": """SELECT name, price, stock
FROM products
WHERE stock < 35
ORDER BY stock ASC;""",
        "starter_sql": """-- Tulis kueri penyaringan produk dengan stok < 35:
SELECT name, price, stock
FROM products
WHERE stock < 35
ORDER BY stock ASC;""",
        "hints": [
            "Use the WHERE clause with condition 'stock < 35'.",
            "Sort the final rows using 'ORDER BY stock ASC'."
        ],
        "hints_id": [
            "Gunakan klausul WHERE dengan kondisi 'stock < 35'.",
            "Urutkan baris hasil akhir menggunakan 'ORDER BY stock ASC'."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "academic-grade-a",
        "title": "Honors List: Grade A Students",
        "title_id": "Daftar Mahasiswa Berprestasi (Nilai A)",
        "level": "Beginner",
        "category": "Multi-table JOINs",
        "category_id": "Relasi Multi-Tabel",
        "dataset": "school",
        "description": "Find student name (as student_name), course title (as course_title), and grade for all enrollments with grade 'A'. Sort alphabetically by student_name ascending.",
        "description_id": "Temukan nama mahasiswa (student_name), judul mata kuliah (course_title), dan nilai untuk semua pendaftaran bernilai 'A'. Urutkan alfabetis dari student_name.",
        "expected_columns": ["student_name", "course_title", "grade"],
        "solution_sql": """SELECT s.name AS student_name, c.title AS course_title, e.grade
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
WHERE e.grade = 'A'
ORDER BY s.name ASC;""",
        "starter_sql": """-- Hubungkan tabel enrollments, students, dan courses:
SELECT s.name AS student_name, c.title AS course_title, e.grade
FROM enrollments e
-- Lengkapi JOIN dan kondisi WHERE:
""",
        "hints": [
            "JOIN enrollments to students on e.student_id = s.id.",
            "JOIN enrollments to courses on e.course_id = c.id.",
            "Add filter WHERE e.grade = 'A' and alias columns with AS student_name and AS course_title."
        ],
        "hints_id": [
            "Lakukan JOIN antara enrollments ke students pada e.student_id = s.id.",
            "Lakukan JOIN ke courses pada e.course_id = c.id.",
            "Tambahkan filter WHERE e.grade = 'A' dan gunakan alias kolom AS student_name dan AS course_title."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "banking-priority-accounts",
        "title": "Priority Banking Balances (> IDR 30M)",
        "title_id": "Audit Saldo Nasabah Prioritas (> 30 Juta)",
        "level": "Intermediate",
        "category": "Filtering & Joins",
        "category_id": "Filter & Relasi",
        "dataset": "banking",
        "description": "Select customer full_name, account_number, account_type, and balance for accounts with status 'ACTIVE' and balance greater than 30,000,000. Sort by balance descending.",
        "description_id": "Tampilkan full_name nasabah, account_number, account_type, dan balance untuk rekening berstatus 'ACTIVE' dengan saldo di atas 30.000.000, diurutkan dari saldo tertinggi.",
        "expected_columns": ["full_name", "account_number", "account_type", "balance"],
        "solution_sql": """SELECT c.full_name, a.account_number, a.account_type, a.balance
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.status = 'ACTIVE' AND a.balance > 30000000.0
ORDER BY a.balance DESC;""",
        "starter_sql": """-- Tulis query nasabah prioritas:
SELECT c.full_name, a.account_number, a.account_type, a.balance
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
-- Lengkapi filter WHERE dan pengurutan ORDER BY:
""",
        "hints": [
            "Join accounts and customers using customer_id.",
            "Apply two conditions in WHERE: a.status = 'ACTIVE' AND a.balance > 30000000.0.",
            "Sort with ORDER BY a.balance DESC."
        ],
        "hints_id": [
            "Gabungkan accounts dan customers menggunakan customer_id.",
            "Gunakan dua filter pada WHERE: a.status = 'ACTIVE' AND a.balance > 30000000.0.",
            "Urutkan dengan ORDER BY a.balance DESC."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "top-spending-customers",
        "title": "Top Spending Customers",
        "title_id": "Pelanggan dengan Pengeluaran Terbesar",
        "level": "Intermediate",
        "category": "Aggregation & Grouping",
        "category_id": "Agregasi & Pengelompokan",
        "dataset": "ecommerce",
        "description": "Calculate total spending per customer with completed orders. Return first_name, city, and total_spent (sum of total_amount), ordered by total_spent descending, limited to 5 rows.",
        "description_id": "Hitung total pengeluaran per pelanggan berpesanan 'completed'. Tampilkan first_name, city, dan total_spent (jumlah total_amount), diurutkan dari pengeluaran terbanyak, batas 5 baris.",
        "expected_columns": ["first_name", "city", "total_spent"],
        "solution_sql": """SELECT c.first_name, c.city, SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id, c.first_name, c.city
ORDER BY total_spent DESC
LIMIT 5;""",
        "starter_sql": """SELECT c.first_name, c.city, SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
-- Tambahkan WHERE, GROUP BY, ORDER BY, dan LIMIT:
GROUP BY c.id, c.first_name, c.city;""",
        "hints": [
            "Filter only completed orders with WHERE o.status = 'completed'.",
            "Group by customer id and name columns.",
            "Use ORDER BY total_spent DESC and LIMIT 5."
        ],
        "hints_id": [
            "Saring hanya pesanan selesai dengan WHERE o.status = 'completed'.",
            "Kelompokkan dengan GROUP BY c.id, c.first_name, c.city.",
            "Gunakan ORDER BY total_spent DESC dan LIMIT 5."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "high-volume-authors",
        "title": "High Volume Blog Authors",
        "title_id": "Penulis Artikel Produktif (> 1 Postingan)",
        "level": "Intermediate",
        "category": "HAVING Clause",
        "category_id": "Klausul HAVING",
        "dataset": "blog",
        "description": "Find authors who have published strictly more than 1 post. Display author username, post count as post_count, and total views across their posts as total_views, sorted by total_views descending.",
        "description_id": "Cari penulis dengan lebih dari 1 artikel. Tampilkan username, jumlah artikel sebagai post_count, dan total pembaca sebagai total_views, diurutkan dari total_views terbesar.",
        "expected_columns": ["username", "post_count", "total_views"],
        "solution_sql": """SELECT a.username, COUNT(p.id) AS post_count, SUM(p.views) AS total_views
FROM authors a
JOIN posts p ON a.id = p.author_id
GROUP BY a.id, a.username
HAVING COUNT(p.id) > 1
ORDER BY total_views DESC;""",
        "starter_sql": """-- Gunakan COUNT, SUM, GROUP BY dan HAVING:
SELECT a.username, COUNT(p.id) AS post_count, SUM(p.views) AS total_views
FROM authors a
JOIN posts p ON a.id = p.author_id
GROUP BY a.id, a.username;""",
        "hints": [
            "Use COUNT(p.id) for post count and SUM(p.views) for total views.",
            "Filter grouped results using HAVING COUNT(p.id) > 1.",
            "Sort with ORDER BY total_views DESC."
        ],
        "hints_id": [
            "Gunakan COUNT(p.id) untuk menghitung post dan SUM(p.views) untuk total tayangan.",
            "Filter kelompok hasil agregasi menggunakan HAVING COUNT(p.id) > 1.",
            "Urutkan hasil dengan ORDER BY total_views DESC."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "monthly-transfer-channels",
        "title": "Banking Transfer Channels Volume",
        "title_id": "Volume Transaksi Saluran Transfer Perbankan",
        "level": "Intermediate",
        "category": "Aggregation",
        "category_id": "Agregasi Keuangan",
        "dataset": "banking",
        "description": "Calculate total volume and average fee for transactions with transaction_type = 'TRANSFER', grouped by channel. Display channel, total_volume (sum of amount), and avg_fee (average fee), ordered by total_volume descending.",
        "description_id": "Hitung total volume dan rata-rata biaya transfer untuk jenis 'TRANSFER' per saluran perbankan. Tampilkan channel, total_volume, dan avg_fee, diurutkan dari total volume tertinggi.",
        "expected_columns": ["channel", "total_volume", "avg_fee"],
        "solution_sql": """SELECT channel, SUM(amount) AS total_volume, AVG(fee) AS avg_fee
FROM transactions
WHERE transaction_type = 'TRANSFER'
GROUP BY channel
ORDER BY total_volume DESC;""",
        "starter_sql": """-- Analisis transfer per channel perbankan:
SELECT channel, SUM(amount) AS total_volume, AVG(fee) AS avg_fee
FROM transactions
WHERE transaction_type = 'TRANSFER'
GROUP BY channel
ORDER BY total_volume DESC;""",
        "hints": [
            "Filter WHERE transaction_type = 'TRANSFER'.",
            "Group by channel and calculate SUM(amount) AS total_volume and AVG(fee) AS avg_fee."
        ],
        "hints_id": [
            "Filter dengan WHERE transaction_type = 'TRANSFER'.",
            "Kelompokkan berdasarkan channel dan hitung SUM(amount) serta AVG(fee)."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "dormant-customers-anti-join",
        "title": "Dormant Customers (Anti-Join)",
        "title_id": "Pelanggan Pasif Tanpa Transaksi (Anti-Join)",
        "level": "Intermediate",
        "category": "Anti-Join Pattern",
        "category_id": "Pola Anti-Join",
        "dataset": "ecommerce",
        "description": "Identify registered customers who have never placed any order. Return id, first_name, last_name, and email, sorted by customer id ascending.",
        "description_id": "Temukan pelanggan terdaftar yang belum pernah memesan barang sama sekali. Tampilkan id, first_name, last_name, dan email, diurutkan dari id terkecil.",
        "expected_columns": ["id", "first_name", "last_name", "email"],
        "solution_sql": """SELECT c.id, c.first_name, c.last_name, c.email
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL
ORDER BY c.id ASC;""",
        "starter_sql": """-- Tulis query Anti-Join menggunakan LEFT JOIN dan WHERE ... IS NULL:
SELECT c.id, c.first_name, c.last_name, c.email
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL
ORDER BY c.id ASC;""",
        "hints": [
            "Use a LEFT JOIN from customers to orders.",
            "Filter for unmatched records using WHERE o.id IS NULL.",
            "Order by c.id ASC."
        ],
        "hints_id": [
            "Gunakan LEFT JOIN dari tabel customers ke orders.",
            "Saring baris yang tidak memiliki pasangan pesanan dengan WHERE o.id IS NULL.",
            "Urutkan dengan ORDER BY c.id ASC."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "cumulative-transaction-ledger",
        "title": "Cumulative Running Total Audit",
        "title_id": "Buku Kas Akumulasi Saldo Berjalan (Window Function)",
        "level": "Advanced",
        "category": "Window Functions",
        "category_id": "Fungsi Jendela (Window)",
        "dataset": "banking",
        "description": "Compute the running cumulative transaction amount across all banking transactions. Display transaction_id, reference_no, amount, and running_total (cumulative sum of amount ordered by transaction_id ascending), sorted by transaction_id ascending.",
        "description_id": "Hitung akumulasi jumlah transaksi kumulatif berjalan. Tampilkan transaction_id, reference_no, amount, dan running_total (akumulasi jumlah bertahap diurutkan dari transaction_id ASC).",
        "expected_columns": ["transaction_id", "reference_no", "amount", "running_total"],
        "solution_sql": """SELECT transaction_id, reference_no, amount,
       SUM(amount) OVER (ORDER BY transaction_id ASC) AS running_total
FROM transactions
ORDER BY transaction_id ASC;""",
        "starter_sql": """-- Terapkan Window Function SUM(...) OVER (ORDER BY ...):
SELECT transaction_id, reference_no, amount,
       SUM(amount) OVER (ORDER BY transaction_id ASC) AS running_total
FROM transactions
ORDER BY transaction_id ASC;""",
        "hints": [
            "Use the window aggregate syntax: SUM(amount) OVER (ORDER BY transaction_id ASC).",
            "Assign alias AS running_total.",
            "Keep the outer ORDER BY transaction_id ASC."
        ],
        "hints_id": [
            "Gunakan sintaks fungsi jendela: SUM(amount) OVER (ORDER BY transaction_id ASC).",
            "Beri alias AS running_total.",
            "Pastikan query luar diurutkan dengan ORDER BY transaction_id ASC."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "product-price-category-rank",
        "title": "Category Price Ranking (DENSE_RANK)",
        "title_id": "Peringkat Harga per Kategori (DENSE_RANK)",
        "level": "Advanced",
        "category": "Window Ranking",
        "category_id": "Peringkat Jendela",
        "dataset": "ecommerce",
        "description": "Rank products by price within each category from highest to lowest. Return category_id, name, price, and price_rank using DENSE_RANK() partitioned by category_id and ordered by price descending. Sort final output by category_id ASC, price_rank ASC.",
        "description_id": "Urutkan produk berdasarkan harga tertinggi dalam setiap kategori. Tampilkan category_id, name, price, dan price_rank menggunakan DENSE_RANK() dipartisi per category_id dan diurutkan dari harga termahal. Urutkan output akhir berdasarkan category_id ASC, price_rank ASC.",
        "expected_columns": ["category_id", "name", "price", "price_rank"],
        "solution_sql": """SELECT category_id, name, price,
       DENSE_RANK() OVER (PARTITION BY category_id ORDER BY price DESC) AS price_rank
FROM products
ORDER BY category_id ASC, price_rank ASC;""",
        "starter_sql": """-- Terapkan DENSE_RANK() OVER (PARTITION BY ... ORDER BY ...):
SELECT category_id, name, price,
       DENSE_RANK() OVER (PARTITION BY category_id ORDER BY price DESC) AS price_rank
FROM products
ORDER BY category_id ASC, price_rank ASC;""",
        "hints": [
            "Partition the ranking window using PARTITION BY category_id.",
            "Order within each category window using ORDER BY price DESC.",
            "Outer sorting should be ORDER BY category_id ASC, price_rank ASC."
        ],
        "hints_id": [
            "Partisi jendela ranking menggunakan PARTITION BY category_id.",
            "Urutkan dalam jendela kategori dengan ORDER BY price DESC.",
            "Pengurutan luar harus berupa ORDER BY category_id ASC, price_rank ASC."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
    {
        "slug": "category-revenue-cte",
        "title": "Category Revenue Contribution (CTE)",
        "title_id": "Kontribusi Pendapatan Kategori (Common Table Expression)",
        "level": "Advanced",
        "category": "Common Table Expressions",
        "category_id": "Ekspresi Tabel Umum (CTE)",
        "dataset": "ecommerce",
        "description": "Using a Common Table Expression (WITH clause), calculate the total revenue generated per category. Display category_name (from categories.name) and total_revenue (sum of quantity * unit_price from order_items), sorted by total_revenue descending.",
        "description_id": "Gunakan Common Table Expression (klausa WITH) untuk menghitung total pendapatan per kategori. Tampilkan category_name (dari categories.name) dan total_revenue (jumlah quantity * unit_price), diurutkan dari total_revenue terbesar.",
        "expected_columns": ["category_name", "total_revenue"],
        "solution_sql": """WITH category_sales AS (
    SELECT p.category_id, SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    GROUP BY p.category_id
)
SELECT c.name AS category_name, cs.total_revenue
FROM category_sales cs
JOIN categories c ON cs.category_id = c.id
ORDER BY cs.total_revenue DESC;""",
        "starter_sql": """-- Definisikan CTE category_sales lalu gabungkan dengan categories:
WITH category_sales AS (
    SELECT p.category_id, SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    GROUP BY p.category_id
)
SELECT c.name AS category_name, cs.total_revenue
FROM category_sales cs
JOIN categories c ON cs.category_id = c.id
ORDER BY cs.total_revenue DESC;""",
        "hints": [
            "Define the CTE with: WITH category_sales AS (SELECT ... GROUP BY p.category_id).",
            "Calculate revenue as SUM(oi.quantity * oi.unit_price).",
            "Join the CTE with categories on cs.category_id = c.id and order by total_revenue DESC."
        ],
        "hints_id": [
            "Definisikan CTE dengan: WITH category_sales AS (SELECT ... GROUP BY p.category_id).",
            "Hitung total pendapatan dengan SUM(oi.quantity * oi.unit_price).",
            "Hubungkan CTE dengan tabel categories pada cs.category_id = c.id dan urutkan dari total_revenue terbesar."
        ],
        "supported_engines": ["sqlite", "postgres", "mysql"],
    },
]


PROFESSIONS = [
    {
        "id": "dba",
        "title": "Database Administrator (DBA)",
        "title_id": "Administrator Basis Data (DBA)",
        "category": "Operations & Reliability",
        "category_id": "Operasional & Keandalan",
        "summary": "Architects, provisions, monitors, and safeguards enterprise database instances to ensure 24/7 uptime, high performance, and rapid disaster recovery.",
        "summary_id": "Merancang, mengelola, memantau, dan menjaga cluster database perusahaan untuk memastikan uptime 24/7, performa maksimal, dan pemulihan bencana instan.",
        "engines": ["PostgreSQL", "MySQL", "Oracle", "SQL Server"],
        "recommended_tools": ["pmm", "pgbackrest", "xtrabackup", "prometheus", "dbeaver"],
        "core_responsibilities": [
            "Maintain database high availability (HA) and automated failover clusters (Patroni / Orchestrator)",
            "Design and test backup strategies (Full, Differential, Point-In-Time Recovery / PITR)",
            "Monitor server resource consumption (Buffer cache hit ratio, lock waits, replication lag)",
            "Perform major version upgrades with zero or near-zero maintenance downtime",
        ],
        "core_responsibilities_id": [
            "Memelihara klaster ketersediaan tinggi (HA) dan failover otomatis (Patroni / Orchestrator)",
            "Merancang dan menguji strategi pencadangan (Full, Diferensial, PITR)",
            "Memantau konsumsi sumber daya (Buffer cache hit ratio, lock wait, lag replikasi)",
            "Melakukan upgrade versi mayor dengan zero-downtime atau downtime minimal",
        ],
        "skills_progression": {
            "junior": [
                "SQL DDL/DML syntax across multiple engines",
                "Logical backup & restore (pg_dump, mysqldump)",
                "User management & privilege grants (least privilege)",
                "Basic configuration tuning (memory limits, connection pools)",
            ],
            "mid": [
                "Physical hot backup configuration (pgBackRest, XtraBackup)",
                "Active-passive & streaming replication topology setup",
                "Slow query log analysis and index defragmentation",
                "Connection pooler deployment (PgBouncer, ProxySQL)",
            ],
            "senior": [
                "Multi-region active-active cluster architecture",
                "Automated chaos engineering & disaster recovery drills",
                "Advanced performance telemetry via eBPF and kernel tuning",
                "Automated migration pipelines and database sharding",
            ],
        },
        "key_metrics": [
            "Replication Lag (seconds / bytes behind master)",
            "Cache Hit Ratio (> 99% target)",
            "Active Connection Utilization (< 80% pool capacity)",
            "Lock Contention & Deadlock Frequency",
        ],
        "runbooks": [
            {
                "name": "Replication Lag Emergency Remediation",
                "name_id": "Penanganan Darurat Lag Replikasi",
                "steps": [
                    "Inspect replica I/O thread and SQL thread status",
                    "Identify blocking long-running analytical queries on replica",
                    "Increase parallel worker threads (e.g., slave_parallel_workers)",
                    "If gap exceeds SLA, reroute read traffic to healthy nodes",
                ],
            },
            {
                "name": "Point-in-Time Recovery (PITR) Execution",
                "name_id": "Eksekusi Point-in-Time Recovery (PITR)",
                "steps": [
                    "Isolate target restore node from production traffic",
                    "Fetch latest consistent base backup from object storage",
                    "Replay WAL / Binlog stream up to the exact target timestamp",
                    "Verify data consistency and promote node as primary",
                ],
            },
        ],
        "recommended_challenges": [
            "banking-priority-accounts",
            "monthly-transfer-channels",
            "cumulative-transaction-ledger",
        ],
    },
    {
        "id": "data-engineer",
        "title": "Backend & Data Engineer",
        "title_id": "Insinyur Backend & Data",
        "category": "Software Architecture",
        "category_id": "Arsitektur Perangkat Lunak",
        "summary": "Designs relational schemas, writes high-throughput queries, avoids ORM anti-patterns, and builds reliable ETL/ELT data pipelines.",
        "summary_id": "Merancang skema relasional efisien, menulis kueri throughput tinggi, mencegah anti-pattern ORM, dan membangun pipa data ETL/ELT terpercaya.",
        "engines": ["PostgreSQL", "MySQL", "SQLite", "SQL Server"],
        "recommended_tools": ["bytebase", "flyway", "pgmustard", "litecli", "dbeaver"],
        "core_responsibilities": [
            "Design normalized (3NF) relational models and denormalized analytical tables",
            "Optimize database access layers in application code (eliminate N+1 query patterns)",
            "Execute zero-downtime schema migrations using expand-contract patterns",
            "Build robust transactional boundaries and concurrency controls (Optimistic / Pessimistic locking)",
        ],
        "core_responsibilities_id": [
            "Merancang model relasional normal (3NF) dan tabel denormalisasi analitik",
            "Mengoptimalkan layer akses database di kode backend (mengatasi kueri N+1)",
            "Mengeksekusi migrasi skema tanpa downtime menggunakan pola expand-contract",
            "Membangun batasan transaksi kuat dan kontrol konkurensi (Optimistic / Pessimistic locking)",
        ],
        "skills_progression": {
            "junior": [
                "Table design with appropriate data types and constraints",
                "Multi-table JOINs and standard aggregations",
                "Writing clean migration scripts using Flyway / Alembic",
                "Basic understanding of transaction isolation levels",
            ],
            "mid": [
                "Composite indexing strategy based on query predicate selectivity",
                "Common Table Expressions (CTEs) and Window functions",
                "Batch processing with pagination (keyset / cursor-based pagination)",
                "Connection lifecycle management in microservices",
            ],
            "senior": [
                "High-volume CDC (Change Data Capture) pipelines with Debezium",
                "Polyglot persistence architecture (Relational + Cache + Search)",
                "Design for distributed transactions (Saga pattern vs 2PC)",
                "Declarative database CI/CD and automated schema linting",
            ],
        },
        "key_metrics": [
            "Query Latency p95 and p99 (< 50ms target)",
            "Query Execution Plan Cost & Temp Spill to Disk",
            "Migration Execution Duration & Table Lock Time",
            "ORM Query Amplification Ratio (Queries per API Request)",
        ],
        "runbooks": [
            {
                "name": "Zero-Downtime Column Addition & Migration",
                "name_id": "Penambahan Kolom & Migrasi Skema Zero-Downtime",
                "steps": [
                    "Add new nullable column without heavy locks",
                    "Deploy dual-writing backend code to write to old and new columns",
                    "Backfill existing records in controlled batches",
                    "Switch reads to new column and deprecate old column",
                ],
            },
        ],
        "recommended_challenges": [
            "top-spending-customers",
            "dormant-customers-anti-join",
            "category-revenue-cte",
        ],
    },
    {
        "id": "data-analyst",
        "title": "Data Analyst & BI Specialist",
        "title_id": "Analis Data & Spesialis BI",
        "category": "Analytics & Business Intelligence",
        "category_id": "Analitik & Kecerdasan Bisnis",
        "summary": "Unlocks strategic insights from relational data through advanced SQL, window functions, statistical aggregations, and dimensional modeling.",
        "summary_id": "Menghasilkan wawasan strategis dari data relasional melalui SQL tingkat lanjut, window function, agregasi statistik, dan pemodelan dimensional.",
        "engines": ["PostgreSQL", "SQLite", "Oracle", "MySQL"],
        "recommended_tools": ["dbeaver", "grafana", "litecli"],
        "core_responsibilities": [
            "Author complex analytical SQL queries (Window functions, cohorts, rolling averages)",
            "Build clean dimensional reporting models (Star Schema / Snowflake Schema)",
            "Create performant database views and materialized views for reporting dashboards",
            "Validate data quality and business metrics against financial ledgers",
        ],
        "core_responsibilities_id": [
            "Menulis kueri SQL analitik kompleks (Fungsi jendela, kohort, rata-rata bergerak)",
            "Membangun model pelaporan dimensional yang bersih (Star Schema / Snowflake Schema)",
            "Membuat database view dan materialized view performa tinggi untuk dashboard",
            "Memvalidasi kualitas data dan akurasi metrik bisnis terhadap buku kas keuangan",
        ],
        "skills_progression": {
            "junior": [
                "Filtering, sorting, and conditional aggregations (CASE WHEN)",
                "GROUP BY, HAVING, and multi-table INNER/LEFT JOINs",
                "Extracting metrics into clean CSV/Excel reports",
                "Date/Time manipulations across database dialects",
            ],
            "mid": [
                "Ranking functions (ROW_NUMBER, RANK, DENSE_RANK)",
                "Cumulative running totals and sliding frame aggregations (ROWS BETWEEN)",
                "Recursive CTEs for hierarchical and tree data navigation",
                "Creating and refreshing materialized views with indexes",
            ],
            "senior": [
                "Advanced statistical analysis in SQL (percentiles, regression, histograms)",
                "Designing self-service data marts for non-technical stakeholders",
                "Optimizing query performance for multi-terabyte data warehouses",
                "Building automated data quality verification tests in SQL",
            ],
        },
        "key_metrics": [
            "Dashboard Refresh Time (< 5s target)",
            "Analytical Query Compute Cost & Memory Usage",
            "Data Accuracy & Reconciliation Match Rate (100%)",
            "Report Delivery SLA Adherence",
        ],
        "runbooks": [
            {
                "name": "Slow Dashboard Query Troubleshooting",
                "name_id": "Troubleshooting Query Dashboard yang Lambat",
                "steps": [
                    "Inspect EXPLAIN plan for full table scans on historical partitions",
                    "Add covering composite index for filter and aggregation columns",
                    "Convert real-time join calculation to a scheduled Materialized View",
                    "Verify dashboard latency drops below 2 seconds",
                ],
            },
        ],
        "recommended_challenges": [
            "product-price-category-rank",
            "cumulative-transaction-ledger",
            "category-revenue-cte",
            "high-volume-authors",
        ],
    },
    {
        "id": "dbre",
        "title": "Site Reliability Engineer (Database SRE / DBRE)",
        "title_id": "Insinyur Keandalan Situs (DBRE / SRE)",
        "category": "Infrastructure & Telemetry",
        "category_id": "Infrastruktur & Telemetri",
        "summary": "Applies software engineering disciplines to database operations, defining SLOs/SLIs, building automated telemetry pipelines, and orchestrating self-healing topologies.",
        "summary_id": "Menerapkan disiplin rekayasa perangkat lunak pada operasional database, merumuskan SLO/SLI, membangun telemetri otomatis, dan orkestrasi arsitektur self-healing.",
        "engines": ["PostgreSQL", "MySQL", "Oracle", "SQL Server"],
        "recommended_tools": ["prometheus", "grafana", "pmm", "pgmustard"],
        "core_responsibilities": [
            "Define and monitor Database Service Level Objectives (SLOs: 99.99% availability, p99 latency < 20ms)",
            "Maintain Prometheus metric exporters and Grafana alert rule pipelines",
            "Automate infrastructure provisioning via Infrastructure-as-Code (Terraform / Ansible)",
            "Conduct automated disaster recovery and chaos engineering drills",
        ],
        "core_responsibilities_id": [
            "Menentukan dan memantau SLO database (Ketersediaan 99.99%, latensi p99 < 20ms)",
            "Memelihara exporter metrik Prometheus dan pipeline aturan peringatan Grafana",
            "Mengotomatiskan penyediaan infrastruktur melalui IaC (Terraform / Ansible)",
            "Melakukan latihan pemulihan bencana otomatis dan pengujian chaos engineering",
        ],
        "skills_progression": {
            "junior": [
                "Linux OS performance fundamentals (CPU, I/O wait, memory buffers, disk queues)",
                "Configuring Prometheus scrape targets and node/database exporters",
                "Basic containerization and orchestration for database sidecars",
                "Incident triage and logging aggregation (Loki, Elasticsearch)",
            ],
            "mid": [
                "SLO / Error Budget alerting strategies (multi-window burn rate alerts)",
                "Kernel sysctl parameter tuning for heavy database I/O (`vm.dirty_ratio`, `swappiness`)",
                "Automated snapshot verification and restore validation bots",
                "Distributed tracing across application and database layers (OpenTelemetry)",
            ],
            "senior": [
                "Autonomous self-healing cluster orchestration and split-brain prevention (etcd, Raft)",
                "Global multi-cloud active replication topologies with automatic traffic steering",
                "Capacity forecasting models using machine learning on Prometheus telemetry",
                "Zero-downtime kernel live-patching and security automation",
            ],
        },
        "key_metrics": [
            "SLO Error Budget Burn Rate",
            "Storage IOPS & Disk Queue Depth",
            "Connection Pool Saturation Ratio",
            "MTTR (Mean Time to Resolution) during Failovers (< 30s)",
        ],
        "runbooks": [
            {
                "name": "Automated Primary Failover Verification",
                "name_id": "Verifikasi Failover Primary Otomatis",
                "steps": [
                    "Verify consensus quorum in distributed coordination store (e.g. etcd)",
                    "Confirm replica has fully applied WAL/Binlog stream with zero transaction loss",
                    "Promote replica to primary and update virtual IP / DNS endpoint",
                    "Demote previous primary to standby upon recovery",
                ],
            },
        ],
        "recommended_challenges": [
            "banking-priority-accounts",
            "cumulative-transaction-ledger",
        ],
    },
    {
        "id": "security-auditor",
        "title": "Database Security & Compliance Specialist",
        "title_id": "Spesialis Keamanan & Kepatuhan Database",
        "category": "Security & Governance",
        "category_id": "Keamanan & Tata Kelola",
        "summary": "Enforces cryptographic protection, fine-grained access governance, audit logging, and regulatory compliance (PCI-DSS, SOC 2, GDPR, HIPAA) across all enterprise database tiers.",
        "summary_id": "Menerapkan proteksi kriptografis, tata kelola akses mendalam, audit logging, dan kepatuhan regulasi (PCI-DSS, SOC 2, GDPR, HIPAA) pada seluruh tier database perusahaan.",
        "engines": ["PostgreSQL", "Oracle", "SQL Server", "MySQL"],
        "recommended_tools": ["bytebase", "dbeaver", "pmm"],
        "core_responsibilities": [
            "Implement Role-Based Access Control (RBAC) and Row-Level Security (RLS) policies",
            "Configure Transparent Data Encryption (TDE) at rest and TLS 1.3 in transit",
            "Audit privileged user activity and detect anomalous data exfiltration queries",
            "Automate PII data masking in staging and development sandboxes",
        ],
        "core_responsibilities_id": [
            "Menerapkan Role-Based Access Control (RBAC) dan kebijakan Row-Level Security (RLS)",
            "Mengonfigurasi Transparent Data Encryption (TDE) saat diam dan TLS 1.3 saat transmisi",
            "Mengaudit aktivitas pengguna istimewa dan mendeteksi kueri eksfiltrasi data anomali",
            "Mengotomatiskan penyamaran data PII pada sandbox staging dan development",
        ],
        "skills_progression": {
            "junior": [
                "Principle of Least Privilege: granting precise table and column permissions",
                "Configuring secure TLS connection certificates for database clients",
                "Password complexity, rotation policies, and connection timeout rules",
                "Reviewing database audit logs for unauthorized access attempts",
            ],
            "mid": [
                "Implementing Row-Level Security (RLS) policies in PostgreSQL / Oracle",
                "Transparent Data Encryption (TDE) and key management integration (Vault / KMS)",
                "Dynamic data masking for sensitive fields (credit cards, national IDs)",
                "SQL injection vulnerability assessment and parameterized query enforcement",
            ],
            "senior": [
                "Zero-Trust database access architecture with ephemeral credentials",
                "Regulatory audit defense and continuous compliance reporting (SOC 2, ISO 27001)",
                "Hardware Security Module (HSM) key lifecycle management",
                "Automated anomaly detection for suspicious bulk SELECT patterns",
            ],
        },
        "key_metrics": [
            "Privileged Account Exposure Count (Target: Minimal/Ephemeral)",
            "Unencrypted Connection Rate (Target: 0%)",
            "Audit Trail Coverage Rate (100% of DDL & DCL statements)",
            "Vulnerability Remediation Mean Time (MTTR < 7 days)",
        ],
        "runbooks": [
            {
                "name": "Row-Level Security (RLS) Policy Implementation",
                "name_id": "Penerapan Kebijakan Row-Level Security (RLS)",
                "steps": [
                    "Enable RLS on target table (`ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;`)",
                    "Define tenant isolation policy based on session variable `current_setting('app.current_tenant_id')`",
                    "Verify standard user cannot read cross-tenant rows even with `SELECT *`",
                    "Log policy violations to centralized SIEM security collector",
                ],
            },
        ],
        "recommended_challenges": [
            "banking-priority-accounts",
            "academic-grade-a",
        ],
    },
]


class ChallengeSubmitRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    language: str = "id"
    engine: str = "sqlite"


class ChallengeSubmitResponse(BaseModel):
    passed: bool
    message: str
    row_count: int
    expected_row_count: int
    user_columns: list[str]
    expected_columns: list[str]
    sample_user_rows: list[list[Any]] = []
    sample_expected_rows: list[list[Any]] = []
    elapsed_ms: float
    feedback: list[str]
    hints: list[str] = []


def _execute_sqlite(dataset_slug: str, ref_sql: str, user_sql: str) -> tuple[list[str], list[list[Any]], list[str], list[list[Any]], float, str | None]:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]
    conn.executescript(seed_sql)

    cur_ref = conn.execute(ref_sql)
    ref_columns = [d[0] for d in cur_ref.description]
    ref_rows = [list(r) for r in cur_ref.fetchall()]

    adapter = SQLiteAdapter()
    adapter._conn = conn
    start_time = time.perf_counter()
    user_res = adapter.execute(user_sql, max_rows=100, read_only=True)
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    conn.close()

    if not user_res.get("success"):
        return ref_columns, ref_rows, [], [], elapsed_ms, user_res.get("error")
    return ref_columns, ref_rows, user_res.get("columns", []), user_res.get("rows", []), elapsed_ms, None


def _execute_postgres(dataset_slug: str, ref_sql: str, user_sql: str) -> tuple[list[str], list[list[Any]], list[str], list[list[Any]], float, str | None]:
    schema_name = f"learn_{secrets.token_hex(4)}"
    seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]

    with psycopg.connect(settings.postgres_sandbox_url, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute(f'CREATE SCHEMA "{schema_name}";')
            cur.execute(f'SET search_path TO "{schema_name}", public;')
            if seed_sql.strip():
                statements = sqlglot.transpile(seed_sql, read="sqlite", write="postgres")
                for stmt in statements:
                    cur.execute(stmt)

            cur.execute(ref_sql)
            ref_columns = [d.name for d in cur.description] if cur.description else []
            ref_rows = [list(r) for r in cur.fetchall()]

            start_time = time.perf_counter()
            err_msg = None
            user_cols: list[str] = []
            user_rows: list[list[Any]] = []
            try:
                cur.execute(user_sql)
                if cur.description:
                    user_cols = [d.name for d in cur.description]
                    user_rows = [list(r) for r in cur.fetchall()[:100]]
            except Exception as e:
                err_msg = str(e)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            cur.execute(f'DROP SCHEMA "{schema_name}" CASCADE;')
            return ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg


def _execute_mysql(dataset_slug: str, ref_sql: str, user_sql: str) -> tuple[list[str], list[list[Any]], list[str], list[list[Any]], float, str | None]:
    db_name = f"learn_{secrets.token_hex(4)}"
    seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]

    conn = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="wiyata",
        password="change-this-dev-password",
        autocommit=True
    )
    with conn.cursor() as cur:
        cur.execute(f"CREATE DATABASE `{db_name}`;")
        cur.execute(f"USE `{db_name}`;")
        if seed_sql.strip():
            statements = sqlglot.transpile(seed_sql, read="sqlite", write="mysql")
            for stmt in statements:
                cur.execute(stmt)

        cur.execute(ref_sql)
        ref_columns = [d[0] for d in cur.description] if cur.description else []
        ref_rows = [list(r) for r in cur.fetchall()]

        start_time = time.perf_counter()
        err_msg = None
        user_cols: list[str] = []
        user_rows: list[list[Any]] = []
        try:
            cur.execute(user_sql)
            if cur.description:
                user_cols = [d[0] for d in cur.description]
                user_rows = [list(r) for r in cur.fetchall()[:100]]
        except Exception as e:
            err_msg = str(e)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        cur.execute(f"DROP DATABASE `{db_name}`;")
    conn.close()
    return ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg


@router.get("/roles")
async def list_professions() -> list[dict]:
    return PROFESSIONS


@router.get("/roles/{role_id}")
async def get_profession(role_id: str) -> dict:
    role = next((r for r in PROFESSIONS if r["id"] == role_id), None)
    if not role:
        raise HTTPException(status_code=404, detail="Profession role not found")
    return role


@router.get("/exercises")
async def list_exercises() -> list[dict]:
    return [
        {
            "slug": c["slug"],
            "title": c["title"],
            "title_id": c["title_id"],
            "level": c["level"],
            "category": c["category"],
            "category_id": c["category_id"],
            "dataset": c["dataset"],
            "description": c["description"],
            "description_id": c["description_id"],
            "expected_columns": c["expected_columns"],
            "starter_sql": c["starter_sql"],
            "hints": c["hints"],
            "hints_id": c["hints_id"],
            "supported_engines": c["supported_engines"],
        }
        for c in CHALLENGES
    ]


@router.get("/datasets/{dataset_slug}/schema")
async def get_dataset_schema(dataset_slug: str) -> dict:
    template = TEMPLATES.get(dataset_slug)
    if not template:
        raise HTTPException(status_code=404, detail="Dataset template not found")

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(template["sql"])

    tables_res = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;"
    ).fetchall()

    schema_tables = []
    for t_row in tables_res:
        t_name = t_row["name"]
        cols_res = conn.execute(f"PRAGMA table_info('{t_name}');").fetchall()
        columns = [
            {
                "cid": c["cid"],
                "name": c["name"],
                "type": c["type"],
                "notnull": bool(c["notnull"]),
                "pk": bool(c["pk"]),
            }
            for c in cols_res
        ]
        row_count = conn.execute(f"SELECT COUNT(*) FROM '{t_name}';").fetchone()[0]
        schema_tables.append({"name": t_name, "columns": columns, "row_count": row_count})

    conn.close()
    return {"dataset": dataset_slug, "tables": schema_tables}


@router.post("/exercises/{slug}/submit", response_model=ChallengeSubmitResponse)
async def submit_exercise(slug: str, body: ChallengeSubmitRequest) -> ChallengeSubmitResponse:
    challenge = next((c for c in CHALLENGES if c["slug"] == slug), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Exercise challenge not found")

    is_id = body.language == "id"
    hints = challenge["hints_id"] if is_id else challenge["hints"]
    engine = body.engine.lower() if body.engine else "sqlite"
    dataset_slug = challenge["dataset"]

    try:
        if engine == "postgres":
            ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = _execute_postgres(
                dataset_slug, challenge["solution_sql"], body.query
            )
        elif engine == "mysql":
            ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = _execute_mysql(
                dataset_slug, challenge["solution_sql"], body.query
            )
        elif engine == "oracle":
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]
            conn.executescript(seed_sql)
            cur_ref = conn.execute(challenge["solution_sql"])
            ref_columns = [d[0] for d in cur_ref.description]
            ref_rows = [list(r) for r in cur_ref.fetchall()]

            adapter = OracleAdapter()
            adapter._conn = conn
            start_time = time.perf_counter()
            user_res = adapter.execute(body.query, max_rows=100, read_only=True)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            conn.close()
            if not user_res.get("success"):
                ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = ref_columns, ref_rows, [], [], elapsed_ms, user_res.get("error")
            else:
                ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = ref_columns, ref_rows, user_res.get("columns", []), user_res.get("rows", []), elapsed_ms, None
        elif engine == "mssql":
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]
            conn.executescript(seed_sql)
            cur_ref = conn.execute(challenge["solution_sql"])
            ref_columns = [d[0] for d in cur_ref.description]
            ref_rows = [list(r) for r in cur_ref.fetchall()]

            adapter = MSSQLAdapter()
            adapter._conn = conn
            start_time = time.perf_counter()
            user_res = adapter.execute(body.query, max_rows=100, read_only=True)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            conn.close()
            if not user_res.get("success"):
                ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = ref_columns, ref_rows, [], [], elapsed_ms, user_res.get("error")
            else:
                ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = ref_columns, ref_rows, user_res.get("columns", []), user_res.get("rows", []), elapsed_ms, None
        else:
            ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = _execute_sqlite(
                dataset_slug, challenge["solution_sql"], body.query
            )
    except Exception as exc:
        return ChallengeSubmitResponse(
            passed=False,
            message=f"Execution Exception: {exc}",
            row_count=0,
            expected_row_count=0,
            user_columns=[],
            expected_columns=challenge["expected_columns"],
            sample_user_rows=[],
            sample_expected_rows=[],
            elapsed_ms=0,
            feedback=[str(exc)],
            hints=hints,
        )

    if err_msg:
        return ChallengeSubmitResponse(
            passed=False,
            message=f"SQL Error: {err_msg}",
            row_count=0,
            expected_row_count=len(ref_rows),
            user_columns=[],
            expected_columns=challenge["expected_columns"],
            sample_user_rows=[],
            sample_expected_rows=ref_rows[:5],
            elapsed_ms=elapsed_ms,
            feedback=[
                "Periksa kembali sintaks SQL dan nama kolom yang Anda gunakan."
                if is_id
                else "Check your SQL syntax and projected column names."
            ],
            hints=hints,
        )

    user_cols_clean = [c.lower() for c in user_cols]
    expected_cols_clean = [c.lower() for c in challenge["expected_columns"]]

    feedback: list[str] = []
    col_match = user_cols_clean == expected_cols_clean
    if not col_match:
        feedback.append(
            f"Kolom tidak cocok. Diharapkan: {expected_cols_clean}, Diterima: {user_cols_clean}"
            if is_id
            else f"Columns mismatch. Expected: {expected_cols_clean}, Got: {user_cols_clean}"
        )

    count_match = len(user_rows) == len(ref_rows)
    if not count_match:
        feedback.append(
            f"Jumlah baris berbeda. Diharapkan: {len(ref_rows)} baris, Diterima: {len(user_rows)} baris."
            if is_id
            else f"Row count mismatch. Expected: {len(ref_rows)} rows, Got: {len(user_rows)} rows."
        )

    passed = col_match and count_match
    if passed and user_rows and ref_rows:
        first_user = [str(x).strip() for x in user_rows[0]]
        first_ref = [str(x).strip() for x in ref_rows[0]]
        if first_user != first_ref:
            passed = False
            feedback.append(
                "Urutan baris data atau nilai tidak sesuai ekspektasi ORDER BY."
                if is_id
                else "Row order or values do not match expected ORDER BY sorting."
            )

    msg = (
        "Selamat! Solusi query Anda benar dan lulus semua pengujian."
        if (passed and is_id)
        else "Congratulations! Your query passed all verification checks."
        if passed
        else "Hasil query belum sesuai dengan kriteria yang diharapkan."
        if is_id
        else "Query results do not match expected criteria."
    )

    return ChallengeSubmitResponse(
        passed=passed,
        message=msg,
        row_count=len(user_rows),
        expected_row_count=len(ref_rows),
        user_columns=user_cols,
        expected_columns=challenge["expected_columns"],
        sample_user_rows=user_rows[:5],
        sample_expected_rows=ref_rows[:5],
        elapsed_ms=elapsed_ms,
        feedback=feedback,
        hints=hints,
    )
