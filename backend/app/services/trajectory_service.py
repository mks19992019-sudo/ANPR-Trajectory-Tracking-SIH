import uuid
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.models.entities import VehicleObservation
from backend.app.schemas.schemas import TrajectoryResponse,TrajectoryWaypoint
from backend.app.services.alert_service import haversine_distance_km
class TrajectoryService:
 @staticmethod
 def reconstruct_trajectory(db:Session,plate_number:str):
  plate=plate_number.strip().upper().replace(" ","").replace("-",""); observations=db.query(VehicleObservation).filter_by(plate_number=plate).order_by(VehicleObservation.observed_at).all()
  if not observations:return None
  # The most recent session is bounded by JOURNEY_GAP_MINUTES; old journeys are not silently joined.
  session=[observations[-1]]
  for x in reversed(observations[:-1]):
   if (session[0].observed_at-x.observed_at).total_seconds()>settings.JOURNEY_GAP_MINUTES*60: break
   session.insert(0,x)
  points=[]; distance=0; notes=[]; status="NORMAL"
  for i,x in enumerate(session):
   delta=seconds=implied=0; anomaly=False; reason=None
   if i:
    p=session[i-1];delta=haversine_distance_km(p.latitude,p.longitude,x.latitude,x.longitude);seconds=(x.observed_at-p.observed_at).total_seconds();implied=delta/seconds*3600 if seconds else float("inf");distance+=delta
    if implied>settings.IMPOSSIBLE_SPEED_THRESHOLD_KMPH: anomaly=True;status="PHYSICALLY_IMPOSSIBLE";reason=f"Data-quality anomaly: implied transition speed {implied:.1f} km/h.";notes.append(reason)
    elif implied>settings.SUSPICIOUS_SPEED_THRESHOLD_KMPH: anomaly=True;status="SUSPICIOUS";reason=f"Unusual transition speed {implied:.1f} km/h.";notes.append(reason)
   points.append(TrajectoryWaypoint(camera_id=x.camera_id,camera_name=x.camera.camera_name,timestamp=x.observed_at,speed_kmph=x.speed_kmph,latitude=x.latitude,longitude=x.longitude,delta_distance_km=round(delta,2),delta_time_seconds=seconds,implied_speed_kmph=round(implied,1),is_anomaly=anomaly,anomaly_reason=reason))
  return TrajectoryResponse(trajectory_id=f"TRJ_{uuid.uuid4().hex[:12]}",plate_number=plate,start_time=session[0].observed_at,end_time=session[-1].observed_at,total_distance_km=round(distance,2),average_speed_kmph=round(sum(x.speed_kmph for x in session)/len(session),1),camera_count=len(session),plausibility_status=status,anomaly_notes=" ".join(notes) or None,route_geometry=[[x.latitude,x.longitude] for x in session],waypoints=points)
