from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref, Mapped, mapped_column

from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(100), nullable=False) # String은 제한 글자수를 지정해야 한다.
    content: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

"""
    id = Column(Integer, primary_key=True)
    subject = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
"""

class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    question_id: Mapped[int] = mapped_column(Integer, ForeignKey("questions.id", name="fk_question_id", ondelete='CASCADE'), nullable=False)
    # author_id가 nullable=True 이므로 Optional["User"]가 일관됩니다.
    question: Mapped["Question"] = relationship("Question", backref=backref("answers_all",
                                                                  lazy="selectin",
                                                                  cascade="all, delete-orphan",
                                                                  passive_deletes=True), lazy="selectin")
    '''
    question 속성은 답변 모델에서 질문 모델을 참조하기 위해 추가했다. 
    위와 같이 relationship으로 question 속성을 생성하면 답변 객체(예: answer)에서 연결된 질문의 제목을 answer.question.subject 처럼 참조할 수 있다.

    relationship의 첫 번째 파라미터는 참조할 모델명이고 두 번째 backref 파라미터는 역참조 설정이다. 역참조란 쉽게 말해 질문에서 답변을 거꾸로 참조하는 것을 의미한다. 
    한 질문에는 여러 개의 답변이 달릴 수 있는데 역참조는 이 질문에 달린 답변들을 참조할 수 있게 한다. 
    예를 들어 어떤 질문에 해당하는 객체가 a_question이라면 a_question.answers_all와 같은 코드로 해당 질문에 달린 답변들을 참조할 수 있다.
    '''
"""
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    question_id = Column(Integer, ForeignKey("questions.id", name="fk_question_id", ondelete='CASCADE'), nullable=False)
    question = relationship("Question", backref=backref("answers",
                                                                  lazy="selectin",
                                                                  cascade="all, delete-orphan",
                                                                  passive_deletes=True), lazy="selectin")
"""

'''
SQLAlchemy 2.0 이상을 사용한다면 첫 번째 스타일(Mapped + mapped_column, 타입 힌트 기반)을 사용하는 것이 더 좋습니다. 
새 프로젝트나 점진적 마이그레이션 모두에 권장되는 방식이며, IDE 지원과 정적 타입 검사에서 이점이 큽니다. 
기존 1.x 스타일(Column 기반)도 동작하지만, 2.0 가이드와 예제는 대부분 Mapped 방식으로 제공됩니다.

왜 첫 번째 스타일이 더 좋은가
- 정적 타입 안전성: Mapped[T]와 relationship 타입 힌트가 mypy/pyright 등과 잘 통합되어, nullable/optional, 관계 타입 등을 컴파일 단계에서 검증할 수 있습니다.
- 2.0 API 일관성: mapped_column/Declarative Base 기반의 2.0 스타일은 최신 문서/기능과 일치합니다. 팀원/미래의 유지보수자가 이해하기 쉽습니다.
- 관계 모델의 명확성: relationship의 타입이 명확해지고, back_populates와 함께 쓰면 양방향 매핑도 안전하게 표현됩니다.
- IDE 지원 향상: 속성 자동완성, 오류 탐지 등 개발 경험이 좋아집니다.
'''