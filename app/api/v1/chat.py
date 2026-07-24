from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    SourceChunk,
)
from app.services.embedding import EmbeddingError
from app.services.rag import (
    AnswerGenerationError,
    NoRelevantContextError,
    answer_question,
)

router = APIRouter(
    prefix="/chat",
    tags=["RAG Chat"],
)


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat_with_documents(
    request: ChatRequest,
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> ChatResponse:
    try:
        answer, retrieved_chunks = await answer_question(
            db,
            user_id=current_user.id,
            question=request.question,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )
    except NoRelevantContextError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except EmbeddingError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except AnswerGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    sources = [
        SourceChunk(
            document_id=chunk.document_id,
            document_name=chunk.document_name,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            similarity=chunk.similarity,
        )
        for chunk in retrieved_chunks
    ]

    return ChatResponse(
        answer=answer,
        sources=sources,
    )
