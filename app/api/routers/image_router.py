# app/api/routers/image_router.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, conlist
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from app.db.session import get_db
from app.models.enums import Equilibrium
from app.services.image_service import build_image_chain

router = APIRouter(prefix="/images", tags=["Image"])   # ← 중복 import 제거

class PromptFurnitureListDTO(BaseModel):
    furnitureTagIds: conlist(int, min_length=1)  # ← 변경됨

class ImageRequest(BaseModel):
    floorPlanId: int
    tagId: int                                   # ← tasteId → tagId
    equilibrium: Equilibrium
    promptFurnitureListDTO: PromptFurnitureListDTO

@router.post("", response_class=JSONResponse)
async def create_image(
    body: ImageRequest,
    db: AsyncSession = Depends(get_db),
):
    return await build_image_chain(
        db=db,
        floor_plan_id=body.floorPlanId,
        equilibrium=body.equilibrium,
        tag_id=body.tagId,  # ← taste_id → tag_id
        furniture_tag_ids=body.promptFurnitureListDTO.furnitureTagIds  # ←
    )
