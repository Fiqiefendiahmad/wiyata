import re
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
    language: str = "en"


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
    suggestions = optimize_query(body.query, dialect=body.dialect, language=body.language)
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
        source_is_db2 = body.source_dialect.lower() == "db2"
        target_is_db2 = body.target_dialect.lower() == "db2"

        src = "postgres" if source_is_db2 else body.source_dialect
        tgt = "postgres" if target_is_db2 else body.target_dialect

        query_in = body.query
        if source_is_db2:
            query_in = re.sub(r"\bFETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY\b", r"LIMIT \1", query_in, flags=re.IGNORECASE)
            query_in = re.sub(r"\s+WITH\s+(UR|CS|RS|RR)\s*;?\s*$", ";", query_in, flags=re.IGNORECASE).rstrip(";")
            query_in = re.sub(r"\bSYSIBM\.SYSDUMMY1\b", "sysdummy1", query_in, flags=re.IGNORECASE)

        result = sqlglot.transpile(
            query_in,
            read=src,
            write=tgt,
            pretty=True,
        )
        converted_sql = result[0] if result else ""

        if target_is_db2:
            converted_sql = re.sub(r"\bLIMIT\s+(\d+)\b", r"FETCH FIRST \1 ROWS ONLY", converted_sql, flags=re.IGNORECASE)
            converted_sql = re.sub(r"\bsysdummy1\b", "SYSIBM.SYSDUMMY1", converted_sql, flags=re.IGNORECASE)

        return {
            "status": "success",
            "source_dialect": body.source_dialect,
            "target_dialect": body.target_dialect,
            "query": converted_sql,
            "warnings": [
                "Verify semantic equivalence before running in production. Some dialect features may differ."
            ],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.post("/validate")
async def validate_query(body: QueryValidateRequest) -> dict:
    try:
        engine_is_db2 = body.engine.lower() == "db2"
        read_engine = "postgres" if engine_is_db2 else body.engine
        query_in = body.query
        if engine_is_db2:
            query_in = re.sub(r"\bFETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY\b", r"LIMIT \1", query_in, flags=re.IGNORECASE)
            query_in = re.sub(r"\s+WITH\s+(UR|CS|RS|RR)\s*;?\s*$", ";", query_in, flags=re.IGNORECASE).rstrip(";")
            query_in = re.sub(r"\bSYSIBM\.SYSDUMMY1\b", "sysdummy1", query_in, flags=re.IGNORECASE)

        sqlglot.parse(
            query_in,
            read=read_engine,
            error_level=sqlglot.ErrorLevel.RAISE,
        )
        return {"valid": True, "engine": body.engine, "parser": "sqlglot"}
    except sqlglot.errors.ParseError as exc:
        return {"valid": False, "engine": body.engine, "error": str(exc)}


@router.post("/format")
async def format_query(body: QueryFormatRequest) -> dict:
    try:
        dialect_is_db2 = body.dialect.lower() == "db2"
        read_dialect = "postgres" if dialect_is_db2 else body.dialect
        query_in = body.query
        if dialect_is_db2:
            query_in = re.sub(r"\bFETCH\s+FIRST\s+(\d+)\s+ROWS?\s+ONLY\b", r"LIMIT \1", query_in, flags=re.IGNORECASE)
            query_in = re.sub(r"\s+WITH\s+(UR|CS|RS|RR)\s*;?\s*$", ";", query_in, flags=re.IGNORECASE).rstrip(";")

        formatted = sqlglot.transpile(
            query_in,
            read=read_dialect,
            write=read_dialect,
            pretty=True,
        )
        out_sql = formatted[0] if formatted else body.query
        if dialect_is_db2:
            out_sql = re.sub(r"\bLIMIT\s+(\d+)\b", r"FETCH FIRST \1 ROWS ONLY", out_sql, flags=re.IGNORECASE)

        return {
            "status": "success",
            "query": out_sql,
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
