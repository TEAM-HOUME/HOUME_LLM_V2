# app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    VECTOR_DOC_PATH: str

    # ── OpenAI ─────────────────────────
    OPENAI_API_KEY: str

    # ── Postgres ───────────────────────
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "houme"

    EMBED_DIM: int = 1536

    OPENAI_IMAGE_MODEL: str = "gpt-image-1"
    OPENAI_IMAGE_N: int = 1
    OPENAI_IMAGE_SIZE: str = "1024x1024"
    OPENAI_IMAGE_QUALITY: str = "medium"
    OPENAI_IMAGE_BACKGROUND: str = "auto"
    OPENAI_IMAGE_OUTPUT_FORMAT: str = "b64_json"  # "b64_json" or "url"

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str
    AWS_REGION: str = "ap-northeast-2"

    # SQLAlchemy 용 접속 문자열 (asyncpg)
    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",            # ← .env 를 자동 로드
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

settings = Settings()
