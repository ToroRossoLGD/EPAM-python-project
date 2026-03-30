from fastapi import APIRouter, Depends, HTTPException, Query, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models.project_access import ProjectAccess
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.auth import TokenOut, UserCreate, UserLogin, UserOut

router = APIRouter()


@router.post("/auth", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)) -> UserOut:
    if payload.password != payload.repeat_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    existing = await db.execute(select(User).where(User.login == payload.login))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already exists")

    user = User(login=payload.login, password_hash=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserOut(id=user.id, login=user.login)


@router.post("/login", response_model=TokenOut)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)) -> TokenOut:
    result = await db.execute(select(User).where(User.login == payload.login))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=token, expires_in=settings.JWT_EXPIRES_MINUTES * 60)

@router.get("/join")
async def join_project(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
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
        return {"detail": "User already has access to this project"}

    db.add(
        ProjectAccess(
            project_id=project_id,
            user_id=current_user.id,
            role="participant",
        )
    )
    await db.commit()

    return {"detail": "Joined project successfully"}