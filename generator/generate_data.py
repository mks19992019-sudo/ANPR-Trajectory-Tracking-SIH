import argparse
import random
import uuid
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to sys.path so we can import backend
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal, Base, engine
from backend.app.models.entities import Camera, Road, VehicleObservation, Blacklist, Alert
from backend.app.seed import seed_database
from generator.cameras_data import CAMERAS, CAMERA_DICT
from generator.routes_data import ROUTES

PREFIXES = ["RJ14", "RJ45", "DL01", "DL08", "HR26", "UP16", "GJ01", "MH02"]
LETTERS = ["AB", "CD", "EF", "GH", "JK", "LM", "PZ", "XY", "RS"]
VTYPES = ["car", "car", "car", "truck", "bus", "motorcycle", "van"]

def generate_random_plate():
    return f"{random.choice(PREFIXES)}{random.choice(LETTERS)}{random.randint(1000, 9999)}"

def generate_batch_data(
    num_events: int = 1000,
    num_vehicles: int = 200,
    anomaly_pct: float = 3.0,
    duplicate_pct: float = 2.0
):
    print(f"[*] Connecting to database and verifying seed data...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    seed_database(db)

    print(f"[*] Generating {num_events} realistic ANPR events across {num_vehicles} synthetic vehicles...")
    
    # Pre-generate vehicle pool
    vehicles = []
    for i in range(num_vehicles):
        vehicles.append({
            "plate": generate_random_plate(),
            "type": random.choice(VTYPES),
            "route": random.choice(ROUTES)
        })

    now = datetime.utcnow()
    generated_count = 0
    duplicate_count = 0
    anomaly_count = 0

    while generated_count < num_events:
        veh = random.choice(vehicles)
        route = veh["route"]
        
        # Vehicle starts its route sometime in the last 6 hours
        route_start_time = now - timedelta(minutes=random.randint(5, 360))

        cumulative_min = 0
        prev_obs = None
        for hop in route["hops"]:
            if generated_count >= num_events:
                break

            cumulative_min += hop["delay_min"] + random.randint(-1, 2)
            obs_time = route_start_time + timedelta(minutes=max(0, cumulative_min))

            camera = CAMERA_DICT[hop["camera_id"]]
            
            # Speed logic with slight variance
            base_speed = hop["avg_speed"] + random.uniform(-6.0, 8.0)
            is_overspeeding = random.random() < 0.08
            if is_overspeeding:
                base_speed = camera["limit"] + random.uniform(15.0, 35.0)
                violation = "OVERSPEEDING"
            else:
                violation = None

            # OCR Confidence
            is_low_conf = random.random() < 0.03
            confidence = random.uniform(0.55, 0.72) if is_low_conf else random.uniform(0.92, 0.99)

            event_id = f"EVT_{uuid.uuid4().hex[:8].upper()}"
            obs_id = f"OBS_{uuid.uuid4().hex[:10].upper()}"

            obs = VehicleObservation(
                observation_id=obs_id,
                event_id=event_id,
                plate_number=veh["plate"],
                camera_id=hop["camera_id"],
                timestamp=obs_time,
                speed_kmph=round(base_speed, 1),
                direction=camera["direction"],
                vehicle_type=veh["type"],
                violation=violation,
                ocr_confidence=round(confidence, 2),
                created_at=datetime.utcnow()
            )
            db.add(obs)
            generated_count += 1
            prev_obs = obs

            # Duplicate generation
            if random.random() < (duplicate_pct / 100.0) and generated_count < num_events:
                dup_obs = VehicleObservation(
                    observation_id=f"OBS_{uuid.uuid4().hex[:10].upper()}",
                    event_id=f"EVT_{uuid.uuid4().hex[:8].upper()}",
                    plate_number=veh["plate"],
                    camera_id=hop["camera_id"],
                    timestamp=obs_time + timedelta(seconds=random.randint(1, 3)),
                    speed_kmph=round(base_speed, 1),
                    direction=camera["direction"],
                    vehicle_type=veh["type"],
                    violation=violation,
                    ocr_confidence=round(confidence, 2),
                    created_at=datetime.utcnow()
                )
                db.add(dup_obs)
                generated_count += 1
                duplicate_count += 1

            # Anomaly injection: Teleportation hop (impossible speed)
            if random.random() < (anomaly_pct / 100.0) and generated_count < num_events:
                # Teleport to opposite end of city in 45 seconds
                teleport_cam = "CAM_015" if hop["camera_id"] != "CAM_015" else "CAM_011"
                teleport_time = obs_time + timedelta(seconds=45)
                anom_obs = VehicleObservation(
                    observation_id=f"OBS_{uuid.uuid4().hex[:10].upper()}",
                    event_id=f"EVT_{uuid.uuid4().hex[:8].upper()}",
                    plate_number=veh["plate"],
                    camera_id=teleport_cam,
                    timestamp=teleport_time,
                    speed_kmph=round(base_speed, 1),
                    direction="NORTH",
                    vehicle_type=veh["type"],
                    violation=None,
                    ocr_confidence=0.96,
                    created_at=datetime.utcnow()
                )
                db.add(anom_obs)
                generated_count += 1
                anomaly_count += 1

    db.commit()
    db.close()
    print(f"[✓] Success! Stored {generated_count} events (including {duplicate_count} duplicates and {anomaly_count} anomalies).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic ANPR Event Generator")
    parser.add_argument("--events", type=int, default=500, help="Number of events to generate (default: 500)")
    parser.add_argument("--vehicles", type=int, default=150, help="Number of synthetic vehicles in pool (default: 150)")
    parser.add_argument("--anomaly-pct", type=float, default=2.5, help="Percentage of anomalous hops (default: 2.5)")
    parser.add_argument("--duplicate-pct", type=float, default=2.0, help="Percentage of duplicate observations (default: 2.0)")

    args = parser.parse_args()
    generate_batch_data(
        num_events=args.events,
        num_vehicles=args.vehicles,
        anomaly_pct=args.anomaly_pct,
        duplicate_pct=args.duplicate_pct
    )
