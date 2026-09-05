from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
import numpy as np
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.entities import VehicleObservation, Camera, Road, Alert
from backend.app.schemas.schemas import (
    TrafficVolumeResponse,
    SpeedAnalyticsResponse,
    TrafficFlowResponse,
    ODMatrixResponse
)
from backend.app.services.congestion_service import CongestionService

# Mapping roads to city geographic zones for OD Matrix analysis
ROAD_ZONE_MAP = {
    "RD_001": "Ajmer Expressway Zone",
    "RD_009": "Ajmer Expressway Zone",
    "RD_002": "Central MI Road",
    "RD_008": "Central MI Road",
    "RD_003": "JL Marg Corridor",
    "RD_004": "Airport South Zone",
    "RD_006": "Airport South Zone",
    "RD_005": "Delhi Highway North",
    "RD_007": "Delhi Highway North",
    "RD_010": "Delhi Highway North",
}

DEFAULT_ZONES = [
    "Ajmer Expressway Zone",
    "Central MI Road",
    "JL Marg Corridor",
    "Airport South Zone",
    "Delhi Highway North"
]

class TrafficService:
    @staticmethod
    def get_city_summary(db: Session) -> TrafficVolumeResponse:
        """
        Aggregates real-time city-wide traffic volume, active cameras, average flow speed,
        and current count of congested road corridors.
        """
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Total vehicle observations today
        total_veh = db.query(VehicleObservation).filter(VehicleObservation.timestamp >= today_start).count()
        if total_veh == 0:
            total_veh = db.query(VehicleObservation).count()

        active_cams = db.query(Camera).filter(Camera.status == "ACTIVE").count()
        total_cams = db.query(Camera).count()
        
        # Real average velocity
        avg_speed_res = db.query(func.avg(VehicleObservation.speed_kmph)).scalar()
        avg_speed = round(float(avg_speed_res), 1) if avg_speed_res is not None else 0.0

        # Real active alerts
        active_alerts = db.query(Alert).filter(Alert.status == "OPEN").count()

        # Real congested corridors calculated dynamically
        congestion_records = CongestionService.calculate_road_congestion(db, minutes=30)
        congested_count = sum(1 for c in congestion_records if c.congestion_level in ["HIGH", "SEVERE"])

        return TrafficVolumeResponse(
            total_vehicles_today=total_veh,
            active_cameras=active_cams,
            total_cameras=total_cams,
            average_speed_city=avg_speed,
            congested_corridors=congested_count,
            active_alerts=active_alerts,
            recorded_at=now
        )

    @staticmethod
    def get_speed_analytics(db: Session, hours: int = 1) -> List[SpeedAnalyticsResponse]:
        """
        Computes real speed percentiles (mean, median, 85th percentile, min, max)
        and speed limit compliance rates across all arterial corridors.
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        roads = db.query(Road).order_by(Road.road_id.asc()).all()
        results: List[SpeedAnalyticsResponse] = []

        for road in roads:
            cam_ids = [c.camera_id for c in db.query(Camera.camera_id).filter(Camera.road_id == road.road_id).all()]
            
            speeds = []
            if cam_ids:
                records = db.query(VehicleObservation.speed_kmph).filter(
                    VehicleObservation.camera_id.in_(cam_ids),
                    VehicleObservation.timestamp >= since
                ).all()
                speeds = [r[0] for r in records]

            if speeds:
                avg_spd = float(np.mean(speeds))
                med_spd = float(np.median(speeds))
                min_spd = float(np.min(speeds))
                max_spd = float(np.max(speeds))
                p85 = float(np.percentile(speeds, 85))
                compliant = sum(1 for s in speeds if s <= road.speed_limit)
                compliance_rate = round((compliant / len(speeds)) * 100.0, 1)
            else:
                avg_spd = 0.0
                med_spd = 0.0
                min_spd = 0.0
                max_spd = 0.0
                p85 = 0.0
                compliance_rate = 100.0

            results.append(SpeedAnalyticsResponse(
                road_id=road.road_id,
                road_name=road.road_name,
                average_speed=round(avg_spd, 1),
                median_speed=round(med_spd, 1),
                min_speed=round(min_spd, 1),
                max_speed=round(max_spd, 1),
                percentile_85_speed=round(p85, 1),
                speed_limit=road.speed_limit,
                compliance_rate=compliance_rate
            ))

        return results

    @staticmethod
    def get_camera_flows(db: Session, hours: int = 1) -> List[TrafficFlowResponse]:
        """
        Computes sequential transitions between checkpoints:
        For vehicles observed across multiple cameras, counts transitions CAM_A -> CAM_B.
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        cameras = {c.camera_id: c for c in db.query(Camera).all()}

        # Sample recent observations sorted by vehicle and timestamp
        obs_list = db.query(
            VehicleObservation.plate_number,
            VehicleObservation.camera_id,
            VehicleObservation.timestamp
        ).filter(VehicleObservation.timestamp >= since).order_by(
            VehicleObservation.plate_number,
            VehicleObservation.timestamp.asc()
        ).all()

        transitions: Dict[tuple, int] = {}
        prev_plate = None
        prev_cam = None

        for plate, cam_id, _ in obs_list:
            if plate == prev_plate and prev_cam and prev_cam != cam_id:
                pair = (prev_cam, cam_id)
                transitions[pair] = transitions.get(pair, 0) + 1
            prev_plate = plate
            prev_cam = cam_id

        results: List[TrafficFlowResponse] = []
        for (c1, c2), count in sorted(transitions.items(), key=lambda x: x[1], reverse=True)[:20]:
            cam1 = cameras.get(c1)
            cam2 = cameras.get(c2)
            if cam1 and cam2:
                results.append(TrafficFlowResponse(
                    source_camera=c1,
                    source_name=cam1.camera_name,
                    destination_camera=c2,
                    destination_name=cam2.camera_name,
                    vehicle_count=count,
                    time_window=f"{hours}h",
                    source_coords=[cam1.latitude, cam1.longitude],
                    destination_coords=[cam2.latitude, cam2.longitude]
                ))

        return results

    @staticmethod
    def get_od_matrix(db: Session, hours: int = 24) -> ODMatrixResponse:
        """
        Dynamically computes Origin-Destination (OD) commuter trip matrix
        from the first (Origin) and last (Destination) observed checkpoint zones of each vehicle.
        """
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        zones = list(DEFAULT_ZONES)
        zone_idx_map = {zone: idx for idx, zone in enumerate(zones)}
        
        # Camera to zone mapping
        cam_zone_map: Dict[str, str] = {}
        for cam in db.query(Camera).all():
            zone = ROAD_ZONE_MAP.get(cam.road_id, "Central MI Road")
            cam_zone_map[cam.camera_id] = zone

        matrix = [[0 for _ in range(len(zones))] for _ in range(len(zones))]

        # Query all observations in time window
        obs_records = db.query(
            VehicleObservation.plate_number,
            VehicleObservation.camera_id,
            VehicleObservation.timestamp
        ).filter(VehicleObservation.timestamp >= since).order_by(
            VehicleObservation.plate_number,
            VehicleObservation.timestamp.asc()
        ).all()

        # Group first and last camera per plate
        plate_trips: Dict[str, list] = {}
        for plate, cam_id, _ in obs_records:
            if plate not in plate_trips:
                plate_trips[plate] = [cam_id, cam_id]
            else:
                plate_trips[plate][1] = cam_id  # Update last observed camera

        # Tally OD matrix
        for plate, (orig_cam, dest_cam) in plate_trips.items():
            orig_zone = cam_zone_map.get(orig_cam, "Central MI Road")
            dest_zone = cam_zone_map.get(dest_cam, "Central MI Road")
            
            orig_idx = zone_idx_map.get(orig_zone, 1)
            dest_idx = zone_idx_map.get(dest_zone, 1)
            matrix[orig_idx][dest_idx] += 1

        return ODMatrixResponse(
            zones=zones,
            matrix=matrix,
            time_window=f"{hours}h"
        )

    @staticmethod
    def get_heatmap_data(db: Session) -> List[Dict[str, Any]]:
        """
        Returns GeoJSON-compatible point dataset with intensity normalized
        by actual camera detection counts.
        """
        cameras = db.query(Camera).all()
        cam_counts = db.query(
            VehicleObservation.camera_id,
            func.count(VehicleObservation.observation_id).label("cnt")
        ).group_by(VehicleObservation.camera_id).all()
        
        counts_dict = {c[0]: c[1] for c in cam_counts}
        max_count = max(counts_dict.values()) if counts_dict else 1

        features = []
        for cam in cameras:
            count = counts_dict.get(cam.camera_id, 0)
            intensity = round(min(1.0, count / max(1, max_count)), 3)
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [cam.longitude, cam.latitude]
                },
                "properties": {
                    "camera_id": cam.camera_id,
                    "camera_name": cam.camera_name,
                    "observation_count": count,
                    "intensity": intensity
                }
            })
        return features
