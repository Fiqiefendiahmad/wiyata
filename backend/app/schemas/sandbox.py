import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SandboxCreate(BaseModel):
    engine: str = Field(default="postgres", pattern="^(postgres|mysql|oracle|mssql|db2|sqlite)$")
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


class ColumnMetadata(BaseModel):
    name: str
    data_type: str
    length: int | None = None
    precision: int | None = None
    scale: int | None = None
    nullable: bool = True
    primary_key: bool = False
    foreign_key: bool = False
    foreign_key_target: str | None = None  # e.g. "customers.customer_id"
    unique: bool = False
    default_value: str | None = None
    auto_increment: bool = False
    comment: str | None = None


class IndexMetadata(BaseModel):
    name: str
    table_name: str
    columns: list[str] = []
    is_unique: bool = False
    is_primary: bool = False
    index_type: str = "B-TREE"
    predicate: str | None = None


class ConstraintMetadata(BaseModel):
    name: str
    table_name: str
    type: str  # "PRIMARY KEY", "FOREIGN KEY", "UNIQUE", "CHECK", "NOT NULL"
    columns: list[str] = []
    definition: str | None = None
    referenced_table: str | None = None
    referenced_columns: list[str] | None = None


class RelationshipMetadata(BaseModel):
    id: str
    from_table: str
    from_column: str
    to_table: str
    to_column: str
    source: str = "declared"  # "declared" | "inferred"
    constraint_name: str | None = None
    cardinality: str = "N:1"  # "1:1", "1:N", "N:1"


class TableMetadata(BaseModel):
    name: str
    type: str = "table"  # "table" | "view"
    schema_name: str = "public"
    columns: list[ColumnMetadata] = []
    indexes: list[IndexMetadata] = []
    constraints: list[ConstraintMetadata] = []
    row_count: int = 0
    row_count_estimated: bool = False


class SchemaMetadata(BaseModel):
    name: str
    tables: list[str] = []
    views: list[str] = []
    functions: list[str] = []
    sequences: list[str] = []


class DatabaseOverview(BaseModel):
    database_name: str
    engine: str
    engine_version: str
    schema_count: int = 1
    table_count: int = 0
    view_count: int = 0
    index_count: int = 0
    relationship_count: int = 0
    total_row_count: int = 0
    row_count_is_estimated: bool = False


class FullDatabaseMetadata(BaseModel):
    overview: DatabaseOverview
    schemas: list[SchemaMetadata] = []
    tables: list[TableMetadata] = []
    relationships: list[RelationshipMetadata] = []
    indexes: list[IndexMetadata] = []
    constraints: list[ConstraintMetadata] = []
    refreshed_at: str


class TableDataPreviewResponse(BaseModel):
    table_name: str
    schema_name: str = "public"
    page: int = 1
    page_size: int = 20
    total_rows: int = 0
    columns: list[str] = []
    column_types: dict[str, str] = {}
    rows: list[dict[str, Any]] = []
    sort_by: str | None = None
    sort_direction: str = "ASC"

