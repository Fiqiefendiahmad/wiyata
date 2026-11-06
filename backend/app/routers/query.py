from fastapi import APIRouter
from pydantic import BaseModel, Field
import sqlglot

from app.schemas.query import (
    QueryConvertRequest,
    QueryGenerateRequest,
    QueryResult,
    QueryValidateRequest,
)

router = APIRouter(prefix="/query", tags=["Query"])


class QueryFormatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    dialect: str = "sqlite"


class QueryExplainRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=50000)
    dialect: str = "sqlite"


@router.post("/generate", response_model=QueryResult)
async def generate_query(body: QueryGenerateRequest) -> QueryResult:
    # Rule: Never execute AI generated SQL automatically. Display for explicit review.
    return QueryResult(
        status="not_implemented",
        engine=body.engine,
        warnings=["AI query generation provider is in manual/offline mode. Connect Ollama or an external LLM key in .env."],
    )


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
