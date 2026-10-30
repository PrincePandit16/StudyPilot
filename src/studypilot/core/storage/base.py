from abc import ABC, abstractmethod
from typing import BinaryIO

class StorageProvider(ABC):
    @abstractmethod
    async def upload(self, file: BinaryIO, path: str) -> str:
        """Upload a file to storage and return its path."""
        pass

    @abstractmethod
    async def download(self, path: str) -> BinaryIO:
        """Download a file from storage."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a file exists in storage."""
        pass
