from fastapi import APIRouter

router = APIRouter(prefix="/library", tags=["Library"])


@router.get("/queries")
async def list_queries() -> list:
    return []
