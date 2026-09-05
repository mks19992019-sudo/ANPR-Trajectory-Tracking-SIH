from datetime import datetime, timezone, timedelta
from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator
from backend.app.config import settings

T = TypeVar("T")

# ----------------------------------------------------
# 1. ANPR Ingestion Event
# ----------------------------------------------------
class ANPREventCreate(BaseModel):
    event_id: str = Field(..., description="Unique event identifier from police ANPR system", min_length=3, max_length=80)
    plate_number: str = Field(..., description="Vehicle license plate number", min_length=3, max_length=30)
    camera_id: str = Field(..., description="Camera identifier", min_length=2, max_length=50)
    timestamp: datetime = Field(..., description="Observation timestamp in UTC/ISO format")
    speed_kmph: float = Field(..., ge=0.0, le=300.0, description="Observed vehicle speed in km/h (0-300)")
    direction: str = Field(..., description="Vehicle traveling direction")
    vehicle_type: str = Field(default="car", description="Classified vehicle type (car, truck, bus, motorcycle, van)")
    violation: Optional[str] = Field(default=None, description="Violation type if any")
    ocr_confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Optical recognition confidence (0.0 - 1.0)")

    @field_validator("plate_number")
    @classmethod
    def clean_plate(cls, v: str) -> str:
        cleaned = v.strip().upper().replace(" ", "").replace("-", "")
        if len(cleaned) < 3 or len(cleaned) > 20:
            raise ValueError("Plate number must be between 3 and 20 alphanumeric characters")
        return cleaned

    @field_validator("direction")
    @classmethod
    def normalize_direction(cls, v: str) -> str:
        valid_map = {
            "N": "NORTH", "S": "SOUTH", "E": "EAST", "W": "WEST",
            "NE": "NORTHEAST", "NW": "NORTHWEST", "SE": "SOUTHEAST", "SW": "SOUTHWEST",
            "NORTH": "NORTH", "SOUTH": "SOUTH", "EAST": "EAST", "WEST": "WEST",
            "NORTHEAST": "NORTHEAST", "NORTHWEST": "NORTHWEST",
            "SOUTHEAST": "SOUTHEAST", "SOUTHWEST": "SOUTHWEST"
        }
        norm = v.strip().upper()
        if norm not in valid_map:
            return "NORTH"
        return valid_map[norm]

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp_bounds(cls, v: datetime) -> datetime:
        # Convert naive to UTC if necessary
        dt = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Future tolerance check
        max_future = now + timedelta(seconds=settings.FUTURE_TIMESTAMP_TOLERANCE_SECONDS)
        if dt > max_future:
            raise ValueError(f"Observation timestamp cannot be in the future (exceeds {settings.FUTURE_TIMESTAMP_TOLERANCE_SECONDS}s clock skew)")
        
        # Historical tolerance check
        min_past = now - timedelta(days=settings.MAX_HISTORICAL_DAYS)
        if dt < min_past:
            raise ValueError(f"Observation timestamp is too old (exceeds {settings.MAX_HISTORICAL_DAYS} days)")
        
        return dt

class ANPREventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    observation_id: str
    event_id: str
    plate_number: str
    camera_id: str
    timestamp: datetime
    speed_kmph: float
    direction: str
    vehicle_type: str
    violation: Optional[str] = None
    ocr_confidence: float
    created_at: datetime

# ----------------------------------------------------
# 2. Camera Schemas
# ----------------------------------------------------
class CameraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    camera_id: str
    camera_name: str
    road_id: Optional[str] = None
    latitude: float
    longitude: float
    location: Optional[str] = None
    direction: str
    status: str

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
    model_config = ConfigDict(from_attributes=True)

    alert_id: str
    alert_type: str
    severity: str
    plate_number: str
    camera_id: str
    camera_name: Optional[str] = None
    timestamp: datetime
    description: str
    status: str

class AlertUpdate(BaseModel):
    status: str  # OPEN, INVESTIGATING, RESOLVED

# ----------------------------------------------------
# 6. Blacklist Schemas
# ----------------------------------------------------
class BlacklistCreate(BaseModel):
    plate_number: str
    reason: str
    reference_number: str

    @field_validator("plate_number")
    @classmethod
    def clean_plate(cls, v: str) -> str:
        return v.strip().upper().replace(" ", "").replace("-", "")

class BlacklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plate_number: str
    reason: str
    reference_number: str
    status: str
    created_at: datetime

# ----------------------------------------------------
# 7. ML Prediction Placeholder
# ----------------------------------------------------
class PredictionPlaceholderResponse(BaseModel):
    status: str = "READY_FOR_MODEL"
    message: str = "XGBoost model pipeline interface ready. Please train and supply traffic_model.json to activate live inference."
    model_version: Optional[str] = None
    corridors: List[dict] = []

# ----------------------------------------------------
# 8. Pagination & Generic Responses
# ----------------------------------------------------
class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
