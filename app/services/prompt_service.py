"""
app/services/prompt_service.py
──────────────────────────────
✔️ FastAPI + SQLAlchemy(Async) + LangChain  기반 “프롬프트 합성” 서비스

▸ 흐름 요약
   1. **DB 조회** : 도면·취향·가구 프롬프트를 *비동기* 로 읽어 온다.
   2. **Enum 설명** : `Equilibrium`(면적 구간) Enum 의 `value`(or description) 를 사용.
   3. **LangChain PromptTemplate** 로 네 가지 텍스트를 줄바꿈(\n) 방식으로 결합.
   4. **DEBUG 로그** 로 각 단계·최종 결과를 확인할 수 있다.
"""
from __future__ import annotations

import logging
from typing import Sequence

from langchain.prompts import PromptTemplate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.automap import AutomapBase          # Reflection 된 ORM 컨테이너
from app.models.enums import Equilibrium        # 면적 구간 Enum

logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────
# 1) PromptTemplate 정의
#    - input_variables: 템플릿에서 {name} 으로 참조할 변수들
#    - template: 입력된 프롬프트를 줄바꿈으로 이어 붙임
# ────────────────────────────────────────────────────────────────
PROMPT_TMPL = PromptTemplate(
    input_variables=[
        "floor_plan_prompt",
        "equilibrium_prompt",
        "tag_prompt",             # ✅ 수정
        "furniture_prompt"
    ],
    template=(
        "{floor_plan_prompt}\n"
        "{equilibrium_prompt}\n"
        "{tag_prompt}\n"          # ✅ 템플릿 안도 같이 수정
        "{furniture_prompt}"
    ),
)

# ────────────────────────────────────────────────────────────────
# 2) 핵심 비동기 함수 : build_prompt
#    - 모든 DB I/O를 await 로 수행 → FastAPI 엔드포인트에서 await 호출
#    - Java Spring 의 PromptServiceImpl.makePrompt() 역할
# ────────────────────────────────────────────────────────────────
# DB의 Id를 받아, 해당하는 프롬프트를 합쳐서 반환함
async def build_prompt(
    db: AsyncSession,
    floor_plan_id: int,
    equilibrium: Equilibrium,
    tag_id: int,
    furniture_tag_ids: Sequence[int],
) -> str:
    """
    Args
    ----
    db : AsyncSession
        FastAPI Depends(get_db) 로 주입된 비동기 세션
    floor_plan_id : int
        FloorPlan 테이블 PK
    equilibrium : Equilibrium
        면적 구간 Enum 값 (예: Equilibrium.UNDER_5)
    taste_id : int
        Taste 테이블 PK
    furniture_ids : Sequence[int]
        포함할 Furniture PK 리스트

    Returns
    -------
    str
        네 가지 프롬프트를 LangChain 템플릿으로 합성한 최종 문자열
    """

    # ── (1) Automap 클래스 – 테이블명 → CamelCase 로 변환된 이름
    FloorPlan = AutomapBase.classes.FloorPlan
    Tag = AutomapBase.classes.Tag
    FurnitureTag = AutomapBase.classes.FurnitureTag

    # ① FloorPlan
    fp_prompt: str = (
            await db.scalar(
                select(FloorPlan.floor_plan_prompt).where(FloorPlan.id == floor_plan_id)
            )
            or "도면 프롬프트가 존재하지 않습니다"
    )

    # ② Tag (기존 Taste)
    tag_prompt: str = (
            await db.scalar(
                select(Tag.tag_prompt).where(Tag.id == tag_id)
            )
            or "태그 프롬프트가 존재하지 않습니다"
    )

    # ③ FurnitureTag (기존 Furniture)
    stmt = (
        select(FurnitureTag.furniture_prompt)
        .where(FurnitureTag.id.in_(furniture_tag_ids))
        .order_by(FurnitureTag.id.asc())
    )


    furniture_tag_rows: list[str] = (await db.execute(stmt)).scalars().all()
    furniture_prompt = "\n".join(furniture_tag_rows)
    logger.info("[Prompt] FurnitureTags %s →\n%s", furniture_tag_ids, furniture_prompt)

    # ④ 최종 프롬프트 LangChain 합성
    final_prompt: str = PROMPT_TMPL.format(
        floor_plan_prompt=fp_prompt,
        equilibrium_prompt=equilibrium.value,
        tag_prompt=tag_prompt,  # ✅ taste_prompt → tag_prompt
        furniture_prompt=furniture_prompt,
    )
    logger.info("🟢 [Prompt] FINAL\n%s", final_prompt)

    return final_prompt
