from datetime import datetime

from pydantic import BaseModel, field_validator, ConfigDict
from pydantic_core import PydanticCustomError

from app.schemas.answer import AnswerOut
from app.schemas.user import UserOrm


class QuestionIn(BaseModel):
    subject: str
    content: str

    @field_validator('subject', 'content')
    def not_empty(cls, v):
        if not v or not v.strip():
            # 'msg': 'Value error, 빈 값은 허용되지 않습니다.' 이렇게 프론트로 넘어간다.
            # raise ValueError('빈 값은 허용되지 않습니다.')
            # 접두사 없이 메시지 그대로 내려감
            raise PydanticCustomError('empty_value', '빈 값은 허용되지 않습니다.')
        return v


class QuestionOut(BaseModel):
    id: int
    subject: str | None = None
    content: str | None = None
    created_at: datetime
    updated_at: datetime
    answers_all: list[AnswerOut] = []
    author: UserOrm | None
    model_config = ConfigDict(from_attributes=True)

class QuestionList(BaseModel):
    total: int = 0
    question_list: list[QuestionOut] = []

    '''
    Answer 모델은 Question 모델과 answers_all 라는 이름으로 연결되어 있다. 
    Answer 모델에 Queston 모델을 연결할 때 backref="answers_all" 속성을 지정했기 때문이다. 
    따라서 Question 스키마에도 answers_all 이라는 이름의 속성을 사용해야 등록된 답변들이 정확하게 매핑된다. 
    만약 answers_all 대신 다른 이름을 사용한다면 값이 채워지지 않을 것이다.
    '''

    """
    - model_config = ConfigDict(from_attributes=True)의 의미
        - Pydantic v2 방식입니다.
        - 딕셔너리(dict) 같은 매핑 타입뿐 아니라, ORM 인스턴스나 일반 파이썬 객체처럼 “속성 접근”으로 값을 꺼내는 객체로부터 모델을 생성/검증하도록 허용합니다.
        - 즉, SQLAlchemy 모델 인스턴스 같은 객체를 QuestionOut.model_validate(obj)로 바로 검증/직렬화할 수 있게 해줍니다.

    - class Config: orm_mode = True는 올바른가?
        - Pydantic v1에서 쓰던 방식으로, v2에서는 권장되지 않으며 무시되거나 동작하지 않습니다.
        - v2에서는 model_config = ConfigDict(from_attributes=True)로 대체해야 합니다.
    """