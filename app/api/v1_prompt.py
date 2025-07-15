# app/api/v1_prompt.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, conlist
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.prompt_service import build_prompt
from app.models.enums import Equilibrium

router = APIRouter(prefix="/prompts", tags=["Prompt"])


class PromptFurnitureListDTO(BaseModel):
    furnitureIds: conlist(int, min_length=1)

class PromptReq(BaseModel):
    floorPlanId: int
    tasteId: int
    equilibrium: Equilibrium
    promptFurnitureListDTO: PromptFurnitureListDTO


@router.post("/compose")
async def compose_prompt(req: PromptReq, db: AsyncSession = Depends(get_db)):
    prompt = await build_prompt(
        db=db,
        floor_plan_id=req.floorPlanId,
        equilibrium=req.equilibrium,
        taste_id=req.tasteId,
        furniture_ids=req.promptFurnitureListDTO.furnitureIds,
    )
    return {"prompt": prompt}
