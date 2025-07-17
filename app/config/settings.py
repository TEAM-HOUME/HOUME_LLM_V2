# # app/config/settings.py
# from pydantic_settings import BaseSettings, SettingsConfigDict
# from langchain_teddynote import logging
# from dotenv import load_dotenv
#
# load_dotenv()
# logging.langsmith("Houme")
#
# class Settings(BaseSettings):
#
#     VECTOR_DOC_PATH: str
#
#     # ── OpenAI ─────────────────────────
#     OPENAI_API_KEY: str
#     LANGSMITH_TRACING_V2: str
#     LANGSMITH_ENDPOINT: str
#     LANGSMITH_API_KEY: str
#     LANGSMITH_PROJECT: str
#
#     # ── Postgres ───────────────────────
#     POSTGRES_USER: str
#     POSTGRES_PASSWORD: str
#     POSTGRES_HOST: str = "localhost"
#     POSTGRES_PORT: int = 5432
#     POSTGRES_DB: str = "houme"
#
#     EMBED_DIM: int = 1536
#
#     OPENAI_IMAGE_MODEL: str = "gpt-image-1"
#     OPENAI_IMAGE_N: int = 1
#     OPENAI_IMAGE_SIZE: str = "1536x1024"  # 3:2 비율
#     OPENAI_IMAGE_QUALITY: str = "medium"
#     OPENAI_IMAGE_BACKGROUND: str = "auto"
#     OPENAI_IMAGE_OUTPUT_FORMAT: str = "b64_json"  # "b64_json" or "url"
#
#     AWS_ACCESS_KEY_ID: str
#     AWS_SECRET_ACCESS_KEY: str
#     AWS_S3_BUCKET_NAME: str
#     AWS_REGION: str = "ap-northeast-2"
#
#     # SQLAlchemy 용 접속 문자열 (asyncpg)
#     @property
#     def database_url_async(self) -> str:
#         return (
#             f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
#             f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
#         )
#
#     model_config = SettingsConfigDict(
#         env_file=".env",            # ← .env 를 자동 로드
#         env_file_encoding="utf-8",
#         case_sensitive=True,
#     )
#
# settings = Settings()

# app/config/settings.py

from urllib.parse import urlparse

from dotenv import load_dotenv
from langchain_teddynote import logging
from pydantic_settings import BaseSettings, SettingsConfigDict


# .env 파일 로딩 및 LangSmith 프로젝트 세팅
load_dotenv()
logging.langsmith("Houme")


class Settings(BaseSettings):
    """
    통합 설정 클래스
    - .env 파일 기반으로 로드
    - LangSmith 및 OpenAI, Postgres, AWS, 기타 환경변수 포함
    - JDBC URL 파싱도 지원
    """

    # ── Postgres (JDBC 포함 파싱 지원) ────────
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str | None = "root"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int | None = 5432
    POSTGRES_DB: str | None = "houme"

    def _extract_from_jdbc(self) -> tuple[str, int | None, str | None]:
        """jdbc:postgresql://host:port/db 형식이면 파싱, 아니면 그대로 반환"""
        jdbc_prefix = "jdbc:"
        if self.POSTGRES_HOST.startswith(jdbc_prefix):
            parsed = urlparse(self.POSTGRES_HOST[len(jdbc_prefix):])
            host = parsed.hostname or self.POSTGRES_HOST
            port = parsed.port or self.POSTGRES_PORT
            db   = parsed.path.lstrip("/") or self.POSTGRES_DB
            return host, port, db
        return self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_DB

    @property
    def database_url_async(self) -> str:
        host, port, db = self._extract_from_jdbc()

        auth = (
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            if self.POSTGRES_PASSWORD
            else f"{self.POSTGRES_USER}@"
        )
        port_part = f":{port}" if port else ""
        db_part   = f"/{db}"   if db   else ""

        return f"postgresql+asyncpg://{auth}{host}{port_part}{db_part}"

    # ── OpenAI ──────────────────────────────
    OPENAI_API_KEY: str
    LANGSMITH_TRACING_V2: str
    LANGSMITH_ENDPOINT: str
    LANGSMITH_API_KEY: str
    LANGSMITH_PROJECT: str

    OPENAI_IMAGE_MODEL: str
    OPENAI_IMAGE_N: int
    OPENAI_IMAGE_SIZE: str
    OPENAI_IMAGE_QUALITY: str
    OPENAI_IMAGE_BACKGROUND: str
    OPENAI_IMAGE_OUTPUT_FORMAT: str

    EMBED_DIM: int

    VECTOR_DOC_PATH: str

    # ── AWS ──────────────────────────────
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_REGION: str

    # ── 설정 파일 구성 ──────────────────────
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# 인스턴스 바로 사용하려면 아래처럼 가져오면 됨
settings = Settings()