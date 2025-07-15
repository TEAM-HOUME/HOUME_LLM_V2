# app/services/image_service.py
from __future__ import annotations
import base64, logging, httpx
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import HTTPException

from app.config.settings import settings
from app.services.prompt_service import build_prompt
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enums import Equilibrium
from typing import Sequence

logger = logging.getLogger(__name__)

async def generate_image_direct(prompt: str) -> StreamingResponse:
    """
    RAG 없이, prompt 그대로 DALL·E(or internal) 호출 → PNG 스트림 반환
    """
    logger.info("📸 Direct Image Prompt →\n%s", prompt)

    # Spring Boot yml 과 동일하게 모든 파라미터 주입
    payload: dict = {
        "model":      settings.OPENAI_IMAGE_MODEL,      # gpt-image-1
        "prompt":     prompt,
        "n":          settings.OPENAI_IMAGE_N,          # 1
        "size":       settings.OPENAI_IMAGE_SIZE,       # "1024x1024"
        "quality":    settings.OPENAI_IMAGE_QUALITY,    # "medium"
        "background": settings.OPENAI_IMAGE_BACKGROUND, # "auto"
        # output-format 이 "b64_json" 이면 base64로, "url" 이면 링크로
        "response_format": settings.OPENAI_IMAGE_OUTPUT_FORMAT,
    }

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
        res = await client.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
        )
    if res.status_code != 200:
        raise HTTPException(status_code=res.status_code, detail=res.text)

    data = res.json()["data"][0]
    # b64_json vs url 처리
    if settings.OPENAI_IMAGE_OUTPUT_FORMAT == "b64_json":
        b64_png = data["b64_json"]
        png_bytes = base64.b64decode(b64_png)
    else:
        # data["url"] 에서 직접 fetch
        img_url   = data["url"]
        async with httpx.AsyncClient() as client:
            img_res = await client.get(img_url)
            img_res.raise_for_status()
            png_bytes = img_res.content

    return StreamingResponse(BytesIO(png_bytes), media_type="image/png")


async def build_and_generate_image(
    db: AsyncSession,
    floor_plan_id: int,
    equilibrium: Equilibrium,
    taste_id: int,
    furniture_ids: Sequence[int],
) -> StreamingResponse:
    """
    1) DB에서 프롬프트 4종 합성 → final_prompt
    2) 곧장 DALL·E(or internal) 호출 → PNG 스트림 반환
    """
    final_prompt = await build_prompt(
        db=db,
        floor_plan_id=floor_plan_id,
        equilibrium=equilibrium,
        taste_id=taste_id,
        furniture_ids=furniture_ids,
    )
    logger.info("📝 최종 Prompt →\n%s", final_prompt)

    return await generate_image_direct(final_prompt)
