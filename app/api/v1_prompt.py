# app/api/v1_prompt.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, conlist
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.prompt_service import build_prompt
from app.models.enums import Equilibrium

router = APIRouter(prefix="/prompts", tags=["Prompt"])


class PromptReq(BaseModel):
    floor_plan_id: int
    equilibrium: Equilibrium
    taste_id: int
    furniture_ids: conlist(int, min_length=1)


@router.post("/compose")
async def compose_prompt(req: PromptReq, db: AsyncSession = Depends(get_db)):

    # 좌우반전 필드 추가
    prompt = await build_prompt(
        db,
        floor_plan_id=req.floor_plan_id,
        equilibrium=req.equilibrium,  # Enum 그대로 넘김
        taste_id=req.taste_id,
        furniture_ids=req.furniture_ids,
    )
    return {"prompt": prompt}
