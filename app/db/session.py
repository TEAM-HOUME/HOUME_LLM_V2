# app/db/session.py
from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config.settings import settings

# ────────────────────────────────────────────────
# 1) Declarative Base
# ────────────────────────────────────────────────
Base = declarative_base()

# ────────────────────────────────────────────────
# 2) Async Engine
# ────────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    settings.database_url_async,
    echo=False,         # SQL 로그 보고 싶으면 True 로 변경
    pool_pre_ping=True,
)

# ────────────────────────────────────────────────
# 3) Async Session Factory
# ────────────────────────────────────────────────
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)

# ────────────────────────────────────────────────
# 4) FastAPI Depends 헬퍼
# ────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI 의 Depends(get_db) 로 사용하세요.
    요청당 하나의 세션을 열고, 요청이 끝나면 자동으로 close 됩니다.
    """
    async with AsyncSessionLocal() as session:
        yield session

async_session = AsyncSessionLocal