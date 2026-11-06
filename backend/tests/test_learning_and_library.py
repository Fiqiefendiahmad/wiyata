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

        # Test PostgreSQL submission
        sub_pg = await client.post(
            "/api/v1/learning/exercises/low-stock-alert/submit",
            json={
                "query": "SELECT name, price, stock FROM products WHERE stock < 35 ORDER BY stock ASC;",
                "engine": "postgres",
                "language": "en",
            },
        )
        assert sub_pg.status_code == 200
        assert sub_pg.json()["passed"] is True

        # Test MySQL submission
        sub_my = await client.post(
            "/api/v1/learning/exercises/low-stock-alert/submit",
            json={
                "query": "SELECT name, price, stock FROM products WHERE stock < 35 ORDER BY stock ASC;",
                "engine": "mysql",
                "language": "en",
            },
        )
        assert sub_my.status_code == 200
        assert sub_my.json()["passed"] is True


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


@pytest.mark.asyncio
async def test_knowledge_v2_endpoints() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. Glossary
        glossary_res = await client.get("/api/v1/knowledge/glossary?search=wal")
        assert glossary_res.status_code == 200
        terms = glossary_res.json()
        assert len(terms) >= 1
        assert terms[0]["acronym"] == "WAL"

        # 2. Comparisons
        comp_res = await client.get("/api/v1/knowledge/comparisons")
        assert comp_res.status_code == 200
        comps = comp_res.json()
        assert len(comps) >= 2
        assert "postgres" in comps[0]["engines"]
        assert "oracle" in comps[0]["engines"]

        # 3. Incidents
        inc_res = await client.get("/api/v1/knowledge/incidents")
        assert inc_res.status_code == 200
        incs = inc_res.json()
        assert len(incs) >= 2
        assert any(i["slug"] == "high-cpu-runaway-queries" for i in incs)

        # 4. Visual Lessons
        vis_res = await client.get("/api/v1/knowledge/visual-lessons")
        assert vis_res.status_code == 200
        vis = vis_res.json()
        assert len(vis) >= 2
        slug = vis[0]["slug"]

        vis_detail = await client.get(f"/api/v1/knowledge/visual-lessons/{slug}")
        assert vis_detail.status_code == 200
        assert len(vis_detail.json()["steps"]) >= 3
