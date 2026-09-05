import math
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from backend.app.models.entities import Alert, Blacklist, VehicleObservation, Camera, Road
from backend.app.config import settings

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Computes great-circle distance in kilometers."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

class AlertService:
    @staticmethod
    def evaluate_observation(db: Session, obs: VehicleObservation, camera: Camera) -> list[Alert]:
        alerts_created = []

        # 1. Blacklist Check
        blacklist_entry = db.query(Blacklist).filter(
            Blacklist.plate_number == obs.plate_number,
            Blacklist.status == "ACTIVE"
        ).first()

        if blacklist_entry:
            alert = Alert(
                alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
                alert_type="BLACKLIST_MATCH",
                severity="CRITICAL",
                plate_number=obs.plate_number,
                camera_id=obs.camera_id,
                timestamp=obs.timestamp,
                description=f"Blacklisted Vehicle Detected! Reason: {blacklist_entry.reason} (Ref: {blacklist_entry.reference_number})",
                status="OPEN"
            )
            db.add(alert)
            alerts_created.append(alert)

        # 2. Overspeeding Check
        speed_limit = settings.DEFAULT_SPEED_LIMIT
        if camera.road_id:
            road = db.query(Road).filter(Road.road_id == camera.road_id).first()
            if road and road.speed_limit:
                speed_limit = road.speed_limit

        if obs.speed_kmph > (speed_limit + 15.0):
            excess = obs.speed_kmph - speed_limit
            alert = Alert(
                alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
                alert_type="OVERSPEEDING",
                severity="WARNING",
                plate_number=obs.plate_number,
                camera_id=obs.camera_id,
                timestamp=obs.timestamp,
                description=f"Overspeeding Violation: Clocked at {obs.speed_kmph:.1f} km/h on corridor with limit {speed_limit:.0f} km/h (+{excess:.1f} km/h)",
                status="OPEN"
            )
            db.add(alert)
            alerts_created.append(alert)

        # 3. Impossible Movement / Anomaly Check against previous observation
        prev_obs = db.query(VehicleObservation).filter(
            VehicleObservation.plate_number == obs.plate_number,
            VehicleObservation.timestamp < obs.timestamp
        ).order_by(VehicleObservation.timestamp.desc()).first()

        if prev_obs and prev_obs.camera_id != obs.camera_id:
            prev_cam = db.query(Camera).filter(Camera.camera_id == prev_obs.camera_id).first()
            if prev_cam:
                dist_km = haversine_distance_km(prev_cam.latitude, prev_cam.longitude, camera.latitude, camera.longitude)
                time_delta_sec = (obs.timestamp - prev_obs.timestamp).total_seconds()
                
                if time_delta_sec > 0:
                    implied_speed = (dist_km / time_delta_sec) * 3600.0
                    if implied_speed > settings.IMPOSSIBLE_SPEED_THRESHOLD_KMPH:
                        alert = Alert(
                            alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
                            alert_type="ANOMALOUS_MOVEMENT",
                            severity="CRITICAL",
                            plate_number=obs.plate_number,
                            camera_id=obs.camera_id,
                            timestamp=obs.timestamp,
                            description=(
                                f"Physically impossible movement: Traveled {dist_km:.1f} km in {time_delta_sec:.0f}s "
                                f"implying velocity of {implied_speed:.1f} km/h. Possible cloned plate / data anomaly."
                            ),
                            status="OPEN"
                        )
                        db.add(alert)
                        alerts_created.append(alert)

        db.commit()
        return alerts_created
