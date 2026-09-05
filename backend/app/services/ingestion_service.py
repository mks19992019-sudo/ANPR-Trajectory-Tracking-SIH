import hashlib, uuid
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from geoalchemy2.elements import WKTElement
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.models.entities import Camera, VehicleObservation
from backend.app.schemas.schemas import ANPREventCreate, ANPREventResponse
from backend.app.services.alert_service import AlertService
from backend.app.services.websocket_manager import ws_manager
class IngestionService:
 @staticmethod
 async def ingest_event(db:Session,event:ANPREventCreate)->ANPREventResponse:
    camera=db.get(Camera,event.camera_id)
    if not camera or camera.status=="OFFLINE": raise HTTPException(status_code=400,detail="camera is not an active registered checkpoint")
    if db.query(VehicleObservation).filter_by(event_id=event.event_id).first(): raise HTTPException(status_code=409,detail="Duplicate event_id already processed")
    # Observation dedupe is independent from event id: same normalized plate/camera/direction in a configurable temporal window.
    key=hashlib.sha256(f"{event.plate_number}|{camera.camera_id}|{event.direction}".encode()).hexdigest()
    window=timedelta(seconds=settings.OBSERVATION_DEDUP_SECONDS)
    duplicate=db.query(VehicleObservation).filter(VehicleObservation.deduplication_key==key,VehicleObservation.observed_at.between(event.timestamp-window,event.timestamp+window)).first()
    if duplicate: raise HTTPException(status_code=409,detail="Duplicate observation within configured observation deduplication window")
    lat=event.latitude if event.latitude is not None else camera.latitude; lon=event.longitude if event.longitude is not None else camera.longitude
    obs=VehicleObservation(observation_id=f"OBS_{uuid.uuid4().hex[:16]}",event_id=event.event_id,plate_number=event.plate_number,camera_id=camera.camera_id,road_id=camera.road_id,observed_at=event.timestamp,speed_kmph=event.speed_kmph,direction=event.direction,vehicle_type=event.vehicle_type.lower(),violation=event.violation,ocr_confidence=event.ocr_confidence,latitude=lat,longitude=lon,location=WKTElement(f"POINT({lon} {lat})",srid=4326),source=event.source,deduplication_key=key,created_at=datetime.now(timezone.utc))
    db.add(obs)
    try: db.flush()
    except IntegrityError:
      db.rollback(); raise HTTPException(status_code=409,detail="Duplicate event_id already processed")
    alerts=AlertService.evaluate_observation(db,obs,camera); db.commit(); db.refresh(obs)
    await ws_manager.broadcast("ANPR_EVENT",{"event_id":obs.event_id,"plate_number":obs.plate_number,"camera_id":obs.camera_id,"observed_at":obs.observed_at.isoformat(),"speed_kmph":obs.speed_kmph,"alerts_triggered":[a.alert_type for a in alerts]})
    return ANPREventResponse.model_validate(obs)
