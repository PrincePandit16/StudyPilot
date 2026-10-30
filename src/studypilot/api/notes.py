from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.studypilot.api.auth import get_current_user
from src.studypilot.core.dependencies import get_db
from src.studypilot.services.note_service import NoteService
from src.studypilot.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/notes", tags=["Smart Notes"])

class NoteGenerateRequest(BaseModel):
    document_ids: List[UUID]

@router.post("/generate")
async def generate_notes(
    payload: NoteGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)
    result = await service.generate_smart_notes(current_user.id, payload.document_ids)
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result

@router.get("")
async def list_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)
    return await service.list_notes(current_user.id)

@router.get("/{note_id}")
async def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)
    note = await service.get_note(note_id, current_user.id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)
    success = await service.delete_note(note_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None

@router.get("/{note_id}/export")
async def export_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = NoteService(db)
    try:
        markdown = await service.export_as_markdown(note_id, current_user.id)
        return Response(content=markdown, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=note.md"})
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
