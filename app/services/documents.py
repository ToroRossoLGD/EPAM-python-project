from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.document import Document
from app.services.projects import require_project_access


async def require_document_access(db: AsyncSession, document_id: int, user_id: int) -> Document:
    doc = await db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")


    await require_project_access(db, doc.project_id, user_id)
    return doc

async def list_documents_for_project(
    db: AsyncSession,
    project_id: int,
) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.id.desc())
    )
    return result.scalars().all()