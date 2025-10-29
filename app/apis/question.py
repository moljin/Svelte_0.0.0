from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, UploadFile, File
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import question as schema_question
from app.services.question_service import QuestionService, get_question_service

router = APIRouter()

@router.post("/post", response_model=schema_question.QuestionOut,)
async def question_create(question_in: schema_question.QuestionIn,
                          question_service: QuestionService = Depends(get_question_service)) -> schema_question.QuestionOut:
    created_question = await question_service.create_question(question_in)
    return created_question # ORM 객체를 그대로 반환해도 Pydantic이 변환해 줍니다.


@router.get("/all", response_model=list[schema_question.QuestionOut])
async def question_all(question_service: QuestionService = Depends(get_question_service)) -> schema_question.QuestionOut:
    questions = await question_service.get_questions()
    if questions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 게시물이 없습니다."
        )
    return questions


@router.get("/detail/{question_id}")
async def get_question(question_id: int,
                      question_service: QuestionService = Depends(get_question_service)):
    question = await question_service.get_question(question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글을 찾을 수 없습니다."
        )
    return question