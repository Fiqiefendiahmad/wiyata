import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.deps import get_db
from app.models.sandbox import Sandbox
from app.schemas.sandbox import SandboxCreate, SandboxExecuteRequest, SandboxResponse

router = APIRouter(prefix="/sandboxes", tags=["Sandbox"])


@router.post("", response_model=SandboxResponse, status_code=201)
async def create_sandbox(
    body: SandboxCreate, db: AsyncSession = Depends(get_db)
) -> SandboxResponse:
    expires_at = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.sandbox_default_ttl_minutes
    )
    sandbox = Sandbox(
        engine=body.engine,
        engine_version=body.engine_version,
        template_slug=body.template_slug,
        status="requested",
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
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    return SandboxResponse.model_validate(sandbox)


@router.delete("/{sandbox_id}", status_code=204)
async def delete_sandbox(
    sandbox_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    sandbox = await db.get(Sandbox, sandbox_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    sandbox.status = "deleted"
    await db.commit()
