"""Sample dataset schemas and seed data for learning sandboxes across SQLite, PostgreSQL, and MySQL."""

TEMPLATES = {
    "banking": {
        "name": "Core Banking System",
        "description": "Nasabah, rekening tabungan/giro, mutasi transaksi (QRIS/Transfer/ATM), dan pinjaman",
        "sql": """
CREATE TABLE branches (
    branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
    branch_code VARCHAR(64) UNIQUE NOT NULL,
    branch_name VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    cif_number VARCHAR(64) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    nik VARCHAR(32) UNIQUE NOT NULL,
    phone_number VARCHAR(32) NOT NULL,
    address TEXT,
    city VARCHAR(100) DEFAULT 'Jakarta',
    kyc_status VARCHAR(20) DEFAULT 'VERIFIED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    account_number VARCHAR(64) PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    branch_id INTEGER NOT NULL REFERENCES branches(branch_id),
    account_type VARCHAR(32) DEFAULT 'SAVINGS',
    currency VARCHAR(8) DEFAULT 'IDR',
    balance REAL NOT NULL DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    opened_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference_no VARCHAR(64) UNIQUE NOT NULL,
    from_account_number VARCHAR(64) NOT NULL REFERENCES accounts(account_number),
    to_account_number VARCHAR(64) REFERENCES accounts(account_number),
    transaction_type VARCHAR(32) NOT NULL,
    amount REAL NOT NULL,
    fee REAL DEFAULT 0.0,
    channel VARCHAR(32) DEFAULT 'MOBILE_BANKING',
    status VARCHAR(20) DEFAULT 'SUCCESS',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE loans (
    loan_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    loan_type VARCHAR(32) NOT NULL,
    principal_amount REAL NOT NULL,
    interest_rate_pct REAL NOT NULL DEFAULT 7.5,
    tenor_months INTEGER NOT NULL,
    monthly_installment REAL NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    disbursed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed Branches
INSERT INTO branches (branch_code, branch_name, city) VALUES
('KC-JKT-01', 'Kantor Cabang Sudirman', 'Jakarta'),
('KC-BDG-01', 'Kantor Cabang Dago', 'Bandung'),
('KC-SBY-01', 'Kantor Cabang Pemuda', 'Surabaya'),
('KC-YOG-01', 'Kantor Cabang Malioboro', 'Yogyakarta');

-- Seed Customers
INSERT INTO customers (cif_number, full_name, nik, phone_number, address, city) VALUES
('CIF-88201', 'Bambang Hartono', '3171012903850001', '081234567890', 'Jl. Sudirman Kav 25', 'Jakarta'),
('CIF-88202', 'Siti Nurhaliza', '3273024805900002', '081398765432', 'Jl. Riau No 14', 'Bandung'),
('CIF-88203', 'Hendra Wijaya', '3578031201780003', '081512344321', 'Jl. Basuki Rahmat 88', 'Surabaya'),
('CIF-88204', 'Ratna Sari Dewi', '3471046511950004', '082167890123', 'Jl. Kaliurang Km 5', 'Yogyakarta'),
('CIF-88205', 'Agus Prayitno', '3174051010880005', '081855566677', 'Jl. Gatot Subroto 12', 'Jakarta');

-- Seed Accounts
INSERT INTO accounts (account_number, customer_id, branch_id, account_type, balance, status) VALUES
('1020304001', 1, 1, 'CHECKING', 145000000.0, 'ACTIVE'),
('1020304002', 1, 1, 'SAVINGS', 38500000.0, 'ACTIVE'),
('1020304003', 2, 2, 'SAVINGS', 18750000.0, 'ACTIVE'),
('1020304004', 3, 3, 'SAVINGS', 92400000.0, 'ACTIVE'),
('1020304005', 4, 4, 'SAVINGS', 4500000.0, 'ACTIVE'),
('1020304006', 5, 1, 'TIME_DEPOSIT', 250000000.0, 'ACTIVE');

-- Seed Transactions (Mutasi Rekening)
INSERT INTO transactions (reference_no, from_account_number, to_account_number, transaction_type, amount, fee, channel, description) VALUES
('TRX-20261101-001', '1020304001', '1020304004', 'TRANSFER', 15000000.0, 6500.0, 'MOBILE_BANKING', 'Pembayaran invoice suplai logistik'),
('TRX-20261102-002', '1020304003', '1020304005', 'QRIS', 350000.0, 0.0, 'QRIS', 'Pembayaran resto Dago Cafe'),
('TRX-20261102-003', '1020304002', NULL, 'WITHDRAWAL', 2000000.0, 0.0, 'ATM', 'Tarik tunai ATM Sudirman'),
('TRX-20261103-004', '1020304004', '1020304002', 'TRANSFER', 8500000.0, 6500.0, 'INTERNET_BANKING', 'Transfer pembagian dividen proyek'),
('TRX-20261104-005', '1020304005', NULL, 'BILL_PAYMENT', 450000.0, 2500.0, 'MOBILE_BANKING', 'Pembayaran tagihan listrik PLN'),
('TRX-20261105-006', '1020304001', '1020304003', 'TRANSFER', 32000000.0, 6500.0, 'MOBILE_BANKING', 'Transfer pembayaran vendor kantor');

-- Seed Loans
INSERT INTO loans (customer_id, loan_type, principal_amount, interest_rate_pct, tenor_months, monthly_installment, status) VALUES
(1, 'MORTGAGE', 850000000.0, 6.8, 120, 9780000.0, 'ACTIVE'),
(3, 'SME_LOAN', 250000000.0, 8.5, 36, 7890000.0, 'ACTIVE'),
(4, 'AUTO_LOAN', 180000000.0, 7.2, 48, 4320000.0, 'ACTIVE');
"""
    },
    "ecommerce": {
        "name": "E-Commerce Store",
        "description": "Pelanggan, produk, kategori, dan transaksi belanja online",
        "sql": """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Indonesia',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    name VARCHAR(255) NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'completed',
    total_amount REAL NOT NULL DEFAULT 0
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price REAL NOT NULL
);

-- Seed Categories
INSERT INTO categories (name, description) VALUES
('Electronics', 'Gadgets, hardware, and accessories'),
('Books', 'Technical and non-technical literature'),
('Home & Living', 'Furniture and essentials');

-- Seed Customers
INSERT INTO customers (first_name, last_name, email, city) VALUES
('Ahmad', 'Fauzi', 'ahmad.fauzi@example.id', 'Jakarta'),
('Dewi', 'Lestari', 'dewi.lestari@example.id', 'Bandung'),
('Budi', 'Santoso', 'budi.santoso@example.id', 'Surabaya'),
('Siti', 'Rahma', 'siti.rahma@example.id', 'Yogyakarta'),
('Reza', 'Pratama', 'reza.pratama@example.id', 'Semarang');

-- Seed Products
INSERT INTO products (category_id, name, price, stock) VALUES
(1, 'Mechanical Keyboard 75%', 850000.0, 45),
(1, 'Wireless Gaming Mouse', 450000.0, 60),
(1, 'USB-C Dual 4K Dock', 1200000.0, 20),
(2, 'Designing Data-Intensive Applications', 420000.0, 30),
(2, 'SQL Performance Explained', 350000.0, 25),
(2, 'Database Internals', 480000.0, 15),
(3, 'Ergonomic Desk Mat', 180000.0, 100),
(3, 'Monitor Arm Heavy Duty', 650000.0, 35);

-- Seed Orders & Items
INSERT INTO orders (customer_id, status, total_amount) VALUES
(1, 'completed', 1300000.0),
(2, 'completed', 420000.0),
(3, 'completed', 1650000.0),
(1, 'pending', 480000.0),
(4, 'completed', 630000.0);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 850000.0),
(1, 2, 1, 450000.0),
(2, 4, 1, 420000.0),
(3, 3, 1, 1200000.0),
(3, 2, 1, 450000.0),
(4, 6, 1, 480000.0),
(5, 5, 1, 350000.0),
(5, 7, 1, 180000.0),
(5, 7, 1, 100000.0);
"""
    },
    "school": {
        "name": "University Academy",
        "description": "Akademik kampus: mahasiswa, dosen, mata kuliah, dan indeks prestasi",
        "sql": """
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE instructors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    major VARCHAR(100) NOT NULL,
    admission_year INTEGER NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    code VARCHAR(32) UNIQUE NOT NULL,
    credits INTEGER NOT NULL,
    instructor_id INTEGER REFERENCES instructors(id)
);

CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade VARCHAR(8),
    semester VARCHAR(32) NOT NULL
);

INSERT INTO departments (name) VALUES ('Computer Science'), ('Information Systems'), ('Data Science');

INSERT INTO instructors (name, department_id, email) VALUES
('Dr. Bambang Wijaya', 1, 'bambang@univ.ac.id'),
('Prof. Sri Mulyani', 2, 'sri.m@univ.ac.id'),
('Dr. Kevin Sanjaya', 3, 'kevin.s@univ.ac.id');

INSERT INTO students (name, email, major, admission_year) VALUES
('Alif Nurrahman', 'alif@student.univ.ac.id', 'Computer Science', 2024),
('Bella Safira', 'bella@student.univ.ac.id', 'Information Systems', 2023),
('Candra Kusuma', 'candra@student.univ.ac.id', 'Data Science', 2024),
('Dian Puspita', 'dian@student.univ.ac.id', 'Computer Science', 2023);

INSERT INTO courses (title, code, credits, instructor_id) VALUES
('Relational Database Systems', 'CS301', 3, 1),
('Database Tuning & Indexing', 'CS402', 3, 1),
('Enterprise Architecture', 'IS201', 3, 2),
('Applied Machine Learning', 'DS301', 4, 3);

INSERT INTO enrollments (student_id, course_id, grade, semester) VALUES
(1, 1, 'A', '2024-1'),
(1, 2, 'B', '2024-2'),
(2, 1, 'B', '2024-1'),
(2, 3, 'A', '2024-1'),
(3, 1, 'A', '2024-1'),
(3, 4, 'A', '2024-1'),
(4, 2, 'A', '2024-2');
"""
    },
    "blog": {
        "name": "Tech Blog Platform",
        "description": "Penulis, publikasi artikel teknik, tag, dan komentar pembaca",
        "sql": """
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    bio TEXT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER REFERENCES authors(id),
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(128) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(64) UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER REFERENCES posts(id),
    author_name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO authors (username, bio) VALUES
('dba_master', '10+ years managing PostgreSQL & MySQL in production'),
('sql_ninja', 'Query optimization and database architecture enthusiast');

INSERT INTO tags (name) VALUES ('SQL'), ('PostgreSQL'), ('Optimization'), ('Indexes'), ('SQLite');

INSERT INTO posts (author_id, title, slug, content, views) VALUES
(1, 'Mastering B-Tree Indexes in PostgreSQL', 'mastering-btree-indexes', 'Indexes are crucial for high-speed query performance...', 1420),
(1, 'Why Write-Ahead Logging (WAL) Matters', 'why-wal-matters', 'Durability is the D in ACID. Let us dive into WAL...', 890),
(2, 'Common Anti-Patterns in SQL Joins', 'common-sql-join-antipatterns', 'Cartesian joins and missing indexes can ruin response times...', 2150);

INSERT INTO post_tags (post_id, tag_id) VALUES (1, 1), (1, 2), (1, 4), (2, 2), (3, 1), (3, 3);

INSERT INTO comments (post_id, author_name, content) VALUES
(1, 'Raden', 'Great breakdown of partial vs expression indexes!'),
(1, 'Gilang', 'Do you recommend covering indexes in PostgreSQL 16?'),
(3, 'Maya', 'This saved me hours of query debugging today.');
"""
    },
    "dba_ops": {
        "name": "Enterprise DBA & Infrastructure Telemetry",
        "description": "Telemetri operasional enterprise: tablespaces, blocking locks, cluster mirroring/replikasi, dan pod database Kubernetes",
        "sql": """
CREATE TABLE dba_tablespaces (
    tablespace_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tablespace_name VARCHAR(64) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    allocated_mb REAL NOT NULL,
    used_mb REAL NOT NULL,
    max_mb REAL NOT NULL,
    autoextensible BOOLEAN NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'ONLINE'
);

CREATE TABLE active_sessions (
    spid INTEGER PRIMARY KEY,
    blocked_by_spid INTEGER REFERENCES active_sessions(spid),
    db_user VARCHAR(64) NOT NULL,
    client_host VARCHAR(100) NOT NULL,
    wait_event VARCHAR(128) NOT NULL,
    wait_time_seconds INTEGER NOT NULL DEFAULT 0,
    lock_type VARCHAR(32) NOT NULL,
    query_snippet TEXT NOT NULL
);

CREATE TABLE cluster_replicas (
    replica_id INTEGER PRIMARY KEY AUTOINCREMENT,
    replica_name VARCHAR(64) NOT NULL,
    replica_role VARCHAR(32) NOT NULL,
    sync_state VARCHAR(32) NOT NULL,
    lag_seconds REAL NOT NULL DEFAULT 0.0,
    replay_queue_kb REAL NOT NULL DEFAULT 0.0,
    network_latency_ms REAL NOT NULL DEFAULT 0.5,
    status VARCHAR(20) NOT NULL DEFAULT 'HEALTHY'
);

CREATE TABLE k8s_db_pods (
    pod_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pod_name VARCHAR(128) NOT NULL,
    node_name VARCHAR(64) NOT NULL,
    db_engine VARCHAR(32) NOT NULL,
    memory_limit_mb INTEGER NOT NULL,
    memory_used_mb INTEGER NOT NULL,
    buffer_cache_reads BIGINT NOT NULL,
    disk_physical_reads BIGINT NOT NULL,
    cpu_throttled_seconds REAL NOT NULL DEFAULT 0.0,
    restart_count INTEGER NOT NULL DEFAULT 0
);

-- Seed Enterprise Tablespaces
INSERT INTO dba_tablespaces (tablespace_name, file_name, allocated_mb, used_mb, max_mb, autoextensible, status) VALUES
('USERS_DATA', '/u01/app/oracle/oradata/prod/users01.dbf', 10240.0, 9420.0, 32768.0, 1, 'ONLINE'),
('FINANCE_TBS', '/var/lib/postgresql/17/data/tblspc/fin01.dat', 40960.0, 36800.0, 40960.0, 0, 'ONLINE'),
('TEMP_TBS', '/var/opt/mssql/data/tempdb01.mdf', 20480.0, 4100.0, 65536.0, 1, 'ONLINE'),
('INDEX_TBS', '/u01/app/oracle/oradata/prod/indx01.dbf', 16384.0, 14200.0, 16384.0, 0, 'ONLINE'),
('AUDIT_ARCHIVE', '/mnt/disks/pg_audit/audit01.dat', 51200.0, 24500.0, 102400.0, 1, 'ONLINE'),
('SYSTEM_TBS', '/u01/app/oracle/oradata/prod/system01.dbf', 8192.0, 7500.0, 8192.0, 1, 'ONLINE');

-- Seed Active Sessions & Lock Blocker Tree
INSERT INTO active_sessions (spid, blocked_by_spid, db_user, client_host, wait_event, wait_time_seconds, lock_type, query_snippet) VALUES
(101, NULL, 'finance_app', '10.244.3.45', 'enq: TX - row lock contention', 0, 'EXCLUSIVE', 'UPDATE accounts SET balance = balance - 500000 WHERE id = 4410;'),
(145, 101, 'portal_svc', '10.244.4.12', 'enq: TX - row lock contention', 48, 'EXCLUSIVE', 'UPDATE accounts SET balance = balance + 500000 WHERE id = 4410;'),
(182, 101, 'batch_etl', '10.244.1.88', 'enq: TX - row lock contention', 125, 'EXCLUSIVE', 'UPDATE accounts SET status = "RECONCILED" WHERE id = 4410;'),
(205, NULL, 'bi_reporting', '10.244.5.19', 'async_io_wait', 1, 'SHARED', 'SELECT customer_id, SUM(amount) FROM ledger GROUP BY customer_id;'),
(220, 145, 'mobile_gateway', '10.244.6.30', 'enq: TX - row lock contention', 32, 'EXCLUSIVE', 'SELECT balance FROM accounts WHERE id = 4410 FOR UPDATE;'),
(300, NULL, 'dba_admin', '10.244.0.5', 'idle', 0, 'NONE', 'SELECT spid, wait_event FROM active_sessions;');

-- Seed Cluster Replicas & Mirroring
INSERT INTO cluster_replicas (replica_name, replica_role, sync_state, lag_seconds, replay_queue_kb, network_latency_ms, status) VALUES
('db-primary-0', 'PRIMARY', 'SYNCHRONIZED', 0.0, 0.0, 0.2, 'HEALTHY'),
('db-sync-standby-1', 'SYNC_STANDBY', 'SYNCHRONIZED', 0.8, 120.0, 1.4, 'HEALTHY'),
('db-dr-replica-2', 'ASYNC_STANDBY', 'STREAMING', 24.5, 12400.0, 18.5, 'DEGRADED'),
('db-bi-analytics-3', 'READ_REPLICA', 'DESYNCHRONIZED', 185.0, 482000.0, 42.0, 'DESYNCHRONIZED'),
('db-edge-cache-4', 'READ_REPLICA', 'STREAMING', 3.2, 450.0, 5.1, 'HEALTHY');

-- Seed Kubernetes Database Pods & Cache Hit Ratio
INSERT INTO k8s_db_pods (pod_name, node_name, db_engine, memory_limit_mb, memory_used_mb, buffer_cache_reads, disk_physical_reads, cpu_throttled_seconds, restart_count) VALUES
('patroni-postgres-0', 'k8s-worker-nvme-01', 'PostgreSQL 17', 32768, 29400, 12500000, 320000, 0.0, 0),
('patroni-postgres-1', 'k8s-worker-nvme-02', 'PostgreSQL 17', 32768, 31800, 8900000, 1450000, 14.8, 1),
('innodb-cluster-mysql-0', 'k8s-worker-hdd-03', 'MySQL 11', 16384, 15900, 4500000, 850000, 26.2, 3),
('oracle-pdb-finance-0', 'k8s-worker-baremetal-04', 'Oracle 23ai', 65536, 58200, 35000000, 700000, 0.0, 0),
('mssql-alwayson-0', 'k8s-worker-nvme-05', 'SQL Server 2022', 49152, 46100, 22000000, 2400000, 18.5, 2);
"""
    },
    "blank": {
        "name": "Blank Database",
        "description": "Database kosong untuk eksperimen skema dan DDL bebas",
        "sql": "-- Clean sandbox\n"
    }
}
