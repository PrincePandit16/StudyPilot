from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from datetime import datetime

# --- Quiz Generation Schemas ---

class QuizGenerateRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Optional topic to focus the quiz on")
    document_ids: List[UUID] = Field(..., description="List of documents to use as context")
    count: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    difficulty: str = Field("medium", pattern="^(easy|medium|hard)$", description="Difficulty level")

class QuizCreate(BaseModel):
    title: str
    description: Optional[str] = None

# --- Quiz Response Schemas ---

class QuestionPublicSchema(BaseModel):
    id: UUID
    question_text: str
    options: List[str]
    difficulty: str

class QuizPublicSchema(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    questions: List[QuestionPublicSchema]

# --- Attempt Schemas ---

class AnswerSubmission(BaseModel):
    question_id: UUID
    provided_answer: str

class QuizAttemptSubmitRequest(BaseModel):
    answers: List[AnswerSubmission]

class AttemptResult(BaseModel):
    attempt_id: UUID
    score: float
    total_questions: int
    correct_count: int
    completed_at: datetime

class AnswerReview(BaseModel):
    question_text: str
    provided_answer: str
    correct_answer: str
    is_correct: bool
    explanation: Optional[str]

class AttemptReviewSchema(BaseModel):
    attempt_id: UUID
    score: float
    answers: List[AnswerReview]
    completed_at: datetime

class QuizAttemptResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    score: Optional[float]
    started_at: datetime
    completed_at: Optional[datetime]
