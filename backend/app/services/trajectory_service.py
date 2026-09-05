from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from backend.app.models.entities import VehicleObservation, Camera
from backend.app.schemas.schemas import TrajectoryResponse, TrajectoryWaypoint
from backend.app.services.alert_service import haversine_distance_km
from backend.app.config import settings

class TrajectoryService:
    @staticmethod
    def reconstruct_trajectory(db: Session, plate_number: str) -> Optional[TrajectoryResponse]:
        """
        Reconstructs multi-hop spatial route for a vehicle from chronological ANPR observations.
        Performs temporal/spatial/speed plausibility checks to identify anomalies.
        """
        clean_plate = plate_number.strip().upper().replace(" ", "").replace("-", "")

        # 1. Fetch observations sorted chronologically
        observations = db.query(VehicleObservation).filter(
            VehicleObservation.plate_number == clean_plate
        ).order_by(VehicleObservation.timestamp.asc()).all()

        if not observations:
            return None

        # 2. Map Camera Coordinates
        camera_ids = {obs.camera_id for obs in observations}
        cameras = {cam.camera_id: cam for cam in db.query(Camera).filter(Camera.camera_id.in_(camera_ids)).all()}

        waypoints: list[TrajectoryWaypoint] = []
        route_coords: list[list[float]] = []
        total_distance_km = 0.0
        total_clocked_speed = 0.0

        plausibility_status = "NORMAL"
        anomaly_notes_list = []

        prev_obs = None
        prev_cam = None

        for idx, obs in enumerate(observations):
            cam = cameras.get(obs.camera_id)
            if not cam:
                continue

            lat, lon = cam.latitude, cam.longitude
            route_coords.append([lat, lon])
            total_clocked_speed += obs.speed_kmph

            delta_dist = 0.0
            delta_sec = 0.0
            implied_spd = 0.0
            is_anomaly = False
            anomaly_reason = None

            if prev_obs and prev_cam:
                delta_dist = haversine_distance_km(prev_cam.latitude, prev_cam.longitude, lat, lon)
                delta_sec = (obs.timestamp - prev_obs.timestamp).total_seconds()
                total_distance_km += delta_dist

                if delta_sec > 0:
                    implied_spd = (delta_dist / delta_sec) * 3600.0
                    
                    # Impossible velocity threshold
                    if implied_spd > settings.IMPOSSIBLE_SPEED_THRESHOLD_KMPH:
                        is_anomaly = True
                        plausibility_status = "PHYSICALLY_IMPOSSIBLE"
                        anomaly_reason = (
                            f"Physically impossible hop: Traveled {delta_dist:.1f} km in {delta_sec:.0f}s "
                            f"(implied velocity: {implied_spd:.1f} km/h). Potential cloned plate or sensor defect."
                        )
                        anomaly_notes_list.append(anomaly_reason)
                    elif implied_spd > settings.SUSPICIOUS_SPEED_THRESHOLD_KMPH:
                        is_anomaly = True
                        if plausibility_status != "PHYSICALLY_IMPOSSIBLE":
                            plausibility_status = "SUSPICIOUS"
                        anomaly_reason = f"Unusually rapid transition: implied velocity {implied_spd:.1f} km/h."
                        anomaly_notes_list.append(anomaly_reason)
                elif delta_dist > 0.5:
                    is_anomaly = True
                    plausibility_status = "PHYSICALLY_IMPOSSIBLE"
                    anomaly_reason = f"Simultaneous detection across distant checkpoints ({delta_dist:.1f} km apart in 0s)."
                    anomaly_notes_list.append(anomaly_reason)

            waypoints.append(TrajectoryWaypoint(
                camera_id=cam.camera_id,
                camera_name=cam.camera_name,
                timestamp=obs.timestamp,
                speed_kmph=obs.speed_kmph,
                latitude=lat,
                longitude=lon,
                delta_distance_km=round(delta_dist, 2),
                delta_time_seconds=round(delta_sec, 1),
                implied_speed_kmph=round(implied_spd, 1),
                is_anomaly=is_anomaly,
                anomaly_reason=anomaly_reason
            ))

            prev_obs = obs
            prev_cam = cam

        avg_speed = round(total_clocked_speed / len(observations), 1) if observations else 0.0
        anomaly_summary = " | ".join(anomaly_notes_list) if anomaly_notes_list else None

        return TrajectoryResponse(
            trajectory_id=f"TRJ_{clean_plate}_{int(observations[0].timestamp.timestamp())}",
            plate_number=clean_plate,
            start_time=observations[0].timestamp,
            end_time=observations[-1].timestamp,
            total_distance_km=round(total_distance_km, 2),
            average_speed_kmph=avg_speed,
            camera_count=len(waypoints),
            plausibility_status=plausibility_status,
            anomaly_notes=anomaly_summary,
            route_geometry=route_coords,
            waypoints=waypoints
        )
