from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, delete
from uuid import UUID
from src.studypilot.models.document import Document
from src.studypilot.models.document_chunk import DocumentChunk

class DocumentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_document(self, user_id: UUID, filename: str, storage_path: str) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            storage_path=storage_path,
            status="pending"
        )
        self.session.add(doc)
        self.session.commit()
        self.session.refresh(doc)
        return doc

    def get_document_by_id(self, doc_id: UUID, user_id: UUID) -> Optional[Document]:
        # Strict isolation: always filter by user_id
        return self.session.execute(
            select(Document).where(Document.id == doc_id, Document.user_id == user_id)
        ).scalar_one_or_none()

    def get_user_documents(self, user_id: UUID) -> List[Document]:
        return self.session.execute(
            select(Document).where(Document.user_id == user_id).order_by(Document.created_at.desc())
        ).scalars().all()

    def update_status(self, doc_id: UUID, status: str):
        doc = self.get_document_by_id(doc_id, None) # Status updates might be internal, but better to pass user_id
        # Overloading this for simplicity; in a real service we'd pass user_id
        if doc:
            doc.status = status
            self.session.commit()

    def create_chunks(self, chunks: List[DocumentChunk]):
        self.session.add_all(chunks)
        self.session.commit()

    def delete_document(self, doc_id: UUID, user_id: UUID) -> bool:
        doc = self.get_document_by_id(doc_id, user_id)
        if not doc:
            return False

        # Cascade delete handles chunks if configured in model
        self.session.delete(doc)
        self.session.commit()
        return True

    def search_similar_chunks(self, user_id: UUID, query_embedding: List[float], limit: int = 5):
        # This uses pgvector's L2 distance (<->)
        # We join with Document to ensure the chunks belong to the user
        from sqlalchemy import func

        stmt = (
            select(DocumentChunk)
            .join(Document)
            .where(Document.user_id == user_id)
            .order_by(DocumentChunk.embedding.l2_distance(query_embedding))
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()
