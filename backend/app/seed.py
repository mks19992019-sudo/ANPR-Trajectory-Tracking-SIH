"""Seeds reference configuration only. It never inserts ANPR observations."""
import uuid
from geoalchemy2.elements import WKTElement
from sqlalchemy.orm import Session
from backend.app.models.entities import Road, Camera, Blacklist
from generator.cameras_data import CAMERAS

ROADS = {
 "RD_001": ("Ajmer Expressway Corridor",80,6,3000), "RD_002": ("Mirza Ismail (MI) Arterial",50,4,1800), "RD_003": ("Jawaharlal Nehru (JL) Marg",60,6,2500), "RD_004": ("Airport VIP Expressway",70,4,2000), "RD_005": ("Tonk Road National Highway",60,6,2600), "RD_006": ("Jaipur-Delhi Highway",90,6,3200), "RD_007": ("Sikar Road Industrial Belt",50,4,1900), "RD_008": ("Vaishali Urban Corridor",45,4,1500), "RD_009": ("B2 Bypass Ring Expressway",80,6,2800), "RD_010": ("Heritage Walled City Spine",40,2,1100)}
def seed_database(db: Session) -> None:
    for road_id, (name, limit, lanes, capacity) in ROADS.items():
        if not db.get(Road, road_id):
            db.add(Road(road_id=road_id, road_name=name, speed_limit_kmph=limit, lanes=lanes, capacity_per_hour=capacity, geometry=WKTElement("LINESTRING(75.80 26.90,75.81 26.91)", srid=4326)))
    db.flush()
    for item in CAMERAS:
        road_id = item["road_id"].replace("RD_", "RD_0")
        if road_id not in ROADS:
            db.add(Road(road_id=road_id, road_name=f"Reference corridor {road_id}", speed_limit_kmph=item["limit"], lanes=2, capacity_per_hour=1200, geometry=WKTElement("LINESTRING(75.80 26.90,75.81 26.91)", srid=4326)))
        if not db.get(Camera, item["camera_id"]):
            lat, lon = item["lat"], item["lng"]
            db.add(Camera(camera_id=item["camera_id"], camera_name=item["name"], road_id=road_id, latitude=lat, longitude=lon, location_name=None, direction=item["direction"], status="ACTIVE", location=WKTElement(f"POINT({lon} {lat})", srid=4326)))
    for plate, reason, ref in [("DL01CZ9999", "Suspected stolen vehicle", "FIR #882/2026"), ("UP14BK8801", "Wanted in robbery investigation", "FIR #441/2026")]:
        if not db.query(Blacklist).filter_by(plate_number=plate).first(): db.add(Blacklist(blacklist_id=f"BL_{uuid.uuid4().hex[:12]}", plate_number=plate, reason=reason, reference_number=ref))
    db.commit()
