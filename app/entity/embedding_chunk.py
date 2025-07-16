# from sqlalchemy import Column, Integer, Text
# from pgvector.sqlalchemy import Vector    # pgvector 의 Vector
# from app.db.session import Base
# from app.config.settings import settings
#
# class EmbeddingChunk(Base):
#     __tablename__ = "embedding_chunks"
#     id        = Column(Integer, primary_key=True)
#     content   = Column(Text, nullable=False)
#     # → 차원값을 위치 인자로 넘깁니다.
#     embedding = Column(
#         Vector(settings.EMBED_DIM),
#         nullable=False
#     )
