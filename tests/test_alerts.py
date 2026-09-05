from datetime import datetime, timezone

def test_blacklist_alert_trigger(client):
    # Ingesting observation for blacklisted plate DL01CZ9999
    payload = {
        "event_id": "EVT_TEST_BLACKLIST_01",
        "plate_number": "DL01CZ9999",
        "camera_id": "CAM_003",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmph": 45.0,
        "direction": "EAST",
        "vehicle_type": "car",
        "violation": None,
        "ocr_confidence": 0.98
    }
    res = client.post("/api/events", json=payload)
    assert res.status_code == 201

    alerts_res = client.get("/api/alerts?severity=CRITICAL")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert any(a["plate_number"] == "DL01CZ9999" and a["alert_type"] == "BLACKLIST_MATCH" for a in alerts)

def test_overspeeding_alert_trigger(client):
    # CAM_001 speed limit is 80 km/h -> clock at 115 km/h
    payload = {
        "event_id": "EVT_TEST_SPEED_01",
        "plate_number": "RJ14SP7777",
        "camera_id": "CAM_001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "speed_kmph": 115.0,
        "direction": "WEST",
        "vehicle_type": "car",
        "violation": "OVERSPEEDING",
        "ocr_confidence": 0.99
    }
    res = client.post("/api/events", json=payload)
    assert res.status_code == 201

    alerts_res = client.get("/api/alerts?severity=WARNING")
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert any(a["plate_number"] == "RJ14SP7777" and a["alert_type"] == "OVERSPEEDING" for a in alerts)
