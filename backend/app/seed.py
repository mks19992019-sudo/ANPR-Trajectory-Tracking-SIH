import json
from datetime import datetime, timedelta
import uuid
from sqlalchemy.orm import Session
from backend.app.models.entities import Camera, Road, VehicleObservation, Blacklist, Alert

# 25 Simulated Checkpoints
SEED_CAMERAS = [
  {"camera_id": "CAM_001", "camera_name": "Ajmer Road Flyover Entrance", "road_id": "RD_01", "latitude": 26.8925, "longitude": 75.7621, "location": "Civil Lines West", "direction": "WEST", "status": "ACTIVE"},
  {"camera_id": "CAM_002", "camera_name": "Ajmer Road - 200ft Bypass Junction", "road_id": "RD_01", "latitude": 26.8850, "longitude": 75.7310, "location": "Heerapura Circle", "direction": "SOUTHWEST", "status": "ACTIVE"},
  {"camera_id": "CAM_003", "camera_name": "MI Road - Panch Batti Intersection", "road_id": "RD_02", "latitude": 26.9188, "longitude": 75.8115, "location": "MI Road Central", "direction": "EAST", "status": "ACTIVE"},
  {"camera_id": "CAM_004", "camera_name": "MI Road - Ajmeri Gate Chauraha", "road_id": "RD_02", "latitude": 26.9172, "longitude": 75.8205, "location": "Ajmeri Gate", "direction": "NORTHEAST", "status": "ACTIVE"},
  {"camera_id": "CAM_005", "camera_name": "JL Marg - Birla Mandir Crossing", "road_id": "RD_03", "latitude": 26.8920, "longitude": 75.8155, "location": "Tilak Nagar", "direction": "SOUTH", "status": "ACTIVE"},
  {"camera_id": "CAM_006", "camera_name": "JL Marg - Rajasthan Univ Main Gate", "road_id": "RD_03", "latitude": 26.8805, "longitude": 75.8140, "location": "Gandhinagar", "direction": "SOUTH", "status": "ACTIVE"},
  {"camera_id": "CAM_007", "camera_name": "JL Marg - World Trade Park Crossing", "road_id": "RD_03", "latitude": 26.8530, "longitude": 75.8052, "location": "Malviya Nagar", "direction": "SOUTH", "status": "ACTIVE"},
  {"camera_id": "CAM_008", "camera_name": "Airport Road - Terminal 2 Arrival", "road_id": "RD_04", "latitude": 26.8285, "longitude": 75.8050, "location": "Jaipur Airport Gate", "direction": "SOUTHEAST", "status": "ACTIVE"},
  {"camera_id": "CAM_009", "camera_name": "Tonk Road - Rambagh Circle Checkpoint", "road_id": "RD_05", "latitude": 26.8962, "longitude": 75.8068, "location": "Rambagh", "direction": "SOUTH", "status": "ACTIVE"},
  {"camera_id": "CAM_010", "camera_name": "Tonk Road - Gopalpura Bypass Underpass", "road_id": "RD_05", "latitude": 26.8625, "longitude": 75.7932, "location": "Gopalpura Flyover", "direction": "SOUTH", "status": "ACTIVE"},
  {"camera_id": "CAM_011", "camera_name": "Tonk Road - Sanganer Flyover Entry", "road_id": "RD_05", "latitude": 26.8152, "longitude": 75.7720, "location": "Sanganer Town", "direction": "SOUTHWEST", "status": "ACTIVE"},
  {"camera_id": "CAM_012", "camera_name": "Delhi Highway - Transport Nagar Toll", "road_id": "RD_06", "latitude": 26.9125, "longitude": 75.8562, "location": "Ghat Ki Guni Tunnel", "direction": "NORTHEAST", "status": "ACTIVE"},
  {"camera_id": "CAM_013", "camera_name": "Delhi Highway - Sisodia Rani Garden", "road_id": "RD_06", "latitude": 26.8995, "longitude": 75.8655, "location": "Kunda Corridor", "direction": "EAST", "status": "ACTIVE"},
  {"camera_id": "CAM_014", "camera_name": "Sikar Road - Chomu Pulia Junction", "road_id": "RD_07", "latitude": 26.9632, "longitude": 75.7750, "location": "Vidyadhar Nagar North", "direction": "NORTHWEST", "status": "ACTIVE"},
  {"camera_id": "CAM_015", "camera_name": "Sikar Road - VKI Area Gate 1", "road_id": "RD_07", "latitude": 26.9850, "longitude": 75.7610, "location": "Vishwakarma Ind Area", "direction": "NORTH", "status": "WARNING"},
  {"camera_id": "CAM_016", "camera_name": "Queens Road - Vaishali Police Chowki", "road_id": "RD_08", "latitude": 26.9045, "longitude": 75.7482, "location": "Vaishali Nagar", "direction": "NORTH", "status": "ACTIVE"},
  {"camera_id": "CAM_017", "camera_name": "Kings Road - Nirman Nagar Square", "road_id": "RD_08", "latitude": 26.8912, "longitude": 75.7510, "location": "Nirman Nagar", "direction": "SOUTH", "status": "ACTIVE"},
  {"camera_id": "CAM_018", "camera_name": "B2 Bypass - Shipra Path Crossroad", "road_id": "RD_09", "latitude": 26.8480, "longitude": 75.7795, "location": "Mansarovar Metro", "direction": "EAST", "status": "ACTIVE"},
  {"camera_id": "CAM_019", "camera_name": "B2 Bypass - Jawahar Circle North", "road_id": "RD_09", "latitude": 26.8475, "longitude": 75.8015, "location": "Jawahar Circle", "direction": "EAST", "status": "ACTIVE"},
  {"camera_id": "CAM_020", "camera_name": "Hawa Mahal Walled City Entry", "road_id": "RD_10", "latitude": 26.9240, "longitude": 75.8267, "location": "Badi Chaupar", "direction": "NORTH", "status": "ACTIVE"},
  {"camera_id": "CAM_021", "camera_name": "Johari Bazaar - Sanganeri Gate", "road_id": "RD_10", "latitude": 26.9160, "longitude": 75.8242, "location": "Johari Bazaar South", "direction": "NORTH", "status": "ACTIVE"},
  {"camera_id": "CAM_022", "camera_name": "Agra Road - Ghat Gate Exit", "road_id": "RD_11", "latitude": 26.9100, "longitude": 75.8350, "location": "Ghat Gate Circle", "direction": "SOUTHEAST", "status": "ACTIVE"},
  {"camera_id": "CAM_023", "camera_name": "Jhotwara Road - Elevated Road Start", "road_id": "RD_12", "latitude": 26.9380, "longitude": 75.7725, "location": "Railway Station North", "direction": "WEST", "status": "OFFLINE"},
  {"camera_id": "CAM_024", "camera_name": "Amer Road - Jal Mahal Viewpoint", "road_id": "RD_13", "latitude": 26.9535, "longitude": 75.8450, "location": "Man Sagar Lake", "direction": "NORTH", "status": "ACTIVE"},
  {"camera_id": "CAM_025", "camera_name": "Amer Road - Elephant Village Entry", "road_id": "RD_13", "latitude": 26.9855, "longitude": 75.8512, "location": "Amer Fort Foothills", "direction": "NORTHEAST", "status": "ACTIVE"},
]

SEED_ROADS = [
  {"road_id": "RD_01", "road_name": "Ajmer Expressway Corridor", "speed_limit": 80.0, "lanes": 6, "capacity": 3000, "geometry": json.dumps([[26.8925, 75.7621], [26.8850, 75.7310]])},
  {"road_id": "RD_02", "road_name": "Mirza Ismail (MI) Arterial", "speed_limit": 50.0, "lanes": 4, "capacity": 1800, "geometry": json.dumps([[26.9188, 75.8115], [26.9172, 75.8205]])},
  {"road_id": "RD_03", "road_name": "Jawaharlal Nehru (JL) Marg", "speed_limit": 60.0, "lanes": 6, "capacity": 2500, "geometry": json.dumps([[26.8920, 75.8155], [26.8805, 75.8140], [26.8530, 75.8052]])},
  {"road_id": "RD_04", "road_name": "Airport VIP Expressway", "speed_limit": 70.0, "lanes": 4, "capacity": 2000, "geometry": json.dumps([[26.8530, 75.8052], [26.8285, 75.8050]])},
  {"road_id": "RD_05", "road_name": "Tonk Road National Highway", "speed_limit": 60.0, "lanes": 6, "capacity": 2600, "geometry": json.dumps([[26.8962, 75.8068], [26.8625, 75.7932], [26.8152, 75.7720]])},
  {"road_id": "RD_06", "road_name": "Jaipur-Delhi Highway", "speed_limit": 90.0, "lanes": 6, "capacity": 3200, "geometry": json.dumps([[26.9125, 75.8562], [26.8995, 75.8655]])},
  {"road_id": "RD_07", "road_name": "Sikar Road Industrial Belt", "speed_limit": 50.0, "lanes": 4, "capacity": 1900, "geometry": json.dumps([[26.9632, 75.7750], [26.9850, 75.7610]])},
  {"road_id": "RD_08", "road_name": "Vaishali Urban Corridor", "speed_limit": 45.0, "lanes": 4, "capacity": 1500, "geometry": json.dumps([[26.9045, 75.7482], [26.8912, 75.7510]])},
  {"road_id": "RD_09", "road_name": "B2 Bypass Ring Expressway", "speed_limit": 80.0, "lanes": 6, "capacity": 2800, "geometry": json.dumps([[26.8480, 75.7795], [26.8475, 75.8015]])},
  {"road_id": "RD_10", "road_name": "Heritage Walled City Spine", "speed_limit": 40.0, "lanes": 2, "capacity": 1100, "geometry": json.dumps([[26.9240, 75.8267], [26.9160, 75.8242]])},
]

def seed_database(db: Session):
    # Check if already seeded
    if db.query(Camera).count() > 0:
        return

    # 1. Seed Roads
    for r in SEED_ROADS:
        road = Road(**r)
        db.add(road)
    db.commit()

    # 2. Seed Cameras
    for c in SEED_CAMERAS:
        cam = Camera(
            camera_id=c["camera_id"],
            camera_name=c["camera_name"],
            road_id=c["road_id"],
            latitude=c["latitude"],
            longitude=c["longitude"],
            location=c["location"],
            direction=c["direction"],
            status=c["status"],
            geometry=json.dumps({"type": "Point", "coordinates": [c["longitude"], c["latitude"]]})
        )
        db.add(cam)
    db.commit()

    # 3. Seed Blacklist
    blacklist_records = [
        Blacklist(plate_number="DL01CZ9999", reason="Suspected Stolen Vehicle / IPC Section 379", reference_number="FIR #882/2026", status="ACTIVE"),
        Blacklist(plate_number="UP14BK8801", reason="Wanted in Highway Robbery Case", reference_number="FIR #441/2026", status="ACTIVE"),
    ]
    for b in blacklist_records:
        db.add(b)
    db.commit()

    # 4. Deterministic Demo Vehicle Scenarios
    now = datetime.utcnow()
    
    # Scenario 1: Normal Vehicle RJ14AB1234
    # Route: CAM_005 -> CAM_006 -> CAM_007 -> CAM_008
    t0 = now - timedelta(minutes=45)
    scenario_1 = [
        ("EVT_S1_01", "RJ14AB1234", "CAM_005", t0, 48.0, "SOUTH", "car", None, 0.98),
        ("EVT_S1_02", "RJ14AB1234", "CAM_006", t0 + timedelta(minutes=7, seconds=15), 51.5, "SOUTH", "car", None, 0.96),
        ("EVT_S1_03", "RJ14AB1234", "CAM_007", t0 + timedelta(minutes=20, seconds=30), 56.0, "SOUTH", "car", None, 0.97),
        ("EVT_S1_04", "RJ14AB1234", "CAM_008", t0 + timedelta(minutes=33, seconds=0), 54.2, "SOUTHEAST", "car", None, 0.99),
    ]

    # Scenario 2: Blacklisted Vehicle DL01CZ9999
    # Route: CAM_012 -> CAM_004 -> CAM_003
    t1 = now - timedelta(minutes=30)
    scenario_2 = [
        ("EVT_S2_01", "DL01CZ9999", "CAM_012", t1, 45.0, "NORTHEAST", "car", None, 0.97),
        ("EVT_S2_02", "DL01CZ9999", "CAM_004", t1 + timedelta(minutes=18, seconds=40), 39.5, "NORTHEAST", "car", None, 0.96),
        ("EVT_S2_03", "DL01CZ9999", "CAM_003", t1 + timedelta(minutes=30, seconds=12), 41.8, "EAST", "car", None, 0.98),
    ]

    # Scenario 3: Physically Impossible Movement HR26XY4040
    # CAM_011 to CAM_015 in 90 seconds (14.8 km distance = 592 km/h)
    t2 = now - timedelta(minutes=15)
    scenario_3 = [
        ("EVT_S3_01", "HR26XY4040", "CAM_011", t2, 60.0, "SOUTHWEST", "truck", None, 0.95),
        ("EVT_S3_02", "HR26XY4040", "CAM_015", t2 + timedelta(seconds=90), 58.0, "NORTH", "truck", None, 0.94),
    ]

    # Overspeeding Demo RJ14GE8819 on Ajmer Road
    scenario_4 = [
        ("EVT_S4_01", "RJ14GE8819", "CAM_001", now - timedelta(minutes=10), 112.4, "WEST", "car", "OVERSPEEDING", 0.99),
    ]

    for item in scenario_1 + scenario_2 + scenario_3 + scenario_4:
        eid, plate, cam, ts, spd, direct, vtype, viol, conf = item
        obs = VehicleObservation(
            observation_id=f"OBS_{uuid.uuid4().hex[:10].upper()}",
            event_id=eid,
            plate_number=plate,
            camera_id=cam,
            timestamp=ts,
            speed_kmph=spd,
            direction=direct,
            vehicle_type=vtype,
            violation=viol,
            ocr_confidence=conf,
            created_at=datetime.utcnow()
        )
        db.add(obs)
    db.commit()

    # Create matching Alerts for Scenarios 2, 3, 4
    alerts = [
        Alert(
            alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
            alert_type="BLACKLIST_MATCH",
            severity="CRITICAL",
            plate_number="DL01CZ9999",
            camera_id="CAM_003",
            timestamp=t1 + timedelta(minutes=30, seconds=12),
            description="Blacklisted Vehicle Detected! Reason: Suspected Stolen Vehicle / IPC Section 379 (Ref: FIR #882/2026)",
            status="OPEN"
        ),
        Alert(
            alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
            alert_type="ANOMALOUS_MOVEMENT",
            severity="CRITICAL",
            plate_number="HR26XY4040",
            camera_id="CAM_015",
            timestamp=t2 + timedelta(seconds=90),
            description="Physically impossible movement: Traveled 14.8 km in 90s implying velocity of 592 km/h. Possible cloned plate / data anomaly.",
            status="OPEN"
        ),
        Alert(
            alert_id=f"ALT_{uuid.uuid4().hex[:8].upper()}",
            alert_type="OVERSPEEDING",
            severity="WARNING",
            plate_number="RJ14GE8819",
            camera_id="CAM_001",
            timestamp=now - timedelta(minutes=10),
            description="Overspeeding Violation: Clocked at 112.4 km/h on corridor with limit 80 km/h (+32.4 km/h)",
            status="OPEN"
        ),
    ]
    for a in alerts:
        db.add(a)
    db.commit()

    # Baseline ambient traffic observations across cameras
    prefixes = ["RJ14", "RJ45", "DL08", "HR26", "UP16"]
    letters = ["AB", "CD", "EF", "GH", "JK", "LM", "PZ"]
    vtypes = ["car", "car", "car", "truck", "bus", "motorcycle", "van"]
    
    ambient_count = 0
    for cam in SEED_CAMERAS:
        for i in range(12):
            ambient_count += 1
            p = f"{prefixes[i % len(prefixes)]}{letters[(i + ambient_count) % len(letters)]}{1000 + (i * 37) % 8999}"
            t = now - timedelta(minutes=(i * 4 + ambient_count % 5))
            spd = 35.0 + (ambient_count * 7) % 45
            viol = "OVERSPEEDING" if spd > 85.0 else None
            obs = VehicleObservation(
                observation_id=f"OBS_AMB_{ambient_count:04d}",
                event_id=f"EVT_AMB_{ambient_count:05d}",
                plate_number=p,
                camera_id=cam["camera_id"],
                timestamp=t,
                speed_kmph=spd,
                direction=cam["direction"],
                vehicle_type=vtypes[ambient_count % len(vtypes)],
                violation=viol,
                ocr_confidence=0.92 + (ambient_count % 7) * 0.01,
                created_at=datetime.utcnow()
            )
            db.add(obs)
    db.commit()
