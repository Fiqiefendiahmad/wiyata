import uuid
from datetime import datetime

from pydantic import BaseModel


class ToolSummary(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    vendor: str | None = None
    summary: str | None = None
    official_url: str | None = None
    documentation_url: str | None = None
    license_model: str | None = None
    supported_platforms: list = []
    supported_engines: list = []
    last_verified_at: datetime | None = None

    model_config = {"from_attributes": True}
