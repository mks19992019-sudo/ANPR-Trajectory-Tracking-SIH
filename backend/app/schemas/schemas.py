from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, field_validator

# ----------------------------------------------------
# 1. ANPR Ingestion Event
# ----------------------------------------------------
class ANPREventCreate(BaseModel):
    event_id: str = Field(..., description="Unique event identifier from police ANPR system", min_length=3)
    plate_number: str = Field(..., description="Vehicle license plate number", min_length=3)
    camera_id: str = Field(..., description="Camera identifier", min_length=2)
    timestamp: datetime = Field(..., description="Observation timestamp")
    speed_kmph: float = Field(..., ge=0.0, le=300.0, description="Observed vehicle speed")
    direction: str = Field(..., description="Vehicle traveling direction")
    vehicle_type: str = Field(default="car", description="Classified vehicle type")
    violation: Optional[str] = Field(default=None, description="Violation type if any")
    ocr_confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Optical recognition confidence")

    @field_validator("plate_number")
    @classmethod
    def clean_plate(cls, v: str) -> str:
        cleaned = v.strip().upper().replace(" ", "").replace("-", "")
        if len(cleaned) < 3:
            raise ValueError("Plate number must be at least 3 characters long")
        return cleaned

    @field_validator("direction")
    @classmethod
    def normalize_direction(cls, v: str) -> str:
        valid = {"N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
                 "NE": "NORTHEAST", "NW": "NORTHWEST", "SE": "SOUTHEAST", "SW": "SOUTHWEST",
                 "NORTH": "NORTH", "SOUTH": "SOUTH", "EAST": "EAST", "WEST": "WEST"}
        norm = v.strip().upper()
        return valid.get(norm, norm)

class ANPREventResponse(BaseModel):
    observation_id: str
    event_id: str
    plate_number: str
    camera_id: str
    timestamp: datetime
    speed_kmph: float
    direction: str
    vehicle_type: str
    violation: Optional[str]
    ocr_confidence: float
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------------------------------------------
# 2. Camera Schemas
# ----------------------------------------------------
class CameraResponse(BaseModel):
    camera_id: str
    camera_name: str
    road_id: Optional[str]
    latitude: float
    longitude: float
    location: Optional[str]
    direction: str
    status: str

    class Config:
        from_attributes = True

# ----------------------------------------------------
# 3. Trajectory Schemas
# ----------------------------------------------------
class TrajectoryWaypoint(BaseModel):
    camera_id: str
    camera_name: str
    timestamp: datetime
    speed_kmph: float
    latitude: float
    longitude: float
    delta_distance_km: float = 0.0
    delta_time_seconds: float = 0.0
    implied_speed_kmph: float = 0.0
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None

class TrajectoryResponse(BaseModel):
    trajectory_id: str
    plate_number: str
    start_time: datetime
    end_time: datetime
    total_distance_km: float
    average_speed_kmph: float
    camera_count: int
    plausibility_status: str  # NORMAL, SUSPICIOUS, PHYSICALLY_IMPOSSIBLE
    anomaly_notes: Optional[str] = None
    route_geometry: List[List[float]]
    waypoints: List[TrajectoryWaypoint]

# ----------------------------------------------------
# 4. Traffic Analytics Schemas
# ----------------------------------------------------
class TrafficVolumeResponse(BaseModel):
    total_vehicles_today: int
    active_cameras: int
    total_cameras: int
    average_speed_city: float
    congested_corridors: int
    active_alerts: int
    recorded_at: datetime

class SpeedAnalyticsResponse(BaseModel):
    road_id: str
    road_name: str
    average_speed: float
    median_speed: float
    min_speed: float
    max_speed: float
    percentile_85_speed: float
    speed_limit: float
    compliance_rate: float

class TrafficFlowResponse(BaseModel):
    source_camera: str
    source_name: str
    destination_camera: str
    destination_name: str
    vehicle_count: int
    time_window: str
    source_coords: List[float]
    destination_coords: List[float]

class CongestionResponse(BaseModel):
    road_id: str
    road_name: str
    vehicle_count: int
    average_speed: float
    median_speed: float
    speed_limit: float
    capacity: int
    congestion_score: float
    congestion_level: str  # LOW, MODERATE, HIGH, SEVERE

class ODMatrixResponse(BaseModel):
    zones: List[str]
    matrix: List[List[int]]
    time_window: str

# ----------------------------------------------------
# 5. Alert Schemas
# ----------------------------------------------------
class AlertResponse(BaseModel):
    alert_id: str
    alert_type: str
    severity: str
    plate_number: str
    camera_id: str
    camera_name: Optional[str] = None
    timestamp: datetime
    description: str
    status: str

    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: str  # OPEN, INVESTIGATING, RESOLVED

# ----------------------------------------------------
# 6. Blacklist Schemas
# ----------------------------------------------------
class BlacklistResponse(BaseModel):
    plate_number: str
    reason: str
    reference_number: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ----------------------------------------------------
# 7. ML Prediction Placeholder
# ----------------------------------------------------
class PredictionPlaceholderResponse(BaseModel):
    status: str = "MODEL_NOT_TRAINED"
    message: str = "XGBoost traffic prediction model is not trained yet. Pipeline placeholder ready for user model."
    model_version: Optional[str] = None
    corridors: List[dict] = []
