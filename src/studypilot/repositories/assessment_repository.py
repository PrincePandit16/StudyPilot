from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from src.studypilot.models.assessment import Quiz, QuizQuestion, QuizAttempt, QuizAnswer
from src.studypilot.schemas.assessment import QuizCreate

class AssessmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_quiz(self, user_id: UUID, title: str, description: Optional[str] = None) -> Quiz:
        quiz = Quiz(user_id=user_id, title=title, description=description)
        self.db.add(quiz)
        await self.db.flush()
        return quiz

    async def create_questions(self, quiz_id: UUID, questions_data: List[dict]) -> List[QuizQuestion]:
        import json
        questions = [
            QuizQuestion(
                quiz_id=quiz_id,
                question_text=q["question_text"],
                question_type="mcq",
                options=json.dumps(q.get("options", [])),
                correct_answer=q["correct_answer"],
                explanation=q.get("explanation"),
                difficulty=q.get("difficulty")
            )
            for q in questions_data
        ]
        self.db.add_all(questions)
        await self.db.flush()
        return questions

    async def get_quiz_with_questions(self, quiz_id: UUID, user_id: UUID) -> Optional[Quiz]:
        stmt = select(Quiz).where(Quiz.id == quiz_id, Quiz.user_id == user_id)
        result = await self.db.execute(stmt)
        quiz = result.scalar_one_or_none()
        if quiz:
            # Lazy load questions if not already joined
            await self.db.refresh(quiz, ["questions"])
        return quiz

    async def list_quizzes_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0) -> List[Quiz]:
        stmt = select(Quiz).where(Quiz.user_id == user_id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_attempt(self, user_id: UUID, quiz_id: UUID) -> QuizAttempt:
        attempt = QuizAttempt(user_id=user_id, quiz_id=quiz_id)
        self.db.add(attempt)
        await self.db.flush()
        return attempt

    async def save_answers(self, attempt_id: UUID, answers_data: List[dict]) -> List[QuizAnswer]:
        answers = [
            QuizAnswer(
                attempt_id=attempt_id,
                question_id=a["question_id"],
                provided_answer=a["provided_answer"],
                is_correct=a["is_correct"]
            )
            for a in answers_data
        ]
        self.db.add_all(answers)
        await self.db.flush()
        return answers

    async def update_attempt_score(self, attempt_id: UUID, score: float, completed_at: datetime) -> QuizAttempt:
        from datetime import datetime
        stmt = update(QuizAttempt).where(QuizAttempt.id == attempt_id).values(
            score=score,
            completed_at=completed_at
        ).returning(QuizAttempt)
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.scalar_one()

    async def get_attempt_by_id(self, attempt_id: UUID, user_id: UUID) -> Optional[QuizAttempt]:
        stmt = select(QuizAttempt).where(QuizAttempt.id == attempt_id, QuizAttempt.user_id == user_id)
        result = await self.db.execute(stmt)
        attempt = result.scalar_one_or_none()
        if attempt:
            await self.db.refresh(attempt, ["answers", "quiz"])
        return attempt

    async def list_attempts_by_user(self, user_id: UUID, limit: int = 10, offset: int = 0) -> List[QuizAttempt]:
        stmt = select(QuizAttempt).where(QuizAttempt.user_id == user_id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()
