import os
import shutil
from typing import BinaryIO
from pathlib import Path
from src.studypilot.core.storage.base import StorageProvider

class LocalStorageProvider(StorageProvider):
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, file: BinaryIO, path: str) -> str:
        full_path = self.upload_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file, f)
        return str(full_path)

    async def download(self, path: str) -> BinaryIO:
        full_path = Path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return open(full_path, "rb")

    async def delete(self, path: str) -> bool:
        full_path = Path(path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    async def exists(self, path: str) -> bool:
        return Path(path).exists()
