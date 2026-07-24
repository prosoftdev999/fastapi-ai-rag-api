import uuid
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.document import DocumentStatus
from app.models.user import User
from app.schemas.document import (
    DocumentProcessingResponse,
    DocumentResponse,
)
from app.services.document import (
    create_document,
    delete_document,
    get_user_document,
    list_user_documents,
)
from app.services.document_processing import (
    DocumentProcessingError,
    process_document,
)
from app.services.storage import (
    delete_stored_file,
    save_upload_file,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> DocumentResponse:
    original_filename = file.filename or "document"
    content_type = file.content_type or "application/octet-stream"

    stored_filename, size_bytes = await save_upload_file(file)

    try:
        document = await create_document(
            db,
            user_id=current_user.id,
            filename=original_filename,
            stored_filename=stored_filename,
            content_type=content_type,
            size_bytes=size_bytes,
        )
    except Exception:
        await delete_stored_file(stored_filename)
        raise

    return DocumentResponse.model_validate(document)


@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def read_documents(
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> list[DocumentResponse]:
    documents = await list_user_documents(
        db,
        current_user.id,
    )

    return [DocumentResponse.model_validate(document) for document in documents]


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def read_document(
    document_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> DocumentResponse:
    document = await get_user_document(
        db,
        document_id,
        current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return DocumentResponse.model_validate(document)


@router.post(
    "/{document_id}/process",
    response_model=DocumentProcessingResponse,
)
async def process_user_document(
    document_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> DocumentProcessingResponse:
    document = await get_user_document(
        db,
        document_id,
        current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if document.status == DocumentStatus.PROCESSING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Document is already being processed",
        )

    try:
        chunks_created = await process_document(
            db,
            document,
        )
    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return DocumentProcessingResponse(
        document=DocumentResponse.model_validate(document),
        chunks_created=chunks_created,
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_document(
    document_id: uuid.UUID,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> Response:
    document = await get_user_document(
        db,
        document_id,
        current_user.id,
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    stored_filename = document.stored_filename

    await delete_document(db, document)
    await delete_stored_file(stored_filename)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
