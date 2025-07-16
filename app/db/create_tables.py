# app/db/create_tables.py
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# ── (A) .env 파일을 프로젝트 루트에서 로드 ──
# __file__ = .../app/db/create_tables.py
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # → .../houme_llm_v2
load_dotenv(PROJECT_ROOT / ".env")

# ── (B) 나머지 import ──
from sqlalchemy import text
from app.db.session import engine, Base
from app.entity.embedding_chunk import EmbeddingChunk

async def init_models():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_models())
