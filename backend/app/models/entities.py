from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    Index
)
from backend.app.database import Base

class Road(Base):
    __tablename__ = "roads"

    road_id = Column(String(50), primary_key=True, index=True)
    road_name = Column(String(150), nullable=False)
    speed_limit = Column(Float, nullable=False, default=60.0)
    lanes = Column(Integer, nullable=False, default=4)
    capacity = Column(Integer, nullable=False, default=2000)
    geometry = Column(Text, nullable=True)  # GeoJSON / WKT LineString

class Camera(Base):
    __tablename__ = "cameras"

    camera_id = Column(String(50), primary_key=True, index=True)
    camera_name = Column(String(150), nullable=False)
    road_id = Column(String(50), ForeignKey("roads.road_id"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(String(200), nullable=True)
    direction = Column(String(20), nullable=False, default="NORTH")
    status = Column(String(30), nullable=False, default="ACTIVE")
    geometry = Column(Text, nullable=True)  # GeoJSON / WKT Point

class VehicleObservation(Base):
    __tablename__ = "vehicle_observations"

    observation_id = Column(String(80), primary_key=True, index=True)
    event_id = Column(String(80), unique=True, index=True, nullable=False)
    plate_number = Column(String(30), index=True, nullable=False)
    camera_id = Column(String(50), ForeignKey("cameras.camera_id"), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    speed_kmph = Column(Float, nullable=False)
    direction = Column(String(20), nullable=False)
    vehicle_type = Column(String(30), nullable=False, default="car")
    violation = Column(String(80), nullable=True)
    ocr_confidence = Column(Float, nullable=False, default=0.95)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_obs_plate_time", "plate_number", "timestamp"),
        Index("ix_obs_cam_time", "camera_id", "timestamp"),
        Index("ix_obs_dedup", "plate_number", "camera_id", "timestamp"),
    )

class Trajectory(Base):
    __tablename__ = "trajectories"

    trajectory_id = Column(String(80), primary_key=True, index=True)
    plate_number = Column(String(30), index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    route_geometry = Column(Text, nullable=False)  # JSON LineString coordinates
    distance = Column(Float, nullable=False, default=0.0)
    number_of_observations = Column(Integer, nullable=False, default=1)
    average_speed = Column(Float, nullable=False, default=0.0)
    plausibility_status = Column(String(50), nullable=False, default="NORMAL")  # NORMAL, SUSPICIOUS, PHYSICALLY_IMPOSSIBLE
    anomaly_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class TrafficMetric(Base):
    __tablename__ = "traffic_metrics"

    metric_id = Column(Integer, primary_key=True, autoincrement=True)
    road_id = Column(String(50), index=True, nullable=False)
    camera_id = Column(String(50), index=True, nullable=True)
    time_window = Column(String(20), nullable=False, default="15m")
    vehicle_count = Column(Integer, nullable=False, default=0)
    average_speed = Column(Float, nullable=False, default=0.0)
    median_speed = Column(Float, nullable=False, default=0.0)
    min_speed = Column(Float, nullable=False, default=0.0)
    max_speed = Column(Float, nullable=False, default=0.0)
    percentile_85_speed = Column(Float, nullable=False, default=0.0)
    congestion_score = Column(Float, nullable=False, default=0.0)
    congestion_level = Column(String(30), nullable=False, default="LOW")
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(80), primary_key=True, index=True)
    alert_type = Column(String(80), nullable=False, index=True)
    severity = Column(String(30), nullable=False, default="MEDIUM")
    plate_number = Column(String(30), index=True, nullable=False)
    camera_id = Column(String(50), index=True, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=False)
    status = Column(String(30), nullable=False, default="OPEN")  # OPEN, INVESTIGATING, RESOLVED

class Blacklist(Base):
    __tablename__ = "blacklist"

    plate_number = Column(String(30), primary_key=True, index=True)
    reason = Column(Text, nullable=False)
    reference_number = Column(String(80), nullable=False)
    status = Column(String(30), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
