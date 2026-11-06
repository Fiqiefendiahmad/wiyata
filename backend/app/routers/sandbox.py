import os
from pathlib import Path
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.sqlite import SQLiteAdapter
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
    template = TEMPLATES.get(template_slug or "ecommerce", TEMPLATES["blank"])
    conn.executescript(template["sql"])
    conn.close()


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

    db_path = STORAGE_DIR / f"{sandbox_id}.db"

    # Provision SQLite file if engine is sqlite
    if body.engine == "sqlite":
        _init_sqlite_db(db_path, body.template_slug)

    sandbox = Sandbox(
        id=sandbox_id,
        engine=body.engine,
        engine_version=body.engine_version or "3.45.0",
        template_slug=body.template_slug or "ecommerce",
        status="ready",
        storage_reference=str(db_path),
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

    db_path = Path(sandbox.storage_reference or (STORAGE_DIR / f"{sandbox_id}.db"))
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Sandbox storage not found")

    adapter = SQLiteAdapter()
    adapter.connect({"path": str(db_path)})
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

    db_path = Path(sandbox.storage_reference or (STORAGE_DIR / f"{sandbox_id}.db"))
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Sandbox storage file missing")

    adapter = SQLiteAdapter()
    adapter.connect({"path": str(db_path)})
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

    db_path = Path(sandbox.storage_reference or (STORAGE_DIR / f"{sandbox_id}.db"))
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


@router.delete("/{sandbox_id}", status_code=204)
async def delete_sandbox(
    sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")

    sandbox.status = "deleted"
    if sandbox.storage_reference:
        path = Path(sandbox.storage_reference)
        if path.exists():
            path.unlink(missing_ok=True)

    await db.commit()
