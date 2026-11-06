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
