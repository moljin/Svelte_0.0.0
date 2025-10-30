from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, UploadFile, File
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas import answer as schema_answer
from app.services.answer_service import AnswerService, get_answer_service
from app.services.question_service import QuestionService, get_question_service

router = APIRouter()

@router.post("/post/{question_id}", response_model=schema_answer.AnswerOut,)
async def answer_create(question_id: int,
                        answer_in: schema_answer.AnswerIn,
                        question_service: QuestionService = Depends(get_question_service),
                        answer_service: AnswerService = Depends(get_answer_service),
                        current_user: User = Depends(get_current_user)) -> schema_answer.AnswerOut:
    question = await question_service.get_question(question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 질문을 찾을 수 없습니다."
        )
    created_answer = await answer_service.create_answer(question, answer_in, current_user)
    return created_answer # ORM 객체를 그대로 반환해도 Pydantic이 변환해 줍니다.