from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    smartcommutex_env: str = Field(default="development", alias="SMARTCOMMUTEX_ENV")
    project_name: str = Field(default="SmartCommuteX", alias="PROJECT_NAME")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_v1_prefix: str = Field(default="/api/v1", alias="API_V1_PREFIX")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_timeout_seconds: float = Field(default=20.0, alias="API_TIMEOUT_SECONDS")
    cors_origins: list[str] = Field(default=["http://localhost:3000"], alias="CORS_ORIGINS")
    postgres_server: str = Field(default="postgres", alias="POSTGRES_SERVER")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="smartcommutex", alias="POSTGRES_DB")
    postgres_user: str = Field(default="smartcommutex", alias="POSTGRES_USER")
    postgres_password: str = Field(default="smartcommutex", alias="POSTGRES_PASSWORD")
    graphhopper_base_url: str = Field(
        default="https://graphhopper.com/api/1", alias="GRAPHHOPPER_BASE_URL"
    )
    graphhopper_api_key: str | None = Field(default=None, alias="GRAPHHOPPER_API_KEY")
    route_cache_ttl_seconds: int = Field(default=300, alias="ROUTE_CACHE_TTL_SECONDS")
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")
    celery_broker_url: str = Field(default="redis://redis:6379/1", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(
        default="redis://redis:6379/2", alias="CELERY_RESULT_BACKEND"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @property
    def async_database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_server}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
