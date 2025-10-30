from datetime import datetime

from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
from pydantic_core import PydanticCustomError
from pydantic_core.core_schema import FieldValidationInfo

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserOrm(UserBase):
    id: int

class UserIn(UserBase):
    password1: str
    password2: str

    @field_validator('username', 'password1', 'password2', 'email')
    def not_empty(cls, v):
        if not v or not v.strip():
            # raise ValueError('빈 값은 허용되지 않습니다.')
            # 접두사 없이 메시지 그대로 내려감
            raise PydanticCustomError('empty_value', '빈 값은 허용되지 않습니다.')
        return v

    @field_validator('password2')
    def passwords_match(cls, v, info: FieldValidationInfo):
        if 'password1' in info.data and v != info.data['password1']:
            # raise ValueError('비밀번호가 일치하지 않습니다')
            # 접두사 없이 메시지 그대로 내려감
            raise PydanticCustomError('empty_value', '비밀번호가 일치하지 않습니다.')
        return v

class UserOut(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)