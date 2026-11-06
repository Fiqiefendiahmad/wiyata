import os
from pathlib import Path
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse
import psycopg
import pymysql
import sqlglot
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.base import DatabaseAdapter
from app.adapters.sqlite import SQLiteAdapter
from app.adapters.postgres import PostgresAdapter
from app.adapters.mysql import MySQLAdapter
from app.adapters.oracle import OracleAdapter
from app.config import settings
from app.deps import get_db
from app.models.sandbox import Sandbox
from app.schemas.sandbox import (
    SandboxCreate,
    SandboxExecuteRequest,
    SandboxExecuteResult,
    SandboxResponse,
    TemplateInfo,
)
from app.templates.datasets import TEMPLATES

router = APIRouter(prefix="/sandboxes", tags=["Sandbox"])

STORAGE_DIR = Path(os.getenv("SANDBOX_STORAGE_DIR", "/tmp/wiyata_sandboxes"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def _init_sqlite_db(db_path: Path, template_slug: str | None) -> None:
    conn = sqlite3.connect(str(db_path))
    template = TEMPLATES.get(template_slug or "banking", TEMPLATES["blank"])
    conn.executescript(template["sql"])
    conn.close()


def _init_postgres_sandbox(schema_name: str, template_slug: str | None) -> None:
    conn = psycopg.connect(settings.postgres_sandbox_url, autocommit=True)
    with conn.cursor() as cur:
        cur.execute(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE;')
        cur.execute(f'CREATE SCHEMA "{schema_name}";')
        cur.execute(f'SET search_path TO "{schema_name}", public;')
        template = TEMPLATES.get(template_slug or "banking", TEMPLATES["blank"])
        if template["sql"].strip():
            statements = sqlglot.transpile(template["sql"], read="sqlite", write="postgres")
            for stmt in statements:
                cur.execute(stmt)
    conn.close()


def _init_mysql_sandbox(db_name: str, template_slug: str | None) -> None:
    conn = pymysql.connect(
        host="127.0.0.1",
        port=3307,
        user="wiyata",
        password="change-this-dev-password",
        autocommit=True,
    )
    with conn.cursor() as cur:
        cur.execute(f"DROP DATABASE IF EXISTS `{db_name}`;")
        cur.execute(f"CREATE DATABASE `{db_name}`;")
        cur.execute(f"USE `{db_name}`;")
        template = TEMPLATES.get(template_slug or "banking", TEMPLATES["blank"])
        if template["sql"].strip():
            statements = sqlglot.transpile(template["sql"], read="sqlite", write="mysql")
            for stmt in statements:
                cur.execute(stmt)
    conn.close()


def _get_adapter(engine: str, storage_ref: str) -> DatabaseAdapter:
    if engine == "postgres":
        adapter = PostgresAdapter()
        adapter.connect({"dsn": settings.postgres_sandbox_url, "schema": storage_ref})
        return adapter
    elif engine == "mysql":
        adapter = MySQLAdapter()
        adapter.connect({"database": storage_ref})
        return adapter
    elif engine == "oracle":
        adapter = OracleAdapter()
        adapter.connect({"path": storage_ref})
        return adapter
    else:
        adapter = SQLiteAdapter()
        adapter.connect({"path": storage_ref})
        return adapter


@router.get("/templates", response_model=list[TemplateInfo])
async def list_templates() -> list[TemplateInfo]:
    return [
        TemplateInfo(
            slug=slug,
            name=data["name"],
            description=data["description"],
        )
        for slug, data in TEMPLATES.items()
    ]


@router.post("", response_model=SandboxResponse, status_code=201)
async def create_sandbox(
    body: SandboxCreate, db: AsyncSession = Depends(get_db)
) -> SandboxResponse:
    sandbox_id = uuid.uuid4()
    expires_at = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.sandbox_default_ttl_minutes
    )

    engine = body.engine.lower()
    template_slug = body.template_slug or "banking"

    if engine == "postgres":
        storage_ref = f"sb_{sandbox_id.hex[:12]}"
        engine_version = body.engine_version or "17.0"
        _init_postgres_sandbox(storage_ref, template_slug)
    elif engine == "mysql":
        storage_ref = f"sb_{sandbox_id.hex[:12]}"
        engine_version = body.engine_version or "11.3 (MariaDB)"
        _init_mysql_sandbox(storage_ref, template_slug)
    elif engine == "oracle":
        db_path = STORAGE_DIR / f"{sandbox_id}.db"
        storage_ref = str(db_path)
        engine_version = body.engine_version or "23ai (Transpiled)"
        _init_sqlite_db(db_path, template_slug)
    else:
        # Default to SQLite
        engine = "sqlite"
        db_path = STORAGE_DIR / f"{sandbox_id}.db"
        storage_ref = str(db_path)
        engine_version = body.engine_version or "3.45.0"
        _init_sqlite_db(db_path, template_slug)

    sandbox = Sandbox(
        id=sandbox_id,
        engine=engine,
        engine_version=engine_version,
        template_slug=template_slug,
        status="ready",
        storage_reference=storage_ref,
        expires_at=expires_at,
        resource_policy={
            "max_rows": settings.sandbox_max_result_rows,
            "max_bytes": settings.sandbox_max_result_bytes,
            "timeout_seconds": settings.sandbox_max_execution_seconds,
        },
    )
    db.add(sandbox)
    await db.commit()
    await db.refresh(sandbox)
    return SandboxResponse.model_validate(sandbox)


@router.get("/{sandbox_id}", response_model=SandboxResponse)
async def get_sandbox(
    sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> SandboxResponse:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox or sandbox.status == "deleted":
        raise HTTPException(status_code=404, detail="Sandbox not found")
    return SandboxResponse.model_validate(sandbox)


@router.get("/{sandbox_id}/schema")
async def get_sandbox_schema(
    sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> list[dict]:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox or sandbox.status == "deleted":
        raise HTTPException(status_code=404, detail="Sandbox not found")

    storage_ref = sandbox.storage_reference or (str(STORAGE_DIR / f"{sandbox_id}.db"))
    adapter = _get_adapter(sandbox.engine, storage_ref)
    try:
        schema = adapter.get_full_schema()
        return schema
    finally:
        adapter.close()


@router.post("/{sandbox_id}/execute", response_model=SandboxExecuteResult)
async def execute_query_in_sandbox(
    sandbox_id: uuid.UUID,
    body: SandboxExecuteRequest,
    db: AsyncSession = Depends(get_db),
) -> SandboxExecuteResult:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox or sandbox.status == "deleted":
        raise HTTPException(status_code=404, detail="Sandbox not found")

    storage_ref = sandbox.storage_reference or (str(STORAGE_DIR / f"{sandbox_id}.db"))
    adapter = _get_adapter(sandbox.engine, storage_ref)
    try:
        read_only = not body.confirmed if not body.read_only else True
        result = adapter.execute(
            body.query,
            max_rows=settings.sandbox_max_result_rows,
            timeout_seconds=settings.sandbox_max_execution_seconds,
            read_only=read_only,
        )
        return SandboxExecuteResult(**result)
    finally:
        adapter.close()


@router.post("/{sandbox_id}/reset", response_model=SandboxResponse)
async def reset_sandbox(
    sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> SandboxResponse:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox or sandbox.status == "deleted":
        raise HTTPException(status_code=404, detail="Sandbox not found")

    storage_ref = sandbox.storage_reference or (str(STORAGE_DIR / f"{sandbox_id}.db"))

    if sandbox.engine == "postgres":
        _init_postgres_sandbox(storage_ref, sandbox.template_slug)
    elif sandbox.engine == "mysql":
        _init_mysql_sandbox(storage_ref, sandbox.template_slug)
    else:
        db_path = Path(storage_ref)
        if db_path.exists():
            db_path.unlink()
        _init_sqlite_db(db_path, sandbox.template_slug)

    sandbox.status = "ready"
    sandbox.expires_at = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.sandbox_default_ttl_minutes
    )
    await db.commit()
    await db.refresh(sandbox)
    return SandboxResponse.model_validate(sandbox)


@router.get("/{sandbox_id}/export")
async def export_sandbox(
    sandbox_id: uuid.UUID,
    format: str = "sql",
    db: AsyncSession = Depends(get_db),
) -> Response:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox or sandbox.status == "deleted":
        raise HTTPException(status_code=404, detail="Sandbox not found")

    storage_ref = sandbox.storage_reference or (str(STORAGE_DIR / f"{sandbox_id}.db"))

    if sandbox.engine in ("sqlite", "oracle"):
        db_path = Path(storage_ref)
        if not db_path.exists():
            raise HTTPException(status_code=404, detail="Sandbox storage file missing")

        if format == "db":
            return FileResponse(
                path=str(db_path),
                filename=f"wiyata_{sandbox.engine}_{sandbox.template_slug}_{sandbox_id}.sqlite3",
                media_type="application/x-sqlite3",
            )
        else:
            conn = sqlite3.connect(str(db_path))
            dump_lines = list(conn.iterdump())
            conn.close()
            sql_content = "\n".join(dump_lines)
            return Response(
                content=sql_content,
                media_type="application/sql",
                headers={
                    "Content-Disposition": f'attachment; filename="wiyata_{sandbox.engine}_{sandbox.template_slug}_{sandbox_id}.sql"'
                },
            )
    else:
        # PostgreSQL / MySQL SQL Dump from template
        template = TEMPLATES.get(sandbox.template_slug, TEMPLATES["blank"])
        statements = sqlglot.transpile(template["sql"], read="sqlite", write=sandbox.engine)
        sql_content = f"-- WIYATA {sandbox.engine.upper()} Export\n-- Sandbox: {sandbox_id}\n\n" + ";\n\n".join(statements) + ";"
        return Response(
            content=sql_content,
            media_type="application/sql",
            headers={
                "Content-Disposition": f'attachment; filename="wiyata_{sandbox.engine}_{sandbox.template_slug}_{sandbox_id}.sql"'
            },
        )


@router.delete("/{sandbox_id}", status_code=204)
async def delete_sandbox(
    sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    sandbox.status = "deleted"
    storage_ref = sandbox.storage_reference
    if storage_ref:
        if sandbox.engine == "postgres":
            try:
                conn = psycopg.connect(settings.postgres_sandbox_url, autocommit=True)
                with conn.cursor() as cur:
                    cur.execute(f'DROP SCHEMA IF EXISTS "{storage_ref}" CASCADE;')
                conn.close()
            except Exception:
                pass
        elif sandbox.engine == "mysql":
            try:
                conn = pymysql.connect(host="127.0.0.1", port=3307, user="wiyata", password="change-this-dev-password", autocommit=True)
                with conn.cursor() as cur:
                    cur.execute(f"DROP DATABASE IF EXISTS `{storage_ref}`;")
                conn.close()
            except Exception:
                pass
        else:
            path = Path(storage_ref)
            if path.exists():
                path.unlink(missing_ok=True)

    await db.commit()
