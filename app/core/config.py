from functools import lru_cache
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    - .env 를 읽어들여 PostgreSQL 접속 정보를 구성한다.
    - POSTGRES_HOST 가 `jdbc:postgresql://host:port/db` 형식이어도 동작.
    """

    # 기본값은 **로컬 개발** 기준 (실제 서비스는 .env 로 덮어씀)
    POSTGRES_USER: str = "root"
    POSTGRES_PASSWORD: str | None = "root"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int | None = 5432
    POSTGRES_DB: str | None = "postgres"

    # ------------------------------------------------------------------ #
    # 내부 헬퍼: JDBC URL → host / port / db 추출
    # ------------------------------------------------------------------ #
    def _extract_from_jdbc(self) -> tuple[str, int | None, str | None]:
        """jdbc:postgresql://host:port/db  형식이면 파싱, 아니면 그대로."""
        jdbc_prefix = "jdbc:"
        if self.POSTGRES_HOST.startswith(jdbc_prefix):
            parsed = urlparse(self.POSTGRES_HOST[len(jdbc_prefix):])
            host = parsed.hostname or self.POSTGRES_HOST
            port = parsed.port or self.POSTGRES_PORT
            db   = parsed.path.lstrip("/") or self.POSTGRES_DB
            return host, port, db
        return self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_DB

    # ------------------------------------------------------------------ #
    # 외부 제공 프로퍼티: SQLAlchemy async URL
    # ------------------------------------------------------------------ #
    @property
    def database_url_async(self) -> str:
        host, port, db = self._extract_from_jdbc()

        # 비밀번호가 있으면 user:pass@, 없으면 user@
        auth = (
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            if self.POSTGRES_PASSWORD
            else f"{self.POSTGRES_USER}@"
        )

        port_part = f":{port}" if port else ""
        db_part   = f"/{db}"   if db   else ""

        return f"postgresql+asyncpg://{auth}{host}{port_part}{db_part}"

    # ------------------------------------------------------------------ #
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# 싱글턴처럼 재사용
@lru_cache
def get_settings() -> Settings:
    return Settings()
