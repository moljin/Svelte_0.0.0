from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Integer, String, DateTime, func, Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # String은 제한 글자수를 지정해야 한다.
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


question_voter = Table('question_voter',
                       Base.metadata,
                       Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                       Column('question_id', Integer, ForeignKey('questions.id'), primary_key=True),
                       # 중복 등록 방지(복합 PK로 이미 보장되지만, 이름 있는 제약 예시)
                       UniqueConstraint("user_id", "question_id", name="uq_question_voter")
                       )


answer_voter = Table('answer_voter',
                     Base.metadata,
                     Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
                     Column('answer_id', Integer, ForeignKey('answers.id'), primary_key=True),
                     # 중복 등록 방지(복합 PK로 이미 보장되지만, 이름 있는 제약 예시)
                     UniqueConstraint("user_id", "answer_id", name="uq_answer_voter")
                     )
