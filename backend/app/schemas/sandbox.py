import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SandboxCreate(BaseModel):
    engine: str = Field(default="sqlite", pattern="^(sqlite|postgres|mysql|oracle)$")
    engine_version: str | None = None
    template_slug: str | None = "ecommerce"


class SandboxExecuteRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    confirmed: bool = Field(
        default=False, description="Explicit user confirmation required for DDL/DML"
    )
    read_only: bool = Field(default=True)


class SandboxExecuteResult(BaseModel):
    success: bool
    columns: list[str] = []
    rows: list[list[Any]] = []
    row_count: int = 0
    elapsed_ms: float = 0.0
    truncated: bool = False
    error: str | None = None


class SandboxResponse(BaseModel):
    id: uuid.UUID
    engine: str
    engine_version: str | None = None
    template_slug: str | None = None
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = {"from_attributes": True}


class TemplateInfo(BaseModel):
    slug: str
    name: str
    description: str
