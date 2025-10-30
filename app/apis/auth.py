from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

from app.schemas.auth import TokenResponse, LoginRequest
from app.services.auth_service import AuthService, get_auth_service, InvalidPasswordError, UserNotFoundError, EmptyFieldError

router = APIRouter()


ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
SECRET_KEY = "18749f68017fc2e9e38d103892b6f74748d5a8e02986d39aaaa176eaf0718749"
ALGORITHM = "HS256"

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),
          auth_service: AuthService = Depends(get_auth_service)):
    # OAuth2 폼 데이터를 LoginRequest로 변환
    print("login_for_access_token form_data: ", form_data)
    """ # 아래 처럼 수정
    login_data = LoginRequest(
        email=form_data.username,  # 내가 수정: email 이지만 OAuth2PasswordRequestForm이 username으로 받기때문에 임시 방편으로 사용하고 있다.
        password=form_data.password
    )
    
    user = await auth_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="인증 실패",
            headers={"WWW-Authenticate": "Bearer"}
        )
    """
    try:
        login_data = LoginRequest(
            email=form_data.username,  # 내가 수정: email 이지만 OAuth2PasswordRequestForm이 username으로 받기때문에 임시 방편으로 사용하고 있다.
            password=form_data.password
        )
        user = await auth_service.authenticate_user(login_data)
    except EmptyFieldError:
        raise HTTPException(
            status_code=401,
            detail="빈칸을 채워주세요!",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidPasswordError:
        # 비밀번호가 틀린 경우에만 명시적인 메시지
        raise HTTPException(
            status_code=401,
            detail="비밀번호가 일치하지 않습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except UserNotFoundError:
        # 사용자 없음은 일반적인 인증 실패로 응답(정보 노출 방지)
        raise HTTPException(
            status_code=401,
            detail="가입된 이메일이 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # make access token
    data = {
        "sub": user.username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }