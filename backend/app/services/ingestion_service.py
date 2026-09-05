from datetime import datetime, timezone, timedelta
import uuid
import logging
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from backend.app.models.entities import VehicleObservation, Camera
from backend.app.schemas.schemas import ANPREventCreate, ANPREventResponse
from backend.app.services.alert_service import AlertService
from backend.app.services.websocket_manager import ws_manager
from backend.app.config import settings

logger = logging.getLogger("anpr.ingestion")

class IngestionService:
    @staticmethod
    async def ingest_event(db: Session, event_in: ANPREventCreate) -> ANPREventResponse:
        """
        Validates, deduplicates, and registers an ANPR event from the municipal camera network.
        Evaluates security and traffic alerts in real time and broadcasts to WebSocket clients.
        """
        # 1. Camera Registry Verification
        camera = db.query(Camera).filter(Camera.camera_id == event_in.camera_id).first()
        if not camera:
            logger.warning(f"Ingestion rejected: camera '{event_in.camera_id}' not found in registry.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Camera checkpoint '{event_in.camera_id}' not found in registry."
            )

        # 2. Idempotency Check: Event ID Uniqueness
        existing_event = db.query(VehicleObservation).filter(
            VehicleObservation.event_id == event_in.event_id
        ).first()
        if existing_event:
            logger.info(f"Duplicate event_id received: {event_in.event_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate event_id '{event_in.event_id}' already processed."
            )

        # 3. Deduplication Check: Sliding Window on (plate_number, camera_id)
        tolerance = timedelta(seconds=settings.DEDUP_WINDOW_SECONDS)
        duplicate_obs = db.query(VehicleObservation).filter(
            VehicleObservation.plate_number == event_in.plate_number,
            VehicleObservation.camera_id == event_in.camera_id,
            VehicleObservation.timestamp >= (event_in.timestamp - tolerance),
            VehicleObservation.timestamp <= (event_in.timestamp + tolerance)
        ).first()
        if duplicate_obs:
            logger.info(f"Duplicate observation detected: plate {event_in.plate_number} at {event_in.camera_id}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Duplicate observation detected for plate '{event_in.plate_number}' at camera '{event_in.camera_id}' within {settings.DEDUP_WINDOW_SECONDS}s sliding window."
            )

        # 4. Create Observation Record
        obs_id = f"OBS_{uuid.uuid4().hex[:10].upper()}"
        obs = VehicleObservation(
            observation_id=obs_id,
            event_id=event_in.event_id,
            plate_number=event_in.plate_number,
            camera_id=event_in.camera_id,
            timestamp=event_in.timestamp,
            speed_kmph=event_in.speed_kmph,
            direction=event_in.direction,
            vehicle_type=event_in.vehicle_type,
            violation=event_in.violation,
            ocr_confidence=event_in.ocr_confidence,
            created_at=datetime.now(timezone.utc)
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)

        # 5. Evaluate Security & Traffic Alerts
        alerts = AlertService.evaluate_observation(db, obs, camera)

        # 6. Real-time WebSocket Broadcast
        payload = {
            "event_id": obs.event_id,
            "observation_id": obs.observation_id,
            "plate_number": obs.plate_number,
            "camera_id": obs.camera_id,
            "camera_name": camera.camera_name,
            "timestamp": obs.timestamp.isoformat(),
            "speed_kmph": obs.speed_kmph,
            "direction": obs.direction,
            "vehicle_type": obs.vehicle_type,
            "violation": obs.violation,
            "confidence": obs.ocr_confidence,
            "alerts_triggered": [a.alert_type for a in alerts]
        }
        await ws_manager.broadcast("ANPR_EVENT", payload)

        return ANPREventResponse.model_validate(obs)
