from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


def validate_document_metadata(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename",
        )

    allowed_extensions = {
        ext.strip().lower()
        for ext in settings.ALLOWED_DOCUMENT_EXTENSIONS.split(",")
        if ext.strip()
    }
    allowed_content_types = {
        item.strip().lower()
        for item in settings.ALLOWED_DOCUMENT_CONTENT_TYPES.split(",")
        if item.strip()
    }

    extension = Path(file.filename).suffix.lower()
    content_type = (file.content_type or "").lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: {extension}",
        )

    if content_type not in allowed_content_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {content_type or 'unknown'}",
        )