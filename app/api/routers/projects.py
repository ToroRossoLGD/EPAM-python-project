from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import create_invite_token
from app.db.models.project import Project
from app.db.models.project_access import ProjectAccess
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services.email import send_invite_email
from app.services.projects import (
    join_project_by_token,
    list_projects_for_user_raw,
    require_owner,
    require_project_access,
)

router = APIRouter()


@router.post("/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectOut:
    project = Project(owner_id=current_user.id, name=payload.name, description=payload.description)
    db.add(project)
    await db.flush()  

    db.add(ProjectAccess(project_id=project.id, user_id=current_user.id, role="owner"))

    await db.commit()
    await db.refresh(project)

    return ProjectOut(id=project.id, name=project.name, description=project.description, owner_id=project.owner_id, total_size_bytes=project.total_size_bytes)


@router.get("/projects", response_model=list[ProjectOut])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ProjectOut]:
    projects = await list_projects_for_user_raw(db, current_user.id)

    return [
        ProjectOut(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            owner_id=p["owner_id"],
            total_size_bytes=p["total_size_bytes"],
        )
        for p in projects
    ]


@router.get("/project/{project_id}/info", response_model=ProjectOut)
async def get_project_info(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectOut:
    project = await require_project_access(db, project_id, current_user.id)
    return ProjectOut(id=project.id, name=project.name, description=project.description, owner_id=project.owner_id, total_size_bytes=project.total_size_bytes)


@router.put("/project/{project_id}/info", response_model=ProjectOut)
async def update_project_info(
    project_id: int,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectOut:
    project = await require_project_access(db, project_id, current_user.id)

    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description

    await db.commit()
    await db.refresh(project)

    return ProjectOut(id=project.id, name=project.name, description=project.description, owner_id=project.owner_id, total_size_bytes=project.total_size_bytes)


@router.delete("/project/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    project = await require_owner(db, project_id, current_user.id)

    await db.delete(project)
    await db.commit()
    return None


@router.post("/project/{project_id}/invite", status_code=status.HTTP_204_NO_CONTENT)
async def invite_user(
    project_id: int,
    user: str = Query(..., description="login of user to invite"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await require_owner(db, project_id, current_user.id)

    result = await db.execute(select(User).where(User.login == user))
    invited = result.scalar_one_or_none()
    if invited is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    exists = await db.execute(
        select(ProjectAccess).where(
            ProjectAccess.project_id == project_id,
            ProjectAccess.user_id == invited.id,
        )
    )
    if exists.scalar_one_or_none() is not None:
        return None  

    db.add(ProjectAccess(project_id=project_id, user_id=invited.id, role="participant"))
    await db.commit()
    return None

@router.post("/project/{project_id}/share")
async def share_project(
    project_id: int,
    email: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await require_owner(db, project_id, current_user.id)

    token = create_invite_token(email, project_id)

    link = f"{settings.FRONTEND_URL}/join?token={token}"

    send_invite_email(email, link)

    return {"detail": "Invite email sent"}

@router.get("/join")
async def join_project(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    detail = await join_project_by_token(
        db=db,
        token=token,
        current_user=current_user,
    )
    return {"detail": detail}