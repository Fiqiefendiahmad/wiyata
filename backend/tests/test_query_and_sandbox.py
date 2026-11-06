import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_format_query() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/api/v1/query/format",
            json={"query": "select id, name from users where active=1", "dialect": "sqlite"},
        )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "SELECT" in data["query"]


@pytest.mark.asyncio
async def test_convert_query_dialects() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/api/v1/query/convert",
            json={
                "source_dialect": "postgres",
                "target_dialect": "mysql",
                "query": "SELECT * FROM orders LIMIT 10;",
            },
        )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert "LIMIT 10" in data["query"]


@pytest.mark.asyncio
async def test_validate_valid_and_invalid_query() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        valid_res = await client.post(
            "/api/v1/query/validate",
            json={"engine": "sqlite", "query": "SELECT 1;"},
        )
        invalid_res = await client.post(
            "/api/v1/query/validate",
            json={"engine": "sqlite", "query": "SELEC * FROM;"},
        )
    assert valid_res.json()["valid"] is True
    assert invalid_res.json()["valid"] is False


@pytest.mark.asyncio
async def test_list_templates() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/api/v1/sandboxes/templates")
    assert res.status_code == 200
    templates = res.json()
    slugs = [t["slug"] for t in templates]
    assert "banking" in slugs
    assert "ecommerce" in slugs
    assert "school" in slugs


@pytest.mark.asyncio
async def test_list_tools_and_knowledge() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        tools_res = await client.get("/api/v1/tools")
        assert tools_res.status_code == 200

        articles_res = await client.get("/api/v1/knowledge/articles?language=id")
        assert articles_res.status_code == 200
        assert len(articles_res.json()) >= 1


@pytest.mark.asyncio
async def test_multi_engine_sandboxes() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. SQLite sandbox
        sb_lite = await client.post("/api/v1/sandboxes", json={"engine": "sqlite", "template_slug": "banking"})
        assert sb_lite.status_code == 201
        lite_id = sb_lite.json()["id"]

        exec_lite = await client.post(
            f"/api/v1/sandboxes/{lite_id}/execute",
            json={"query": "SELECT COUNT(*) AS total FROM accounts;", "read_only": True},
        )
        assert exec_lite.status_code == 200
        assert exec_lite.json()["success"] is True
        assert exec_lite.json()["rows"][0][0] == 6

        # 2. PostgreSQL sandbox
        sb_pg = await client.post("/api/v1/sandboxes", json={"engine": "postgres", "template_slug": "banking"})
        assert sb_pg.status_code == 201
        pg_id = sb_pg.json()["id"]

        exec_pg = await client.post(
            f"/api/v1/sandboxes/{pg_id}/execute",
            json={"query": "SELECT COUNT(*) AS total FROM accounts;", "read_only": True},
        )
        assert exec_pg.status_code == 200
        assert exec_pg.json()["success"] is True
        assert exec_pg.json()["rows"][0][0] == 6

        # 3. MySQL sandbox
        sb_my = await client.post("/api/v1/sandboxes", json={"engine": "mysql", "template_slug": "banking"})
        assert sb_my.status_code == 201
        my_id = sb_my.json()["id"]

        exec_my = await client.post(
            f"/api/v1/sandboxes/{my_id}/execute",
            json={"query": "SELECT COUNT(*) AS total FROM accounts;", "read_only": True},
        )
        assert exec_my.status_code == 200
        assert exec_my.json()["success"] is True
        assert exec_my.json()["rows"][0][0] == 6

        # 4. Oracle sandbox (Transpiled / Emulated)
        sb_ora = await client.post("/api/v1/sandboxes", json={"engine": "oracle", "template_slug": "banking"})
        assert sb_ora.status_code == 201
        ora_id = sb_ora.json()["id"]

        exec_ora = await client.post(
            f"/api/v1/sandboxes/{ora_id}/execute",
            json={"query": "SELECT COUNT(*) FROM accounts WHERE ROWNUM <= 5;", "read_only": True},
        )
        assert exec_ora.status_code == 200
        assert exec_ora.json()["success"] is True
        assert exec_ora.json()["rows"][0][0] == 6

        schema_ora = await client.get(f"/api/v1/sandboxes/{ora_id}/schema")
        assert schema_ora.status_code == 200
        assert any(t["name"] == "ACCOUNTS" for t in schema_ora.json())

        # 5. MSSQL sandbox (T-SQL Transpiled / Emulated)
        sb_ms = await client.post("/api/v1/sandboxes", json={"engine": "mssql", "template_slug": "banking"})
        assert sb_ms.status_code == 201
        ms_id = sb_ms.json()["id"]

        exec_ms = await client.post(
            f"/api/v1/sandboxes/{ms_id}/execute",
            json={"query": "SELECT TOP 5 COUNT(*) AS total FROM [accounts];", "read_only": True},
        )
        assert exec_ms.status_code == 200
        assert exec_ms.json()["success"] is True
        assert exec_ms.json()["rows"][0][0] == 6

        schema_ms = await client.get(f"/api/v1/sandboxes/{ms_id}/schema")
        assert schema_ms.status_code == 200
        assert any(t["name"] == "accounts" for t in schema_ms.json())

        # Clean up
        await client.delete(f"/api/v1/sandboxes/{lite_id}")
        await client.delete(f"/api/v1/sandboxes/{pg_id}")
        await client.delete(f"/api/v1/sandboxes/{my_id}")
        await client.delete(f"/api/v1/sandboxes/{ora_id}")
        await client.delete(f"/api/v1/sandboxes/{ms_id}")

