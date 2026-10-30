from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.studypilot.api.auth import get_current_user
from src.studypilot.core.dependencies import get_db
from src.studypilot.services.tutor_service import TutorService
from src.studypilot.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/conversations", tags=["Tutor"])

class ConversationCreate(BaseModel):
    title: str

class MessageSend(BaseModel):
    message: str
    document_ids: Optional[List[UUID]] = None

@router.post("", status_code=201)
async def create_conversation(
    payload: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TutorService(db)
    return await service.create_conversation(current_user.id, payload.title)

@router.get("")
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TutorService(db)
    return await service.list_conversations(current_user.id)

@router.get("/{conv_id}")
async def get_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TutorService(db)
    conv = await service.get_conversation(conv_id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv

@router.get("/{conv_id}/messages")
async def get_messages(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TutorService(db)
    try:
        return await service.get_messages(conv_id, current_user.id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.post("/{conv_id}/messages")
async def send_message(
    conv_id: UUID,
    payload: MessageSend,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TutorService(db)
    try:
        return await service.send_message(
            user_id=current_user.id,
            conv_id=conv_id,
            message=payload.message,
            document_ids=payload.document_ids
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{conv_id}", status_code=204)
async def delete_conversation(
    conv_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = TutorService(db)
    success = await service.delete_conversation(conv_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return None
