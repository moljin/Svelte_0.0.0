from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.qua import Question
from app.schemas.question import QuestionIn


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(self, question_in: QuestionIn):
        create_question = Question(**question_in.model_dump())

        self.db.add(create_question)
        await self.db.commit()
        await self.db.refresh(create_question)

        return create_question

    async def get_questions(self):
        query = (select(Question).order_by(Question.created_at.desc()))
        result = await self.db.execute(query)
        created_desc_questions = result.scalars().all()
        return created_desc_questions

    async def get_question(self, question_id: int):
        query = (select(Question).where(Question.id == question_id))
        result = await self.db.execute(query)
        question = result.scalar_one_or_none()
        return question

def get_question_service(db: AsyncSession = Depends(get_db)) -> 'QuestionService':
    return QuestionService(db)