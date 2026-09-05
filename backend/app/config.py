import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "City-Wide ANPR Intelligence & Traffic Analytics Platform"
    API_PREFIX: str = "/api"
    
    # Database: Supports Postgres with PostGIS, with SQLite fallback if Postgres is unavailable
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./traffic_anpr.db")
    
    # Deduplication tolerance window (seconds)
    DEDUP_WINDOW_SECONDS: int = 5
    
    # Speed threshold for overspeeding alerts (km/h) default
    DEFAULT_SPEED_LIMIT: float = 60.0
    
    # Anomaly speed threshold for impossible movement (km/h)
    IMPOSSIBLE_SPEED_THRESHOLD_KMPH: float = 160.0
    
    # API authentication key (optional header for police ANPR feed)
    ANPR_API_KEY: str = os.getenv("ANPR_API_KEY", "POLICE_ANPR_SECRET_KEY_2026")
    
    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
