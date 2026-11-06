from fastapi import APIRouter

router = APIRouter(prefix="/learning", tags=["Learning"])


@router.get("/roles")
async def list_roles() -> list:
    return []


@router.get("/paths")
async def list_paths() -> list:
    return []
