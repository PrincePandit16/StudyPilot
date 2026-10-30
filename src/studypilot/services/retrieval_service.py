import logging
from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from src.studypilot.core.config import settings
from src.studypilot.services.embedding_service import embedding_service
from src.studypilot.repositories.document_repository import DocumentRepository
from src.studypilot.models.document_chunk import DocumentChunk

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    chunk_id: UUID
    content: str
    document_id: UUID
    document_name: str
    page_number: int
    score: float

class RetrievalService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = DocumentRepository(session)

    def retrieve_context(
        self,
        user_id: UUID,
        query: str,
        document_ids: Optional[List[UUID]] = None,
        top_k: Optional[int] = None
    ) -> List[RetrievalResult]:
        """
        Converts a natural language query into embeddings and retrieves the most relevant chunks.
        """
        k = top_k or settings.TOP_K

        try:
            # 1. Generate embedding for the query
            query_vector = embedding_service.generate_embedding(query)

            # 2. Search for similar chunks in the database
            # Repository returns List[tuple(DocumentChunk, distance)]
            search_results = self.repository.search_similar_chunks(
                user_id=user_id,
                query_embedding=query_vector,
                document_ids=document_ids,
                limit=k
            )

            final_results = []
            for chunk, distance in search_results:
                # Convert cosine distance to similarity score (Similarity = 1 - Distance)
                similarity = 1.0 - distance

                if similarity < settings.SIMILARITY_THRESHOLD:
                    continue

                # Document name is needed for RetrievalResult
                # We can access it via the relationship in DocumentChunk
                results_item = RetrievalResult(
                    chunk_id=chunk.id,
                    content=chunk.content,
                    document_id=chunk.document_id,
                    document_name=chunk.document.filename,
                    page_number=chunk.page_number,
                    score=similarity
                )
                final_results.append(results_item)

            return final_results

        except Exception as e:
            logger.error(f"Error during retrieval for user {user_id}: {e}")
            return []

# Singleton-like helper for FastAPI dependencies
def get_retrieval_service(session: Session):
    return RetrievalService(session)
