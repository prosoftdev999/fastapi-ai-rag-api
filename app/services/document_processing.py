import uuid
from pathlib import Path

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.document_chunk import DocumentChunk
from app.services.chunking import chunk_text, estimate_token_count
from app.services.embedding import create_embeddings
from app.services.text_extraction import extract_text


class DocumentProcessingError(Exception):
    """Raised when document processing fails."""


def get_document_file_path(document: Document) -> Path:
    return Path(settings.upload_directory) / document.stored_filename


async def remove_existing_chunks(
    db: AsyncSession,
    document_id: uuid.UUID,
) -> None:
    await db.execute(
        delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
    )


async def mark_document_failed(
    db: AsyncSession,
    document: Document,
    error_message: str,
) -> None:
    document.status = DocumentStatus.FAILED
    document.error_message = error_message[:2000]

    await db.commit()
    await db.refresh(document)


async def process_document(
    db: AsyncSession,
    document: Document,
) -> int:
    document.status = DocumentStatus.PROCESSING
    document.error_message = None

    await db.commit()
    await db.refresh(document)

    try:
        file_path = get_document_file_path(document)

        text = await extract_text(file_path)

        chunks = chunk_text(
            text,
            chunk_size=settings.chunk_size,
            overlap=settings.chunk_overlap,
        )

        if not chunks:
            raise DocumentProcessingError("The document produced no text chunks")

        embeddings = await create_embeddings(chunks)

        if len(embeddings) != len(chunks):
            raise DocumentProcessingError("Chunk and embedding counts do not match")

        await remove_existing_chunks(
            db,
            document.id,
        )

        chunk_records: list[DocumentChunk] = []

        for index, (content, embedding) in enumerate(
            zip(chunks, embeddings, strict=True)
        ):
            chunk_records.append(
                DocumentChunk(
                    document_id=document.id,
                    chunk_index=index,
                    content=content,
                    token_count=estimate_token_count(content),
                    embedding=embedding,
                )
            )

        db.add_all(chunk_records)

        document.status = DocumentStatus.COMPLETED
        document.error_message = None

        await db.commit()
        await db.refresh(document)

        return len(chunk_records)

    except Exception as exc:
        await db.rollback()

        error_message = (
            str(exc) or exc.__class__.__name__ or "Document processing failed"
        )

        try:
            await mark_document_failed(
                db,
                document,
                error_message,
            )
        except Exception:  # noqa: BLE001
            await db.rollback()

        raise DocumentProcessingError(error_message) from exc
