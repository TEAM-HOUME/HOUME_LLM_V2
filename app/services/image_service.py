from app.config.settings import settings
from langchain_core.runnables import RunnableLambda
from langchain_core.runnables import RunnableSequence

from app.services.prompt_service import build_prompt
from app.libs.s3 import upload_image_to_s3
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enums import Equilibrium
from typing import Sequence
import uuid, base64, httpx
from app.utils.CLIPScore import calculate_clip_score


# 1. 이미지 생성 함수 (LangChain용)
async def generate_image(prompt: str) -> bytes:
    payload: dict = {
                "model":      settings.OPENAI_IMAGE_MODEL,      # gpt-image-1
                "prompt":     prompt,
                "n":          settings.OPENAI_IMAGE_N,          # 1
                "size":       settings.OPENAI_IMAGE_SIZE,       # "1536x1024"
                "quality":    settings.OPENAI_IMAGE_QUALITY,    # "medium"
                "background": settings.OPENAI_IMAGE_BACKGROUND, # "auto"
                # output-format 이 "b64_json" 이면 base64로, "url" 이면 링크로
            }
    headers = {"Authorization": f"Bearer {settings.OPENAI_API_KEY}"}

    async with httpx.AsyncClient(timeout=httpx.Timeout(120)) as client:
        res = await client.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers
        )
    res.raise_for_status()
    b64 = res.json()["data"][0]["b64_json"]
    return base64.b64decode(b64)


# 2. 이미지 후처리 및 업로드
def process_and_upload(png_bytes: bytes, prompt: str) -> dict:
    uid = uuid.uuid4()
    filename = f"generated/{uid}.png"
    content_type = "image/png"

    s3_url = upload_image_to_s3(png_bytes, content_type)
    clip_score = calculate_clip_score(png_bytes, prompt)

    return {
        "filename": filename,
        "originalFilename": f"{uid}.png",
        "imageLink": s3_url,
        "contentType": content_type,
        "clipScore": clip_score,
        "pullPrompt": prompt
    }

# 3. 체인 정의
async def build_image_chain(
    db: AsyncSession,
    floor_plan_id: int,
    equilibrium: Equilibrium,
    tag_id: int,
    furniture_tag_ids: Sequence[int],
) -> dict:
    # Step 1: DB 기반 프롬프트 생성
    prompt = await build_prompt(
        db=db,
        floor_plan_id=floor_plan_id,
        equilibrium=equilibrium,
        tag_id=tag_id,
        furniture_tag_ids=furniture_tag_ids,
    )

    # Step 2: LangChain-style chain 구성
    chain: RunnableSequence = (
            RunnableLambda(generate_image)  # async function
            | RunnableLambda(lambda img: process_and_upload(img, prompt))  # 동기 함수로 처리
    )

    return await chain.ainvoke(prompt)

