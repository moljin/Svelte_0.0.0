from fastapi import APIRouter, status, Depends, HTTPException

from app.schemas import user as schema_user
from app.services.user_service import UserService, get_user_service

router = APIRouter()

@router.post("/register",
             response_model=schema_user.UserOut,)
async def register_user(user_in: schema_user.UserIn,
                        user_service: UserService = Depends(get_user_service)):
    """입력값이 채워지지 않으면, js단에서 처리한다. 입력값이 채워져야 여기로 진입한다."""
    existed_username = await user_service.get_user_by_username(user_in.username)
    if existed_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 사용자 닉네임입니다."
        )

    existed_user_email = await user_service.get_user_by_email(str(user_in.email))
    if existed_user_email:
        print(f"Registration failed: Email already exists - {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 존재하는 이메일입니다.",
        )

    created_user = await user_service.create_user(user_in)

    return created_user