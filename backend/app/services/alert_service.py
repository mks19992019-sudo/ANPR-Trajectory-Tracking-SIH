import math, uuid
from sqlalchemy.orm import Session
from backend.app.config import settings
from backend.app.models.entities import Alert, Blacklist, Camera, VehicleObservation
def haversine_distance_km(lat1,lon1,lat2,lon2):
    r=6371; a=math.sin(math.radians(lat2-lat1)/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return r*2*math.atan2(math.sqrt(a),math.sqrt(1-a))
class AlertService:
 @staticmethod
 def create(db, observation, alert_type, severity, description):
    alert=Alert(alert_id=f"ALT_{uuid.uuid4().hex[:16]}",observation_id=observation.observation_id,alert_type=alert_type,severity=severity,plate_number=observation.plate_number,camera_id=observation.camera_id,description=description)
    db.add(alert); return alert
 @classmethod
 def evaluate_observation(cls,db:Session,obs:VehicleObservation,camera:Camera):
    alerts=[]
    blacklist=db.query(Blacklist).filter_by(plate_number=obs.plate_number,status="ACTIVE").first()
    if blacklist: alerts.append(cls.create(db,obs,"BLACKLIST_MATCH","CRITICAL",f"Active blacklist match: {blacklist.reason} (reference {blacklist.reference_number})."))
    speed_limit=obs.road.speed_limit_kmph if obs.road else settings.DEFAULT_SPEED_LIMIT
    if obs.speed_kmph>speed_limit+settings.SPEED_VIOLATION_DELTA_KMPH: alerts.append(cls.create(db,obs,"OVERSPEEDING","WARNING",f"Observed {obs.speed_kmph:.1f} km/h; road limit is {speed_limit:.1f} km/h."))
    previous=db.query(VehicleObservation).filter(VehicleObservation.plate_number==obs.plate_number,VehicleObservation.observed_at<obs.observed_at).order_by(VehicleObservation.observed_at.desc()).first()
    if previous and previous.camera_id!=obs.camera_id:
      seconds=(obs.observed_at-previous.observed_at).total_seconds(); distance=haversine_distance_km(previous.latitude,previous.longitude,obs.latitude,obs.longitude); implied=(distance/seconds*3600) if seconds>0 else float("inf")
      if implied>settings.IMPOSSIBLE_SPEED_THRESHOLD_KMPH: alerts.append(cls.create(db,obs,"ANOMALOUS_MOVEMENT","CRITICAL",f"Data-quality anomaly: {distance:.1f} km in {seconds:.0f}s implies {implied:.1f} km/h. Review camera/OCR data; this is not a finding of criminal activity."))
    return alerts
