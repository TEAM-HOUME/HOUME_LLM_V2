# app/api/routers/image_router.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, conlist
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.enums import Equilibrium
from app.services.image_service import build_and_generate_image

router = APIRouter(prefix="/images", tags=["Image"])   # ← 중복 import 제거

class ImageRequest(BaseModel):
    floor_plan_id: int
    equilibrium: Equilibrium
    taste_id: int
    furniture_ids: conlist(int, min_length=1)            # ← v1: min_items

@router.post("/", response_class=StreamingResponse)
async def create_image(
    body: ImageRequest,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return await build_and_generate_image(
        db=db,
        floor_plan_id=body.floor_plan_id,
        equilibrium=body.equilibrium,
        taste_id=body.taste_id,
        furniture_ids=body.furniture_ids,
    )
