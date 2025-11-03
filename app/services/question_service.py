from fastapi import Depends
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.qua import Question
from app.models.user import User, question_voter
from app.schemas.question import QuestionIn


class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_question(self, question_in: QuestionIn, user: User):
        create_question = Question(**question_in.model_dump())
        create_question.author_id = user.id

        self.db.add(create_question)
        await self.db.commit()
        await self.db.refresh(create_question)

        return create_question

    async def get_questions(self, skip: int = 0, limit: int = 10):
        # 1) 전체 건수
        total = await self.db.scalar(
            select(func.count(Question.id))
        )
        total = total or 0

        # 2) 페이징 목록
        query = (
            select(Question)
            .order_by(Question.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        question_list = result.scalars().all()

        return total, question_list  # (전체 건수, 페이징 적용된 질문 목록)

    async def get_question(self, question_id: int):
        query = (select(Question).where(Question.id == question_id))
        result = await self.db.execute(query)
        question = result.scalar_one_or_none()
        return question

    async def update_question(self, question_id: int, question_in: QuestionIn, user: User):
        question = await self.get_question(question_id)
        if question is None:
            return None
        if question.author_id != user.id:
            return False
        question.subject = question_in.subject
        question.content = question_in.content
        await self.db.commit()
        await self.db.refresh(question)
        return question

    async def delete_question(self, question_id: int, user: User):
        question = await self.get_question(question_id)
        if question is None:
            return None
        if question.author_id != user.id:
            return False
        await self.db.delete(question)
        await self.db.commit()
        return True

    async def vote_question(self, question_id: int, user: User):
        question = await self.get_question(question_id)
        if question is None:
            return None
        if question.author_id == user.id:
            return False
        # 2) 이미 투표했는지 확인
        query = select(question_voter.c.user_id).where(
                and_(question_voter.c.question_id == question_id,
                question_voter.c.user_id == user.id)
            )
        result = await self.db.execute(query)
        exists = result.scalar_one_or_none()
        if exists is not None:
            # 이미 투표했다면 아무 것도 하지 않음(또는 에러 반환)
            return None

        # 3) 직접 연결 테이블에 insert (관계 접근 없음 -> MissingGreenlet 회피)
        await self.db.execute(
            question_voter.insert().values(
                question_id=question_id,
                user_id=user.id,
            )
        )

        await self.db.commit()
        await self.db.refresh(question)
        return True

def get_question_service(db: AsyncSession = Depends(get_db)) -> 'QuestionService':
    return QuestionService(db)