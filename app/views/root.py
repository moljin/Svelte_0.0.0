from fastapi import APIRouter, Request, Depends

router = APIRouter()

@router.get("/")
def get_root():
    return {"message": "안녕하세요 파이보 Hello 시작이다."}