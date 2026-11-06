from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory
from app.schemas.knowledge import ArticleDetail, ArticleSummary
from app.templates.knowledge_v2 import (
    GLOSSARY_TERMS,
    CROSS_COMPARISONS,
    INCIDENT_RUNBOOKS,
    VISUAL_LESSONS,
)

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("/categories")
async def list_categories(db: AsyncSession = Depends(get_db)) -> list[dict]:
    result = await db.execute(select(KnowledgeCategory).order_by(KnowledgeCategory.sort_order))
    cats = result.scalars().all()
    return [{"id": str(c.id), "slug": c.slug} for c in cats]


@router.get("/articles", response_model=list[ArticleSummary])
async def list_articles(
    language: str = Query(default="en", pattern="^(en|id)$"),
    db: AsyncSession = Depends(get_db),
) -> list[ArticleSummary]:
    result = await db.execute(
        select(KnowledgeArticle)
        .where(KnowledgeArticle.language == language, KnowledgeArticle.status == "published")
        .order_by(KnowledgeArticle.updated_at.desc())
        .limit(50)
    )
    return [ArticleSummary.model_validate(a) for a in result.scalars().all()]


@router.get("/articles/{slug}", response_model=ArticleDetail)
async def get_article(
    slug: str,
    language: str = Query(default="en", pattern="^(en|id)$"),
    db: AsyncSession = Depends(get_db),
) -> ArticleDetail:
    from fastapi import HTTPException

    result = await db.execute(
        select(KnowledgeArticle).where(
            KnowledgeArticle.slug == slug,
            KnowledgeArticle.language == language,
        )
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return ArticleDetail.model_validate(article)


@router.get("/glossary")
async def list_glossary_terms(
    category: str | None = None,
    engine: str | None = None,
    search: str | None = None,
) -> list[dict]:
    terms = list(GLOSSARY_TERMS)
    if category and category != "ALL":
        terms = [t for t in terms if t["category"].lower() == category.lower()]
    if engine and engine != "ALL":
        terms = [t for t in terms if engine.lower() in [e.lower() for e in t.get("engines", [])]]
    if search and search.strip():
        q = search.strip().lower()
        terms = [
            t for t in terms
            if q in t["term"].lower()
            or q in t["acronym"].lower()
            or any(q in a.lower() for a in t.get("aliases", []))
            or q in t.get("field_slang", "").lower()
            or q in t["definition_en"].lower()
            or q in t["definition_id"].lower()
        ]
    return terms


@router.get("/comparisons")
async def list_cross_comparisons() -> list[dict]:
    return CROSS_COMPARISONS


@router.get("/incidents")
async def list_incident_runbooks() -> list[dict]:
    return INCIDENT_RUNBOOKS


@router.get("/visual-lessons")
async def list_visual_lessons() -> list[dict]:
    return VISUAL_LESSONS


@router.get("/visual-lessons/{slug}")
async def get_visual_lesson(slug: str) -> dict:
    from fastapi import HTTPException
    lesson = next((l for l in VISUAL_LESSONS if l["slug"] == slug), None)
    if not lesson:
        raise HTTPException(status_code=404, detail="Visual lesson not found")
    return lesson
