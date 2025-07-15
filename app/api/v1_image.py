from fastapi import APIRouter, Body
from app.services.image_service import generate_image_with_rag

router = APIRouter(prefix="/images", tags=["Image"])

@router.post("/generate")
async def generate_image(prompt: str = Body(..., embed=True)):
    """
    prompt: 유저 입력 문장
    returns: PNG 스트림
    """
    return await generate_image_with_rag(prompt)
