from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import knowledge, learning, library, query, sandbox, tools


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield


app = FastAPI(
    title="WIYATA API",
    description="Your Database Learning Center — API",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/api/v1")
app.include_router(sandbox.router, prefix="/api/v1")
app.include_router(knowledge.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")
app.include_router(learning.router, prefix="/api/v1")
app.include_router(library.router, prefix="/api/v1")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": "0.1.0", "service": "wiyata-api"}
