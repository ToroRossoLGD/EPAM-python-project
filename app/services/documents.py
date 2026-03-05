from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document
from app.services.projects import require_project_access


async def require_document_access(db: AsyncSession, document_id: int, user_id: int) -> Document:
    doc = await db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # proveri pristup projektu kojem dokument pripada
    await require_project_access(db, doc.project_id, user_id)
    return doc