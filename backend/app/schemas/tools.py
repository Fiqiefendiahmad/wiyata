import uuid
from datetime import datetime

from pydantic import BaseModel


class ToolSummary(BaseModel):
    id: uuid.UUID
    slug: str
    name: str
    vendor: str | None
    summary: str | None
    license_model: str | None
    supported_engines: list
    last_verified_at: datetime | None

    model_config = {"from_attributes": True}
