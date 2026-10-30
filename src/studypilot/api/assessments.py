from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List

from src.studypilot.core.dependencies import get_db, get_current_user
from src.studypilot.services.assessment_service import AssessmentService
from src.studypilot.schemas.assessment import (
    QuizGenerateRequest, QuizPublicSchema,
    QuizAttemptSubmitRequest, AttemptResult,
    AttemptReviewSchema, QuizAttemptResponse,
    QuizAttemptResponse as AttemptSchema
)
from src.studypilot.models.user import User

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])

@router.post("/generate", response_model=QuizPublicSchema)
async def generate_quiz(
    request: QuizGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate a new quiz based on documents and topic."""
    try:
        service = AssessmentService(db)
        return await service.generate_quiz(current_user.id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[QuizAttemptResponse]) # Should be QuizPublicSchema or similar
async def list_quizzes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all quizzes owned by the user."""
    from src.studypilot.repositories.assessment_repository import AssessmentRepository
    repo = AssessmentRepository(db)
    quizzes = await repo.list_quizzes_by_user(current_user.id)
    # Map to a simple schema
    return quizzes

@router.get("/{id}", response_model=QuizPublicSchema)
async def get_quiz(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get quiz details (without correct answers)."""
    try:
        service = AssessmentService(db)
        return await service.get_quiz_public(current_user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{id}/attempts", response_model=QuizAttemptResponse)
async def start_attempt(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Start a new quiz attempt."""
    try:
        service = AssessmentService(db)
        return await service.start_attempt(current_user.id, id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{id}/attempts/submit", response_model=AttemptResult)
async def submit_attempt(
    id: UUID,
    attempt_id: UUID,
    request: QuizAttemptSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit answers for a quiz attempt."""
    try:
        service = AssessmentService(db)
        return await service.submit_attempt(current_user.id, attempt_id, request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/attempts/{attempt_id}/review", response_model=AttemptReviewSchema)
async def review_attempt(
    attempt_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Review a completed quiz attempt."""
    try:
        service = AssessmentService(db)
        return await service.get_attempt_review(current_user.id, attempt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
