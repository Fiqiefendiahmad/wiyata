import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_tools_catalog_list_and_categories() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # 1. List tools
        res = await client.get("/api/v1/tools")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 20
        assert len(data["items"]) >= 20

        # Check category responses
        assert len(data["categories"]) >= 6

        # 2. Categories endpoint
        cat_res = await client.get("/api/v1/tools/categories")
        assert cat_res.status_code == 200
        cats = cat_res.json()
        assert len(cats) >= 6
        cat_slugs = [c["slug"] for c in cats]
        assert "clients" in cat_slugs
        assert "monitoring" in cat_slugs
        assert "migration" in cat_slugs
        assert "backup" in cat_slugs

        # 3. Filters endpoint
        filt_res = await client.get("/api/v1/tools/filters")
        assert filt_res.status_code == 200
        filters = filt_res.json()
        assert "PostgreSQL" in filters["engines"]
        assert "Linux" in filters["platforms"]


@pytest.mark.asyncio
async def test_tools_catalog_search_and_filtering() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Filter by category: monitoring
        mon_res = await client.get("/api/v1/tools?category=monitoring")
        assert mon_res.status_code == 200
        mon_tools = mon_res.json()["items"]
        assert all(t["category_slug"] == "monitoring" for t in mon_tools)
        mon_slugs = [t["slug"] for t in mon_tools]
        assert "prometheus" in mon_slugs
        assert "grafana" in mon_slugs

        # Search by term
        search_res = await client.get("/api/v1/tools?search=dbeaver")
        assert search_res.status_code == 200
        search_items = search_res.json()["items"]
        assert len(search_items) >= 1
        assert search_items[0]["slug"] == "dbeaver"

        # Engine filter
        pg_res = await client.get("/api/v1/tools?engine=PostgreSQL")
        assert pg_res.status_code == 200
        pg_items = pg_res.json()["items"]
        assert len(pg_items) >= 5


@pytest.mark.asyncio
async def test_tool_detail_comprehensive_sections() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.get("/api/v1/tools/dbeaver")
        assert res.status_code == 200
        tool = res.json()

        # Section A: Identity & Quick Facts
        assert tool["slug"] == "dbeaver"
        assert tool["name"] == "DBeaver Community"
        assert tool["verification_status"] == "verified"
        assert tool["license_model"] == "Open Source (Apache 2.0)"
        assert tool["official_url"] == "https://dbeaver.io/"
        assert tool["documentation_url"] == "https://dbeaver.com/docs/dbeaver/"

        # Section B: What it does
        assert tool["overview_en"] is not None
        assert tool["overview_id"] is not None
        assert len(tool["primary_use_cases_en"]) >= 2
        assert len(tool["explicit_boundaries_en"]) >= 1

        # Section C: Features & Constraints
        assert len(tool["features"]) >= 2
        assert len(tool["compatibility_matrix"]) >= 3
        assert tool["security_considerations"] is not None
        assert "credential_storage" in tool["security_considerations"]

        # Section D: Getting started
        assert tool["getting_started"] is not None
        assert len(tool["getting_started"]["steps"]) >= 2
        assert tool["getting_started"]["safe_first_test_en"] is not None

        # Section E: Practical professional scenarios
        assert len(tool["practical_scenarios"]) >= 2
        scen1 = tool["practical_scenarios"][0]
        assert "goal_en" in scen1
        assert "steps_en" in scen1
        assert "validation_en" in scen1
        assert "expected_result_en" in scen1

        # Section F: Learning connections
        assert len(tool["career_connections"]) >= 1
        assert tool["career_connections"][0]["role_id"] in ["sql-developer", "database-administrator"]

        # Section G: Alternatives
        assert len(tool["alternatives"]) >= 1

        # Section H: Verified sources
        assert len(tool["verified_sources"]) >= 1
        assert tool["verified_sources"][0]["status"] == "verified"

        # Related tools
        rel_res = await client.get("/api/v1/tools/dbeaver/related")
        assert rel_res.status_code == 200
        rel_tools = rel_res.json()
        assert len(rel_tools) >= 1
        assert all(r["slug"] != "dbeaver" for r in rel_tools)
