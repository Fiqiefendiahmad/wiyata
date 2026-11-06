from fastapi import APIRouter

from app.schemas.query import (
    QueryConvertRequest,
    QueryGenerateRequest,
    QueryResult,
    QueryValidateRequest,
)

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/generate", response_model=QueryResult)
async def generate_query(body: QueryGenerateRequest) -> QueryResult:
    return QueryResult(
        status="not_implemented",
        engine=body.engine,
        warnings=["AI query generation is not configured yet."],
    )


@router.post("/convert")
async def convert_query(body: QueryConvertRequest) -> dict:
    import sqlglot

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
            "warnings": ["Verify semantic equivalence before use."],
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}


@router.post("/validate")
async def validate_query(body: QueryValidateRequest) -> dict:
    import sqlglot

    try:
        sqlglot.parse(body.query, error_level=sqlglot.ErrorLevel.RAISE)
        return {"valid": True, "engine": body.engine, "parser": "sqlglot"}
    except sqlglot.errors.ParseError as exc:
        return {"valid": False, "engine": body.engine, "error": str(exc)}
