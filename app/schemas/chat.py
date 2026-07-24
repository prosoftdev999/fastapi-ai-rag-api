import uuid

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=4000,
    )
    top_k: int | None = Field(
        default=None,
        ge=1,
        le=10,
    )
    document_ids: list[uuid.UUID] | None = None

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        cleaned = value.strip()

        if not cleaned:
            raise ValueError("Question cannot be empty")

        return cleaned

    @field_validator("document_ids")
    @classmethod
    def remove_duplicate_document_ids(
        cls,
        value: list[uuid.UUID] | None,
    ) -> list[uuid.UUID] | None:
        if value is None:
            return None

        return list(dict.fromkeys(value))


class SourceChunk(BaseModel):
    document_id: uuid.UUID
    document_name: str
    chunk_index: int
    content: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
