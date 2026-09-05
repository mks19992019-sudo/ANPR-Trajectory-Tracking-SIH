from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone, timedelta
from backend.app.models.entities import VehicleObservation, Camera, Road
from backend.app.schemas.schemas import CongestionResponse

class CongestionService:
    @staticmethod
    def calculate_road_congestion(
        db: Session,
        minutes: int = 15
    ) -> List[CongestionResponse]:
        """
        Calculates corridor congestion scores from stored ANPR observations.
        Formula:
          Congestion Score = (V / C_scaled) * [ 0.3 + 0.7 * (1 - (v_avg / v_limit)) ]
        """
        since_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        roads = db.query(Road).order_by(Road.road_id.asc()).all()
        results: List[CongestionResponse] = []

        for road in roads:
            cam_ids = [c.camera_id for c in db.query(Camera.camera_id).filter(Camera.road_id == road.road_id).all()]
            
            if cam_ids:
                stats = db.query(
                    func.count(VehicleObservation.observation_id).label("count"),
                    func.avg(VehicleObservation.speed_kmph).label("avg_speed")
                ).filter(
                    VehicleObservation.camera_id.in_(cam_ids),
                    VehicleObservation.timestamp >= since_time
                ).first()

                vol = stats.count if stats and stats.count else 0
                avg_spd = float(stats.avg_speed) if stats and stats.avg_speed is not None else road.speed_limit
            else:
                vol = 0
                avg_spd = road.speed_limit

            # Scaled corridor capacity for the given time window
            scaled_capacity = max(50, int(road.capacity * (minutes / 60.0)))
            
            # Volume-to-capacity ratio
            vc_ratio = min(1.5, vol / scaled_capacity) if scaled_capacity > 0 else 0.0
            
            # Speed degradation factor
            speed_ratio = min(1.0, max(0.0, avg_spd / road.speed_limit)) if road.speed_limit > 0 else 1.0
            speed_degradation = 1.0 - speed_ratio

            # Congestion score calculation
            if vol == 0:
                score = 0.0
            else:
                raw_score = vc_ratio * (0.3 + 0.7 * speed_degradation)
                score = round(max(0.0, min(1.0, raw_score)), 2)

            # Categorize congestion level
            if score >= 0.80:
                level = "SEVERE"
            elif score >= 0.60:
                level = "HIGH"
            elif score >= 0.35:
                level = "MODERATE"
            else:
                level = "LOW"

            results.append(CongestionResponse(
                road_id=road.road_id,
                road_name=road.road_name,
                vehicle_count=vol,
                average_speed=round(avg_spd, 1),
                median_speed=round(avg_spd, 1),
                speed_limit=road.speed_limit,
                capacity=scaled_capacity,
                congestion_score=score,
                congestion_level=level
            ))

        return results
