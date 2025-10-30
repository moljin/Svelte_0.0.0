from fastapi import APIRouter, Request, Depends

router = APIRouter()

@router.get("/")
def get_root():
    """svelte 프론트엔드 단에서는 Home.svelte ("/") 으로 가게 변경함"""
    return {"message": "안녕하세요 파이보 Hello 시작이다."}