from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.qua import Answer, Question
from app.models.user import User, answer_voter
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

    async def get_answer(self, answer_id: int):
        query = (select(Answer).where(Answer.id == answer_id))
        result = await self.db.execute(query)
        answer = result.scalar_one_or_none()
        return answer

    async def update_answer(self, answer_id: int, answer_in: AnswerIn, user: User):
        answer = await self.get_answer(answer_id)
        if answer is None:
            return None
        if answer.author_id != user.id:
            return False
        answer.content = answer_in.content
        await self.db.commit()
        await self.db.refresh(answer)
        return answer

    async def delete_answer(self, answer_id: int, user: User):
        answer = await self.get_answer(answer_id)
        if answer is None:
            return None
        if answer.author_id != user.id:
            return False
        await self.db.delete(answer)
        await self.db.commit()
        return True

    async def vote_answer(self, answer_id: int, user: User):
        answer = await self.get_answer(answer_id)
        if answer is None:
            return None
        if answer.author_id == user.id:
            return False
        # 2) 이미 투표했는지 확인

        query = select(answer_voter.c.user_id).where(
                and_(answer_voter.c.answer_id == answer_id,
                     answer_voter.c.user_id == user.id)
            )
        result = await self.db.execute(query)
        exists = result.scalar_one_or_none()
        if exists is not None:
            # 이미 투표했다면 아무 것도 하지 않음(또는 에러 반환)
            return None

        # 3) 직접 연결 테이블에 insert (관계 접근 없음 -> MissingGreenlet 회피)
        await self.db.execute(
            answer_voter.insert().values(
                answer_id=answer_id,
                user_id=user.id,
            )
        )
        await self.db.commit()
        await self.db.refresh(answer)
        return True

def get_answer_service(db: AsyncSession = Depends(get_db)) -> 'AnswerService':
    return AnswerService(db)