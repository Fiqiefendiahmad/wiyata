import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SandboxCreate(BaseModel):
    engine: str = Field(default="sqlite", pattern="^(sqlite|postgres|mysql)$")
    engine_version: str | None = None
    template_slug: str | None = None


class SandboxExecuteRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    confirmed: bool = Field(
        default=False, description="Explicit user confirmation required for execution"
    )


class SandboxResponse(BaseModel):
    id: uuid.UUID
    engine: str
    engine_version: str | None
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}
