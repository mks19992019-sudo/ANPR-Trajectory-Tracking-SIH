import argparse
import random
import time
import uuid
from datetime import datetime, timezone
import requests
import sys

from generator.cameras_data import CAMERAS, CAMERA_DICT
from generator.routes_data import ROUTES

PREFIXES = ["RJ14", "RJ45", "DL01", "DL08", "HR26", "UP16", "GJ01", "MH02"]
LETTERS = ["AB", "CD", "EF", "GH", "JK", "LM", "PZ"]
VTYPES = ["car", "car", "car", "truck", "bus", "motorcycle", "van"]

def get_random_plate():
    return f"{random.choice(PREFIXES)}{random.choice(LETTERS)}{random.randint(1000, 9999)}"

class ActiveVehicleJourney:
    def __init__(self, plate: str, vtype: str, route: dict):
        self.plate = plate
        self.vtype = vtype
        self.route = route
        self.current_hop_idx = 0
        self.next_hop_due = time.time()

def run_stream(
    api_url: str = "http://localhost:8000/api/v1/events",
    api_key: str = "local-dev-anpr-4Rz8sN1qK6vP2x",
    rate_hz: float = 1.0,
    inject_anomalies: bool = True
):
    print(f"[*] Starting continuous police ANPR synthetic stream...")
    print(f"[*] Ingesting into: {api_url} at ~{rate_hz} events/second")
    print(f"[*] Press Ctrl+C to stop.\n")
    headers = {"X-API-Key": api_key} if api_key else {}

    # Maintain a pool of 25 active vehicles moving across city routes
    active_journeys: list[ActiveVehicleJourney] = []
    for _ in range(25):
        active_journeys.append(ActiveVehicleJourney(
            plate=get_random_plate(),
            vtype=random.choice(VTYPES),
            route=random.choice(ROUTES)
        ))

    event_counter = 0
    cycle_tick = 0

    while True:
        try:
            cycle_tick += 1
            now = datetime.now(timezone.utc)
            now_ts = time.time()

            # Special Demo Injections
            event_payload = None

            # Every 25 ticks, inject Blacklisted Vehicle
            if inject_anomalies and cycle_tick % 25 == 0:
                cam = CAMERA_DICT["CAM_003"]
                event_payload = {
                    "event_id": f"EVT_STR_{uuid.uuid4().hex[:8].upper()}",
                    "plate_number": "DL01CZ9999",
                    "camera_id": "CAM_003",
                    "timestamp": now.isoformat(),
                    "speed_kmph": 42.0,
                    "direction": "EAST",
                    "vehicle_type": "car",
                    "violation": None,
                    "ocr_confidence": 0.98
                }
                print(f"[!] Injected Demo Blacklist Hit: DL01CZ9999 at CAM_003")

            # Every 40 ticks, inject Impossible Hop (Teleportation Anomaly)
            elif inject_anomalies and cycle_tick % 40 == 0:
                event_payload = {
                    "event_id": f"EVT_STR_{uuid.uuid4().hex[:8].upper()}",
                    "plate_number": "HR26XY4040",
                    "camera_id": "CAM_015",
                    "timestamp": now.isoformat(),
                    "speed_kmph": 58.0,
                    "direction": "NORTH",
                    "vehicle_type": "truck",
                    "violation": None,
                    "ocr_confidence": 0.96
                }
                print(f"[!] Injected Demo Impossible Movement: HR26XY4040 at CAM_015")

            # Every 18 ticks, inject Overspeeding Speed Violation
            elif inject_anomalies and cycle_tick % 18 == 0:
                cam = CAMERA_DICT["CAM_001"]
                event_payload = {
                    "event_id": f"EVT_STR_{uuid.uuid4().hex[:8].upper()}",
                    "plate_number": "RJ14GE8819",
                    "camera_id": "CAM_001",
                    "timestamp": now.isoformat(),
                    "speed_kmph": 114.5,
                    "direction": "WEST",
                    "vehicle_type": "car",
                    "violation": "OVERSPEEDING",
                    "ocr_confidence": 0.99
                }
                print(f"[!] Injected Demo Overspeeding Event: RJ14GE8819 at 114.5 km/h")

            # Standard route progress
            if not event_payload:
                # Find a journey that is ready
                journey = random.choice(active_journeys)
                hop = journey.route["hops"][journey.current_hop_idx]
                cam = CAMERA_DICT[hop["camera_id"]]

                base_spd = hop["avg_speed"] + random.uniform(-4.0, 5.0)
                is_speeding = random.random() < 0.05
                if is_speeding:
                    base_spd = cam["limit"] + random.uniform(15.0, 30.0)
                    viol = "OVERSPEEDING"
                else:
                    viol = None

                conf = random.uniform(0.91, 0.99)

                event_payload = {
                    "event_id": f"EVT_STR_{uuid.uuid4().hex[:8].upper()}",
                    "plate_number": journey.plate,
                    "camera_id": hop["camera_id"],
                    "timestamp": now.isoformat(),
                    "speed_kmph": round(base_spd, 1),
                    "direction": cam["direction"],
                    "vehicle_type": journey.vtype,
                    "violation": viol,
                    "ocr_confidence": round(conf, 2)
                }

                # Advance journey or replace with new vehicle
                journey.current_hop_idx += 1
                if journey.current_hop_idx >= len(journey.route["hops"]):
                    # Completed journey, start new vehicle
                    active_journeys.remove(journey)
                    active_journeys.append(ActiveVehicleJourney(
                        plate=get_random_plate(),
                        vtype=random.choice(VTYPES),
                        route=random.choice(ROUTES)
                    ))

            # Send HTTP POST to Ingestion API
            try:
                res = requests.post(api_url, json=event_payload, headers=headers, timeout=2.0)
                event_counter += 1
                if res.status_code == 201:
                    print(f"[{event_counter:04d}] Sent {event_payload['plate_number']} -> {event_payload['camera_id']} ({event_payload['speed_kmph']} km/h)")
                else:
                    print(f"[!] API Response {res.status_code}: {res.text}")
            except requests.exceptions.RequestException as e:
                print(f"[x] Connection error connecting to {api_url}: {e}")

            time.sleep(1.0 / max(0.1, rate_hz))

        except KeyboardInterrupt:
            print("\n[*] Stopping stream generator.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Continuous ANPR Stream Simulator")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/events", help="Backend ingestion endpoint")
    parser.add_argument("--api-key", default="local-dev-anpr-4Rz8sN1qK6vP2x", help="ANPR Ingestion API Key")
    parser.add_argument("--rate", type=float, default=1.0, help="Events per second (default: 1.0)")
    parser.add_argument("--no-anomalies", action="store_true", help="Disable periodic anomaly injection")

    args = parser.parse_args()
    run_stream(
        api_url=args.url,
        api_key=args.api_key,
        rate_hz=args.rate,
        inject_anomalies=not args.no_anomalies
    )
