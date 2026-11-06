import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ToolCategory(Base):
    __tablename__ = "tool_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(160))
    name_id: Mapped[str | None] = mapped_column(String(160), nullable=True)
    description_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    description_id: Mapped[str | None] = mapped_column(Text, nullable=True)


class ProfessionalTool(Base):
    __tablename__ = "professional_tools"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    slug: Mapped[str] = mapped_column(String(160), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    vendor: Mapped[str | None] = mapped_column(String(200), nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    category_slug: Mapped[str | None] = mapped_column(String(120), nullable=True)
    publication_status: Mapped[str] = mapped_column(String(50), default="published")
    verification_status: Mapped[str] = mapped_column(String(50), default="verified")
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    official_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    documentation_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_model: Mapped[str | None] = mapped_column(String(200), nullable=True)
    supported_platforms: Mapped[list] = mapped_column(JSONB, default=list)
    supported_engines: Mapped[list] = mapped_column(JSONB, default=list)
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    last_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
