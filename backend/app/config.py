import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "City-Wide ANPR Intelligence & Traffic Analytics Platform"
    API_PREFIX: str = "/api/v1"

    # Database — PostgreSQL + PostGIS only (set via environment or .env file)
    DATABASE_URL: str = "postgresql://anpr_admin:anpr_secure_password@localhost:5432/anpr_traffic_db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    # ANPR Ingestion Parameters
    DEDUP_WINDOW_SECONDS: int = 5          # event_id uniqueness check window (s)
    OBSERVATION_DEDUP_SECONDS: int = 30    # plate+camera sliding window deduplication (s)
    FUTURE_TIMESTAMP_TOLERANCE_SECONDS: int = 300   # Max 5 min clock skew
    MAX_HISTORICAL_DAYS: int = 30

    # Trajectory / Journey Parameters
    JOURNEY_GAP_MINUTES: int = 60         # Gap between observations that splits journeys

    # Speed limits and anomaly thresholds (km/h)
    DEFAULT_SPEED_LIMIT: float = 60.0
    SPEED_VIOLATION_DELTA_KMPH: float = 15.0
    IMPOSSIBLE_SPEED_THRESHOLD_KMPH: float = 160.0
    SUSPICIOUS_SPEED_THRESHOLD_KMPH: float = 120.0

    # Security & Authentication
    ANPR_API_KEY: str = "POLICE_ANPR_SECRET_KEY_2026"
    REQUIRE_API_KEY: bool = False   # Set True in production

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
