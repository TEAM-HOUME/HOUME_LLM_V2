# app/services/image_service.py
from __future__ import annotations
import base64, logging, httpx, uuid
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import HTTPException

from app.config.settings import settings
from app.services.prompt_service import build_prompt
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enums import Equilibrium
from typing import Sequence

from app.libs.s3 import upload_image_to_s3

logger = logging.getLogger(__name__)

async def generate_image_and_upload(prompt: str) -> dict:
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

        uid = uuid.uuid4()
        filename = f"generated/{uid}.png"
        original_filename = f"{uid}.png"
        content_type = "image/png"
    else:
        # data["url"] 에서 직접 fetch
        img_url   = data["url"]
        async with httpx.AsyncClient() as client:
            img_res = await client.get(img_url)
            img_res.raise_for_status()
            png_bytes = img_res.content

    s3_url = upload_image_to_s3(png_bytes, content_type)

    logger.info("✅ S3 업로드 성공 → %s", s3_url)

    return {
        "filename": filename,
        "originalFilename": original_filename,
        "imageLink": s3_url,
        "contentType": content_type,
        "pullPrompt": prompt  # setter 가능한 필드
    }


async def build_and_generate_image(
    db: AsyncSession,
    floor_plan_id: int,
    equilibrium: Equilibrium,
    taste_id: int,
    furniture_ids: Sequence[int],
) -> dict:
    """
    DB에서 프롬프트 합성 → 이미지 생성 + 업로드 → 응답 DTO
    """
    final_prompt = await build_prompt(
        db=db,
        floor_plan_id=floor_plan_id,
        equilibrium=equilibrium,
        taste_id=taste_id,
        furniture_ids=furniture_ids,
    )
    logger.info("📝 최종 Prompt →\n%s", final_prompt)

    return await generate_image_and_upload(final_prompt)
