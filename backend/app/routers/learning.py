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
from app.adapters.db2 import Db2Adapter
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
-- Lengkapi klausul WHERE (stock < 35) dan pengurutan ORDER BY:
""",
        "hints": [
            "Use the WHERE clause with condition 'stock < 35'.",
            "Sort the final rows using 'ORDER BY stock ASC'."
        ],
        "hints_id": [
            "Gunakan klausul WHERE dengan kondisi 'stock < 35'.",
            "Urutkan baris hasil akhir menggunakan 'ORDER BY stock ASC'."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
        "starter_sql": """-- Hubungkan tabel enrollments, students, dan courses untuk nilai 'A':
SELECT s.name AS student_name, c.title AS course_title, e.grade
FROM enrollments e
-- Lengkapi JOIN ke students (on e.student_id = s.id) dan courses (on e.course_id = c.id)
-- serta klausul WHERE dan ORDER BY:
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
        "starter_sql": """-- Tulis query nasabah prioritas (status 'ACTIVE' dan saldo > 30.000.000):
SELECT c.full_name, a.account_number, a.account_type, a.balance
FROM accounts a
-- Lengkapi JOIN ke customers pada customer_id
-- dan saring dengan WHERE status = 'ACTIVE' AND balance > 30000000.0
-- urutkan dengan ORDER BY balance DESC:
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
        "starter_sql": """-- Hitung total belanja 5 pelanggan teratas dengan pesanan 'completed':
SELECT c.first_name, c.city, -- Hitung SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
-- Lengkapi filter WHERE o.status = 'completed'
-- kelompokkan dengan GROUP BY c.id, c.first_name, c.city
-- urutkan dengan ORDER BY total_spent DESC LIMIT 5:
""",
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
        "starter_sql": """-- Cari penulis dengan lebih dari 1 artikel:
SELECT a.username,
       -- Hitung COUNT(p.id) AS post_count dan SUM(p.views) AS total_views:
FROM authors a
JOIN posts p ON a.id = p.author_id
-- Lengkapi GROUP BY a.id, a.username
-- saring kelompok dengan HAVING COUNT(p.id) > 1
-- dan urutkan dengan ORDER BY total_views DESC:
""",
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
SELECT channel,
       -- Hitung SUM(amount) AS total_volume dan AVG(fee) AS avg_fee:
FROM transactions
-- Lengkapi filter WHERE transaction_type = 'TRANSFER'
-- kelompokkan dengan GROUP BY channel
-- urutkan dengan ORDER BY total_volume DESC:
""",
        "hints": [
            "Filter WHERE transaction_type = 'TRANSFER'.",
            "Group by channel and calculate SUM(amount) AS total_volume and AVG(fee) AS avg_fee."
        ],
        "hints_id": [
            "Filter dengan WHERE transaction_type = 'TRANSFER'.",
            "Kelompokkan berdasarkan channel dan hitung SUM(amount) serta AVG(fee)."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
-- Lengkapi LEFT JOIN ke tabel orders (on c.id = o.customer_id)
-- saring baris yang belum pernah berbelanja dengan WHERE o.id IS NULL
-- urutkan dengan ORDER BY c.id ASC:
""",
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
       -- Lengkapi Window Function SUM(...) OVER (ORDER BY transaction_id ASC) AS running_total:
FROM transactions
ORDER BY transaction_id ASC;
""",
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
       -- Lengkapi DENSE_RANK() OVER (PARTITION BY category_id ORDER BY price DESC) AS price_rank:
FROM products
-- Lengkapi ORDER BY category_id ASC, price_rank ASC:
""",
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
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
        "starter_sql": """-- Definisikan CTE category_sales lalu gabungkan dengan tabel categories:
WITH category_sales AS (
    SELECT p.category_id, -- Hitung SUM(oi.quantity * oi.unit_price) AS total_revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.id
    GROUP BY p.category_id
)
SELECT c.name AS category_name, cs.total_revenue
FROM category_sales cs
-- Lengkapi JOIN ke tabel categories dan ORDER BY total_revenue DESC:
""",
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
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "tablespace-capacity-alert",
        "title": "Tablespace Capacity & High Water Mark Alert",
        "title_id": "Peringatan Ambang Batas Kapasitas Tablespace (> 80%)",
        "level": "Intermediate",
        "category": "Storage & Capacity Planning",
        "category_id": "Penyimpanan & Kapasitas",
        "dataset": "dba_ops",
        "description": "Enterprise monitoring tools (OEM, SSMS, PEM) raise alerts when tablespace usage breaches 80%. Select tablespace_name, allocated_mb, used_mb, and used_percent (calculated as ROUND((used_mb * 100.0) / allocated_mb, 1)) for all tablespaces where used_percent is >= 80.0. Sort by used_percent descending.",
        "description_id": "Aplikasi monitoring enterprise (OEM, SSMS, PEM) membunyikan alert saat utilisasi tablespace melampaui 80%. Tampilkan tablespace_name, allocated_mb, used_mb, dan used_percent (dihitung sebagai ROUND((used_mb * 100.0) / allocated_mb, 1)) untuk semua tablespace dengan used_percent >= 80.0. Urutkan dari used_percent tertinggi.",
        "expected_columns": ["tablespace_name", "allocated_mb", "used_mb", "used_percent"],
        "solution_sql": """SELECT tablespace_name, allocated_mb, used_mb, ROUND((used_mb * 100.0) / allocated_mb, 1) AS used_percent
FROM dba_tablespaces
WHERE (used_mb * 100.0) / allocated_mb >= 80.0
ORDER BY used_percent DESC;""",
        "starter_sql": """-- Deteksi tablespace dengan utilisasi >= 80.0%:
SELECT tablespace_name, allocated_mb, used_mb,
       -- Hitung used_percent: ROUND((used_mb * 100.0) / allocated_mb, 1) AS used_percent
FROM dba_tablespaces
-- Lengkapi filter WHERE (used_mb * 100.0) / allocated_mb >= 80.0
-- urutkan dengan ORDER BY used_percent DESC:
""",
        "hints": [
            "Compute the percentage with ROUND((used_mb * 100.0) / allocated_mb, 1).",
            "Filter using WHERE (used_mb * 100.0) / allocated_mb >= 80.0.",
            "Order by used_percent DESC."
        ],
        "hints_id": [
            "Hitung persentase dengan ROUND((used_mb * 100.0) / allocated_mb, 1).",
            "Filter kondisi menggunakan WHERE (used_mb * 100.0) / allocated_mb >= 80.0.",
            "Urutkan hasil dengan ORDER BY used_percent DESC."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "blocking-sessions-root-cause",
        "title": "Root Blocking Session Detector (Head of Blocker Tree)",
        "title_id": "Deteksi Root Blocker (Induk Antrean Lock Menggantung)",
        "level": "Advanced",
        "category": "Concurrency & Lock Diagnostics",
        "category_id": "Konkurensi & Diagnostik Lock",
        "dataset": "dba_ops",
        "description": "In transactional databases, a chain of blocked sessions traces back to a lead blocker that is not waiting on any other session. Find all root blocking sessions: sessions whose spid appears as blocked_by_spid for other waiting sessions, but who themselves have blocked_by_spid IS NULL. Return distinct spid, db_user, lock_type, wait_time_seconds, and query_snippet.",
        "description_id": "Pada database transaksional, rantai sesi menggantung bermuara pada satu sesi induk (lead blocker) yang tidak terblokir sesi mana pun. Temukan semua root blocking session: sesi yang nilai spid-nya tercantum dalam blocked_by_spid sesi lain, namun spid miliknya memiliki blocked_by_spid IS NULL. Tampilkan spid unik, db_user, lock_type, wait_time_seconds, dan query_snippet.",
        "expected_columns": ["spid", "db_user", "lock_type", "wait_time_seconds", "query_snippet"],
        "solution_sql": """SELECT DISTINCT s.spid, s.db_user, s.lock_type, s.wait_time_seconds, s.query_snippet
FROM active_sessions s
WHERE s.blocked_by_spid IS NULL
  AND s.spid IN (
    SELECT blocked_by_spid 
    FROM active_sessions 
    WHERE blocked_by_spid IS NOT NULL
  );""",
        "starter_sql": """-- Temukan lead blocker yang menahan lock tanpa diblokir oleh sesi lain:
SELECT DISTINCT s.spid, s.db_user, s.lock_type, s.wait_time_seconds, s.query_snippet
FROM active_sessions s
WHERE s.blocked_by_spid IS NULL
  AND s.spid IN (
    -- Tulis subquery untuk mengambil blocked_by_spid dari active_sessions di mana blocked_by_spid IS NOT NULL:
  );""",
        "hints": [
            "Use a subquery to find all blocked_by_spid values that are NOT NULL.",
            "Filter the outer query for sessions where blocked_by_spid IS NULL AND spid IN (subquery).",
            "Use DISTINCT to ensure no duplicate root SPIDs."
        ],
        "hints_id": [
            "Gunakan subquery untuk memilih semua blocked_by_spid yang NOT NULL.",
            "Filter tabel induk dengan kondisi blocked_by_spid IS NULL AND spid IN (subquery).",
            "Gunakan klausa DISTINCT untuk menghindari duplikasi SPID root."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "replication-mirroring-lag-monitor",
        "title": "Database Mirroring & Replication Lag Audit",
        "title_id": "Audit Keterlambatan Replikasi & Mirroring Cluster",
        "level": "Intermediate",
        "category": "High Availability & Disaster Recovery",
        "category_id": "Ketersediaan Tinggi & Replikasi",
        "dataset": "dba_ops",
        "description": "High Availability clusters (AlwaysOn, Data Guard, Patroni) require low replication lag. Identify all replica nodes violating SLA where lag_seconds > 10.0, or replay_queue_kb > 500.0, or sync_state = 'DESYNCHRONIZED'. Display replica_name, replica_role, sync_state, lag_seconds, and replay_queue_kb, ordered by lag_seconds descending.",
        "description_id": "Cluster High Availability (AlwaysOn, Data Guard, Patroni) menuntut replikasi real-time. Identifikasi replica yang melanggar SLA yaitu lag_seconds > 10.0, atau replay_queue_kb > 500.0, atau sync_state = 'DESYNCHRONIZED'. Tampilkan replica_name, replica_role, sync_state, lag_seconds, dan replay_queue_kb, diurutkan dari lag_seconds terbesar.",
        "expected_columns": ["replica_name", "replica_role", "sync_state", "lag_seconds", "replay_queue_kb"],
        "solution_sql": """SELECT replica_name, replica_role, sync_state, lag_seconds, replay_queue_kb
FROM cluster_replicas
WHERE lag_seconds > 10.0 
   OR replay_queue_kb > 500.0 
   OR sync_state = 'DESYNCHRONIZED'
ORDER BY lag_seconds DESC;""",
        "starter_sql": """-- Cari replika cluster dengan lag tinggi atau status desynchronized:
SELECT replica_name, replica_role, sync_state, lag_seconds, replay_queue_kb
FROM cluster_replicas
-- Lengkapi filter WHERE dengan kondisi OR:
-- lag_seconds > 10.0 ATAU replay_queue_kb > 500.0 ATAU sync_state = 'DESYNCHRONIZED'
-- urutkan dengan ORDER BY lag_seconds DESC:
""",
        "hints": [
            "Combine the conditions using OR: lag_seconds > 10.0 OR replay_queue_kb > 500.0 OR sync_state = 'DESYNCHRONIZED'.",
            "Order results by lag_seconds DESC."
        ],
        "hints_id": [
            "Gabungkan kondisi dengan operator OR: lag_seconds > 10.0 OR replay_queue_kb > 500.0 OR sync_state = 'DESYNCHRONIZED'.",
            "Urutkan hasil kueri dengan ORDER BY lag_seconds DESC."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "k8s-pod-buffer-cache-ratio",
        "title": "Kubernetes Database Pod Buffer Cache Hit Ratio",
        "title_id": "Rasio Hit Buffer Cache Pod Database Kubernetes",
        "level": "Advanced",
        "category": "Container & Server Telemetry",
        "category_id": "Telemetri Server & Kontainer",
        "dataset": "dba_ops",
        "description": "In Kubernetes StatefulSets, low buffer cache hit ratio (< 95%) forces frequent disk reads, causing I/O bottleneck and cgroup CPU throttling. Compute the buffer cache hit percentage for each database pod as ROUND(((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads, 2) AS cache_hit_pct. Filter for pods where cache_hit_pct < 95.0 or cpu_throttled_seconds > 10.0. Return pod_name, node_name, db_engine, memory_used_mb, cache_hit_pct, ordered by cache_hit_pct ascending.",
        "description_id": "Pada StatefulSet Kubernetes, rasio hit buffer cache yang rendah (< 95%) memicu disk read fisik berlebih dan throttling CPU cgroup. Hitung persentase cache hit untuk tiap pod database sebagai ROUND(((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads, 2) AS cache_hit_pct. Filter pod dengan cache_hit_pct < 95.0 atau cpu_throttled_seconds > 10.0. Tampilkan pod_name, node_name, db_engine, memory_used_mb, cache_hit_pct, diurutkan dari cache_hit_pct terkecil.",
        "expected_columns": ["pod_name", "node_name", "db_engine", "memory_used_mb", "cache_hit_pct"],
        "solution_sql": """SELECT 
  pod_name, 
  node_name, 
  db_engine, 
  memory_used_mb, 
  ROUND(((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads, 2) AS cache_hit_pct
FROM k8s_db_pods
WHERE (((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads) < 95.0
   OR cpu_throttled_seconds > 10.0
ORDER BY cache_hit_pct ASC;""",
        "starter_sql": """-- Hitung efisiensi buffer cache per pod database di Kubernetes:
SELECT 
  pod_name, 
  node_name, 
  db_engine, 
  memory_used_mb, 
  -- Hitung cache_hit_pct: ROUND(((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads, 2) AS cache_hit_pct
FROM k8s_db_pods
-- Lengkapi filter WHERE (hitung persentase < 95.0 ATAU cpu_throttled_seconds > 10.0)
-- urutkan dengan ORDER BY cache_hit_pct ASC:
""",
        "hints": [
            "Formula for hit ratio: ((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads.",
            "Round to 2 decimal places using ROUND(..., 2).",
            "Order by cache_hit_pct ASC to show the most degraded pods first."
        ],
        "hints_id": [
            "Rumus rasio hit: ((buffer_cache_reads - disk_physical_reads) * 100.0) / buffer_cache_reads.",
            "Bulatkan ke 2 tempat desimal menggunakan fungsi ROUND(..., 2).",
            "Urutkan dengan ORDER BY cache_hit_pct ASC agar pod bermasalah tampil paling atas."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "deadlock-contention-hotspot",
        "title": "Exclusive Lock Contention Hotspot",
        "title_id": "Pusat Antrean & Kontensi Exclusive Lock",
        "level": "Intermediate",
        "category": "Concurrency & Lock Diagnostics",
        "category_id": "Konkurensi & Diagnostik Lock",
        "dataset": "dba_ops",
        "description": "Identify users and lock types generating high cumulative wait times in the lock queue. For all sessions where blocked_by_spid IS NOT NULL, calculate blocked_count (COUNT(*)) and total_wait_sec (SUM(wait_time_seconds)) grouped by db_user and lock_type. Include only groups with total_wait_sec > 30, ordered by total_wait_sec descending.",
        "description_id": "Identifikasi user dan tipe lock yang menimbulkan akumulasi waktu antrean terpanjang. Untuk sesi yang memiliki blocked_by_spid IS NOT NULL, hitung blocked_count (COUNT(*)) dan total_wait_sec (SUM(wait_time_seconds)) dikelompokkan berdasarkan db_user dan lock_type. Hanya sertakan grup dengan total_wait_sec > 30, diurutkan dari total_wait_sec terbesar.",
        "expected_columns": ["db_user", "lock_type", "blocked_count", "total_wait_sec"],
        "solution_sql": """SELECT db_user, lock_type, COUNT(*) AS blocked_count, SUM(wait_time_seconds) AS total_wait_sec
FROM active_sessions
WHERE blocked_by_spid IS NOT NULL
GROUP BY db_user, lock_type
HAVING SUM(wait_time_seconds) > 30
ORDER BY total_wait_sec DESC;""",
        "starter_sql": """-- Agregasi durasi tunggu lock yang menggantung:
SELECT db_user, lock_type,
       -- Hitung COUNT(*) AS blocked_count dan SUM(wait_time_seconds) AS total_wait_sec:
FROM active_sessions
WHERE blocked_by_spid IS NOT NULL
-- Lengkapi GROUP BY db_user, lock_type
-- saring dengan HAVING SUM(wait_time_seconds) > 30
-- urutkan dengan ORDER BY total_wait_sec DESC:
""",
        "hints": [
            "Filter blocked sessions with WHERE blocked_by_spid IS NOT NULL.",
            "Group by db_user, lock_type.",
            "Use HAVING SUM(wait_time_seconds) > 30 to isolate severe contention."
        ],
        "hints_id": [
            "Filter sesi yang terblokir dengan WHERE blocked_by_spid IS NOT NULL.",
            "Kelompokkan dengan GROUP BY db_user, lock_type.",
            "Gunakan klausa HAVING SUM(wait_time_seconds) > 30 untuk menyaring antrean kritis."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "tablespace-autoextend-exhaustion",
        "title": "Datafile Autoextend & Disk Headroom Exhaustion",
        "title_id": "Risiko Kehabisan Ruang Datafile & Autoextend",
        "level": "Advanced",
        "category": "Storage & Capacity Planning",
        "category_id": "Penyimpanan & Kapasitas",
        "dataset": "dba_ops",
        "description": "Detect tablespaces at imminent risk of storage exhaustion: either autoextensible = 0 with used_mb >= 85% of allocated_mb (risk_level = 'CRITICAL_FIXED'), or autoextensible = 1 where allocated_mb >= 90% of max_mb (risk_level = 'NEAR_MAX_LIMIT'). Select tablespace_name, file_name, allocated_mb, max_mb, autoextensible, and calculated risk_level. Order by allocated_mb descending.",
        "description_id": "Deteksi datafile yang terancam kehabisan ruang disk: autoextensible = 0 dengan used_mb >= 85% dari allocated_mb (risk_level = 'CRITICAL_FIXED'), atau autoextensible = 1 di mana allocated_mb >= 90% dari batas max_mb (risk_level = 'NEAR_MAX_LIMIT'). Tampilkan tablespace_name, file_name, allocated_mb, max_mb, autoextensible, dan risk_level. Urutkan dari allocated_mb terbesar.",
        "expected_columns": ["tablespace_name", "file_name", "allocated_mb", "max_mb", "autoextensible", "risk_level"],
        "solution_sql": """SELECT 
  tablespace_name, 
  file_name, 
  allocated_mb, 
  max_mb, 
  autoextensible,
  CASE 
    WHEN autoextensible = 0 AND (used_mb * 1.0 / allocated_mb) >= 0.85 THEN 'CRITICAL_FIXED'
    ELSE 'NEAR_MAX_LIMIT'
  END AS risk_level
FROM dba_tablespaces
WHERE (autoextensible = 0 AND (used_mb * 1.0 / allocated_mb) >= 0.85)
   OR (autoextensible = 1 AND allocated_mb >= max_mb * 0.90)
ORDER BY allocated_mb DESC;""",
        "starter_sql": """-- Klasifikasikan risiko kepenuhan datafile dengan klausul CASE WHEN:
SELECT 
  tablespace_name, 
  file_name, 
  allocated_mb, 
  max_mb, 
  autoextensible,
  -- Tulis ekspresi CASE WHEN: autoextensible = 0 AND (used_mb * 1.0 / allocated_mb) >= 0.85 THEN 'CRITICAL_FIXED' ELSE 'NEAR_MAX_LIMIT' END AS risk_level
FROM dba_tablespaces
-- Lengkapi filter WHERE dengan kondisi OR untuk kedua kasus risiko
-- urutkan dengan ORDER BY allocated_mb DESC:
""",
        "hints": [
            "Use a CASE expression to evaluate 'CRITICAL_FIXED' vs 'NEAR_MAX_LIMIT'.",
            "Check condition (autoextensible = 0 AND used_mb/allocated_mb >= 0.85) OR (autoextensible = 1 AND allocated_mb >= max_mb * 0.90).",
            "Order by allocated_mb DESC."
        ],
        "hints_id": [
            "Gunakan ekspresi CASE untuk menentukan label 'CRITICAL_FIXED' atau 'NEAR_MAX_LIMIT'.",
            "Periksa kondisi (autoextensible = 0 AND used_mb/allocated_mb >= 0.85) OR (autoextensible = 1 AND allocated_mb >= max_mb * 0.90).",
            "Urutkan hasil dengan ORDER BY allocated_mb DESC."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
    {
        "slug": "concurrency-serializable-anomaly",
        "title": "High-Value Transaction Ledger Concurrency Audit",
        "title_id": "Audit Konkurensi Buku Kas Transaksi Bernilai Tinggi",
        "level": "Professional",
        "category": "Transactions & ACID",
        "category_id": "Transaksi & ACID",
        "dataset": "banking",
        "description": "Audit high-throughput banking accounts where multiple transactions exceed 5,000,000 IDR. Select a.account_number, a.account_type, a.balance, COUNT(t.transaction_id) AS high_val_count, and SUM(t.amount) AS total_high_val_amount for transactions where t.amount >= 5000000.0. Group by account, include only accounts with strictly more than 1 high-value transaction, ordered by total_high_val_amount descending.",
        "description_id": "Audit rekening perbankan bertrafik tinggi di mana terjadi beberapa transaksi bernilai >= 5.000.000 IDR. Tampilkan account_number, account_type, balance, high_val_count (COUNT), dan total_high_val_amount (SUM) untuk transaksi bernilai >= 5.000.000 IDR. Saring hanya rekening dengan lebih dari 1 transaksi besar, diurutkan dari total nominal terbesar.",
        "expected_columns": ["account_number", "account_type", "balance", "high_val_count", "total_high_val_amount"],
        "solution_sql": """SELECT a.account_number, a.account_type, a.balance, COUNT(t.transaction_id) AS high_val_count, SUM(t.amount) AS total_high_val_amount
FROM accounts a
JOIN transactions t ON a.account_number = t.from_account_number
WHERE t.amount >= 5000000.0
GROUP BY a.account_number, a.account_type, a.balance
HAVING COUNT(t.transaction_id) > 1
ORDER BY total_high_val_amount DESC;""",
        "starter_sql": """-- Audit transaksi bernilai besar (>= 5.000.000 IDR) per rekening:
SELECT a.account_number, a.account_type, a.balance,
       -- Hitung COUNT(t.transaction_id) AS high_val_count
       -- dan SUM(t.amount) AS total_high_val_amount:
FROM accounts a
JOIN transactions t ON a.account_number = t.from_account_number
-- Lengkapi filter WHERE t.amount >= 5000000.0
-- kelompokkan dengan GROUP BY a.account_number, a.account_type, a.balance
-- saring dengan HAVING COUNT(t.transaction_id) > 1
-- urutkan dengan ORDER BY total_high_val_amount DESC:
""",
        "hints": [
            "Join accounts and transactions on a.account_number = t.from_account_number.",
            "Filter transactions with WHERE t.amount >= 5000000.0.",
            "Group by a.account_number, a.account_type, a.balance and filter HAVING COUNT(t.transaction_id) > 1.",
            "Sort with ORDER BY total_high_val_amount DESC."
        ],
        "hints_id": [
            "Hubungkan accounts dan transactions pada a.account_number = t.from_account_number.",
            "Filter transaksi besar dengan WHERE t.amount >= 5000000.0.",
            "Kelompokkan per rekening dan filter dengan HAVING COUNT(t.transaction_id) > 1.",
            "Urutkan dengan ORDER BY total_high_val_amount DESC."
        ],
        "supported_engines": ["postgres", "mysql", "oracle", "mssql", "db2", "sqlite"],
    },
]


PROFESSIONS = [
    {
        "id": "sql-developer",
        "title": "SQL Developer & Query Engineer",
        "title_id": "Pengembang SQL & Insinyur Kueri",
        "category": "Application Engineering",
        "category_id": "Rekayasa Aplikasi",
        "summary": "Authors high-performance analytical and transactional queries, designs indexed views, eliminates ORM query bottlenecks, and constructs robust business logic in modern SQL.",
        "summary_id": "Merancang kueri transaksional dan analitis berkecepatan tinggi, optimasi indeks, eliminasi bottleneck ORM, dan membangun logika bisnis tangguh dalam dialek SQL modern.",
        "engines": ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "SQLite"],
        "recommended_tools": ["dbeaver", "datagrip", "flyway", "liquibase"],
        "core_responsibilities": [
            "Write sargable queries that leverage composite, covering, and partial indexes",
            "Eliminate N+1 database amplification anti-patterns in backend ORMs (Hibernate, Prisma, SQLAlchemy)",
            "Construct complex data pipelines using Common Table Expressions (CTEs) and Window Functions",
            "Maintain version-controlled database schema migration scripts"
        ],
        "core_responsibilities_id": [
            "Menulis kueri sargable yang memanfaatkan indeks komposit, covering, dan parsial",
            "Mengatasi masalah kueri N+1 pada ORM backend (Hibernate, Prisma, SQLAlchemy)",
            "Membangun pipeline transformasi data dengan Common Table Expressions (CTEs) dan Window Functions",
            "Mengelola skrip migrasi skema database terversi secara konsisten"
        ],
        "skills_progression": {
            "junior": [
                "ANSI SQL DDL/DML, multi-table joins, aggregations, and subqueries",
                "Understanding primary, foreign, and unique key constraint enforcement",
                "Basic EXPLAIN plan interpretation (Seq Scan vs Index Scan)",
                "Writing idempotent migration scripts using Flyway / Liquibase"
            ],
            "mid": [
                "Window functions (ROW_NUMBER, DENSE_RANK, LAG/LEAD, running totals)",
                "Recursive CTEs for hierarchical tree traversal and graph queries",
                "Index optimization: B-Tree index selectivity, covering indexes (INCLUDE clause)",
                "Transactions and locking: dirty reads, non-repeatable reads, phantom reads"
            ],
            "senior": [
                "Advanced Cost-Based Optimizer mechanics and statistics calibration",
                "Partition pruning strategies across range, list, and hash partitioning",
                "Cross-engine dialect porting and transpilation (Postgres to Oracle / T-SQL)",
                "Automated SQL query linting and CI/CD quality gate enforcement"
            ]
        },
        "key_metrics": [
            "Query Latency p95 and p99 (< 20ms target)",
            "Index Scan vs Sequential Scan Ratio (> 95% indexed)",
            "ORM Query Multiplication Factor (Queries per HTTP request <= 2)",
            "Execution Plan Cost and Temp Spill to Disk (0 bytes)"
        ],
        "runbooks": [
            {
                "name": "Slow Query Plan Diagnostics & Index Tuning",
                "name_id": "Diagnostik Rencana Eksekusi Kueri Lambat & Penalaan Indeks",
                "steps": [
                    "Run EXPLAIN (ANALYZE, BUFFERS) or SET STATISTICS IO ON to inspect page reads",
                    "Identify predicates causing Full Table Scan (e.g. function wrapping column: UPPER(email))",
                    "Rewrite predicate to be sargable or introduce an expression/functional index",
                    "Verify buffer read count drops by at least 90%"
                ]
            }
        ],
        "recommended_challenges": [
            "low-stock-alert",
            "top-spending-customers",
            "category-revenue-cte",
            "cumulative-transaction-ledger",
            "product-price-category-rank"
        ]
    },
    {
        "id": "dba-general",
        "title": "Enterprise Database Administrator (DBA)",
        "title_id": "Administrator Basis Data Enterprise (DBA)",
        "category": "Operations & Reliability",
        "category_id": "Operasional & Keandalan",
        "summary": "Architects, provisions, monitors, and safeguards enterprise database instances to ensure 24/7 uptime, high performance, and rapid disaster recovery.",
        "summary_id": "Merancang, mengelola, memantau, dan menjaga cluster database perusahaan untuk memastikan uptime 24/7, performa maksimal, dan pemulihan bencana instan.",
        "engines": ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "IBM Db2"],
        "recommended_tools": [
            "pmm",
            "prometheus",
            "grafana",
            "pgbackrest",
            "xtrabackup",
            "dbeaver"
        ],
        "core_responsibilities": [
            "Maintain database high availability (HA), mirroring, and automated failover clusters",
            "Design and test backup strategies (Full, Differential, Point-In-Time Recovery / PITR)",
            "Monitor server resource consumption (Tablespace High Water Mark, buffer cache hit ratio, lock waits)",
            "Perform major version upgrades with zero or near-zero maintenance downtime"
        ],
        "core_responsibilities_id": [
            "Memelihara klaster ketersediaan tinggi (HA), mirroring, dan failover otomatis",
            "Merancang dan menguji strategi pencadangan (Full, Diferensial, PITR)",
            "Memantau konsumsi sumber daya (High Water Mark tablespace, buffer cache hit ratio, lock wait)",
            "Melakukan upgrade versi mayor dengan zero-downtime atau downtime minimal"
        ],
        "skills_progression": {
            "junior": [
                "SQL DDL/DML syntax across multiple engines",
                "Tablespace and datafile management (autoextend, HWM, storage allocation)",
                "Logical backup & restore (pg_dump, mysqldump)",
                "User management & privilege grants (least privilege)"
            ],
            "mid": [
                "Physical hot backup configuration (pgBackRest, XtraBackup)",
                "Diagnosing blocking sessions, lock trees, and deadlock victims",
                "Active-passive & streaming replication topology setup",
                "Slow query log analysis and index defragmentation"
            ],
            "senior": [
                "Multi-region active-active cluster architecture and zero-downtime failover",
                "Automated chaos engineering & disaster recovery drills",
                "Advanced performance telemetry via ASH, AWR, Extended Events, and kernel tuning",
                "Automated migration pipelines and database sharding"
            ]
        },
        "key_metrics": [
            "Tablespace Capacity & Datafile Headroom (> 85% alert)",
            "Replication Lag (seconds / bytes behind master)",
            "Cache Hit Ratio (> 99% target)",
            "Lock Contention & Root Blocker Waiting Duration"
        ],
        "runbooks": [
            {
                "name": "Root Blocking Session Emergency Resolution",
                "name_id": "Penanganan Darurat Rantai Sesi Menggantung (Root Blocker)",
                "steps": [
                    "Query lock catalogs to identify the root blocker SPID (blocked_by_spid IS NULL)",
                    "Inspect the root blocker query snippet and transaction start time",
                    "Attempt graceful statement cancellation before hard killing the connection",
                    "Terminate session if uncommitted transaction blocks business-critical traffic"
                ]
            },
            {
                "name": "Tablespace Storage Headroom Emergency Expansion",
                "name_id": "Ekspansi Ruang Darurat Tablespace Kritis",
                "steps": [
                    "Check underlying OS mount filesystem space (df -h)",
                    "Verify if tablespace datafiles are fixed-size or autoextensible",
                    "Add new secondary datafile or resize existing datafile",
                    "Schedule table segment shrink / VACUUM FULL to reclaim deleted block space"
                ]
            }
        ],
        "recommended_challenges": [
            "tablespace-capacity-alert",
            "blocking-sessions-root-cause",
            "tablespace-autoextend-exhaustion",
            "deadlock-contention-hotspot"
        ]
    },
    {
        "id": "oracle-dba",
        "title": "Oracle Database Administrator",
        "title_id": "Administrator Basis Data Oracle",
        "category": "Enterprise RDBMS Administration",
        "category_id": "Administrasi RDBMS Enterprise",
        "summary": "Specializes in mission-critical Oracle instances, Multitenant CDB/PDB architecture, Real Application Clusters (RAC), Data Guard disaster recovery, and deep AWR/ASH performance diagnostics.",
        "summary_id": "Spesialis arsitektur Oracle Enterprise, Multitenant CDB/PDB, Real Application Clusters (RAC), disaster recovery Data Guard, dan diagnostik performa AWR/ASH.",
        "engines": ["Oracle 23ai", "Oracle 19c"],
        "recommended_tools": ["oracle-sql-developer", "oem", "sqlcl", "sqlplus", "rman"],
        "core_responsibilities": [
            "Manage SGA and PGA memory allocation (Buffer Cache, Shared Pool, Large Pool, PGA Target)",
            "Configure and administer Oracle Data Guard physical standby and automated Fast-Start Failover (FSFO)",
            "Perform backup and recovery operations with Oracle Recovery Manager (RMAN)",
            "Analyze system performance bottlenecks using AWR, ASH, and ADDM reports"
        ],
        "core_responsibilities_id": [
            "Mengelola alokasi memori SGA dan PGA (Buffer Cache, Shared Pool, PGA Target)",
            "Mengonfigurasi dan memelihara Oracle Data Guard standby dan Fast-Start Failover",
            "Mengeksekusi backup dan recovery fisik dengan Oracle Recovery Manager (RMAN)",
            "Mendiagnosis kemacetan performa melalui laporan AWR, ASH, dan ADDM"
        ],
        "skills_progression": {
            "junior": [
                "CDB and PDB provisioning, user roles, tablespaces, and datafiles",
                "Basic SQL*Plus / SQLcl command-line navigation and alert.log monitoring",
                "Configuring listener.ora and tnsnames.ora networking",
                "Taking cold/hot database backups via RMAN"
            ],
            "mid": [
                "Oracle Data Guard replication, switchover/failover validation",
                "AWR and ASH report generation, analyzing top wait events (db file sequential read, enqueue)",
                "Managing Automatic Storage Management (ASM) disk groups and rebalancing",
                "Tuning undo tablespace retention to eliminate ORA-01555 (Snapshot too old)"
            ],
            "senior": [
                "Oracle Real Application Clusters (RAC) multi-node cache fusion and interconnect tuning",
                "Zero-downtime rolling database patching with opatch / Grid Infrastructure",
                "Advanced GoldenGate bidirectional replication and conflict resolution",
                "Database consolidation and Exadata storage cell offloading optimization"
            ]
        },
        "key_metrics": [
            "SGA Buffer Cache Hit Ratio (> 98%)",
            "Top 5 Timed Foreground Wait Events (% of DB Time)",
            "Redo Log Switch Frequency (< 4 per hour recommended)",
            "Data Guard Transport & Apply Lag (0 seconds SLA)",
            "Tablespace High Water Mark & Datafile Free Space"
        ],
        "runbooks": [
            {
                "name": "Oracle Data Guard Switchover Procedure",
                "name_id": "Prosedur Switchover Terencana Oracle Data Guard",
                "steps": [
                    "Verify primary and standby are fully synchronized: check V$ARCHIVE_DEST_STATUS",
                    "Switch primary to standby: ALTER DATABASE COMMIT TO SWITCHOVER TO PHYSICAL STANDBY",
                    "Convert standby to primary: ALTER DATABASE COMMIT TO SWITCHOVER TO PRIMARY",
                    "Open new primary database: ALTER DATABASE OPEN",
                    "Verify log shipping resumes in reverse direction"
                ]
            },
            {
                "name": "ORA-01555 Snapshot Too Old Mitigation",
                "name_id": "Mitigasi Error ORA-01555 (Snapshot Too Old)",
                "steps": [
                    "Query V$UNDOSTAT to identify the longest-running query duration",
                    "Increase UNDO_RETENTION parameter to exceed max query execution time",
                    "Add storage space to UNDO tablespace or enable AUTOEXTEND",
                    "Tune long-running transaction fetch loops to avoid excessive commits"
                ]
            }
        ],
        "recommended_challenges": [
            "tablespace-capacity-alert",
            "blocking-sessions-root-cause",
            "tablespace-autoextend-exhaustion"
        ]
    },
    {
        "id": "postgres-dba",
        "title": "PostgreSQL Database Administrator",
        "title_id": "Administrator Basis Data PostgreSQL",
        "category": "Open Source Database Administration",
        "category_id": "Administrasi Database Open Source",
        "summary": "Master of PostgreSQL internals: MVCC multi-versioning, autovacuum optimization, Write-Ahead Logging (WAL), streaming replication, and Patroni high-availability clusters.",
        "summary_id": "Ahli internal PostgreSQL: kontrol konkurensi MVCC, tuning autovacuum, WAL, replikasi streaming, dan arsitektur klaster Patroni berkeandalan tinggi.",
        "engines": ["PostgreSQL 17", "PostgreSQL 16"],
        "recommended_tools": ["pgadmin", "pgmustard", "pgbackrest", "patroni", "prometheus"],
        "core_responsibilities": [
            "Tune shared_buffers, work_mem, maintenance_work_mem, and wal_buffers",
            "Manage Autovacuum cost limits and scale factors to eliminate table and index bloat",
            "Deploy and monitor physical streaming replication with replication slots",
            "Build zero-loss physical backup and Point-In-Time Recovery pipelines with pgBackRest"
        ],
        "core_responsibilities_id": [
            "Menyetel alokasi shared_buffers, work_mem, maintenance_work_mem, dan wal_buffers",
            "Mengelola parameter autovacuum untuk memberantas pembengkakan bloat tabel dan indeks",
            "Menerapkan replikasi streaming fisik dengan slot replikasi aman",
            "Membangun arsitektur backup fisik zero-loss dan PITR menggunakan pgBackRest"
        ],
        "skills_progression": {
            "junior": [
                "PostgreSQL process model (postmaster, backends, background workers)",
                "Managing roles, schemas, search_path, and least-privilege grants",
                "Logical backups via pg_dump and restoration via pg_restore",
                "Basic EXPLAIN and EXPLAIN ANALYZE query inspection"
            ],
            "mid": [
                "Tuning autovacuum_vacuum_cost_limit and autovacuum_vacuum_scale_factor per table",
                "Configuring PgBouncer for transaction-level connection pooling",
                "Setting up hot standby streaming replication and monitoring pg_stat_replication",
                "Diagnosing lock conflicts in pg_locks and slow queries in pg_stat_statements"
            ],
            "senior": [
                "High availability cluster orchestration with Patroni, etcd, and HAProxy",
                "Major version upgrades using pg_upgrade with hardlinks with zero data copy",
                "Declarative partitioning and foreign data wrappers (postgres_fdw)",
                "Transaction ID wraparound prevention and vacuum_freeze tuning"
            ]
        },
        "key_metrics": [
            "Transaction ID Age vs autovacuum_freeze_max_age (Wraparound headroom)",
            "Replication Slot Lag Bytes & WAL Directory Spool Size",
            "Cache Hit Ratio via pg_stat_database (> 99%)",
            "Dead Tuple Bloat Ratio via pg_stat_user_tables",
            "Connection Pool Saturation (Active vs max_connections)"
        ],
        "runbooks": [
            {
                "name": "Zero-Downtime Table Bloat Elimination (pg_repack)",
                "name_id": "Pembersihan Bloat Tabel Zero-Downtime (pg_repack)",
                "steps": [
                    "Identify bloated tables using pg_stat_user_tables dead tuple metrics",
                    "Verify available disk space is at least 2x the bloated table size",
                    "Run pg_repack utility targeting bloated table without taking exclusive table locks",
                    "Verify physical disk consumption drops and index scan latency improves"
                ]
            },
            {
                "name": "PostgreSQL Standby Replica Desynchronization Repair",
                "name_id": "Pemulihan Desinkronisasi Standby Replica PostgreSQL",
                "steps": [
                    "Check replication status on standby: SELECT * FROM pg_stat_wal_receiver",
                    "Check primary slot status: SELECT * FROM pg_stat_replication_slots",
                    "If replication slot was dropped, restore missing WAL segments from pgBackRest archive",
                    "Re-initialize standby via pg_basebackup or pgbackrest restore --delta if WAL is lost"
                ]
            }
        ],
        "recommended_challenges": [
            "blocking-sessions-root-cause",
            "replication-mirroring-lag-monitor",
            "deadlock-contention-hotspot"
        ]
    },
    {
        "id": "mysql-dba",
        "title": "MySQL & MariaDB Administrator",
        "title_id": "Administrator Basis Data MySQL & MariaDB",
        "category": "Open Source Database Administration",
        "category_id": "Administrasi Database Open Source",
        "summary": "Specialist in MySQL/MariaDB InnoDB storage engine, buffer pool memory management, GTID replication topologies, Galera multi-master clusters, and Percona toolkits.",
        "summary_id": "Spesialis mesin InnoDB MySQL/MariaDB, manajemen buffer pool, replikasi berbasis GTID, klaster multi-master Galera, dan toolkit Percona.",
        "engines": ["MariaDB 11.3", "MySQL 8.4 LTS"],
        "recommended_tools": ["mysql-workbench", "pmm", "xtrabackup", "percona-toolkit"],
        "core_responsibilities": [
            "Tune InnoDB Buffer Pool instances, redo log capacity, and flush algorithms",
            "Maintain Global Transaction Identifier (GTID) replication topologies and replication filters",
            "Execute online physical hot backups and point-in-time recovery with Percona XtraBackup",
            "Perform zero-downtime online schema alterations using pt-online-schema-change"
        ],
        "core_responsibilities_id": [
            "Menyetel alokasi InnoDB Buffer Pool, kapasitas redo log, dan algoritma flush",
            "Memelihara topologi replikasi berbasis GTID dan filter replikasi",
            "Mengeksekusi pencadangan fisik hot backup dan PITR dengan Percona XtraBackup",
            "Melakukan perubahan skema online tanpa downtime dengan pt-online-schema-change"
        ],
        "skills_progression": {
            "junior": [
                "InnoDB table creation, clustered indexes, and foreign keys",
                "User privileges, authentication plugins, and network bind configuration",
                "Taking logical backups via mysqldump / mydumper",
                "Enabling and inspecting slow query log output"
            ],
            "mid": [
                "Configuring master-replica streaming replication using GTID",
                "InnoDB buffer pool sizing (70-80% of server RAM) and dirty page flush tuning",
                "Non-blocking physical backups using Percona XtraBackup",
                "Diagnosing lock wait timeouts and deadlocks via SHOW ENGINE INNODB STATUS"
            ],
            "senior": [
                "Galera Cluster / Group Replication synchronous multi-primary architecture",
                "ProxySQL routing: read/write splitting, query caching, and connection pooling",
                "Zero-downtime MySQL major version rolling upgrades with minimal failover lag",
                "Kernel I/O tuning for SSD flash storage (innodb_io_capacity, innodb_flush_method)"
            ]
        },
        "key_metrics": [
            "Seconds_Behind_Source (Replication Lag in seconds)",
            "InnoDB Buffer Pool Read Hit Ratio (> 99.5%)",
            "Deadlocks Count / sec (mysql_global_status_innodb_deadlocks)",
            "Threads_connected vs max_connections capacity (> 80% alert)",
            "InnoDB Log Wait Ratio (Redo log buffer saturation)"
        ],
        "runbooks": [
            {
                "name": "Percona XtraBackup Hot Physical Restore",
                "name_id": "Restorasi Fisik Hot Backup Percona XtraBackup",
                "steps": [
                    "Stop running mysqld service: systemctl stop mysqld",
                    "Prepare the backup: xtrabackup --prepare --target-dir=/data/backup",
                    "Empty corrupted data directory: rm -rf /var/lib/mysql/*",
                    "Copy back database files: xtrabackup --copy-back --target-dir=/data/backup",
                    "Fix ownership: chown -R mysql:mysql /var/lib/mysql and start service"
                ]
            },
            {
                "name": "Broken GTID Replication Stream Repair",
                "name_id": "Perbaikan Aliran Replikasi GTID yang Terputus",
                "steps": [
                    "Inspect replica error: SHOW REPLICA STATUS\\G",
                    "Identify offending GTID causing duplicate key or table missing error",
                    "Inject empty transaction on replica to skip offending GTID cleanly",
                    "Restart replication thread: START REPLICA; verify Seconds_Behind_Source returns to 0"
                ]
            }
        ],
        "recommended_challenges": [
            "top-spending-customers",
            "replication-mirroring-lag-monitor",
            "deadlock-contention-hotspot"
        ]
    },
    {
        "id": "sqlserver-dba",
        "title": "Microsoft SQL Server DBA",
        "title_id": "Administrator Basis Data Microsoft SQL Server",
        "category": "Enterprise RDBMS Administration",
        "category_id": "Administrasi RDBMS Enterprise",
        "summary": "Focuses on enterprise SQL Server estates, Always On Availability Groups, TempDB contention mitigation, Query Store plan regressions, and Dynamic Management Views (DMVs).",
        "summary_id": "Fokus pada pengelolaan SQL Server enterprise, Always On Availability Groups, mitigasi kontensi TempDB, analisis Query Store, dan DMV.",
        "engines": ["SQL Server 2022", "Azure SQL Managed Instance"],
        "recommended_tools": ["ssms", "azure-data-studio", "extended-events"],
        "core_responsibilities": [
            "Administer Always On Availability Groups (Synchronous-Commit & Asynchronous-Commit)",
            "Optimize TempDB file layout to prevent allocation bottleneck on PFS/GAM/SGAM pages",
            "Analyze query performance regressions and force optimal plans via Query Store",
            "Automate index maintenance, statistics updates, and database integrity checks (DBCC CHECKDB)"
        ],
        "core_responsibilities_id": [
            "Mengelola cluster Always On Availability Groups (Sync & Async commit)",
            "Mengoptimalkan layout file TempDB untuk mencegah kontensi halaman PFS/GAM/SGAM",
            "Menganalisis regresi kueri dan memaksa plan optimal melalui Query Store",
            "Mengotomatiskan pemeliharaan indeks, statistik data, dan integritas DBCC CHECKDB"
        ],
        "skills_progression": {
            "junior": [
                "SQL Server Management Studio (SSMS) navigation, T-SQL scripting",
                "Database filegroups, log files (LDF), and recovery models (Full, Simple)",
                "Configuring SQL Server Agent maintenance plans and backup jobs",
                "Basic permissions, SQL logins, database users, and server roles"
            ],
            "mid": [
                "Always On Availability Group replica administration and listener routing",
                "Configuring TempDB with multiple uniform data files to prevent latch contention",
                "Diagnosing blocking locks and deadlocks using sys.dm_exec_requests and Extended Events",
                "Index defragmentation strategy: Reorganize vs Rebuild based on fragmentation %"
            ],
            "senior": [
                "Multi-subnet cross-datacenter Always On failover clustering (WSFC)",
                "Query Store plan forcing and automated tuning parameter calibration",
                "In-Memory OLTP memory-optimized tables and natively compiled stored procedures",
                "Disaster recovery auditing: Page Life Expectancy (PLE) and buffer pool memory pressures"
            ]
        },
        "key_metrics": [
            "Page Life Expectancy (PLE) in seconds (> 300s baseline, higher for large RAM)",
            "Always On Synchronization Health (HEALTHY / SYNCHRONIZED)",
            "Wait Statistics: PAGEIOLATCH_SH, CXPACKET, LCK_M_X % of total wait time",
            "TempDB Allocation Contention (PFS/GAM/SGAM latch wait duration)",
            "Log Space Used % & Virtual Log File (VLF) Count"
        ],
        "runbooks": [
            {
                "name": "Always On Availability Group Planned Failover",
                "name_id": "Failover Terencana Always On Availability Group",
                "steps": [
                    "Connect to target synchronous secondary replica via SSMS",
                    "Verify secondary replica synchronization state is SYNCHRONIZED",
                    "Execute failover command: ALTER AVAILABILITY GROUP [AG1] FAILOVER;",
                    "Verify listener routes application traffic to new primary replica",
                    "Confirm previous primary becomes secondary and resumes log synchronization"
                ]
            },
            {
                "name": "TempDB Allocation Contention Resolution",
                "name_id": "Resolusi Kontensi Alokasi TempDB",
                "steps": [
                    "Query sys.dm_os_waiting_tasks for PAGELATCH_UP waits on TempDB pages (2:1:1, 2:1:2)",
                    "Configure TempDB to have 8 equal-sized data files matching logical CPU cores",
                    "Enable Trace Flag 1118 (uniform extent allocation) if on legacy SQL Server versions",
                    "Restart SQL Server service during maintenance window to apply new file distribution"
                ]
            }
        ],
        "recommended_challenges": [
            "blocking-sessions-root-cause",
            "replication-mirroring-lag-monitor",
            "deadlock-contention-hotspot"
        ]
    },
    {
        "id": "db2-dba",
        "title": "IBM Db2 Database Administrator",
        "title_id": "Administrator Basis Data IBM Db2",
        "category": "Enterprise Core Banking & Financial DBA",
        "category_id": "Administrasi Database Perbankan Enterprise",
        "summary": "Manages enterprise IBM Db2 environments for banking, telecommunications, and high-security transactional workloads, specializing in HADR, pureScale, and db2pd diagnostic telemetry.",
        "summary_id": "Mengelola IBM Db2 untuk perbankan, telekomunikasi, dan beban kerja finansial, spesialisasi HADR, pureScale, dan telemetri diagnostik db2pd.",
        "engines": ["IBM Db2 11.5", "IBM Db2 11.1"],
        "recommended_tools": ["ibm-dmc", "db2-clp", "db2pd", "dbeaver"],
        "core_responsibilities": [
            "Administer High Availability Disaster Recovery (HADR) synchronization modes",
            "Configure bufferpools, SMS/DMS tablespaces, and multi-temperature storage tiers",
            "Perform live system and lock troubleshooting using the db2pd diagnostic tool",
            "Calibrate Workload Manager (WLM) thresholds to prevent runaway queries"
        ],
        "core_responsibilities_id": [
            "Mengelola sinkronisasi High Availability Disaster Recovery (HADR)",
            "Mengonfigurasi bufferpool, tablespace SMS/DMS, dan tier penyimpanan multi-temperature",
            "Melakukan troubleshooting lock dan memori secara live menggunakan alat db2pd",
            "Mengonfigurasi Workload Manager (WLM) untuk mencegah query monopoli sumber daya"
        ],
        "skills_progression": {
            "junior": [
                "Db2 instance, database creation, and catalog navigation via Db2 CLP",
                "Tablespace management (automatic storage, containers, prefetch size)",
                "Full database backup and restore commands (BACKUP DATABASE ... TO)",
                "User authentication, DBADM authority, and grant cascades"
            ],
            "mid": [
                "HADR configuration (SYNC, NEARSYNC, ASYNC, SUPERASYNC)",
                "Diagnosing lock waits, lock escalations, and deadlocks via db2pd -locks -wlocks",
                "Reorganizing fragmented tables and updating statistics (REORG TABLE, RUNSTATS)",
                "Tuning bufferpool hit ratios using MON_GET_BUFFERPOOL table functions"
            ],
            "senior": [
                "Db2 pureScale active-active clustering and Cluster Caching Facility (CF) tuning",
                "Automated HADR failover orchestration using Tivoli System Automation (TSA)",
                "Database partition feature (DPF) for massive parallel processing analytics",
                "Zero-downtime rolling fixpack updates and database catalog migrations"
            ]
        },
        "key_metrics": [
            "Bufferpool Hit Ratio (> 98%)",
            "HADR Log Shipping Gap & Peer State (PEER vs DISCONNECTED)",
            "Lock Escalation Rate (LOCKS_HELD approaching MAXLOCKS)",
            "Package Cache Hit Ratio (> 95%)",
            "Log Space Utilization % & Active Log Files Available"
        ],
        "runbooks": [
            {
                "name": "IBM Db2 HADR Graceful Takeover",
                "name_id": "Takeover Terencana IBM Db2 HADR",
                "steps": [
                    "Connect to standby database via db2 CLP: db2 connect to DB_NAME",
                    "Verify HADR state is PEER: db2pd -db DB_NAME -hadr",
                    "Initiate graceful takeover: db2 TAKEOVER HADR ON DB DB_NAME",
                    "Verify new primary transitions to PRIMARY state and previous primary becomes STANDBY"
                ]
            },
            {
                "name": "Db2 Lock Escalation & Deadlock Diagnostics",
                "name_id": "Diagnostik Eskalasi Lock & Deadlock Db2",
                "steps": [
                    "Inspect lock contention: db2pd -db DB_NAME -wlocks",
                    "Identify application handles holding exclusive locks on table rows",
                    "Check db2diag.log for DIA8300E lock escalation events",
                    "Increase LOCKLIST and MAXLOCKS database configuration parameters to prevent row-to-table escalation"
                ]
            }
        ],
        "recommended_challenges": [
            "tablespace-capacity-alert",
            "blocking-sessions-root-cause",
            "tablespace-autoextend-exhaustion"
        ]
    },
    {
        "id": "database-engineer",
        "title": "Database Engineer & Data Platform Specialist",
        "title_id": "Insinyur Basis Data & Spesialis Platform Data",
        "category": "Data Platform Engineering",
        "category_id": "Rekayasa Platform Data",
        "summary": "Bridges software engineering and database administration: builds declarative database migration pipelines, manages distributed SQL architectures, and optimizes microservice data layers.",
        "summary_id": "Menjembatani rekayasa software dan DBA: membangun pipeline migrasi skema deklaratif, mengelola arsitektur Distributed SQL, dan optimasi data microservices.",
        "engines": ["PostgreSQL", "CockroachDB", "MySQL", "Redis"],
        "recommended_tools": ["bytebase", "liquibase", "flyway", "terraform", "prisma"],
        "core_responsibilities": [
            "Design normalized transactional schemas and zero-downtime expand-contract migration patterns",
            "Manage connection pooling, client timeout budgets, and retry semantics across microservices",
            "Evaluate and deploy Distributed SQL databases (CockroachDB, YugabyteDB) for global horizontal scaling",
            "Implement Change Data Capture (CDC) streaming pipelines from transactional databases into Kafka"
        ],
        "core_responsibilities_id": [
            "Merancang skema transaksional dan pola migrasi expand-contract tanpa downtime",
            "Mengelola connection pooling, timeout budget, dan retry logic pada microservices",
            "Menerapkan database Distributed SQL (CockroachDB, YugabyteDB) untuk skalabilitas horizontal",
            "Membangun pipeline Change Data Capture (CDC) dari database transaksional ke Kafka"
        ],
        "skills_progression": {
            "junior": [
                "Relational schema modeling, constraints, foreign keys, and indexes",
                "Authoring repeatable migration scripts via Flyway or Liquibase",
                "Understanding connection pool configuration (min/max connections, idle timeouts)",
                "Identifying and resolving slow N+1 query patterns in application logs"
            ],
            "mid": [
                "Zero-downtime column renames and drops using expand-contract phasing",
                "Designing caching layers with Redis (Cache-Aside, Write-Through, cache invalidation)",
                "Implementing optimistic concurrency control using version numbers",
                "Configuring Debezium CDC connectors for event-driven architectures"
            ],
            "senior": [
                "Distributed SQL transaction coordination (Raft consensus, range leases, clock synchronization)",
                "Horizontal sharding key selection to prevent hot range / hot spot partitions",
                "Multi-region active-active database replication and conflict-free data types (CRDTs)",
                "Database CI/CD automation with automated schema drift detection"
            ]
        },
        "key_metrics": [
            "Migration Failure Rate (Target: 0% in production)",
            "Connection Pool Saturation % across service pods",
            "p99 Read and Write Transaction Latency",
            "CDC Replication Lag to Message Broker (< 1 second)"
        ],
        "runbooks": [
            {
                "name": "Zero-Downtime Column Addition with Default Value",
                "name_id": "Penambahan Kolom Skema Zero-Downtime dengan Default Value",
                "steps": [
                    "Add new nullable column without heavy table lock",
                    "Deploy application update writing to both old and new columns",
                    "Execute background data backfill script in controlled batches",
                    "Apply NOT NULL and DEFAULT constraint once backfill completes"
                ]
            }
        ],
        "recommended_challenges": [
            "category-revenue-cte",
            "dormant-customers-anti-join",
            "cumulative-transaction-ledger"
        ]
    },
    {
        "id": "dbre",
        "title": "Database Reliability Engineer (DBRE)",
        "title_id": "Insinyur Keandalan Basis Data (DBRE / SRE)",
        "category": "Infrastructure & Reliability",
        "category_id": "Infrastruktur & Keandalan",
        "summary": "Applies software engineering principles to database operations: automates failover mechanics, defines Service Level Objectives (SLOs), instruments telemetry, and conducts chaos engineering drills.",
        "summary_id": "Menerapkan prinsip rekayasa perangkat lunak pada operasional database: otomatisasi failover, rumusan SLO, telemetri observabilitas, dan chaos engineering.",
        "engines": ["PostgreSQL", "MySQL", "Redis", "Cassandra"],
        "recommended_tools": [
            "prometheus",
            "node-exporter",
            "grafana",
            "ansible",
            "terraform",
            "docker",
            "kubernetes"
        ],
        "core_responsibilities": [
            "Define and enforce Database Service Level Objectives (SLOs: 99.99% uptime, p99 latency < 20ms)",
            "Automate Kubernetes database operators (CloudNativePG, Percona Operators)",
            "Instrument Prometheus metric exporters and multi-window burn rate alert rules",
            "Conduct automated disaster recovery and chaos injection drills"
        ],
        "core_responsibilities_id": [
            "Menentukan dan memantau SLO database (Ketersediaan 99.99%, latensi p99 < 20ms)",
            "Mengotomatiskan operator database di Kubernetes (CloudNativePG, Percona Operators)",
            "Mengelola exporter Prometheus dan aturan alert multi-window burn rate",
            "Melakukan latihan pemulihan bencana otomatis dan chaos engineering"
        ],
        "skills_progression": {
            "junior": [
                "Linux OS telemetry: CPU, memory buffers, I/O wait, disk queue depth, inode capacity",
                "Deploying Prometheus database exporters (postgres_exporter, mysqld_exporter)",
                "Docker container volume persistence, storage classes, and /dev/shm tuning",
                "Aggregating error and slow query logs with Promtail and Loki"
            ],
            "mid": [
                "Multi-window error budget burn rate alerting implementation",
                "Kubernetes StatefulSet persistence, anti-affinity, and graceful termination hooks",
                "Kernel sysctl parameter calibration (vm.dirty_ratio, vm.swappiness, fs.file-max)",
                "Automated snapshot verification and automated PITR recovery tests"
            ],
            "senior": [
                "Self-healing database topology orchestration with Raft / etcd consensus",
                "Global multi-cloud active replication with automated DNS traffic steering",
                "Predictive capacity planning using time-series forecasting algorithms",
                "Architecting zero-downtime database disaster recovery with RPO=0 and RTO < 30s"
            ]
        },
        "key_metrics": [
            "SLO Error Budget Burn Rate",
            "Disk I/O Utilization % and IOPS Saturation",
            "Replication Lag in Seconds & Replay Queue Bytes",
            "Kubernetes Database Pod Buffer Cache Ratio & CPU Throttling Duration"
        ],
        "runbooks": [
            {
                "name": "Kubernetes Pod Buffer Cache & OOM Throttling Remediation",
                "name_id": "Penanganan Degradasi Buffer Cache & Throttling Pod K8s",
                "steps": [
                    "Inspect pod memory usage vs cgroup memory limit to prevent OOMKilled (ExitCode 137)",
                    "Check buffer cache hit ratio: if < 95%, scale pod memory limit or adjust shared_buffers",
                    "Verify /dev/shm size: ensure --shm-size or tmpfs volume is >= 1GB for parallel query IPC",
                    "Enforce pod anti-affinity rules so replicas never share the same physical node"
                ]
            },
            {
                "name": "Automated Primary Failover Quorum Verification",
                "name_id": "Verifikasi Kuorum Failover Primary Otomatis",
                "steps": [
                    "Verify consensus quorum in distributed coordination store (etcd / Consul)",
                    "Confirm replica has fully applied WAL/Binlog stream with zero transaction loss",
                    "Promote replica to primary and update virtual IP / DNS routing endpoint",
                    "Demote previous primary to standby upon recovery"
                ]
            }
        ],
        "recommended_challenges": [
            "replication-mirroring-lag-monitor",
            "k8s-pod-buffer-cache-ratio",
            "deadlock-contention-hotspot"
        ]
    },
    {
        "id": "perf-engineer",
        "title": "Database Performance & Capacity Engineer",
        "title_id": "Insinyur Optimasi Performa & Kapasitas Database",
        "category": "Performance & Capacity",
        "category_id": "Performa & Kapasitas",
        "summary": "Specialist in identifying query performance regressions, deep wait event analysis, latch contention profiling, and memory/storage subsystem hardware optimization.",
        "summary_id": "Spesialis identifikasi regresi performa query, analisis mendalam wait event, profiling kontensi latch, dan optimasi hardware subsistem memori/storage.",
        "engines": ["PostgreSQL", "Oracle", "SQL Server", "MySQL"],
        "recommended_tools": ["pmm", "pgmustard", "grafana", "extended-events"],
        "core_responsibilities": [
            "Perform wait-state analysis (AWR/ASH, Extended Events, pg_stat_statements)",
            "Identify and resolve parameter sniffing and execution plan regressions",
            "Design advanced indexing strategies (covering, functional, partial, and GiST/GIN indexes)",
            "Calibrate Cost-Based Optimizer cost parameters against storage NVMe I/O profiles"
        ],
        "core_responsibilities_id": [
            "Melakukan analisis wait-state (AWR/ASH, Extended Events, pg_stat_statements)",
            "Mengidentifikasi dan mengatasi masalah parameter sniffing dan regresi execution plan",
            "Merancang strategi indeks tingkat lanjut (covering, fungsional, parsial, GiST/GIN)",
            "Mengalibrasi parameter cost optimizer sesuai profil performa storage NVMe"
        ],
        "skills_progression": {
            "junior": [
                "Detailed query execution plan reading (Nested Loop, Hash Join, Merge Join)",
                "Identifying missing index warnings and redundant / duplicate indexes",
                "Understanding CPU vs I/O bound queries in database telemetry",
                "Monitoring slow query log trends over time"
            ],
            "mid": [
                "Wait event profiling: distinguishing CPU starvation from storage queue waits",
                "Parameter sniffing diagnosis and query hint application",
                "Partition pruning verification for massive historical tables",
                "Index defragmentation analysis and fillfactor calibration"
            ],
            "senior": [
                "Kernel I/O subsystem profiling with eBPF / bpftrace",
                "Memory latch and spinlock contention analysis on high-core NUMA machines",
                "Optimizer cost parameter calibration (random_page_cost, effective_cache_size)",
                "Designing automated query regression detection testbeds for staging environments"
            ]
        },
        "key_metrics": [
            "p95 and p99 Query Latency (< 15ms target for OLTP)",
            "Top 5 Wait Events % of Total Active DB Time",
            "Buffer Cache Miss % (< 1%)",
            "Physical Disk Read / Write Latency in ms (< 1ms on NVMe)"
        ],
        "runbooks": [
            {
                "name": "Parameter Sniffing Execution Plan Regression Resolution",
                "name_id": "Resolusi Regresi Execution Plan Akibat Parameter Sniffing",
                "steps": [
                    "Compare current poor execution plan with historical plan in Query Store / AWR",
                    "Identify skew in predicate value cardinality causing suboptimal plan selection",
                    "Force known good plan via Query Store / SQL Plan Baseline or rewrite query with RECOMPILE hint",
                    "Update statistics with FULLSCAN on affected table columns"
                ]
            }
        ],
        "recommended_challenges": [
            "k8s-pod-buffer-cache-ratio",
            "tablespace-capacity-alert",
            "deadlock-contention-hotspot"
        ]
    },
    {
        "id": "data-engineer",
        "title": "Data Engineer & Analytics Architect",
        "title_id": "Insinyur Data & Arsitek Analitika",
        "category": "Data Platform & Analytics",
        "category_id": "Platform Data & Analitika",
        "summary": "Builds scalable data lakehouses, designs star/snowflake dimensional schemas, manages streaming data pipelines, and provisions columnar analytical engines.",
        "summary_id": "Membangun data lakehouse terukur, merancang skema dimensional star/snowflake, mengelola pipeline streaming data, dan optimasi mesin analitik kolumnar.",
        "engines": ["Snowflake", "ClickHouse", "BigQuery", "PostgreSQL", "DuckDB"],
        "recommended_tools": ["dbeaver", "grafana", "bytebase"],
        "core_responsibilities": [
            "Design Kimball dimensional models (Star Schema, Fact tables, Slowly Changing Dimensions)",
            "Construct batch and real-time streaming ETL/ELT pipelines",
            "Optimize columnar storage engines (micro-partitioning, sorting keys, compression)",
            "Enforce data quality gates, schema evolution governance, and SLA monitoring"
        ],
        "core_responsibilities_id": [
            "Merancang model dimensional Kimball (Star Schema, tabel fakta, dimensi SCD)",
            "Membangun pipeline data ETL/ELT batch dan streaming real-time",
            "Mengoptimalkan mesin penyimpanan kolumnar (micro-partitioning, sorting key, kompresi)",
            "Menerapkan audit kualitas data, tata kelola evolusi skema, dan SLA data"
        ],
        "skills_progression": {
            "junior": [
                "SQL transformations, date/time manipulations, conditional aggregations",
                "Dimensional modeling fundamentals (Star vs Snowflake schema)",
                "Loading raw data into staging tables and basic cleansing",
                "Materialized view creation and incremental refresh strategies"
            ],
            "mid": [
                "Slowly Changing Dimensions (SCD Type 1, Type 2, Type 4)",
                "Partitioning and clustering key selection on columnar data platforms",
                "Real-time Change Data Capture (CDC) streaming integration with Kafka",
                "Data quality testing frameworks in SQL (dbt tests, Great Expectations)"
            ],
            "senior": [
                "Open table formats architecture (Apache Iceberg, Delta Lake, Apache Hudi)",
                "Data mesh architecture: federated data governance and domain data products",
                "Cost optimization across serverless query engines (BigQuery slots, Snowflake warehouses)",
                "Streaming analytical processing with vectorized ClickHouse engines"
            ]
        },
        "key_metrics": [
            "Data Freshness SLA Adherence (> 99.5%)",
            "Pipeline Ingestion Lag (Seconds from transactional commit to analytics)",
            "Data Quality Test Pass Rate (100% on financial ledgers)",
            "Query Compute Cost per Terabyte Scanned"
        ],
        "runbooks": [
            {
                "name": "Broken Analytical Ingestion Pipeline Recovery",
                "name_id": "Pemulihan Pipa Ingesti Analitik yang Terputus",
                "steps": [
                    "Inspect ingestion consumer group offset lag in Kafka / message queue",
                    "Identify poison pill schema mismatch or malformed JSON payload",
                    "Reroute malformed record to Dead Letter Queue (DLQ) for manual inspection",
                    "Resume consumer worker and verify downstream data freshness recovers"
                ]
            }
        ],
        "recommended_challenges": [
            "category-revenue-cte",
            "product-price-category-rank",
            "cumulative-transaction-ledger",
            "high-volume-authors"
        ]
    },
    {
        "id": "db-architect",
        "title": "Enterprise Database Architect",
        "title_id": "Arsitek Basis Data Enterprise",
        "category": "Enterprise Architecture",
        "category_id": "Arsitektur Enterprise",
        "summary": "Defines enterprise data strategies, navigates CAP/PACELC trade-offs, architects polyglot persistence systems, and ensures regulatory compliance across hybrid multi-cloud topologies.",
        "summary_id": "Menentukan strategi data enterprise, menavigasi trade-off CAP/PACELC, arsitektur polyglot persistence, dan kepatuhan regulasi di multi-cloud.",
        "engines": ["PostgreSQL", "Oracle", "CockroachDB", "MongoDB", "Snowflake"],
        "recommended_tools": ["bytebase", "terraform", "prometheus", "dbeaver"],
        "core_responsibilities": [
            "Formulate polyglot persistence blueprints (Relational + Document + Cache + Search)",
            "Evaluate CAP and PACELC trade-offs for distributed global transaction systems",
            "Design disaster recovery architectures with multi-decade data retention rules",
            "Establish enterprise security, data sovereignty, and encryption standards"
        ],
        "core_responsibilities_id": [
            "Merumuskan cetak biru polyglot persistence (Relasional + Dokumen + Cache + Search)",
            "Mengevaluasi trade-off CAP dan PACELC untuk sistem transaksi global terdistribusi",
            "Merancang arsitektur disaster recovery dengan retensi data multi-dekade",
            "Menetapkan standar keamanan enterprise, kedaulatan data, dan enkripsi"
        ],
        "skills_progression": {
            "junior": [
                "Relational vs NoSQL vs Analytical engine strengths and trade-offs",
                "Entity Relationship Diagram (ERD) design and normalization principles",
                "Basic data encryption at rest and in transit compliance",
                "Designing backup retention policies"
            ],
            "mid": [
                "Polyglot persistence patterns: event-driven consistency and read/write segregation (CQRS)",
                "Multi-region active-passive disaster recovery topology design",
                "Database sharding architectures vs scale-up enterprise systems",
                "Regulatory compliance standards (PCI-DSS, GDPR, HIPAA, SOC 2)"
            ],
            "senior": [
                "Distributed consistency models: Linearizable, Serializable, Snapshot, Eventual",
                "Global multi-cloud data sovereignty and cross-border regulatory compliance",
                "Total Cost of Ownership (TCO) modeling across database license models",
                "Enterprise data mesh architecture and multi-tenant isolation patterns"
            ]
        },
        "key_metrics": [
            "Total Cost of Ownership (TCO) per Business Transaction",
            "Enterprise High Availability SLA (99.999% Five Nines)",
            "Compliance Audit Pass Rate (100% across PCI-DSS / SOC 2)",
            "Architectural Technical Debt Index"
        ],
        "runbooks": [
            {
                "name": "Enterprise Database Architecture Review",
                "name_id": "Tinjauan Kelayakan Arsitektur Database Enterprise",
                "steps": [
                    "Audit data volume growth and peak write TPS projections over 3 years",
                    "Evaluate consistency requirements: Strong Consistency (ACID) vs Eventual Consistency",
                    "Review single point of failure (SPOF) risks across compute, network, and storage",
                    "Produce architecture decision record (ADR) documenting trade-offs and vendor choices"
                ]
            }
        ],
        "recommended_challenges": [
            "concurrency-serializable-anomaly",
            "tablespace-autoextend-exhaustion",
            "replication-mirroring-lag-monitor"
        ]
    }
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
    for (t_name,) in tables_res:
        cols_res = conn.execute(f"PRAGMA table_info('{t_name}');").fetchall()
        count_res = conn.execute(f"SELECT COUNT(*) FROM '{t_name}';").fetchone()
        row_count = count_res[0] if count_res else 0

        schema_tables.append({
            "name": t_name,
            "columns": [
                {
                    "cid": col["cid"],
                    "name": col["name"],
                    "type": col["type"],
                    "notnull": bool(col["notnull"]),
                    "pk": bool(col["pk"]),
                }
                for col in cols_res
            ],
            "row_count": row_count,
        })

    conn.close()
    return {
        "slug": dataset_slug,
        "name": template["name"],
        "description": template["description"],
        "tables": schema_tables,
    }


@router.post("/exercises/{slug}/submit", response_model=ChallengeSubmitResponse)
async def submit_challenge(slug: str, body: ChallengeSubmitRequest) -> ChallengeSubmitResponse:
    challenge = next((c for c in CHALLENGES if c["slug"] == slug), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge exercise not found")

    dataset_slug = challenge["dataset"]
    engine_type = body.engine.lower().strip()
    is_id = body.language == "id"
    hints = challenge["hints_id"] if is_id else challenge["hints"]

    try:
        if engine_type == "postgres":
            ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = _execute_postgres(
                dataset_slug, challenge["solution_sql"], body.query
            )
        elif engine_type in ("mysql", "mariadb"):
            ref_columns, ref_rows, user_cols, user_rows, elapsed_ms, err_msg = _execute_mysql(
                dataset_slug, challenge["solution_sql"], body.query
            )
        elif engine_type == "oracle":
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
        elif engine_type in ("mssql", "sqlserver"):
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
        elif engine_type == "db2":
            conn = sqlite3.connect(":memory:")
            conn.row_factory = sqlite3.Row
            seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]
            conn.executescript(seed_sql)
            cur_ref = conn.execute(challenge["solution_sql"])
            ref_columns = [d[0] for d in cur_ref.description]
            ref_rows = [list(r) for r in cur_ref.fetchall()]

            adapter = Db2Adapter()
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
            elapsed_ms=0.0,
            feedback=["Terjadi kegagalan koneksi ke sandbox engine." if is_id else "Database engine connection failed."],
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
