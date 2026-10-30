import logging
from typing import List
from sentence_transformers import SentenceTransformer
from src.studypilot.core.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Ensure model is only loaded once
        if self._model is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_NAME}")
                self._model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model {settings.EMBEDDING_MODEL_NAME}: {e}")
                raise e

    def generate_embedding(self, text: str) -> List[float]:
        """Generates a vector embedding for a single string."""
        if not text:
            return [0.0] * settings.EMBEDDING_DIMENSIONS

        embedding = self._model.encode(text)
        return embedding.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates vector embeddings for a list of strings efficiently."""
        if not texts:
            return []

        embeddings = self._model.encode(texts)
        return embeddings.tolist()

# Singleton instance for easy import
embedding_service = EmbeddingService()
