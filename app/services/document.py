import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus


async def create_document(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    filename: str,
    stored_filename: str,
    content_type: str,
    size_bytes: int,
) -> Document:
    document = Document(
        user_id=user_id,
        filename=filename,
        stored_filename=stored_filename,
        content_type=content_type,
        size_bytes=size_bytes,
        status=DocumentStatus.PENDING,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return document


async def list_user_documents(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc())
    )

    return list(result.scalars().all())


async def get_user_document(
    db: AsyncSession,
    document_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Document | None:
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )

    return result.scalar_one_or_none()


async def delete_document(
    db: AsyncSession,
    document: Document,
) -> None:
    await db.delete(document)
    await db.commit()
