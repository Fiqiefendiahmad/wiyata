import sqlite3
from typing import Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.adapters.sqlite import SQLiteAdapter
from app.templates.datasets import TEMPLATES

router = APIRouter(prefix="/learning", tags=["Learning"])

CHALLENGES = [
    {
        "slug": "top-spending-customers",
        "title": "Top Spending Customers",
        "title_id": "5 Pelanggan dengan Pengeluaran Terbesar",
        "level": "Intermediate",
        "dataset": "ecommerce",
        "description": "Write a query that returns the first_name, city, and sum of total_amount (as total_spent) for customers with completed orders, sorted by total_spent descending, limited to 5 rows.",
        "description_id": "Tulis query yang menghasilkan first_name, city, dan total pengeluaran (total_spent) untuk pelanggan dengan pesanan 'completed', diurutkan dari yang terbanyak, dibatasi 5 baris.",
        "expected_columns": ["first_name", "city", "total_spent"],
        "solution_sql": """
SELECT c.first_name, c.city, SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id
ORDER BY total_spent DESC
LIMIT 5;
""",
        "starter_sql": """-- Tulis query Anda di bawah:
SELECT c.first_name, c.city, SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.id = o.customer_id
-- Lengkapi WHERE, GROUP BY, ORDER BY, dan LIMIT:
GROUP BY c.id;
""",
    },
    {
        "slug": "low-stock-alert",
        "title": "Restock Warning Alert",
        "title_id": "Peringatan Stok Barang Menipis",
        "level": "Beginner",
        "dataset": "ecommerce",
        "description": "Select the product name, price, and stock for all products where stock is strictly less than 35 units, ordered by stock ascending.",
        "description_id": "Pilih kolom name, price, dan stock untuk semua produk dengan stok di bawah 35 unit, diurutkan dari stok paling sedikit.",
        "expected_columns": ["name", "price", "stock"],
        "solution_sql": """
SELECT name, price, stock
FROM products
WHERE stock < 35
ORDER BY stock ASC;
""",
        "starter_sql": """SELECT name, price, stock
FROM products
WHERE stock < 35
ORDER BY stock ASC;
""",
    },
    {
        "slug": "academic-grade-a",
        "title": "Honors List: Grade A Students",
        "title_id": "Daftar Mahasiswa Berprestasi (Nilai A)",
        "level": "Beginner",
        "dataset": "school",
        "description": "Find student name (as student_name), course title (as course_title), and grade for all enrollments with grade 'A'. Sort alphabetically by student_name.",
        "description_id": "Temukan nama mahasiswa (student_name), judul mata kuliah (course_title), dan nilai untuk semua pendaftaran dengan nilai 'A'. Urutkan alfabetis berdasarkan student_name.",
        "expected_columns": ["student_name", "course_title", "grade"],
        "solution_sql": """
SELECT s.name AS student_name, c.title AS course_title, e.grade
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
WHERE e.grade = 'A'
ORDER BY s.name ASC;
""",
        "starter_sql": """SELECT s.name AS student_name, c.title AS course_title, e.grade
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
WHERE e.grade = 'A'
ORDER BY s.name ASC;
""",
    },
]


class ChallengeSubmitRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    language: str = "id"


class ChallengeSubmitResponse(BaseModel):
    passed: bool
    message: str
    row_count: int
    expected_row_count: int
    user_columns: list[str]
    expected_columns: list[str]
    elapsed_ms: float
    feedback: list[str]


@router.get("/exercises")
async def list_exercises() -> list[dict]:
    return [
        {
            "slug": c["slug"],
            "title": c["title"],
            "title_id": c["title_id"],
            "level": c["level"],
            "dataset": c["dataset"],
            "description": c["description"],
            "description_id": c["description_id"],
            "expected_columns": c["expected_columns"],
            "starter_sql": c["starter_sql"],
        }
        for c in CHALLENGES
    ]


@router.post("/exercises/{slug}/submit", response_model=ChallengeSubmitResponse)
async def submit_exercise(
    slug: str, body: ChallengeSubmitRequest
) -> ChallengeSubmitResponse:
    challenge = next((c for c in CHALLENGES if c["slug"] == slug), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Exercise challenge not found")

    is_id = body.language == "id"

    # Spin in-memory SQLite with the required template dataset
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    dataset_slug = challenge["dataset"]
    seed_sql = TEMPLATES.get(dataset_slug, TEMPLATES["ecommerce"])["sql"]
    conn.executescript(seed_sql)

    # 1. Run reference solution to get ground truth
    cur_ref = conn.execute(challenge["solution_sql"])
    ref_columns = [d[0] for d in cur_ref.description]
    ref_rows = [list(r) for r in cur_ref.fetchall()]

    # 2. Run user query
    adapter = SQLiteAdapter()
    adapter._conn = conn

    result = adapter.execute(body.query, max_rows=100, read_only=True)
    conn.close()

    if not result.get("success"):
        return ChallengeSubmitResponse(
            passed=False,
            message=f"SQL Error: {result.get('error')}",
            row_count=0,
            expected_row_count=len(ref_rows),
            user_columns=[],
            expected_columns=challenge["expected_columns"],
            elapsed_ms=result.get("elapsed_ms", 0),
            feedback=[
                "Periksa kembali sintaks SQL dan nama kolom yang Anda gunakan."
                if is_id
                else "Check your SQL syntax and projected column names."
            ],
        )

    user_cols = [c.lower() for c in result.get("columns", [])]
    expected_cols = [c.lower() for c in challenge["expected_columns"]]
    user_rows = result.get("rows", [])

    feedback: list[str] = []

    # Column comparison
    col_match = user_cols == expected_cols
    if not col_match:
        feedback.append(
            f"Kolom tidak cocok. Diharapkan: {expected_cols}, Diterima: {user_cols}"
            if is_id
            else f"Columns mismatch. Expected: {expected_cols}, Got: {user_cols}"
        )

    # Row count comparison
    count_match = len(user_rows) == len(ref_rows)
    if not count_match:
        feedback.append(
            f"Jumlah baris berbeda. Diharapkan: {len(ref_rows)} baris, Diterima: {len(user_rows)} baris."
            if is_id
            else f"Row count mismatch. Expected: {len(ref_rows)} rows, Got: {len(user_rows)} rows."
        )

    # Content comparison (loosely sorted or first element comparison)
    passed = col_match and count_match
    if passed and user_rows:
        # Check first row values match
        first_user = [str(x).strip() for x in user_rows[0]]
        first_ref = [str(x).strip() for x in ref_rows[0]]
        if first_user != first_ref:
            passed = False
            feedback.append(
                "Urutan data atau nilai baris pertama tidak sesuai dengan ekspektasi ORDER BY."
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
        else "Query results do not match expected output."
    )

    return ChallengeSubmitResponse(
        passed=passed,
        message=msg,
        row_count=len(user_rows),
        expected_row_count=len(ref_rows),
        user_columns=result.get("columns", []),
        expected_columns=challenge["expected_columns"],
        elapsed_ms=result.get("elapsed_ms", 0),
        feedback=feedback,
    )
