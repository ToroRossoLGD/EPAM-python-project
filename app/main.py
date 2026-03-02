from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
    )

    app.include_router(health_router, tags=["health"])
    return app


app = create_app()