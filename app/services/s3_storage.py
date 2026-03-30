from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
from fastapi import HTTPException, UploadFile, status

from app.services.storage_base import Storage


class S3Storage(Storage):
    def __init__(
        self,
        *,
        bucket_name: str,
        region: str,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        endpoint_url: str | None = None,
        use_ssl: bool = False,
    ):
        
        
        self.bucket_name = bucket_name
        self.region = region
        self.client: BaseClient = boto3.client(
            "s3",
            region_name=region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            endpoint_url=endpoint_url,
            use_ssl=use_ssl,
        )

    def ensure_exists(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as exc:
            raise RuntimeError(
                f"S3 bucket '{self.bucket_name}' does not exist or is not accessible"
            ) from exc

    def build_key(self, project_id: int, filename: str) -> str:
        safe_name = Path(filename).name
        return f"projects/{project_id}/{uuid4().hex}_{safe_name}"

    async def save(self, *, key: str, file: UploadFile, max_size_bytes: int) -> int:
        content = await file.read()
        size = len(content)

        if size > max_size_bytes:
            await file.close()
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds max size of {max_size_bytes} bytes",
            )

        try:
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=content,
                ContentType=file.content_type or "application/octet-stream",
            )
        finally:
            await file.close()

        return size

    def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket_name, Key=key)

    def path_for(self, key: str) -> Path | None:
        return None

    def generate_download_url(self, key: str, expires_in: int = 600) -> str | None:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket_name, "Key": key},
            ExpiresIn=expires_in,
        )