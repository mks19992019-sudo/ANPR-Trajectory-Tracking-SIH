from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "ANPR Traffic Intelligence"
    API_PREFIX: str = "/api/v1"
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10; DB_MAX_OVERFLOW: int = 10; DB_POOL_TIMEOUT: int = 30
    OBSERVATION_DEDUP_SECONDS: int = 30; FUTURE_TIMESTAMP_TOLERANCE_SECONDS: int = 300; MAX_HISTORICAL_DAYS: int = 30; JOURNEY_GAP_MINUTES: int = 60
    DEFAULT_SPEED_LIMIT: float = 60; SPEED_VIOLATION_DELTA_KMPH: float = 15; IMPOSSIBLE_SPEED_THRESHOLD_KMPH: float = 160; SUSPICIOUS_SPEED_THRESHOLD_KMPH: float = 120
    ANPR_API_KEY: str; REQUIRE_API_KEY: bool = True; CORS_ORIGINS: List[str] = ["http://localhost:5173"]; LOG_LEVEL: str = "INFO"; RETENTION_DAYS: int | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @field_validator("DATABASE_URL")
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if not value.startswith(("postgresql://", "postgresql+psycopg2://")): raise ValueError("DATABASE_URL must use PostgreSQL")
        return value
settings = Settings()
