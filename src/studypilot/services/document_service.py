import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.studypilot.models.document import Document, DocumentStatus
from src.studypilot.models.document_chunk import DocumentChunk
from src.studypilot.repositories.document_repository import DocumentRepository
from src.studypilot.core.storage.factory import get_storage_provider
from src.studypilot.services.processor import DocumentProcessor
from src.studypilot.services.embedding_service import embedding_service
from src.studypilot.core.worker import worker, DocumentJob, JobAction
import sqlalchemy as sa
from typing import List, BinaryIO
import io

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = DocumentRepository(db)
        self.storage = get_storage_provider()
        self.processor = DocumentProcessor()

    async def upload_document(self, user_id: uuid.UUID, filename: str, file_content: bytes) -> Document:
        # 1. Calculate hash and detect duplicates
        file_hash = self.processor.calculate_hash(file_content)
        existing = self.db.execute(
            sa.select(Document).where(Document.sha256_hash == file_hash, Document.user_id == user_id)
        ).scalar_one_or_none()

        if existing:
            return existing

        # 2. Store physically
        storage_path = f"users/{user_id}/{uuid.uuid4()}_{filename}"
        await self.storage.upload(io.BytesIO(file_content), storage_path)

        # 3. Create DB record
        doc = Document(
            user_id=user_id,
            filename=filename,
            storage_path=storage_path,
            sha256_hash=file_hash,
            status=DocumentStatus.UPLOADED
        )
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)

        # 4. Queue for processing
        await worker.enqueue(DocumentJob(document_id=str(doc.id), action=JobAction.PROCESS))

        return doc

    async def process_document(self, document_id: uuid.UUID):
        doc = self.repo.get_by_id(document_id)
        if not doc:
            return

        try:
            doc.status = DocumentStatus.PROCESSING
            self.db.commit()

            # Download from storage
            file_stream = await self.storage.download(doc.storage_path)

            # Extract and chunk
            import fitz
            with fitz.open(stream=file_stream.read(), filetype="pdf") as doc_pdf:
                pages = []
                for page_num, page in enumerate(doc_pdf, start=1):
                    from src.studypilot.services.processor import ExtractedPage
                    pages.append(ExtractedPage(page_number=page_num, text=page.get_text("text")))

            chunks_data = self.processor.chunk_text(pages)

            # Generate embeddings for all chunks in batch
            texts_to_embed = [content for _, _, content in chunks_data]
            embeddings = embedding_service.generate_embeddings_batch(texts_to_embed)

            # Clear old chunks (idempotency)
            self.db.execute(sa.delete(DocumentChunk).where(DocumentChunk.document_id == doc.id))

            # Store new chunks
            for i, (page_num, chunk_idx, content) in enumerate(chunks_data):
                chunk = DocumentChunk(
                    document_id=doc.id,
                    content=content,
                    content_hash=self.processor.calculate_hash(content.encode()),
                    page_number=page_num,
                    chunk_index=chunk_idx,
                    embedding=embeddings[i]
                )
                self.db.add(chunk)

            doc.status = DocumentStatus.READY
            self.db.commit()
        except Exception as e:
            doc.status = DocumentStatus.FAILED
            self.db.commit()
            raise e

    async def delete_document(self, user_id: uuid.UUID, document_id: uuid.UUID) -> bool:
        doc = self.repo.get_by_id(document_id)
        if not doc or doc.user_id != user_id:
            return False

        await self.storage.delete(doc.storage_path)
        self.repo.delete(document_id)
        return True

    async def reindex_document(self, document_id: uuid.UUID):
        """Clears embeddings and regenerates them for a document."""
        await self.process_document(document_id)
