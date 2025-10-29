import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_ENV = "development"
# APP_ENV = "production"
APP_NAME = "Svelte_FastAPI"
APP_VERSION = "0.0.0"
APP_DESCRIPTION = "JumpToFastAPI_Svelte을 재현한 프로젝트"

""" DEBUG MODE
개발 과정: true
배포 시: false
"""

PRESENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = Path(__file__).resolve().parent.parent
print("APP_DIR: ", APP_DIR)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent  ## root폴더
print("ROOT_DIR: ", ROOT_DIR)

ENV_PATH = os.path.join(ROOT_DIR, ".env")

ORIGINS = [
    # 아래 두개는 별개로 인식한다. 둘다 필요하다.
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]