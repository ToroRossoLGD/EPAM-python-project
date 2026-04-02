from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.db.models.document
import app.db.models.project
import app.db.models.project_access
import app.db.models.user
from app.api.routers.auth import router as auth_router
from app.api.routers.documents import router as documents_router
from app.api.routers.health import router as health_router
from app.api.routers.projects import router as projects_router
from app.api.routers.users import router as users_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=None if settings.TESTING else lifespan,
    )

    app.include_router(health_router, tags=["health"])
    app.include_router(auth_router, tags=["auth"])
    app.include_router(users_router, tags=["users"])
    app.include_router(projects_router, tags=["projects"])
    app.include_router(documents_router, tags=["documents"])
    
    return app


app = create_app()