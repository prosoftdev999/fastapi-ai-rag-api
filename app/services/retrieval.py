import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.services.embedding import create_embedding


@dataclass(slots=True)
class RetrievedChunk:
    document_id: uuid.UUID
    document_name: str
    chunk_index: int
    content: str
    similarity: float


async def search_similar_chunks(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    question: str,
    top_k: int | None = None,
    document_ids: list[uuid.UUID] | None = None,
) -> list[RetrievedChunk]:
    query_embedding = await create_embedding(question)

    result_limit = top_k or settings.rag_top_k
    result_limit = min(
        result_limit,
        settings.rag_max_top_k,
    )

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            Document.id == DocumentChunk.document_id,
        )
        .where(
            Document.user_id == user_id,
            Document.status == DocumentStatus.COMPLETED,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(result_limit)
    )

    if document_ids:
        statement = statement.where(Document.id.in_(document_ids))

    result = await db.execute(statement)

    retrieved_chunks: list[RetrievedChunk] = []

    for chunk, document_name, distance_value in result.all():
        similarity = 1.0 - float(distance_value)
        similarity = max(-1.0, min(1.0, similarity))

        if similarity < settings.rag_min_similarity:
            continue

        retrieved_chunks.append(
            RetrievedChunk(
                document_id=chunk.document_id,
                document_name=document_name,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                similarity=round(similarity, 6),
            )
        )

    return retrieved_chunks
