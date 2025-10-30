from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserIn
from app.utils.user import get_password_hash


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: UserIn):
        hashed_password = await get_password_hash(user_in.password1)
        db_user = User(
            email=str(user_in.email),
            username=user_in.username,
            password=hashed_password,
        )

        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)

        return db_user

    async def get_user_by_email(self, email: str):
        query = (select(User).where(User.email == email))
        result = await self.db.execute(query)  # await 추가
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str):
        query = (select(User).where(User.username == username))
        result = await self.db.execute(query)  # await 추가
        return result.scalar_one_or_none()

def get_user_service(db: AsyncSession = Depends(get_db)) -> 'UserService':
    return UserService(db)