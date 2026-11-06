from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.models.tools import ProfessionalTool
from app.schemas.tools import ToolSummary

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.get("", response_model=list[ToolSummary])
async def list_tools(db: AsyncSession = Depends(get_db)) -> list[ToolSummary]:
    result = await db.execute(
        select(ProfessionalTool).order_by(ProfessionalTool.name).limit(100)
    )
    return [ToolSummary.model_validate(t) for t in result.scalars().all()]


@router.get("/{slug}", response_model=ToolSummary)
async def get_tool(slug: str, db: AsyncSession = Depends(get_db)) -> ToolSummary:
    from fastapi import HTTPException

    result = await db.execute(
        select(ProfessionalTool).where(ProfessionalTool.slug == slug)
    )
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return ToolSummary.model_validate(tool)
