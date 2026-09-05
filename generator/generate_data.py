"""Synthetic external ANPR producer. This module deliberately has no backend/database imports."""
import argparse, random, uuid
from datetime import datetime, timedelta, timezone
import requests
from generator.cameras_data import CAMERA_DICT
from generator.routes_data import ROUTES
def run(api_url, api_key, events, duplicates):
    session=requests.Session(); headers={"X-API-Key":api_key} if api_key else {}
    sent=0; vehicles=[(f"RJ14{random.choice(['AB','CD','EF'])}{random.randint(1000,9999)}",random.choice(ROUTES)) for _ in range(max(5,events//3))]
    for plate, route in vehicles:
      start=datetime.now(timezone.utc)-timedelta(minutes=random.randint(1,20))
      for hop in route["hops"]:
       if sent>=events: return
       cam=CAMERA_DICT[hop["camera_id"]]; payload={"event_id":f"GEN_{uuid.uuid4().hex}","plate_number":plate,"camera_id":hop["camera_id"],"timestamp":(start+timedelta(minutes=hop["delay_min"])).isoformat(),"speed_kmph":round(hop["avg_speed"]+random.uniform(-5,8),1),"direction":cam["direction"],"vehicle_type":"car","ocr_confidence":.97,"source":"SYNTHETIC_ANPR"}
       response=session.post(api_url,json=payload,headers=headers,timeout=10); response.raise_for_status(); sent+=1
       if duplicates and random.random()<.1: session.post(api_url,json={**payload,"event_id":f"GEN_{uuid.uuid4().hex}"},headers=headers,timeout=10)
if __name__=="__main__":
 p=argparse.ArgumentParser();p.add_argument("--url",default="http://localhost:8000/api/v1/events");p.add_argument("--api-key",default="");p.add_argument("--events",type=int,default=100);p.add_argument("--duplicates",action="store_true");a=p.parse_args();run(a.url,a.api_key,a.events,a.duplicates)
