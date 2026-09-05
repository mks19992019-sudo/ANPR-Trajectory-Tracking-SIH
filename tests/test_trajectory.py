def test_normal_trajectory_reconstruction(client):
    # RJ14AB1234 is seeded as a normal corridor transit
    response = client.get("/api/vehicles/RJ14AB1234/trajectory")
    assert response.status_code == 200
    data = response.json()
    assert data["plate_number"] == "RJ14AB1234"
    assert data["camera_count"] == 4
    assert data["plausibility_status"] == "NORMAL"
    assert len(data["waypoints"]) == 4

def test_impossible_movement_trajectory_detection(client):
    # HR26XY4040 is seeded with 14.8 km in 90 seconds = 592 km/h
    response = client.get("/api/vehicles/HR26XY4040/trajectory")
    assert response.status_code == 200
    data = response.json()
    assert data["plate_number"] == "HR26XY4040"
    assert data["plausibility_status"] == "PHYSICALLY_IMPOSSIBLE"
    assert any(wp["is_anomaly"] for wp in data["waypoints"])
    assert "Physically impossible" in data["anomaly_notes"]
