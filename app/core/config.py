from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Project Dashboard API"
    APP_VERSION: str = "0.1.0"

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_EXPIRES_MINUTES: int = 60
    JWT_ALGORITHM: str = "HS256"
    STORAGE_DIR: str = "storage"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()