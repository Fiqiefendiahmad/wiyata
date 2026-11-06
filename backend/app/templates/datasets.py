"""Sample dataset schemas and seed data for learning sandboxes."""

TEMPLATES = {
    "ecommerce": {
        "name": "E-Commerce Store",
        "description": "Customers, products, orders, and order items with realistic data",
        "sql": """
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    city TEXT,
    country TEXT DEFAULT 'Indonesia',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER REFERENCES categories(id),
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT CHECK(status IN ('pending', 'completed', 'cancelled')) DEFAULT 'completed',
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
        "description": "Students, instructors, courses, and grade enrollments",
        "sql": """
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE instructors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    department_id INTEGER REFERENCES departments(id),
    email TEXT UNIQUE NOT NULL
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    major TEXT NOT NULL,
    admission_year INTEGER NOT NULL
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    credits INTEGER NOT NULL,
    instructor_id INTEGER REFERENCES instructors(id)
);

CREATE TABLE enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    grade TEXT CHECK(grade IN ('A', 'B', 'C', 'D', 'F', 'IP')),
    semester TEXT NOT NULL
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
        "description": "Authors, articles, tags, and reader comments",
        "sql": """
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    bio TEXT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER REFERENCES authors(id),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    views INTEGER DEFAULT 0,
    published BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(id),
    tag_id INTEGER REFERENCES tags(id),
    PRIMARY KEY (post_id, tag_id)
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER REFERENCES posts(id),
    author_name TEXT NOT NULL,
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
    "blank": {
        "name": "Blank Database",
        "description": "Clean, empty SQLite database ready for DDL experimentation",
        "sql": "-- Clean sandbox\n"
    }
}
