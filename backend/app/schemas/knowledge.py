import uuid
from datetime import datetime

from pydantic import BaseModel


class ArticleSummary(BaseModel):
    id: uuid.UUID
    slug: str
    language: str
    title: str
    summary: str | None
    status: str
    engine: str | None
    category_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleDetail(ArticleSummary):
    body_markdown: str
    version_scope: list
    references_json: list
    last_reviewed_at: datetime | None
