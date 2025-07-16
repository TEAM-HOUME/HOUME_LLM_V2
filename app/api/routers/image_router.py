# app/api/routers/image_router.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, conlist
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.db.session import get_db
from app.models.enums import Equilibrium
from app.services.image_service import build_and_generate_image

router = APIRouter(prefix="/images", tags=["Image"])   # ← 중복 import 제거

class PromptFurnitureListDTO(BaseModel):
    furnitureIds: conlist(int, min_length=1)

# 요청 DTO
class ImageRequest(BaseModel):
    floorPlanId: int
    tasteId: int
    equilibrium: Equilibrium
    promptFurnitureListDTO: PromptFurnitureListDTO        # ← v1: min_items

@router.post("", response_class=JSONResponse)
async def create_image(
    body: ImageRequest,
    db: AsyncSession = Depends(get_db),
):
    return await build_and_generate_image(  # image_service의 함수 호출
        db=db,
        floor_plan_id=body.floorPlanId,
        equilibrium=body.equilibrium,
        taste_id=body.tasteId,
        furniture_ids=body.promptFurnitureListDTO.furnitureIds,
    )