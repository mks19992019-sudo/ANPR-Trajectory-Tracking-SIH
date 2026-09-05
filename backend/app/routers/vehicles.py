from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.entities import VehicleObservation
from backend.app.schemas.schemas import TrajectoryResponse, ANPREventResponse
from backend.app.services.trajectory_service import TrajectoryService

router = APIRouter(prefix="/vehicles", tags=["Vehicle Trajectory & History"])

@router.get("/{plate}/trajectory", response_model=TrajectoryResponse)
def get_vehicle_trajectory(plate: str, db: Session = Depends(get_db)):
    """
    Reconstructs vehicle trajectory from chronological camera observations,
    calculating distances, transit times, implied speeds, and plausibility.
    """
    trajectory = TrajectoryService.reconstruct_trajectory(db, plate)
    if not trajectory:
        raise HTTPException(status_code=404, detail=f"No observations found for vehicle plate '{plate}'.")
    return trajectory

@router.get("/{plate}/history", response_model=List[ANPREventResponse])
def get_vehicle_history(plate: str, db: Session = Depends(get_db)):
    """
    Retrieves chronological detection history for a given vehicle plate number.
    """
    clean_plate = plate.strip().upper().replace(" ", "").replace("-", "")
    records = db.query(VehicleObservation).filter(
        VehicleObservation.plate_number == clean_plate
    ).order_by(VehicleObservation.timestamp.asc()).all()

    if not records:
        raise HTTPException(status_code=404, detail=f"No history found for plate '{plate}'.")
    return records
