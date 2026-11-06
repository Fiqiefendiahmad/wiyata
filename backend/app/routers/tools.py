from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models.tools import ProfessionalTool, ToolCategory
from app.schemas.tools import (
    ToolCategoryResponse,
    ToolDetail,
    ToolFiltersResponse,
    ToolListResponse,
    ToolSummary,
)

router = APIRouter(prefix="/tools", tags=["Tools"])


def _extract_summary(tool: ProfessionalTool, cat_map: dict[str, Any]) -> ToolSummary:
    details = tool.details or {}
    cat_slug = tool.category_slug or details.get("category_slug")
    cat_info = cat_map.get(cat_slug, {}) if cat_slug else {}

    return ToolSummary(
        id=str(tool.id),
        slug=tool.slug,
        name=tool.name,
        vendor=tool.vendor,
        category_slug=cat_slug,
        category_name=cat_info.get("name_en") or details.get("category_name"),
        category_name_id=cat_info.get("name_id") or details.get("category_name_id"),
        product_type=details.get("product_type", "Standalone Utility"),
        summary=tool.summary or details.get("summary_en"),
        summary_id=details.get("summary_id") or tool.summary,
        official_url=tool.official_url,
        documentation_url=tool.documentation_url,
        license_model=tool.license_model,
        supported_platforms=tool.supported_platforms or [],
        supported_engines=tool.supported_engines or [],
        verification_status=tool.verification_status or "verified",
        publication_status=tool.publication_status or "published",
        lifecycle_status=details.get("lifecycle_status", "active"),
        last_verified_at=tool.last_verified_at,
    )


def _extract_detail(tool: ProfessionalTool, cat_map: dict[str, Any]) -> ToolDetail:
    summary = _extract_summary(tool, cat_map)
    details = tool.details or {}

    return ToolDetail(
        **summary.model_dump(),
        repository_url=details.get("repository_url"),
        download_url=details.get("download_url"),
        overview_en=details.get("overview_en"),
        overview_id=details.get("overview_id"),
        primary_use_cases_en=details.get("primary_use_cases_en", []),
        primary_use_cases_id=details.get("primary_use_cases_id", []),
        explicit_boundaries_en=details.get("explicit_boundaries_en", []),
        explicit_boundaries_id=details.get("explicit_boundaries_id", []),
        features=details.get("features", []),
        compatibility_matrix=details.get("compatibility_matrix", []),
        security_considerations=details.get("security_considerations"),
        getting_started=details.get("getting_started"),
        practical_scenarios=details.get("practical_scenarios", []),
        career_connections=details.get("career_connections", []),
        knowledge_connections=details.get("knowledge_connections", []),
        exercise_connections=details.get("exercise_connections", []),
        alternatives=details.get("alternatives", []),
        verified_sources=details.get("verified_sources", []),
        content_reviewed_at=details.get("content_reviewed_at"),
    )


@router.get("", response_model=ToolListResponse)
async def list_tools(
    search: str | None = Query(None, description="Search query by name, vendor, summary, or tags"),
    category: str | None = Query(None, description="Filter by category slug"),
    engine: str | None = Query(None, description="Filter by supported database engine"),
    platform: str | None = Query(None, description="Filter by supported operating system/platform"),
    license: str | None = Query(None, description="Filter by license model keyword"),
    status: str | None = Query(None, description="Filter by verification status"),
    sort: str = Query("name", description="Sort by: name, recent, verified"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> ToolListResponse:
    # 1. Load Categories Map
    cat_res = await db.execute(select(ToolCategory))
    categories = cat_res.scalars().all()
    cat_map = {
        c.slug: {
            "id": str(c.id),
            "name_en": c.name,
            "name_id": getattr(c, "name_id", None) or c.name,
            "description_en": getattr(c, "description_en", None),
            "description_id": getattr(c, "description_id", None),
        }
        for c in categories
    }

    # 2. Build Query
    query = select(ProfessionalTool).where(ProfessionalTool.publication_status == "published")

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.where(
            or_(
                func.lower(ProfessionalTool.name).like(term),
                func.lower(ProfessionalTool.vendor).like(term),
                func.lower(ProfessionalTool.summary).like(term),
                func.lower(ProfessionalTool.slug).like(term),
            )
        )

    if category and category != "all":
        query = query.where(ProfessionalTool.category_slug == category)

    if status and status != "all":
        query = query.where(ProfessionalTool.verification_status == status)

    if license and license != "all":
        query = query.where(func.lower(ProfessionalTool.license_model).like(f"%{license.lower()}%"))

    # Sorting
    if sort == "recent":
        query = query.order_by(ProfessionalTool.created_at.desc())
    elif sort == "verified":
        query = query.order_by(ProfessionalTool.last_verified_at.desc().nullslast())
    else:
        query = query.order_by(ProfessionalTool.name.asc())

    # Count Total
    count_query = select(func.count()).select_from(query.subquery())
    total_res = await db.execute(count_query)
    total = total_res.scalar_one()

    # Pagination
    offset = (page - 1) * limit
    paged_query = query.offset(offset).limit(limit)
    tools_res = await db.execute(paged_query)
    tools = tools_res.scalars().all()

    # Filter in-memory for JSONB arrays if engine or platform specified
    filtered_items = []
    for t in tools:
        if engine and engine != "all":
            supported = [e.lower() for e in (t.supported_engines or [])]
            if not any(engine.lower() in s for s in supported):
                continue
        if platform and platform != "all":
            platforms = [p.lower() for p in (t.supported_platforms or [])]
            if not any(platform.lower() in p for p in platforms):
                continue
        filtered_items.append(_extract_summary(t, cat_map))

    # Category summaries with counts
    category_responses = []
    for c in categories:
        cnt_res = await db.execute(
            select(func.count())
            .select_from(ProfessionalTool)
            .where(ProfessionalTool.category_slug == c.slug)
            .where(ProfessionalTool.publication_status == "published")
        )
        cnt = cnt_res.scalar_one()
        category_responses.append(
            ToolCategoryResponse(
                id=str(c.id),
                slug=c.slug,
                name_en=c.name,
                name_id=getattr(c, "name_id", None) or c.name,
                description_en=getattr(c, "description_en", None),
                description_id=getattr(c, "description_id", None),
                tool_count=cnt,
            )
        )

    return ToolListResponse(
        items=filtered_items,
        total=total if not (engine or platform) else len(filtered_items),
        page=page,
        limit=limit,
        categories=category_responses,
    )


@router.get("/categories", response_model=list[ToolCategoryResponse])
async def list_tool_categories(db: AsyncSession = Depends(get_db)) -> list[ToolCategoryResponse]:
    cat_res = await db.execute(select(ToolCategory).order_by(ToolCategory.name))
    categories = cat_res.scalars().all()

    output = []
    for c in categories:
        cnt_res = await db.execute(
            select(func.count())
            .select_from(ProfessionalTool)
            .where(ProfessionalTool.category_slug == c.slug)
            .where(ProfessionalTool.publication_status == "published")
        )
        output.append(
            ToolCategoryResponse(
                id=str(c.id),
                slug=c.slug,
                name_en=c.name,
                name_id=getattr(c, "name_id", None) or c.name,
                description_en=getattr(c, "description_en", None),
                description_id=getattr(c, "description_id", None),
                tool_count=cnt_res.scalar_one(),
            )
        )
    return output


@router.get("/filters", response_model=ToolFiltersResponse)
async def get_tool_filters(db: AsyncSession = Depends(get_db)) -> ToolFiltersResponse:
    cat_res = await db.execute(select(ToolCategory).order_by(ToolCategory.name))
    categories = cat_res.scalars().all()

    return ToolFiltersResponse(
        categories=[
            {
                "slug": c.slug,
                "name_en": c.name,
                "name_id": getattr(c, "name_id", None) or c.name,
            }
            for c in categories
        ],
        engines=[
            "PostgreSQL",
            "MySQL",
            "MariaDB",
            "Oracle",
            "SQL Server",
            "IBM Db2",
            "SQLite",
            "DuckDB",
            "Snowflake",
            "MongoDB",
        ],
        platforms=["Linux", "macOS", "Windows", "Docker", "Kubernetes"],
        licenses=["Open Source", "Free Proprietary", "Commercial", "Engine Built-in"],
        verification_statuses=["verified", "partially_verified", "deprecated"],
    )


@router.get("/{slug}", response_model=ToolDetail)
async def get_tool(slug: str, db: AsyncSession = Depends(get_db)) -> ToolDetail:
    cat_res = await db.execute(select(ToolCategory))
    categories = cat_res.scalars().all()
    cat_map = {
        c.slug: {
            "id": str(c.id),
            "name_en": c.name,
            "name_id": getattr(c, "name_id", None) or c.name,
            "description_en": getattr(c, "description_en", None),
            "description_id": getattr(c, "description_id", None),
        }
        for c in categories
    }

    result = await db.execute(select(ProfessionalTool).where(ProfessionalTool.slug == slug))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool with slug '{slug}' not found")

    return _extract_detail(tool, cat_map)


@router.get("/{slug}/related", response_model=list[ToolSummary])
async def get_related_tools(slug: str, db: AsyncSession = Depends(get_db)) -> list[ToolSummary]:
    cat_res = await db.execute(select(ToolCategory))
    categories = cat_res.scalars().all()
    cat_map = {
        c.slug: {
            "id": str(c.id),
            "name_en": c.name,
            "name_id": getattr(c, "name_id", None) or c.name,
        }
        for c in categories
    }

    result = await db.execute(select(ProfessionalTool).where(ProfessionalTool.slug == slug))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    # Related by category, excluding current tool
    related_res = await db.execute(
        select(ProfessionalTool)
        .where(ProfessionalTool.category_slug == tool.category_slug)
        .where(ProfessionalTool.slug != slug)
        .where(ProfessionalTool.publication_status == "published")
        .limit(6)
    )
    related = related_res.scalars().all()
    return [_extract_summary(r, cat_map) for r in related]
