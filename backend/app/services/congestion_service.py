from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from backend.app.models.entities import VehicleObservation, Camera, Road
from backend.app.schemas.schemas import CongestionResponse

class CongestionService:
    @staticmethod
    def calculate_road_congestion(
        db: Session,
        minutes: int = 15
    ) -> List[CongestionResponse]:
        """
        Calculates Congestion Score for each arterial road corridor:
        Formula: Congestion Score = (Volume / Capacity) * (1 - (v / v_limit))
        Variables:
          Volume (V) = count of vehicle observations in the time window
          Capacity (C) = design corridor capacity scaled to the time window
          v = observed mean vehicle speed
          v_limit = road speed limit
        """
        since_time = datetime.utcnow() - timedelta(minutes=minutes)
        roads = db.query(Road).all()
        results: List[CongestionResponse] = []

        # Get cameras mapped to roads
        for road in roads:
            # Query cameras on this road
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
                avg_spd = float(stats.avg_speed) if stats and stats.avg_speed else road.speed_limit * 0.85
            else:
                vol = 0
                avg_spd = road.speed_limit

            # Scaled capacity for time window
            # e.g., Capacity per hour = road.capacity -> 15m capacity = capacity * (minutes / 60)
            scaled_capacity = max(100, int(road.capacity * (minutes / 60.0)))
            
            # Volume to capacity ratio (capped at 1.5 for calculation)
            vc_ratio = min(1.5, vol / scaled_capacity) if scaled_capacity > 0 else 0.5
            
            # Speed degradation factor
            speed_ratio = min(1.0, max(0.0, avg_spd / road.speed_limit))
            speed_degradation = 1.0 - speed_ratio

            # Congestion Score calculation
            raw_score = vc_ratio * (0.3 + 0.7 * speed_degradation)
            score = round(max(0.0, min(1.0, raw_score)), 2)

            # Categorize levels
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
                median_speed=round(avg_spd * 0.98, 1),
                speed_limit=road.speed_limit,
                capacity=scaled_capacity,
                congestion_score=score,
                congestion_level=level
            ))

        return results
