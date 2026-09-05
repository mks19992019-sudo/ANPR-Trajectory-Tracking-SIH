from datetime import datetime,timedelta,timezone
import statistics
from sqlalchemy.orm import Session
from backend.app.models.entities import Road,VehicleObservation
from backend.app.schemas.schemas import CongestionResponse
class CongestionService:
 @staticmethod
 def calculate_road_congestion(db:Session,minutes:int=15):
  since=datetime.now(timezone.utc)-timedelta(minutes=minutes); result=[]
  for road in db.query(Road).order_by(Road.road_id):
   speeds=[x[0] for x in db.query(VehicleObservation.speed_kmph).filter(VehicleObservation.road_id==road.road_id,VehicleObservation.observed_at>=since)]
   volume=len(speeds); avg=statistics.mean(speeds) if speeds else 0; median=statistics.median(speeds) if speeds else 0
   capacity=road.capacity_per_hour*minutes/60
   score=0 if not volume or not capacity or not road.speed_limit_kmph else min(1.0,max(0.0,(volume/capacity)*(1-avg/road.speed_limit_kmph)))
   level="SEVERE" if score>=.8 else "HIGH" if score>=.6 else "MODERATE" if score>=.35 else "LOW"
   result.append(CongestionResponse(road_id=road.road_id,road_name=road.road_name,vehicle_count=volume,average_speed=round(avg,1),median_speed=round(median,1),speed_limit=road.speed_limit_kmph,capacity=int(capacity),congestion_score=round(score,3),congestion_level=level))
  return result
