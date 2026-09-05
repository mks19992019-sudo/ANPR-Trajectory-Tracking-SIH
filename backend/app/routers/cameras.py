from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.entities import Camera
from backend.app.schemas.schemas import CameraResponse

router = APIRouter(prefix="/cameras", tags=["Camera Grid"])

@router.get("", response_model=List[CameraResponse])
def list_cameras(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns registered camera checkpoints with GPS coordinates, direction, and operational status.
    """
    return db.query(Camera).order_by(Camera.camera_id.asc()).offset(offset).limit(limit).all()

@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: str, db: Session = Depends(get_db)):
    """
    Returns telemetry and details for a single camera checkpoint.
    """
    cam = db.query(Camera).filter(Camera.camera_id == camera_id).first()
    if not cam:
        raise HTTPException(status_code=404, detail=f"Camera checkpoint '{camera_id}' not found.")
    return cam
