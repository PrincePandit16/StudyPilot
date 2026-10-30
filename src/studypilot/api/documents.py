from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from src.studypilot.core.database import get_db
from src.studypilot.core.dependencies import get_current_user
from src.studypilot.services.document_service import DocumentService
from src.studypilot.models.document import Document, DocumentStatus
from src.studypilot.models.user import User
import uuid

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.post("/", response_model=None) # Use a proper schema in production
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.content_type == "application/pdf":
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Only PDFs are allowed")

    # Max size check (e.g., 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large")

    service = DocumentService(db)
    doc = await service.upload_document(current_user.id, file.filename, content)
    return {"document_id": doc.id, "status": doc.status}

@router.get("/", response_model=None)
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Use repository to list documents for user
    from src.studypilot.repositories.document_repository import DocumentRepository
    repo = DocumentRepository(db)
    # Assume repo has get_all_by_user
    return repo.get_all_by_user(current_user.id)

@router.get("/{id}", response_model=None)
async def get_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from src.studypilot.repositories.document_repository import DocumentRepository
    repo = DocumentRepository(db)
    doc = repo.get_by_id(id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return doc

@router.get("/{id}/status", response_model=None)
async def get_document_status(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from src.studypilot.repositories.document_repository import DocumentRepository
    repo = DocumentRepository(db)
    doc = repo.get_by_id(id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return {"status": doc.status}

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = DocumentService(db)
    if not await service.delete_document(current_user.id, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return None

@router.post("/{id}/reprocess")
async def reprocess_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from src.studypilot.repositories.document_repository import DocumentRepository
    repo = DocumentRepository(db)
    doc = repo.get_by_id(id)
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    from src.studypilot.core.worker import worker, DocumentJob, JobAction
    await worker.enqueue(DocumentJob(document_id=str(doc.id), action=JobAction.PROCESS))
    return {"detail": "Reprocessing queued"}
