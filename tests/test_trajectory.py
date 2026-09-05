def test_normal_trajectory_reconstruction(client):
    # RJ14AB1234 is seeded as a normal corridor transit across 4 checkpoints
    response = client.get("/api/vehicles/RJ14AB1234/trajectory")
    assert response.status_code == 200
    data = response.json()
    assert data["plate_number"] == "RJ14AB1234"
    assert data["camera_count"] == 4
    assert data["plausibility_status"] == "NORMAL"
    assert len(data["waypoints"]) == 4
    assert data["total_distance_km"] > 0.0
    assert data["average_speed_kmph"] > 0.0

def test_impossible_movement_trajectory_detection(client):
    # HR26XY4040 is seeded with 14.8 km in 90 seconds (592 km/h)
    response = client.get("/api/vehicles/HR26XY4040/trajectory")
    assert response.status_code == 200
    data = response.json()
    assert data["plate_number"] == "HR26XY4040"
    assert data["plausibility_status"] == "PHYSICALLY_IMPOSSIBLE"
    assert any(wp["is_anomaly"] for wp in data["waypoints"])
    assert "Physically impossible" in data["anomaly_notes"]

def test_vehicle_history(client):
    response = client.get("/api/vehicles/RJ14AB1234/history")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    assert all(d["plate_number"] == "RJ14AB1234" for d in data)

def test_missing_vehicle_trajectory_404(client):
    response = client.get("/api/vehicles/NON_EXISTENT_PLATE/trajectory")
    assert response.status_code == 404
