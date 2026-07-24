from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-ready Retrieval-Augmented Generation API.",
)

app.include_router(api_router, prefix="/api")


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
    }
