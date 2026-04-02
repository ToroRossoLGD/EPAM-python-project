from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.project import Project
from app.db.models.project_access import ProjectAccess
from app.db.models.user import User


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

async def join_project_by_token(
    db: AsyncSession,
    token: str,
    current_user: User,
) -> str:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "invite":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite token",
        )

    project_id = payload.get("project_id")
    email = payload.get("sub")

    if project_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite token payload",
        )

    existing = await db.execute(
        select(ProjectAccess).where(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        return "User already has access to this project"

    db.add(
        ProjectAccess(
            project_id=project_id,
            user_id=current_user.id,
            role="participant",
        )
    )
    await db.commit()

    return "Joined project successfully"