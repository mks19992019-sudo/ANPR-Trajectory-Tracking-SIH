from datetime import datetime, timezone, timedelta

def test_ingest_valid_anpr_event(client):
    payload = {
        "event_id": "EVT_TEST_VALID_01",
        "plate_number": "RJ14AB9999",
        "camera_id": "CAM_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmph": 55.0,
        "direction": "WEST",
        "vehicle_type": "car",
        "violation": None,
        "ocr_confidence": 0.98
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["event_id"] == "EVT_TEST_VALID_01"
    assert data["plate_number"] == "RJ14AB9999"
    assert data["camera_id"] == "CAM_001"
    assert data["direction"] == "WEST"

def test_reject_duplicate_event_id(client):
    payload = {
        "event_id": "EVT_DUP_TEST_01",
        "plate_number": "RJ14DUP999",
        "camera_id": "CAM_002",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmph": 50.0,
        "direction": "WEST",
        "vehicle_type": "car",
        "violation": None,
        "ocr_confidence": 0.95
    }
    res1 = client.post("/api/events", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/events", json=payload)
    assert res2.status_code == 409
    assert "Duplicate" in res2.json()["detail"]

def test_reject_sliding_window_duplicate_observation(client):
    ts = datetime.now(timezone.utc)
    payload1 = {
        "event_id": "EVT_WIN_01",
        "plate_number": "RJ14WIN111",
        "camera_id": "CAM_003",
        "timestamp": ts.isoformat(),
        "speed_kmph": 45.0,
        "direction": "EAST",
        "vehicle_type": "car",
        "violation": None,
        "ocr_confidence": 0.95
    }
    res1 = client.post("/api/events", json=payload1)
    assert res1.status_code == 201

    # Same plate + same camera 2 seconds later
    payload2 = {
        "event_id": "EVT_WIN_02",
        "plate_number": "RJ14WIN111",
        "camera_id": "CAM_003",
        "timestamp": (ts + timedelta(seconds=2)).isoformat(),
        "speed_kmph": 46.0,
        "direction": "EAST",
        "vehicle_type": "car",
        "violation": None,
        "ocr_confidence": 0.95
    }
    res2 = client.post("/api/events", json=payload2)
    assert res2.status_code == 409
    assert "sliding window" in res2.json()["detail"]

def test_reject_unknown_camera(client):
    payload = {
        "event_id": "EVT_UNKNOWN_CAM",
        "plate_number": "RJ14AB9999",
        "camera_id": "CAM_NON_EXISTENT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmph": 50.0,
        "direction": "WEST",
        "vehicle_type": "car",
        "violation": None,
        "ocr_confidence": 0.95
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 400
    assert "not found in registry" in response.json()["detail"]

def test_reject_future_timestamp(client):
    future_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        "event_id": "EVT_FUTURE_01",
        "plate_number": "RJ14FUT999",
        "camera_id": "CAM_001",
        "timestamp": future_time.isoformat(),
        "speed_kmph": 50.0,
        "direction": "WEST",
        "vehicle_type": "car"
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 422

def test_reject_invalid_speed(client):
    payload = {
        "event_id": "EVT_SPEED_INVALID",
        "plate_number": "RJ14SPD999",
        "camera_id": "CAM_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmph": 450.0,  # exceeds 300.0 limit
        "direction": "WEST",
        "vehicle_type": "car"
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 422

def test_events_listing_and_pagination(client):
    res = client.get("/api/events?limit=5&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert len(data) <= 5
