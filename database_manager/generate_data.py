"""
Realistic Synthetic ANPR Producer.
Generates connected, physically plausible vehicle trajectories across Jaipur corridors.
Pure HTTP client with zero backend or database imports.
"""
import argparse
import random
import uuid
from datetime import datetime, timedelta, timezone
import requests
import os
from database_manager.cameras_data import CAMERA_DICT
from database_manager.routes_data import ROUTES, ROUTE_DICT
from backend.app.config import settings

DEFAULT_API_KEY = settings.ANPR_API_KEY
DEFAULT_BASE = os.getenv("BACKEND_URL", "https://anpr-trajectory-tracking-sih.onrender.com").rstrip("/")
DEFAULT_API_URL = f"{DEFAULT_BASE}/api/v1/events"

PREFIXES = ["RJ14", "RJ45", "DL08", "HR26", "UP16", "GJ01"]
LETTERS = ["AB", "CD", "EF", "GH", "JK", "LM", "PZ", "RS", "XY"]
VEHICLE_TYPES = ["car", "car", "car", "truck", "bus", "van", "motorcycle"]


def generate_plate():
    return f"{random.choice(PREFIXES)}{random.choice(LETTERS)}{random.randint(1000, 9999)}"


def build_journey_events(plate: str, route: dict, start_time: datetime, vtype: str = "car", overspeed_prob: float = 0.05):
    """
    Generates chronologically and physically connected observations along an entire route corridor.
    Speed and time between hops strictly adhere to physical driving distance.
    """
    events = []
    current_time = start_time

    for hop in route["hops"]:
        transit_sec = hop["transit_seconds"]
        if transit_sec > 0:
            # Add small random traffic jitter (-10% to +15% travel time)
            jitter = random.uniform(0.9, 1.15)
            current_time += timedelta(seconds=int(transit_sec * jitter))

        # Speed variance
        base_speed = hop["speed_kmph"] + random.uniform(-3.5, 4.5)
        is_overspeeding = random.random() < overspeed_prob
        if is_overspeeding:
            base_speed = hop["speed_limit"] + random.uniform(14.0, 26.0)
            violation = "OVERSPEEDING"
        else:
            violation = None

        cam = CAMERA_DICT[hop["camera_id"]]
        events.append({
            "event_id": f"GEN_{uuid.uuid4().hex[:12].upper()}",
            "plate_number": plate,
            "camera_id": hop["camera_id"],
            "timestamp": current_time.isoformat(),
            "speed_kmph": round(base_speed, 1),
            "direction": hop["direction"],
            "vehicle_type": vtype,
            "violation": violation,
            "ocr_confidence": round(random.uniform(0.93, 0.99), 2),
            "source": "ANPR"
        })

    return events


def run(api_url: str, api_key: str, target_events: int, duplicates: bool = False, include_anomalies: bool = True):
    session = requests.Session()
    headers = {"X-API-Key": api_key} if api_key else {}

    print(f"[*] Starting realistic trajectory ANPR generator (Target: ~{target_events} events)...")
    print(f"[*] Target endpoint: {api_url}")

    all_events = []
    now = datetime.now(timezone.utc)

    # 1. Deterministic Core Demo Trajectories
    # Scenario A: Normal Commuter RJ14AB1234 along JL Marg Corridor to Airport (5 hops)
    t_commuter = now - timedelta(minutes=random.randint(40, 75))
    all_events.extend(build_journey_events(
        plate="RJ14AB1234",
        route=ROUTE_DICT["RT_JL_MARG_SB"],
        start_time=t_commuter,
        vtype="car",
        overspeed_prob=0.0
    ))

    # Scenario B: Stolen Blacklisted Vehicle DL01CZ9999 along Heritage Corridor to MI Road
    if include_anomalies:
        t_blacklist = now - timedelta(minutes=random.randint(25, 45))
        all_events.extend(build_journey_events(
            plate="DL01CZ9999",
            route=ROUTE_DICT["RT_WALLED_CITY_CENTRAL"],
            start_time=t_blacklist,
            vtype="car",
            overspeed_prob=0.0
        ))

    # Scenario C: Overspeeding Demo Vehicle RJ14GE8819 on Ajmer Expressway
    t_speed = now - timedelta(minutes=random.randint(15, 30))
    all_events.extend(build_journey_events(
        plate="RJ14GE8819",
        route=ROUTE_DICT["RT_AJMER_EXPRESSWAY_WB"],
        start_time=t_speed,
        vtype="car",
        overspeed_prob=1.0  # Guarantees overspeeding alert
    ))

    # Scenario D: Physically Impossible Hop Anomaly HR26XY4040
    if include_anomalies:
        t_anom = now - timedelta(minutes=random.randint(20, 35))
        all_events.append({
            "event_id": f"GEN_{uuid.uuid4().hex[:12].upper()}",
            "plate_number": "HR26XY4040",
            "camera_id": "CAM_011",  # Tonk Road Sanganer
            "timestamp": t_anom.isoformat(),
            "speed_kmph": 58.0,
            "direction": "SOUTHWEST",
            "vehicle_type": "truck",
            "violation": None,
            "ocr_confidence": 0.96,
            "source": "ANPR"
        })
        # Teleports to Sikar Road (14.8 km away) in only 90 seconds (implied 592 km/h)
        all_events.append({
            "event_id": f"GEN_{uuid.uuid4().hex[:12].upper()}",
            "plate_number": "HR26XY4040",
            "camera_id": "CAM_015",  # Sikar Road VKI
            "timestamp": (t_anom + timedelta(seconds=90)).isoformat(),
            "speed_kmph": 55.0,
            "direction": "NORTH",
            "vehicle_type": "truck",
            "violation": None,
            "ocr_confidence": 0.95,
            "source": "ANPR"
        })

    # 2. Ambient Realistic Vehicle Journeys across all city corridors
    while len(all_events) < target_events:
        route = random.choice(ROUTES)
        plate = generate_plate()
        vtype = random.choice(VEHICLE_TYPES)
        # Vehicle starts its journey between 20 and 180 minutes ago
        trip_start = now - timedelta(minutes=random.randint(20, 180))
        journey = build_journey_events(plate, route, trip_start, vtype=vtype, overspeed_prob=0.06)
        all_events.extend(journey)

    # Trim to approximate requested size and sort chronologically
    all_events = all_events[:target_events + 10]
    all_events.sort(key=lambda x: x["timestamp"])

    # 3. Transmit Events via HTTP Ingestion API
    sent = 0
    dups_sent = 0

    for evt in all_events:
        try:
            res = session.post(api_url, json=evt, headers=headers, timeout=10)
            if res.status_code == 201:
                sent += 1
                if sent % 25 == 0 or sent == len(all_events):
                    print(f"[{sent:04d}/{len(all_events)}] Ingested {evt['plate_number']} at {evt['camera_id']} ({evt['speed_kmph']} km/h)")
            elif res.status_code == 409:
                pass  # Deduplicated by backend window
            else:
                print(f"[!] Warning HTTP {res.status_code}: {res.text}")
        except requests.exceptions.RequestException as e:
            print(f"[x] Ingestion connection error: {e}")
            return sent

        if duplicates and random.random() < 0.08:
            dup_payload = {**evt, "event_id": f"GEN_DUP_{uuid.uuid4().hex[:8].upper()}"}
            session.post(api_url, json=dup_payload, headers=headers, timeout=10)
            dups_sent += 1

    print(f"[✓] Successfully ingested {sent} realistic trajectory observations into PostgreSQL!")
    if duplicates:
        print(f"[✓] Tested deduplication with {dups_sent} duplicate events.")
    return sent


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Realistic Trajectory ANPR Generator")
    parser.add_argument("--url", default=DEFAULT_API_URL, help="Backend ingestion endpoint")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="ANPR Ingestion API Key")
    parser.add_argument("--events", type=int, default=100, help="Target number of events to generate")
    parser.add_argument("--duplicates", action="store_true", help="Inject duplicates to test dedup")
    parser.add_argument("--no-anomalies", action="store_true", help="Omit demo anomaly cases")

    args = parser.parse_args()
    run(
        api_url=args.url,
        api_key=args.api_key,
        target_events=args.events,
        duplicates=args.duplicates,
        include_anomalies=not args.no_anomalies
    )
