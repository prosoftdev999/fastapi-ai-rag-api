import uuid
from pathlib import Path

import aiofiles
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "text/plain",
    "text/markdown",
    "application/octet-stream",
}


def get_upload_directory() -> Path:
    upload_directory = Path(settings.upload_directory)
    upload_directory.mkdir(parents=True, exist_ok=True)
    return upload_directory


async def save_upload_file(
    upload_file: UploadFile,
) -> tuple[str, int]:
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file must have a filename",
        )

    extension = Path(upload_file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Only PDF, TXT, and Markdown files are supported",
        )

    if (
        upload_file.content_type
        and upload_file.content_type not in ALLOWED_CONTENT_TYPES
    ):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file content type",
        )

    content = await upload_file.read()
    size_bytes = len(content)
    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024

    if size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty",
        )

    if size_bytes > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=(
                f"File exceeds the maximum size of {settings.max_upload_size_mb} MB"
            ),
        )

    stored_filename = f"{uuid.uuid4()}{extension}"
    destination = get_upload_directory() / stored_filename

    try:
        async with aiofiles.open(destination, "wb") as output_file:
            await output_file.write(content)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save uploaded file",
        ) from exc
    finally:
        await upload_file.close()

    return stored_filename, size_bytes


async def delete_stored_file(stored_filename: str) -> None:
    file_path = get_upload_directory() / stored_filename

    try:
        file_path.unlink(missing_ok=True)
    except OSError:
        pass
