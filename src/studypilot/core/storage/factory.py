from typing import BinaryIO
from src.studypilot.core.storage.base import StorageProvider
from src.studypilot.core.storage.local import LocalStorageProvider
from src.studypilot.core.config import settings

def get_storage_provider() -> StorageProvider:
    # In a real app, this would check settings.STORAGE_TYPE
    # Defaulting to LocalStorageProvider for development
    return LocalStorageProvider()
