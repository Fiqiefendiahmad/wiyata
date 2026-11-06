import re
from typing import Any

import sqlglot
from sqlglot import exp

from app.config import settings


def optimize_query(query: str, dialect: str = "sqlite") -> list[dict[str, str]]:
    """Analyzes SQL query AST for common anti-patterns and performance optimizations."""
    suggestions: list[dict[str, str]] = []

    try:
        parsed = sqlglot.parse_one(query, read=dialect)
    except Exception:
        return [{"type": "syntax_error", "message": "Cannot parse SQL for optimization check."}]

    # 1. SELECT * check
    select_all = False
    for select in parsed.find_all(exp.Select):
        for expr in select.expressions:
            if isinstance(expr, exp.Star):
                select_all = True
                break

    if select_all:
        suggestions.append({
            "type": "projection_overhead",
            "severity": "warning",
            "message": "Query uses 'SELECT *'. In production workloads, explicitly project only required columns to reduce memory, network bandwidth, and prevent table schema change breakages.",
            "rule": "RULE-SQL-01"
        })

    # 2. Missing LIMIT on SELECT query
    if isinstance(parsed, exp.Select) and not parsed.args.get("limit"):
        suggestions.append({
            "type": "unbounded_result",
            "severity": "info",
            "message": "Query does not specify a 'LIMIT' clause. Unbounded queries can exhaust database memory or lock buffers on large tables.",
            "rule": "RULE-SQL-02"
        })

    # 3. Comma join (Implicit cross join / Cartesian product risk)
    joins = parsed.find_all(exp.Join)
    for join in joins:
        if not join.args.get("on") and not join.args.get("using") and join.args.get("kind") != "CROSS":
            suggestions.append({
                "type": "implicit_join",
                "severity": "warning",
                "message": "Detected join without explicit 'ON' or 'USING' clause. Ensure this is not an unintentional Cartesian product.",
                "rule": "RULE-SQL-03"
            })

    # 4. Leading wildcard LIKE pattern (e.g. LIKE '%text')
    for like_expr in parsed.find_all(exp.Like):
        pattern = str(like_expr.this)
        if pattern.startswith("'%") or pattern.startswith('"%'):
            suggestions.append({
                "type": "unindexed_like",
                "severity": "warning",
                "message": "Leading wildcard pattern 'LIKE %...' prevents standard B-Tree index utilization and forces a full table scan. Consider trigram indexes or full-text search.",
                "rule": "RULE-SQL-04"
            })

    return suggestions


def explain_query_natural(query: str, language: str = "en") -> list[str]:
    """Generates a plain-language explanation of what the query is doing step-by-step."""
    steps: list[str] = []
    is_id = language == "id"

    try:
        parsed = sqlglot.parse_one(query)
    except Exception:
        return ["Query format parsing error." if not is_id else "Format query tidak dapat diurai."]

    if isinstance(parsed, exp.Select):
        # 1. FROM clause
        from_table = parsed.find(exp.From)
        if from_table:
            tbl_name = from_table.this.sql()
            if is_id:
                steps.append(f"1. Membaca data dasar dari tabel '{tbl_name}'.")
            else:
                steps.append(f"1. Scans base records from source table '{tbl_name}'.")

        # 2. JOINS
        joins = list(parsed.find_all(exp.Join))
        if joins:
            join_names = [j.this.sql() for j in joins]
            if is_id:
                steps.append(f"2. Menggabungkan data dengan tabel berelasi: {', '.join(join_names)}.")
            else:
                steps.append(f"2. Joins with related tables: {', '.join(join_names)}.")

        # 3. WHERE filters
        where = parsed.find(exp.Where)
        if where:
            if is_id:
                steps.append(f"3. Menyaring baris data berdasarkan kriteria: {where.this.sql()}.")
            else:
                steps.append(f"3. Filters rows meeting predicate: {where.this.sql()}.")

        # 4. GROUP BY
        group = parsed.find(exp.Group)
        if group:
            if is_id:
                steps.append(f"4. Mengelompokkan hasil agregat berdasarkan: {group.sql()}.")
            else:
                steps.append(f"4. Groups results for aggregation by: {group.sql()}.")

        # 5. ORDER BY
        order = parsed.find(exp.Order)
        if order:
            if is_id:
                steps.append(f"5. Mengurutkan hasil akhir berdasarkan: {order.sql()}.")
            else:
                steps.append(f"5. Sorts the output rows by: {order.sql()}.")

        # 6. LIMIT
        limit = parsed.find(exp.Limit)
        if limit:
            if is_id:
                steps.append(f"6. Membatasi jumlah output maksimal sebanyak {limit.expression.sql()} baris.")
            else:
                steps.append(f"6. Restricts output to maximum {limit.expression.sql()} rows.")

    return steps if steps else (["Query executed as custom expression."] if not is_id else ["Query dijalankan sebagai ekspresi kustom."])


async def generate_sql_from_prompt(
    prompt: str,
    schema: list[dict[str, Any]],
    engine: str = "sqlite",
    language: str = "en",
) -> dict[str, Any]:
    """Generates schema-aware SQL from user natural language prompt."""
    p_lower = prompt.lower().strip()
    is_id = language == "id" or any(w in p_lower for w in ["cari", "tampilkan", "semua", "pelanggan", "produk", "pesanan", "berapa"])

    # Extract available table names
    table_names = [t.get("name") for t in schema]

    generated_sql = ""
    explanation = []

    # Banking / Core Banking System matching
    if any(k in p_lower for k in ["bank", "rekening", "saldo", "nasabah", "account", "balance", "transfer", "mutasi", "pinjaman", "loan", "cif"]):
        if any(k in p_lower for k in ["transaksi", "transfer", "mutasi", "trx", "kirim"]):
            generated_sql = (
                "SELECT t.reference_no, t.from_account_number, t.to_account_number, t.transaction_type, t.amount, t.fee, t.channel, t.description\n"
                "FROM transactions t\n"
                "ORDER BY t.created_at DESC\n"
                "LIMIT 10;"
            )
            explanation = [
                "Menampilkan daftar mutasi transaksi perbankan terbaru" if is_id else "Queries recent banking transactions with reference numbers and fee details",
                "Diurutkan berdasarkan waktu transaksi terbaru" if is_id else "Sorted by most recent transaction timestamp"
            ]
        elif any(k in p_lower for k in ["pinjaman", "loan", "kredit", "cicilan"]):
            generated_sql = (
                "SELECT l.loan_id, c.full_name, l.loan_type, l.principal_amount, l.tenor_months, l.monthly_installment, l.status\n"
                "FROM loans l\n"
                "JOIN customers c ON l.customer_id = c.customer_id\n"
                "WHERE l.status = 'ACTIVE'\n"
                "ORDER BY l.principal_amount DESC;"
            )
            explanation = [
                "Menampilkan portofolio fasilitas kredit/pinjaman aktif nasabah" if is_id else "Lists active credit and loan accounts across bank customers"
            ]
        else:
            generated_sql = (
                "SELECT c.cif_number, c.full_name, a.account_number, a.account_type, a.balance, b.branch_name\n"
                "FROM accounts a\n"
                "JOIN customers c ON a.customer_id = c.customer_id\n"
                "JOIN branches b ON a.branch_id = b.branch_id\n"
                "ORDER BY a.balance DESC;"
            )
            explanation = [
                "Menampilkan rekap saldo rekening nasabah diurutkan dari yang tertinggi" if is_id else "Ranks customer bank accounts by current balance in descending order"
            ]

    # Heuristic intent matching with schema awareness
    elif "customer" in p_lower or "pelanggan" in p_lower or "user" in p_lower or "pembeli" in p_lower:
        if "order" in table_names or "orders" in table_names:
            generated_sql = (
                "SELECT c.first_name, c.last_name, c.email, COUNT(o.id) AS total_orders, SUM(o.total_amount) AS total_spend\n"
                "FROM customers c\n"
                "LEFT JOIN orders o ON c.id = o.customer_id\n"
                "GROUP BY c.id\n"
                "ORDER BY total_spend DESC\n"
                "LIMIT 10;"
            )
            explanation = [
                "Menghitung total pesanan dan akumulasi transaksi tiap pelanggan" if is_id else "Aggregates total orders and lifetime transaction volume per customer",
                "Menggunakan LEFT JOIN agar pelanggan tanpa pesanan tetap terdata" if is_id else "Uses LEFT JOIN to ensure new customers without orders are not omitted"
            ]
        else:
            generated_sql = "SELECT id, first_name, last_name, email, city FROM customers LIMIT 20;"
            explanation = ["Menampilkan daftar pelanggan aktif" if is_id else "Lists active customers"]

    elif "product" in p_lower or "produk" in p_lower or "barang" in p_lower or "harga" in p_lower or "stock" in p_lower:
        if "stock" in p_lower or "habis" in p_lower or "sedikit" in p_lower or "low" in p_lower:
            generated_sql = "SELECT id, name, price, stock FROM products WHERE stock < 30 ORDER BY stock ASC;"
            explanation = ["Menampilkan produk dengan stok menipis (di bawah 30 unit)" if is_id else "Identifies inventory items with low stock level"]
        else:
            generated_sql = (
                "SELECT p.id, p.name, p.price, p.stock, c.name AS category\n"
                "FROM products p\n"
                "LEFT JOIN categories c ON p.category_id = c.id\n"
                "ORDER BY p.price DESC\n"
                "LIMIT 20;"
            )
            explanation = ["Menampilkan katalog produk beserta nama kategorinya" if is_id else "Fetches product catalog enriched with category names"]

    elif "order" in p_lower or "pesanan" in p_lower or "transaksi" in p_lower:
        generated_sql = (
            "SELECT o.id AS order_id, c.first_name || ' ' || c.last_name AS customer, o.total_amount, o.status, o.order_date\n"
            "FROM orders o\n"
            "JOIN customers c ON o.customer_id = c.id\n"
            "ORDER BY o.order_date DESC\n"
            "LIMIT 15;"
        )
        explanation = ["Menampilkan riwayat pesanan terbaru beserta detail pemesan" if is_id else "Queries recent orders with customer identity details"]

    elif "student" in p_lower or "siswa" in p_lower or "mahasiswa" in p_lower or "course" in p_lower or "kursus" in p_lower:
        generated_sql = (
            "SELECT s.name AS student_name, c.title AS course_title, e.grade, e.semester\n"
            "FROM enrollments e\n"
            "JOIN students s ON e.student_id = s.id\n"
            "JOIN courses c ON e.course_id = c.id\n"
            "ORDER BY s.name ASC;"
        )
        explanation = ["Menampilkan data mahasiswa beserta mata kuliah dan nilai yang diperoleh" if is_id else "Lists enrolled students with their associated course grades"]

    else:
        # Fallback to smart first-table query
        first_table = table_names[0] if table_names else "sqlite_master"
        generated_sql = f"SELECT * FROM {first_table} LIMIT 10;"
        explanation = [
            f"Query inspeksi dasar untuk tabel '{first_table}'" if is_id else f"Initial discovery query for table '{first_table}'"
        ]

    # Validate against dialect
    try:
        sqlglot.parse_one(generated_sql, read=engine)
        parser_valid = True
    except Exception:
        parser_valid = False

    return {
        "status": "success",
        "engine": engine,
        "query": generated_sql,
        "explanation": explanation,
        "warnings": [
            "AI-generated query for review. Always confirm before executing in production." if not is_id else "Query dihasilkan oleh asisten untuk ditinjau. Selalu verifikasi sebelum eksekusi."
        ],
        "validation": {
            "parser_valid": parser_valid,
            "database_validated": False,
        },
        "execution": {
            "executed": False
        }
    }
