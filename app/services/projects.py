from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project
from app.db.models.project_access import ProjectAccess


async def require_project_access(db: AsyncSession, project_id: int, user_id: int) -> Project:
    project = await db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    result = await db.execute(
        select(ProjectAccess).where(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == user_id,
        )
    )
    access = result.scalar_one_or_none()
    if access is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access to project")

    return project


async def require_owner(db: AsyncSession, project_id: int, user_id: int) -> Project:
    project = await require_project_access(db, project_id, user_id)
    if project.owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owner permission required")
    return project