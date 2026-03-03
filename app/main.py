from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.auth import router as auth_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.routers.users import router as users_router


from app.db import models  


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    app.include_router(health_router, tags=["health"])
    app.include_router(auth_router, tags=["auth"])
    app.include_router(users_router, tags=["users"])

    return app


app = create_app()