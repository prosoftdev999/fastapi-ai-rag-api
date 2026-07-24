from fastapi import FastAPI

app = FastAPI(
    title="FastAPI AI RAG API",
    version="0.1.0",
    description="A production-ready Retrieval-Augmented Generation API.",
)


@app.get("/", tags=["General"])
async def root() -> dict[str, str]:
    return {
        "message": "Welcome to FastAPI AI RAG API",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
