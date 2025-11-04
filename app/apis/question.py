from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Form, UploadFile, File, Query
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas import question as schema_question
from app.schemas.question import QuestionOut
from app.services.question_service import QuestionService, get_question_service

router = APIRouter()

@router.post("/post", response_model=schema_question.QuestionOut,)
async def question_create(question_in: schema_question.QuestionIn,
                          question_service: QuestionService = Depends(get_question_service),
                          current_user: User = Depends(get_current_user)) -> schema_question.QuestionOut:
    created_question = await question_service.create_question(question_in, current_user)
    return created_question # ORM 객체를 그대로 반환해도 Pydantic이 변환해 줍니다.


@router.get("/all", response_model=schema_question.QuestionList)
async def question_all(question_service: QuestionService = Depends(get_question_service),
                       page: int = Query(0, ge=0),
                       size: int = Query(10, gt=0),
                       response: Response = None,
                       keyword: str | None = None
                       ) -> dict:
    total, question_list = await question_service.get_questions(skip=page * size, limit=size, keyword=keyword)
    if question_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="등록된 게시물이 없습니다."
        )

    return {
        'total': total,
        'question_list': question_list
    }


@router.get("/detail/{question_id}", response_model=QuestionOut)
async def get_question(question_id: int,
                      question_service: QuestionService = Depends(get_question_service)):
    question = await question_service.get_question(question_id)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 게시글을 찾을 수 없습니다."
        )
    return question


@router.put("/update/{question_id}",
            response_model=schema_question.QuestionOut,
            # 각 answer의 question 필드를 제외하여 순환 제거
            response_model_exclude={'answers_all': {'__all__': {'question'}}},
            )
async def update_question(question_id: int,
                          question_in: schema_question.QuestionIn,
                          question_service: QuestionService = Depends(get_question_service),
                          current_user: User = Depends(get_current_user)):
    """ Swagger Docs 에서
        RecursionError: maximum recursion depth exceeded 에러 발생하여 아래처럼 수정했다.
            - 빠르게 우회(스키마 변경 없이): 응답에서 역참조 제외
            - update 응답에서 answers_all 안의 question 필드를 제외

            response_model=schema_question.QuestionOut,
            # 각 answer의 question 필드를 제외하여 순환 제거
            response_model_exclude={'answers_all': {'__all__': {'question'}}},
    """
    question = await question_service.update_question(question_id, question_in, current_user)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="질문 데이터를 찾을 수 없습니다."
        )
    if question is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not authorized: 접근 권한이 없습니다."
        )
    return question


@router.delete("/delete/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(question_id: int,
                         question_service: QuestionService = Depends(get_question_service),
                         current_user: User = Depends(get_current_user)):
    question = await question_service.delete_question(question_id, current_user)
    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="게시글을 찾을 수 없습니다."
        )
    if question is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized: 접근 권한이 없습니다."
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/vote/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def question_vote(question_id: int,
                  question_service: QuestionService = Depends(get_question_service),
                  current_user: User = Depends(get_current_user)):
    question = await question_service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을수 없습니다.")
    await question_service.vote_question(question_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)