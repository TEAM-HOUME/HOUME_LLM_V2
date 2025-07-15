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
#    - template: 네 줄로 구성된 최종 문자열 포맷
# ────────────────────────────────────────────────────────────────
PROMPT_TMPL = PromptTemplate(
    input_variables=[
        "floor_plan_prompt",     # ① 도면 설명
        "equilibrium_prompt",    # ② 평형(면적) 설명
        "taste_prompt",          # ③ 취향(무드보드) 설명
        "furniture_prompt",      # ④ 가구 설명(여러 줄)
    ],
    template=(
        "{floor_plan_prompt}\n"
        "{equilibrium_prompt}\n"
        "{taste_prompt}\n"
        "{furniture_prompt}"
    ),
)

# ────────────────────────────────────────────────────────────────
# 2) 핵심 비동기 함수 : build_prompt
#    - 모든 DB I/O를 await 로 수행 → FastAPI 엔드포인트에서 await 호출
#    - Java Spring 의 PromptServiceImpl.makePrompt() 역할
# ────────────────────────────────────────────────────────────────
async def build_prompt(
    db: AsyncSession,
    floor_plan_id: int,
    equilibrium: Equilibrium,
    taste_id: int,
    furniture_ids: Sequence[int],
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
    Taste     = AutomapBase.classes.Taste
    Furniture = AutomapBase.classes.Furniture

    # ── (2) FloorPlan 프롬프트 ───────────────────────────────
    fp_prompt: str = (
        await db.scalar(
            select(FloorPlan.floor_plan_prompt).where(FloorPlan.id == floor_plan_id)
        )
        or "도면 프롬프트가 존재하지 않습니다"
    )
    logger.info("[Prompt] FloorPlan %s → %s", floor_plan_id, fp_prompt)

    # ── (3) Taste 프롬프트 ─────────────────────────────────
    taste_prompt: str = (
        await db.scalar(
            select(Taste.taste_prompt).where(Taste.id == taste_id)
        )
        or "무드보드 프롬프트가 존재하지 않습니다"
    )
    logger.info("[Prompt] Taste %s → %s", taste_id, taste_prompt)

    # ── (4) Furniture 프롬프트(다중) ───────────────────────
    stmt = (
        select(Furniture.furniture_prompt)
        .where(Furniture.id.in_(furniture_ids))
        .order_by(Furniture.id.asc())
    )
    furniture_rows: list[str] = (await db.execute(stmt)).scalars().all()
    furniture_prompt = "\n".join(furniture_rows)  # 줄바꿈으로 합치기
    logger.info("[Prompt] Furniture %s →\n%s", furniture_ids, furniture_prompt)

    # ── (5) LangChain 템플릿 합성 ──────────────────────────
    final_prompt: str = PROMPT_TMPL.format(
        floor_plan_prompt=fp_prompt,
        equilibrium_prompt=equilibrium.value,
        taste_prompt=taste_prompt,
        furniture_prompt=furniture_prompt,
    )
    logger.info("🟢 [Prompt] FINAL\n%s", final_prompt)

    # ── (6) 완성 프롬프트 반환 ─────────────────────────────
    return final_prompt
