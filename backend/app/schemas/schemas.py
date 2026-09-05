from datetime import datetime, timezone, timedelta
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field, field_validator
from backend.app.config import settings
T=TypeVar("T")
class ANPREventCreate(BaseModel):
    event_id:str=Field(min_length=3,max_length=100); plate_number:str=Field(min_length=3,max_length=30); camera_id:str=Field(min_length=2,max_length=50); timestamp:datetime; speed_kmph:float=Field(ge=0,le=300); direction:str; vehicle_type:str="car"; violation:Optional[str]=None; ocr_confidence:float=Field(default=.95,ge=0,le=1); latitude:Optional[float]=Field(default=None,ge=-90,le=90); longitude:Optional[float]=Field(default=None,ge=-180,le=180); source:str="ANPR"
    @field_validator("event_id","camera_id","source")
    @classmethod
    def identifiers(cls,v): return v.strip().upper()
    @field_validator("plate_number")
    @classmethod
    def plate(cls,v):
        result=v.strip().upper().replace(" ","").replace("-","")
        if not result.isalnum(): raise ValueError("plate number must be alphanumeric")
        return result
    @field_validator("direction")
    @classmethod
    def direction(cls,v):
        values={"N":"NORTH","S":"SOUTH","E":"EAST","W":"WEST","NE":"NORTHEAST","NW":"NORTHWEST","SE":"SOUTHEAST","SW":"SOUTHWEST","NORTH":"NORTH","SOUTH":"SOUTH","EAST":"EAST","WEST":"WEST","NORTHEAST":"NORTHEAST","NORTHWEST":"NORTHWEST","SOUTHEAST":"SOUTHEAST","SOUTHWEST":"SOUTHWEST"}
        if v.strip().upper() not in values: raise ValueError("unsupported direction")
        return values[v.strip().upper()]
    @field_validator("timestamp")
    @classmethod
    def date(cls,v):
        v=v if v.tzinfo else v.replace(tzinfo=timezone.utc); now=datetime.now(timezone.utc)
        if v>now+timedelta(seconds=settings.FUTURE_TIMESTAMP_TOLERANCE_SECONDS): raise ValueError("timestamp exceeds permitted clock skew")
        if v<now-timedelta(days=settings.MAX_HISTORICAL_DAYS): raise ValueError("timestamp exceeds historical retention window")
        return v
class ANPREventResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    observation_id:str; event_id:str; plate_number:str; camera_id:str; road_id:str; observed_at:datetime; speed_kmph:float; direction:str; vehicle_type:str; violation:Optional[str]; ocr_confidence:float; latitude:float; longitude:float; source:str; created_at:datetime
class CameraResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    camera_id:str; camera_name:str; road_id:str; latitude:float; longitude:float; location_name:Optional[str]; direction:str; status:str
class AlertResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    alert_id:str; alert_type:str; severity:str; plate_number:Optional[str]; camera_id:Optional[str]; timestamp:datetime=Field(validation_alias="created_at"); description:str; status:str
class AlertUpdate(BaseModel): status:str
class BlacklistCreate(BaseModel):
    plate_number:str; reason:str=Field(min_length=1); reference_number:str=Field(min_length=1)
    @field_validator("plate_number")
    @classmethod
    def normalize(cls,v): return v.strip().upper().replace(" ","").replace("-","")
class BlacklistResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    blacklist_id:str; plate_number:str; reason:str; reference_number:str; status:str; created_at:datetime
class PaginatedResponse(BaseModel,Generic[T]): items:list[T]; total:int; limit:int; offset:int
class ModelUnavailableResponse(BaseModel): status:str="MODEL_NOT_AVAILABLE"; detail:str="No trained model artifact is configured."; model_version:Optional[str]=None
class TrafficVolumeResponse(BaseModel): total_vehicles_today:int; active_cameras:int; total_cameras:int; average_speed_city:float; congested_corridors:int; active_alerts:int; recorded_at:datetime
class SpeedAnalyticsResponse(BaseModel): road_id:str; road_name:str; average_speed:float; median_speed:float; min_speed:float; max_speed:float; percentile_85_speed:float; speed_limit:float; compliance_rate:float
class TrafficFlowResponse(BaseModel): source_camera:str; source_name:str; destination_camera:str; destination_name:str; vehicle_count:int; time_window:str; source_coords:list[float]; destination_coords:list[float]
class CongestionResponse(BaseModel): road_id:str; road_name:str; vehicle_count:int; average_speed:float; median_speed:float; speed_limit:float; capacity:int; congestion_score:float; congestion_level:str
class ODMatrixResponse(BaseModel): zones:list[str]; matrix:list[list[int]]; time_window:str
class TrajectoryWaypoint(BaseModel): camera_id:str; camera_name:str; timestamp:datetime; speed_kmph:float; latitude:float; longitude:float; delta_distance_km:float=0; delta_time_seconds:float=0; implied_speed_kmph:float=0; is_anomaly:bool=False; anomaly_reason:Optional[str]=None
class TrajectoryResponse(BaseModel): trajectory_id:str; plate_number:str; start_time:datetime; end_time:datetime; total_distance_km:float; average_speed_kmph:float; camera_count:int; plausibility_status:str; anomaly_notes:Optional[str]=None; route_geometry:list[list[float]]; waypoints:list[TrajectoryWaypoint]
