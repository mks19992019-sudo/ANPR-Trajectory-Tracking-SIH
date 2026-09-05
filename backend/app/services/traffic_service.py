from datetime import datetime,timedelta,timezone
import statistics
from sqlalchemy import func
from sqlalchemy.orm import Session
from backend.app.models.entities import Alert,Camera,Road,VehicleObservation
from backend.app.schemas.schemas import TrafficVolumeResponse,SpeedAnalyticsResponse,TrafficFlowResponse,ODMatrixResponse
from backend.app.services.congestion_service import CongestionService
class TrafficService:
 @staticmethod
 def get_city_summary(db):
  now=datetime.now(timezone.utc); start=now.replace(hour=0,minute=0,second=0,microsecond=0); n=db.query(VehicleObservation).filter(VehicleObservation.observed_at>=start).count(); avg=db.query(func.avg(VehicleObservation.speed_kmph)).scalar() or 0; congestion=CongestionService.calculate_road_congestion(db,30)
  return TrafficVolumeResponse(total_vehicles_today=n,active_cameras=db.query(Camera).filter_by(status="ACTIVE").count(),total_cameras=db.query(Camera).count(),average_speed_city=round(float(avg),1),congested_corridors=sum(x.congestion_level in ("HIGH","SEVERE") for x in congestion),active_alerts=db.query(Alert).filter_by(status="OPEN").count(),recorded_at=now)
 @staticmethod
 def get_speed_analytics(db,hours=1):
  since=datetime.now(timezone.utc)-timedelta(hours=hours); out=[]
  for r in db.query(Road):
   speeds=[x[0] for x in db.query(VehicleObservation.speed_kmph).filter_by(road_id=r.road_id).filter(VehicleObservation.observed_at>=since)]
   vals=sorted(speeds); n=len(vals); p85=vals[min(n-1,int(.85*(n-1)))] if n else 0
   out.append(SpeedAnalyticsResponse(road_id=r.road_id,road_name=r.road_name,average_speed=round(statistics.mean(vals),1) if n else 0,median_speed=round(statistics.median(vals),1) if n else 0,min_speed=min(vals) if n else 0,max_speed=max(vals) if n else 0,percentile_85_speed=p85,speed_limit=r.speed_limit_kmph,compliance_rate=round(100*sum(v<=r.speed_limit_kmph for v in vals)/n,1) if n else 0))
  return out
 @staticmethod
 def get_camera_flows(db,hours=1):
  since=datetime.now(timezone.utc)-timedelta(hours=hours); rows=db.query(VehicleObservation).filter(VehicleObservation.observed_at>=since).order_by(VehicleObservation.plate_number,VehicleObservation.observed_at).all(); cams={x.camera_id:x for x in db.query(Camera)}; counts={}; prior={}
  for x in rows:
   p=prior.get(x.plate_number)
   if p and p.camera_id!=x.camera_id: counts[(p.camera_id,x.camera_id)]=counts.get((p.camera_id,x.camera_id),0)+1
   prior[x.plate_number]=x
  return [TrafficFlowResponse(source_camera=a,source_name=cams[a].camera_name,destination_camera=b,destination_name=cams[b].camera_name,vehicle_count=n,time_window=f"{hours}h",source_coords=[cams[a].latitude,cams[a].longitude],destination_coords=[cams[b].latitude,cams[b].longitude]) for (a,b),n in counts.items()]
 @staticmethod
 def get_od_matrix(db,hours=24):
  roads=[r.road_id for r in db.query(Road).order_by(Road.road_id)]; index={r:i for i,r in enumerate(roads)}; matrix=[[0]*len(roads) for _ in roads]; since=datetime.now(timezone.utc)-timedelta(hours=hours); grouped={}
  for x in db.query(VehicleObservation).filter(VehicleObservation.observed_at>=since).order_by(VehicleObservation.plate_number,VehicleObservation.observed_at): grouped.setdefault(x.plate_number,[]).append(x.road_id)
  for route in grouped.values():
   if len(route)>1: matrix[index[route[0]]][index[route[-1]]]+=1
  return ODMatrixResponse(zones=roads,matrix=matrix,time_window=f"{hours}h")
 @staticmethod
 def get_heatmap_data(db):
  counts=dict(db.query(VehicleObservation.camera_id,func.count()).group_by(VehicleObservation.camera_id)); maximum=max(counts.values(),default=1)
  return [{"type":"Feature","geometry":{"type":"Point","coordinates":[c.longitude,c.latitude]},"properties":{"camera_id":c.camera_id,"camera_name":c.camera_name,"observation_count":counts.get(c.camera_id,0),"intensity":counts.get(c.camera_id,0)/maximum}} for c in db.query(Camera)]
