from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FastAPI AI RAG API"
    app_version: str = "0.1.0"
    debug: bool = True

    database_url: str
    redis_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Keep these for the final AI answer endpoint.
    # They are no longer required for local embeddings.
    openai_api_key: str = ""
    openai_model: str = "gpt-4.1-mini"

    # Local embedding model
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    max_upload_size_mb: int = 10
    upload_directory: str = "uploads"

    chunk_size: int = 1000
    chunk_overlap: int = 200

    rag_top_k: int = 5
    rag_max_top_k: int = 10
    rag_min_similarity: float = 0.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
