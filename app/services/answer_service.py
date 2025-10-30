from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.qua import Answer, Question
from app.models.user import User
from app.schemas.answer import AnswerIn


class AnswerService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_answer(self, question: Question, answer_in: AnswerIn, user: User):
        create_answer = Answer(**answer_in.model_dump())
        create_answer.question_id = question.id
        create_answer.author_id = user.id

        self.db.add(create_answer)
        await self.db.commit()
        await self.db.refresh(create_answer)

        return create_answer

def get_answer_service(db: AsyncSession = Depends(get_db)) -> 'AnswerService':
    return AnswerService(db)