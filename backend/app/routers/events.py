from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy import text
from backend.app.database import get_db, engine
from backend.app.models.entities import VehicleObservation
from backend.app.schemas.schemas import ANPREventCreate, ANPREventResponse, PaginatedResponse
from backend.app.services.ingestion_service import IngestionService
from backend.app.security import verify_api_key

router = APIRouter(tags=["ANPR Ingestion & Events"])


@router.delete("/events", status_code=status.HTTP_200_OK)
def delete_all_events():
    """
    Deletes all vehicle observation records while keeping table structure and columns intact.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE vehicle_observations, alerts, traffic_metrics, trajectories, trajectory_points, audit_logs CASCADE;"))
            conn.commit()
        return {"status": "SUCCESS", "message": "All vehicle observations and related data records deleted. Table columns and schemas preserved."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete records: {e}")

@router.post("/events", response_model=ANPREventResponse, status_code=status.HTTP_201_CREATED)
async def ingest_anpr_event(
    event_in: ANPREventCreate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    """
    Securely ingests, validates, deduplicates, and registers an ANPR event from municipal police cameras.
    Triggers immediate security blacklist and anomaly alerts, broadcasting to live dashboards.
    """
    return await IngestionService.ingest_event(db, event_in)

@router.get("/events", response_model=PaginatedResponse[ANPREventResponse])
def list_anpr_events(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    plate: Optional[str] = None,
    camera_id: Optional[str] = None,
    violation_only: bool = False, start_time: Optional[str] = None, end_time: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Returns recent ANPR observations with pagination and optional filters for plate, camera, and violations.
    """
    query = db.query(VehicleObservation)
    if plate:
        clean = plate.strip().upper().replace(" ", "").replace("-", "")
        query = query.filter(VehicleObservation.plate_number.contains(clean))
    if camera_id:
        query = query.filter(VehicleObservation.camera_id == camera_id)
    if violation_only:
        query = query.filter(VehicleObservation.violation.isnot(None))

    total=query.count()
    observations = query.order_by(VehicleObservation.observed_at.desc()).offset(offset).limit(limit).all()
    return {"items":observations,"total":total,"limit":limit,"offset":offset}

@router.get("/events/{event_id}", response_model=ANPREventResponse)
def get_event_by_id(event_id: str, db: Session = Depends(get_db)):
    """
    Fetch a single ANPR observation event by its unique ID.
    """
    obs = db.query(VehicleObservation).filter(VehicleObservation.event_id == event_id).first()
    if not obs:
        raise HTTPException(status_code=404, detail=f"ANPR event '{event_id}' not found.")
    return obs
