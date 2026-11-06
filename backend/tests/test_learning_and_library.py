import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_list_and_submit_learning_exercise() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # List exercises
        res = await client.get("/api/v1/learning/exercises")
        assert res.status_code == 200
        exercises = res.json()
        assert len(exercises) >= 3

        # Submit correct query for top-spending-customers
        correct_sql = """
        SELECT c.first_name, c.city, SUM(o.total_amount) AS total_spent
        FROM customers c
        JOIN orders o ON c.id = o.customer_id
        WHERE o.status = 'completed'
        GROUP BY c.id
        ORDER BY total_spent DESC
        LIMIT 5;
        """
        sub_res = await client.post(
            "/api/v1/learning/exercises/top-spending-customers/submit",
            json={"query": correct_sql, "language": "en"},
        )
        assert sub_res.status_code == 200
        data = sub_res.json()
        assert data["passed"] is True
        assert data["row_count"] == 4  # 4 distinct customers with completed orders


@pytest.mark.asyncio
async def test_query_optimizer_rules() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/api/v1/query/optimize",
            json={"query": "SELECT * FROM orders;", "dialect": "sqlite"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["suggestions_count"] >= 1
        rule_ids = [s.get("rule") for s in data["suggestions"]]
        assert "RULE-SQL-01" in rule_ids  # SELECT * rule


@pytest.mark.asyncio
async def test_query_generator_schema_aware() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/api/v1/query/generate",
            json={
                "request": "tampilkan pelanggan dengan pembelian terbanyak",
                "engine": "sqlite",
                "language": "id",
                "schema_context": [
                    {"name": "customers", "columns": [{"name": "id"}, {"name": "first_name"}]},
                    {"name": "orders", "columns": [{"name": "id"}, {"name": "customer_id"}, {"name": "total_amount"}]},
                ],
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "success"
        assert "SELECT" in data["query"]
        assert "customers" in data["query"]
