def test_health_and_readiness_probes(client):
    # GET /health
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] == "HEALTHY"

    # GET /api/health
    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json()["database"] == "CONNECTED"

    # GET /ready
    res3 = client.get("/ready")
    assert res3.status_code == 200
    assert res3.json()["status"] == "READY"

def test_blacklist_crud_operations(client):
    # 1. Fetch Blacklist
    res1 = client.get("/api/blacklist")
    assert res1.status_code == 200
    bl = res1.json()
    assert len(bl) >= 2

    # 2. Add new plate to blacklist
    new_plate = {
        "plate_number": "RJ14SEC007",
        "reason": "Vehicle involved in bank transit heist",
        "reference_number": "FIR #999/2026"
    }
    res2 = client.post("/api/blacklist", json=new_plate)
    assert res2.status_code == 201
    assert res2.json()["plate_number"] == "RJ14SEC007"

    # 3. Verify presence
    res3 = client.get("/api/blacklist")
    assert any(b["plate_number"] == "RJ14SEC007" for b in res3.json())

def test_ml_prediction_endpoint_placeholder(client):
    res = client.get("/api/ml/prediction")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "READY_FOR_MODEL"
    assert "XGBoost" in data["message"]
