from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Project Dashboard API"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str

    EMAIL_FROM: str = "noreply@example.com"
    FRONTEND_URL: str = "http://localhost:8000"
    JWT_SECRET: str
    JWT_EXPIRES_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    STORAGE_DIR: str = "storage"
    ALLOWED_DOCUMENT_EXTENSIONS: str = ".pdf,.docx"
    ALLOWED_DOCUMENT_CONTENT_TYPES: str = (
        "application/pdf,"
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    MAX_DOCUMENT_SIZE_BYTES: int = 10 * 1024 * 1024  
    MAX_PROJECT_SIZE_BYTES: int = 50 * 1024 * 1024

    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    AWS_S3_ENDPOINT_URL: str | None = None
    AWS_S3_USE_SSL: bool = False
    AWS_S3_BUCKET: str | None = None
    AWS_REGION: str = "eu-central-1"

    USE_S3_STORAGE: bool = False

    TESTING: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()