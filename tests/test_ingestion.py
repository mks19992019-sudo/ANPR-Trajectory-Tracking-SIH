from datetime import datetime, timezone

def test_ingest_valid_anpr_event(client):
    payload = {
        "event_id": "EVT_TEST_001",
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
    assert data["event_id"] == "EVT_TEST_001"
    assert data["plate_number"] == "RJ14AB9999"
    assert data["camera_id"] == "CAM_001"

def test_reject_duplicate_event_id(client):
    payload = {
        "event_id": "EVT_DUP_001",
        "plate_number": "RJ14DUP1111",
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
