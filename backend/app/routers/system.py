"""
System Administration, Reset, and Mock Data Generation Endpoints.
Allows resetting observations and triggering realistic trajectory generation from API/UI.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.app.database import get_db, engine
from backend.app.config import settings
from backend.app.models.entities import Camera, Road, VehicleObservation, Alert
from generator.generate_data import run as run_generator

router = APIRouter(prefix="/system", tags=["System Management"])


class GenerateRequest(BaseModel):
    events: int = Field(default=80, ge=10, le=500, description="Target number of ANPR events to generate")
    duplicates: bool = Field(default=False, description="Include duplicate events to test deduplication")
    include_anomalies: bool = Field(default=True, description="Include test anomaly and blacklist cases")


class ResetResponse(BaseModel):
    status: str
    message: str
    tables_cleared: list[str]


class GenerateResponse(BaseModel):
    status: str
    message: str
    events_generated: int


class SystemStatusResponse(BaseModel):
    total_observations: int
    total_alerts: int
    registered_cameras: int
    registered_corridors: int


@router.get("/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    """Returns total observation and alert records currently stored in the database."""
    obs_count = db.query(VehicleObservation).count()
    alert_count = db.query(Alert).count()
    cam_count = db.query(Camera).count()
    road_count = db.query(Road).count()
    return SystemStatusResponse(
        total_observations=obs_count,
        total_alerts=alert_count,
        registered_cameras=cam_count,
        registered_corridors=road_count
    )


@router.post("/reset-data", response_model=ResetResponse)
def reset_traffic_data():
    """
    Clears all generated operational ANPR traffic data (observations, alerts, metrics, trajectories).
    Keeps the camera checkpoints and road network configurations intact.
    """
    tables = ["vehicle_observations", "alerts", "traffic_metrics", "trajectories", "trajectory_points", "audit_logs"]
    try:
        with engine.connect() as conn:
            conn.execute(text(
                "TRUNCATE TABLE vehicle_observations, alerts, traffic_metrics, trajectories, trajectory_points, audit_logs CASCADE;"
            ))
            conn.commit()
        return ResetResponse(
            status="SUCCESS",
            message="All vehicle observations, trajectories, alerts, and metrics have been cleared.",
            tables_cleared=tables
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset data: {e}"
        )


@router.post("/generate-data", response_model=GenerateResponse)
def generate_traffic_data(payload: GenerateRequest = GenerateRequest()):
    """
    Triggers realistic multi-hop ANPR trajectory generation across Jaipur corridors.
    Pushes data directly through the FastAPI ingestion pipeline.
    """
    api_url = f"http://localhost:8000{settings.API_PREFIX}/events"
    api_key = settings.ANPR_API_KEY
    try:
        sent = run_generator(
            api_url=api_url,
            api_key=api_key,
            target_events=payload.events,
            duplicates=payload.duplicates,
            include_anomalies=payload.include_anomalies
        )
        return GenerateResponse(
            status="SUCCESS",
            message=f"Generated {sent} realistic multi-hop vehicle observations.",
            events_generated=sent
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {e}"
        )
