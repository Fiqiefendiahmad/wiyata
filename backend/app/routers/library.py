import uuid
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models.query import SavedQuery
from app.models.user import Workspace

router = APIRouter(prefix="/library", tags=["Library"])

DEFAULT_WORKSPACE_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

STARTER_QUERIES = [
    {
        "title": "Customer Lifetime Value (LTV) Summary",
        "engine": "sqlite",
        "dialect": "sqlite",
        "description": "Calculates order frequencies, average transaction size, and cumulative spend per customer.",
        "query_text": """SELECT
    c.id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.city,
    COUNT(o.id) AS total_orders,
    ROUND(AVG(o.total_amount), 2) AS avg_order_value,
    SUM(o.total_amount) AS total_lifetime_spend
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id
ORDER BY total_lifetime_spend DESC;""",
    },
    {
        "title": "Top Selling Products by Revenue",
        "engine": "sqlite",
        "dialect": "sqlite",
        "description": "Ranks products by total sales revenue and volume across completed orders.",
        "query_text": """SELECT
    p.name AS product_name,
    c.name AS category_name,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS gross_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.id
JOIN categories c ON p.category_id = c.id
GROUP BY p.id
ORDER BY gross_revenue DESC;""",
    },
    {
        "title": "Inventory Restock Priority Monitor",
        "engine": "sqlite",
        "dialect": "sqlite",
        "description": "Finds critical catalog items running below minimum safety stock threshold.",
        "query_text": """SELECT
    p.id,
    p.name,
    p.stock,
    p.price,
    CASE
        WHEN p.stock <= 20 THEN 'CRITICAL'
        WHEN p.stock <= 35 THEN 'WARNING'
        ELSE 'OPTIMAL'
    END AS inventory_status
FROM products p
WHERE p.stock <= 35
ORDER BY p.stock ASC;""",
    },
]


class SavedQueryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    query_text: str = Field(..., min_length=1, max_length=50000)
    engine: str = "sqlite"
    dialect: str = "sqlite"
    description: str | None = None


class SavedQueryResponse(BaseModel):
    id: uuid.UUID
    title: str
    query_text: str
    engine: str | None
    dialect: str | None
    description: str | None
    created_at: Any

    model_config = {"from_attributes": True}


async def _ensure_default_workspace(db: AsyncSession) -> Workspace:
    ws = await db.get(Workspace, DEFAULT_WORKSPACE_ID)
    if not ws:
        ws = Workspace(id=DEFAULT_WORKSPACE_ID, name="Default Learning Workspace")
        db.add(ws)
        await db.commit()
    return ws


@router.get("/queries", response_model=list[SavedQueryResponse])
async def list_queries(db: AsyncSession = Depends(get_db)) -> list[SavedQueryResponse]:
    await _ensure_default_workspace(db)

    result = await db.execute(
        select(SavedQuery).order_by(SavedQuery.created_at.desc()).limit(100)
    )
    queries = list(result.scalars().all())

    # If empty, seed initial starter queries
    if not queries:
        for seed in STARTER_QUERIES:
            sq = SavedQuery(
                workspace_id=DEFAULT_WORKSPACE_ID,
                title=seed["title"],
                engine=seed["engine"],
                dialect=seed["dialect"],
                description=seed["description"],
                query_text=seed["query_text"],
            )
            db.add(sq)
        await db.commit()

        result = await db.execute(
            select(SavedQuery).order_by(SavedQuery.created_at.desc()).limit(100)
        )
        queries = list(result.scalars().all())

    return [SavedQueryResponse.model_validate(q) for q in queries]


@router.post("/queries", response_model=SavedQueryResponse, status_code=201)
async def create_query(
    body: SavedQueryCreate, db: AsyncSession = Depends(get_db)
) -> SavedQueryResponse:
    await _ensure_default_workspace(db)

    sq = SavedQuery(
        workspace_id=DEFAULT_WORKSPACE_ID,
        title=body.title,
        query_text=body.query_text,
        engine=body.engine,
        dialect=body.dialect,
        description=body.description,
    )
    db.add(sq)
    await db.commit()
    await db.refresh(sq)
    return SavedQueryResponse.model_validate(sq)


@router.delete("/queries/{query_id}", status_code=204)
async def delete_query(
    query_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    sq = await db.get(SavedQuery, query_id)
    if not sq:
        raise HTTPException(status_code=404, detail="Saved query not found")
    await db.delete(sq)
    await db.commit()
