from app.core.config import settings
from app.services.s3_storage import S3Storage
from app.services.storage import LocalStorage
from app.services.storage_base import Storage


def get_storage() -> Storage:
    if settings.USE_S3_STORAGE:
        if not settings.AWS_S3_BUCKET:
            raise RuntimeError("AWS_S3_BUCKET is not configured")

        if not settings.AWS_ACCESS_KEY_ID:
            raise RuntimeError("AWS_ACCESS_KEY_ID is not configured")

        if not settings.AWS_SECRET_ACCESS_KEY:
            raise RuntimeError("AWS_SECRET_ACCESS_KEY is not configured")
        
        endpoint_url = settings.AWS_S3_ENDPOINT_URL or None
        

        return S3Storage(
            bucket_name=settings.AWS_S3_BUCKET,
            region=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=endpoint_url,
            use_ssl=settings.AWS_S3_USE_SSL,
        )

    storage = LocalStorage(settings.STORAGE_DIR)
    storage.ensure_exists()
    return storage