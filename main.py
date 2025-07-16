# app/main.py
from __future__ import annotations

########################################################################
#  Houme API – FastAPI 엔트리 포인트 (Clean Version)
#  - pgvector 타입 매핑 + Automap reflection
#  - 라우터 모듈(app.api.*) 일괄 등록
#  - 기본 로깅 / CORS 예시 포함
########################################################################

import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.dialects.postgresql.base import ischema_names
from sqlalchemy.ext.asyncio import AsyncSession

from pgvector.sqlalchemy import Vector

from app.db.session import engine, get_db
from app.db.automap import AutomapBase, init_automap
from app.api.routers import image_router
from app.api import prompt

# ──────────────────────────
# 0) 로깅 기본 설정
#    (uvicorn 자체 로거 제외 전역)
# ──────────────────────────
logging.basicConfig(
    level=logging.INFO,  # INFO 이상의 로그만 출력
    format="%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

# ──────────────────────────
# 1) FastAPI 인스턴스
# ──────────────────────────
app = FastAPI(
    title="Houme API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ──────────────────────────
# 2) (선택) CORS – 프론트엔드와 통신 시 필요
# ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # TODO: 프로덕션에서는 도메인 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────
# 3) Startup : pgvector + Automap
# ──────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    # PostgreSQL에서 vector 타입을 SQLAlchemy가 인식할 수 있도록 등록
    ischema_names["vector"] = Vector

    # DB에 있는 테이블들을 SQLAlchemy ORM 모델로 자동 매핑
    await init_automap(engine)
    logger.info("Automap reflection complete – tables: %s", list(AutomapBase.classes.keys()))
    print("[DEBUG] 자동 매핑된 클래스:", list(AutomapBase.classes.keys()))

# ──────────────────────────
# 4) API 라우터 등록
# ──────────────────────────
app.include_router(image_router.router)  # POST /images
app.include_router(prompt.router)

# ──────────────────────────
# 5) 데모 엔드포인트 (users)
# ──────────────────────────
@app.get("/users", tags=["User"], summary="전체 사용자 조회")
async def get_users(db: AsyncSession = Depends(get_db)):  # 비동기 세션을 가져오는 의존성 주입
    """users 테이블 전체 행을 반환"""
    User = AutomapBase.classes.users
    rows = (await db.execute(select(User))).scalars().all()
    return [dict(r.__dict__) for r in rows]  # __dict__로 JSON 응답 포맷 변환


@app.get("/user-ids", tags=["User"], summary="사용자 PK 목록")
async def list_user_ids(db: AsyncSession = Depends(get_db)):
    """users PK(id) 컬럼만 리스트로 반환"""
    User = AutomapBase.classes.users
    res = await db.execute(select(User.id))
    return [row.id for row in res]
