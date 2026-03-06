from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import  HTTPException, UploadFile, status


class LocalStorage:
   

    def __init__(self, base_dir: str):
        self.base_path = Path(base_dir)

    def ensure_exists(self) -> None:
        self.base_path.mkdir(parents=True, exist_ok=True)

    def build_key(self, project_id: int, filename: str) -> str:
        
        safe_name = filename.replace("/", "_").replace("\\", "_")
        return f"projects/{project_id}/{uuid4().hex}_{safe_name}"

    async def save(self, *, key: str, file: UploadFile, max_size_bytes: int) -> int:
        target = self.base_path / key
        target.parent.mkdir(parents=True, exist_ok=True)

        size = 0
        try:
            with target.open("wb") as f:
                while True:
                    chunk = await file.read(1024 * 1024)
                    if not chunk:
                        break

                    size += len(chunk)
                    if size > max_size_bytes:
                        raise HTTPException(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail=f"File exceeds max size of {max_size_bytes} bytes",
                        )

                    f.write(chunk)
        except Exception:
            if target.exists():
                target.unlink()
            raise
        finally:
            await file.close()

        return size

    def path_for(self, key: str) -> Path:
        return self.base_path / key

    def delete(self, key: str) -> None:
        path = self.path_for(key)
        if path.exists():
            path.unlink()