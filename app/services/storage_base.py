from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from fastapi import UploadFile


class Storage(ABC):
    @abstractmethod
    def ensure_exists(self) -> None:
        pass

    @abstractmethod
    def build_key(self, project_id: int, filename: str) -> str:
        pass

    @abstractmethod
    async def save(self, *, key: str, file: UploadFile, max_size_bytes: int) -> int:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def path_for(self, key: str) -> Path | None:
        pass

    @abstractmethod
    def generate_download_url(self, key: str, expires_in: int = 600) -> str | None:
        pass