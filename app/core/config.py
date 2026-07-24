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

    openai_api_key: str
    openai_model: str = "gpt-4.1-mini"

    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    max_upload_size_mb: int = 10
    upload_directory: str = "uploads"

    chunk_size: int = 1000
    chunk_overlap: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
