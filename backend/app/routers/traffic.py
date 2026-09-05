from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Any
from backend.app.database import get_db
from backend.app.schemas.schemas import (
    TrafficVolumeResponse,
    SpeedAnalyticsResponse,
    TrafficFlowResponse,
    CongestionResponse,
    ODMatrixResponse
)
from backend.app.services.traffic_service import TrafficService
from backend.app.services.congestion_service import CongestionService

router = APIRouter(tags=["Traffic Analytics & Flow"])

@router.get("/traffic/live", response_model=TrafficVolumeResponse)
@router.get("/traffic/volume", response_model=TrafficVolumeResponse)
@router.get("/traffic/summary", response_model=TrafficVolumeResponse)
@router.get("/analytics/summary", response_model=TrafficVolumeResponse)
def get_live_traffic_volume(db: Session = Depends(get_db)):
    """
    Returns city-wide traffic volume, active cameras, average flow speed, and incident count.
    """
    return TrafficService.get_city_summary(db)

@router.get("/traffic/speed", response_model=List[SpeedAnalyticsResponse])
@router.get("/traffic/speed-analytics", response_model=List[SpeedAnalyticsResponse])
def get_speed_analytics(
    hours: int = Query(1, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """
    Returns speed percentiles (mean, median, 85th percentile, max) and compliance rates across corridors.
    """
    return TrafficService.get_speed_analytics(db, hours=hours)

@router.get("/traffic/flow", response_model=List[TrafficFlowResponse])
def get_traffic_flows(
    hours: int = Query(1, ge=1, le=24),
    db: Session = Depends(get_db)
):
    """
    Returns camera-to-camera directional flow counts from sequential vehicle observations.
    """
    return TrafficService.get_camera_flows(db, hours=hours)

@router.get("/traffic/congestion", response_model=List[CongestionResponse])
def get_corridor_congestion(
    minutes: int = Query(15, ge=5, le=120),
    db: Session = Depends(get_db)
):
    """
    Computes Congestion Score and levels (LOW, MODERATE, HIGH, SEVERE) for each road corridor.
    """
    return CongestionService.calculate_road_congestion(db, minutes=minutes)

@router.get("/traffic/od", response_model=ODMatrixResponse)
@router.get("/traffic/od-matrix", response_model=ODMatrixResponse)
def get_origin_destination_matrix(db: Session = Depends(get_db)):
    """
    Returns Origin-Destination (OD) trip matrix computed from vehicle entry and exit checkpoints.
    """
    return TrafficService.get_od_matrix(db)

@router.get("/heatmap")
@router.get("/traffic/heatmap")
def get_traffic_heatmap(db: Session = Depends(get_db)):
    """
    Returns GeoJSON point dataset with detection intensity for GIS heatmap visualization.
    """
    return {
        "type": "FeatureCollection",
        "features": TrafficService.get_heatmap_data(db)
    }
