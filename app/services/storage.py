from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.services.storage_base import Storage


class LocalStorage(Storage):
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)

    def ensure_exists(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def build_key(self, project_id: int, filename: str) -> str:
        safe_name = Path(filename).name
        return f"projects/{project_id}/{uuid4().hex}_{safe_name}"

    async def save(self, *, key: str, file: UploadFile, max_size_bytes: int) -> int:
        path = self.path_for(key)
        if path is None:
            raise RuntimeError("Local storage path could not be resolved")

        path.parent.mkdir(parents=True, exist_ok=True)

        size = 0
        try:
            with path.open("wb") as buffer:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > max_size_bytes:
                        buffer.close()
                        path.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds max size of {max_size_bytes} bytes",
                        )
                    buffer.write(chunk)
        finally:
            await file.close()

        return size

    def delete(self, key: str) -> None:
        path = self.path_for(key)
        if path is not None:
            path.unlink(missing_ok=True)

    def path_for(self, key: str) -> Path | None:
        return self.base_dir / key

    def generate_download_url(self, key: str, expires_in: int = 600) -> str | None:
        return None