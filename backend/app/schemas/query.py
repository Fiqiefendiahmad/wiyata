from pydantic import BaseModel, Field


class QueryGenerateRequest(BaseModel):
    engine: str
    engine_version: str | None = None
    schema_reference: str | None = None
    request: str = Field(..., min_length=1, max_length=2000)
    language: str = Field(default="en", pattern="^(en|id)$")
    include_explanation: bool = True
    include_warnings: bool = True


class QueryConvertRequest(BaseModel):
    source_dialect: str
    target_dialect: str
    query: str = Field(..., min_length=1, max_length=50000)


class QueryValidateRequest(BaseModel):
    engine: str
    query: str = Field(..., min_length=1, max_length=50000)


class QueryResult(BaseModel):
    status: str
    engine: str
    query: str | None = None
    explanation: list[str] = []
    warnings: list[str] = []
    validation: dict = {}
    execution: dict = {"executed": False}
