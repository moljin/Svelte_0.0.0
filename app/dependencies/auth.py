from typing import Optional, Set

from fastapi import Depends, HTTPException, Request, status, Response, Security

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.apis.auth import SECRET_KEY, ALGORITHM
from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService, get_auth_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/apis/auth/login")

"""
토큰에서 현재 사용자 정보를 가져오는 의존성 함수
"""

async def get_current_user(
        request: Request, response: Response,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증되지 않은 사용자입니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    else:
        query = (select(User).where(User.username == username))
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="사용자를 찾을 수 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


async def get_optional_current_user(request: Request, response: Response,
                                    db: AsyncSession = Depends(get_db)) -> Optional[User]:
    """
    인증 토큰이 없거나 유효하지 않은 경우 None을 반환하고, 다른 예외는 그대로 전달합니다.
    AI Chat:
        - 익명 접근을 허용하는 엔드포인트에서는 Depends(get_optional_current_user)를 사용하세요.
            이것을 적용하고 if current_user is None or current_user != user 로 분기하여 "Not authorized: 접근권한이 없습니다."로 raise 날려도 된다.
            그러면, Depends(get_current_user) 주입해서, "Not authenticated: 로그인하지 않았습니다."를 raise 날리는 것과 효과가 같다.
            효과는 같지만, 엄밀한 의미에서는 다르다.
        - 인증이 반드시 필요한 엔드포인트는 기존처럼 Depends(get_current_user)를 유지하면 됩니다.
    """
    try:
        # 핵심: get_current_user를 직접 호출하되, db를 명시적으로 전달
        return await get_current_user(request=request, response=response, db=db)
    except HTTPException as e:
        if e.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            return None
        raise
