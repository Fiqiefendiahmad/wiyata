from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory
from app.schemas.knowledge import ArticleDetail, ArticleSummary

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
