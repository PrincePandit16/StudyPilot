import json
import logging
from uuid import UUID
from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.studypilot.repositories.assessment_repository import AssessmentRepository
from src.studypilot.schemas.assessment import (
    QuizGenerateRequest, QuizPublicSchema, QuestionPublicSchema,
    QuizAttemptSubmitRequest, AttemptResult, AttemptReviewSchema,
    AnswerReview, QuizAttemptResponse
)
from src.studypilot.core.llm.prompts import StudyPrompts
from src.studypilot.core.llm.provider import get_llm_provider
from src.studypilot.services.document_service import DocumentService

logger = logging.getLogger(__name__)

class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AssessmentRepository(db)
        self.doc_service = DocumentService(db)

    async def generate_quiz(self, user_id: UUID, request: QuizGenerateRequest) -> QuizPublicSchema:
        # 1. Context Retrieval
        texts = []
        for doc_id in request.document_ids:
            doc = await self.doc_service.get_document(doc_id)
            if doc:
                texts.append(doc.content)

        context_text = "\n\n".join(texts)
        if request.topic:
            context_text = f"Focus on the topic: {request.topic}\n\n{context_text}"

        # 2. LLM Call
        llm = get_llm_provider()
        prompt = StudyPrompts.QUIZ_GEN
        formatted_user_prompt = prompt.user_template.format(
            text=context_text,
            count=request.count,
            difficulty=request.difficulty
        )

        response = await llm.generate(prompt.system_prompt, formatted_user_prompt)

        try:
            # Assume response is a JSON string or wrapped in markdown
            clean_json = response.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json.split("```json")[1].split("```")[0].strip()
            elif clean_json.startswith("```"):
                clean_json = clean_json.split("```")[1].split("```")[0].strip()

            questions_data = json.loads(clean_json)
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse LLM quiz response: {e}")
            raise ValueError("The AI generated an invalid quiz format. Please try again.")

        # 3. Validation
        validated_questions = []
        for q in questions_data:
            if not all(k in q for k in ("question_text", "options", "correct_answer")):
                continue

            # Ensure correct answer is one of the options
            if q["correct_answer"] not in q["options"]:
                logger.warning(f"Correct answer {q['correct_answer']} not in options {q['options']}")
                continue

            validated_questions.append(q)

        if len(validated_questions) == 0:
            raise ValueError("No valid questions could be generated from the content.")

        # 4. Persistence
        title = f"Quiz on {request.topic or 'Documents'}"
        quiz = await self.repo.create_quiz(user_id, title, f"Generated {request.difficulty} quiz")
        await self.repo.create_questions(quiz.id, validated_questions)

        # Return as public schema
        return await self.get_quiz_public(user_id, quiz.id)

    async def start_attempt(self, user_id: UUID, quiz_id: UUID) -> QuizAttemptResponse:
        quiz = await self.repo.get_quiz_with_questions(quiz_id, user_id)
        if not quiz:
            raise ValueError("Quiz not found or access denied.")

        attempt = await self.repo.create_attempt(user_id, quiz_id)
        return QuizAttemptResponse(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=None,
            started_at=attempt.started_at,
            completed_at=None
        )

    async def submit_attempt(self, user_id: UUID, attempt_id: UUID, request: QuizAttemptSubmitRequest) -> AttemptResult:
        attempt = await self.repo.get_attempt_by_id(attempt_id, user_id)
        if not attempt:
            raise ValueError("Attempt not found.")
        if attempt.completed_at:
            raise ValueError("This attempt has already been submitted.")

        # Get the quiz questions
        quiz = await self.repo.get_quiz_with_questions(attempt.quiz_id, user_id)
        if not quiz:
            raise ValueError("Quiz not found.")

        questions_map = {q.id: q for q in quiz.questions}
        correct_count = 0
        answers_to_save = []

        for sub in request.answers:
            q = questions_map.get(sub.question_id)
            if not q:
                continue

            is_correct = sub.provided_answer == q.correct_answer
            if is_correct:
                correct_count += 1

            answers_to_save.append({
                "question_id": q.id,
                "provided_answer": sub.provided_answer,
                "is_correct": is_correct
            })

        # Calculate score
        total = len(quiz.questions)
        score = (correct_count / total * 100) if total > 0 else 0.0

        # Save results
        await self.repo.save_answers(attempt_id, answers_to_save)
        await self.repo.update_attempt_score(attempt_id, score, datetime.utcnow())

        return AttemptResult(
            attempt_id=attempt_id,
            score=score,
            total_questions=total,
            correct_count=correct_count,
            completed_at=datetime.utcnow()
        )

    async def get_quiz_public(self, user_id: UUID, quiz_id: UUID) -> QuizPublicSchema:
        import json
        quiz = await self.repo.get_quiz_with_questions(quiz_id, user_id)
        if not quiz:
            raise ValueError("Quiz not found.")

        questions = [
            QuestionPublicSchema(
                id=q.id,
                question_text=q.question_text,
                options=json.loads(q.options) if q.options else [],
                difficulty=q.difficulty or "medium"
            )
            for q in quiz.questions
        ]

        return QuizPublicSchema(
            id=quiz.id,
            title=quiz.title,
            description=quiz.description,
            questions=questions
        )

    async def get_attempt_review(self, user_id: UUID, attempt_id: UUID) -> AttemptReviewSchema:
        attempt = await self.repo.get_attempt_by_id(attempt_id, user_id)
        if not attempt:
            raise ValueError("Attempt not found.")

        review_answers = []
        for ans in attempt.answers:
            # Use a join or fetch the question
            # For simplicity, fetching from DB here
            from sqlalchemy import select
            from src.studypilot.models.assessment import QuizQuestion
            stmt = select(QuizQuestion).where(QuizQuestion.id == ans.question_id)
            res = await self.db.execute(stmt)
            q = res.scalar_one()

            review_answers.append(AnswerReview(
                question_text=q.question_text,
                provided_answer=ans.provided_answer,
                correct_answer=q.correct_answer,
                is_correct=ans.is_correct,
                explanation=q.explanation
            ))

        return AttemptReviewSchema(
            attempt_id=attempt.id,
            score=attempt.score or 0.0,
            answers=review_answers,
            completed_at=attempt.completed_at or datetime.utcnow()
        )
