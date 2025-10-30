import asyncio
from passlib.context import CryptContext
""" 아래의 순서대로, 
pip install "bcrypt==4.0.1"  # 반드시 bcrypt==4.0.1로 설치해야 한다.
pip install "passlib[bcrypt]"
"""

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 미리 컴파일된 정규식 (알파벳, 숫자, 특수문자 포함 9~50자)
# PASSWORD_REGEX = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[!@#$%^&*?_=+-])[A-Za-z\d!@#$%^&*?_=+-]{9,50}$")

async def get_password_hash(password: str) -> str:
    # CPU 바운드 작업: 스레드 풀로 오프로드
    return await asyncio.to_thread(pwd_context.hash, password)

async def verify_password(plain_password: str, hashed_password: str) -> bool:
    # CPU 바운드 작업: 스레드 풀로 오프로드
    return await asyncio.to_thread(pwd_context.verify, plain_password, hashed_password)