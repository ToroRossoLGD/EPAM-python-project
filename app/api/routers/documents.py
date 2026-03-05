from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.db.models.document import Document
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.document import DocumentOut
from app.services.documents import require_document_access
from app.services.projects import require_project_access
from app.services.storage import LocalStorage

router = APIRouter()


def get_storage() -> LocalStorage:
    storage = LocalStorage(settings.STORAGE_DIR)
    storage.ensure_exists()
    return storage


@router.get("/project/{project_id}/documents", response_model=list[DocumentOut])
async def list_project_documents(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentOut]:
    await require_project_access(db, project_id, current_user.id)

    result = await db.execute(select(Document).where(Document.project_id == project_id).order_by(Document.id.desc()))
    docs = result.scalars().all()
    return [
        DocumentOut(
            id=d.id,
            project_id=d.project_id,
            uploaded_by=d.uploaded_by,
            filename=d.filename,
            content_type=d.content_type,
            size_bytes=d.size_bytes,
        )
        for d in docs
    ]


@router.post("/project/{project_id}/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_project_document(
    project_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentOut:
    await require_project_access(db, project_id, current_user.id)
    storage = get_storage()

    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a filename")

    key = storage.build_key(project_id, file.filename)
    size = await storage.save(key=key, file=file)

    doc = Document(
        project_id=project_id,
        uploaded_by=current_user.id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        storage_key=key,
        size_bytes=size,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return DocumentOut(
        id=doc.id,
        project_id=doc.project_id,
        uploaded_by=doc.uploaded_by,
        filename=doc.filename,
        content_type=doc.content_type,
        size_bytes=doc.size_bytes,
    )




@router.get("/document/{document_id}")
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc = await require_document_access(db, document_id, current_user.id)
    storage = get_storage()

    path = storage.path_for(doc.storage_key)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")

    return FileResponse(
        path=path,
        media_type=doc.content_type,
        filename=doc.filename,
    )


@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    doc = await require_document_access(db, document_id, current_user.id)
    storage = get_storage()

    storage.delete(doc.storage_key)
    await db.delete(doc)
    await db.commit()
    return None