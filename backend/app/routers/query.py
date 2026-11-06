from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field
import sqlglot

from app.schemas.query import (
    QueryConvertRequest,
    QueryGenerateRequest,
    QueryResult,
    QueryValidateRequest,
)
from app.services.query_ai import (
    explain_query_natural,
    generate_sql_from_prompt,
    optimize_query,
)

router = APIRouter(prefix="/query", tags=["Query"])


class QueryFormatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    dialect: str = "sqlite"


class QueryOptimizeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    dialect: str = "sqlite"


class QueryExplainNaturalRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    language: str = "en"


class SchemaContext(BaseModel):
    tables: list[dict[str, Any]] = []


class QueryGenerateWithSchemaRequest(BaseModel):
    request: str = Field(..., min_length=1, max_length=2000)
    engine: str = "sqlite"
    language: str = "en"
    schema_context: list[dict[str, Any]] = []


@router.post("/generate", response_model=QueryResult)
async def generate_query(body: QueryGenerateWithSchemaRequest) -> QueryResult:
    result = await generate_sql_from_prompt(
        prompt=body.request,
        schema=body.schema_context,
        engine=body.engine,
        language=body.language,
    )
    return QueryResult(**result)


@router.post("/optimize")
async def check_query_optimizations(body: QueryOptimizeRequest) -> dict:
    suggestions = optimize_query(body.query, dialect=body.dialect)
    return {
        "status": "success",
        "suggestions_count": len(suggestions),
        "suggestions": suggestions,
    }


@router.post("/explain-natural")
async def explain_query_in_plain_language(body: QueryExplainNaturalRequest) -> dict:
    steps = explain_query_natural(body.query, language=body.language)
    return {
        "status": "success",
        "steps": steps,
    }


@router.post("/convert")
async def convert_query(body: QueryConvertRequest) -> dict:
    try:
        result = sqlglot.transpile(
            body.query,
            read=body.source_dialect,
            write=body.target_dialect,
            pretty=True,
        )
        return {
            "status": "success",
            "source_dialect": body.source_dialect,
            "target_dialect": body.target_dialect,
            "query": result[0] if result else "",
            "warnings": [
                "Verify semantic equivalence before running in production. Some dialect features may differ."
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.post("/validate")
async def validate_query(body: QueryValidateRequest) -> dict:
    try:
        sqlglot.parse(
            body.query,
            read=body.engine,
            error_level=sqlglot.ErrorLevel.RAISE,
        )
        return {"valid": True, "engine": body.engine, "parser": "sqlglot"}
    except sqlglot.errors.ParseError as exc:
        return {"valid": False, "engine": body.engine, "error": str(exc)}


@router.post("/format")
async def format_query(body: QueryFormatRequest) -> dict:
    try:
        formatted = sqlglot.transpile(
            body.query,
            read=body.dialect,
            write=body.dialect,
            pretty=True,
        )
        return {
            "status": "success",
            "query": formatted[0] if formatted else body.query,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
