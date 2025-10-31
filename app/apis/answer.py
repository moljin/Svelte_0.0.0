from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, UploadFile, File
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas import answer as schema_answer
from app.schemas.answer import AnswerOut
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


@router.get("/detail/{answer_id}", response_model=AnswerOut)
async def get_answer(answer_id: int,
                     answer_service: AnswerService = Depends(get_answer_service)):
    answer = await answer_service.get_answer(answer_id)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글을 찾을 수 없습니다."
        )
    return answer


@router.put("/update/{answer_id}",
            response_model = schema_answer.AnswerOut)
async def update_answer(answer_id: int,
                        answer_in: schema_answer.AnswerIn,
                        answer_service: AnswerService = Depends(get_answer_service),
                        current_user: User = Depends(get_current_user)):
    answer = await answer_service.update_answer(answer_id, answer_in, current_user)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="답변 데이터를 찾을 수 없습니다."
        )
    if answer is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not authorized: 접근 권한이 없습니다."
        )
    # return answer
    # ORM -> Pydantic 변환
    return schema_answer.AnswerOut.model_validate(answer, from_attributes=True)


@router.delete("/delete/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_answer(answer_id: int,
                         answer_service: AnswerService = Depends(get_answer_service),
                         current_user: User = Depends(get_current_user)):
    answer = await answer_service.delete_answer(answer_id, current_user)
    if answer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )
    if answer is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized: 접근 권한이 없습니다."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/vote/{answer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def answer_vote(answer_id: int,
                answer_service: AnswerService = Depends(get_answer_service),
                current_user: User = Depends(get_current_user)):
    answer = await answer_service.get_answer(answer_id)
    if not answer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    await answer_service.vote_answer(answer_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)