from datetime import timedelta, datetime, timezone

from fastapi import Depends, HTTPException, status
from jose import jwt
from pydantic_core import PydanticCustomError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.utils.user import verify_password


# 도메인 예외 정의
class EmptyFieldError(Exception):
    pass

class InvalidPasswordError(Exception):
    pass

class UserNotFoundError(Exception):
    pass


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    """
    사용자 인증을 수행합니다.
    """

    async def authenticate_user(self, login_data: LoginRequest):
        # 사용자 조회
        print("login_data: ", login_data)
        print("login_data.email: ", login_data.email)
        if not login_data.email or not login_data.password:
            raise EmptyFieldError()

        query = (
            select(User).
            where(User.email == login_data.email)
        )
        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            # return None
            # 사용자 없음
            raise UserNotFoundError()

        password_ok = await verify_password(login_data.password, str(user.password))
        if not password_ok:
            # return None
            # raise PydanticCustomError를 던지면 Internal Server Error가 터져버린다.
            # raise PydanticCustomError('empty_value', '비밀번호 불일치')
            # 비밀번호 불일치
            raise InvalidPasswordError()

        print("user: ", user)
        return user

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)