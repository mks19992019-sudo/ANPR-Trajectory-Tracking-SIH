def test_traffic_city_summary(client):
    res = client.get("/api/traffic/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_vehicles_today" in data
    assert "active_cameras" in data
    assert "average_speed_city" in data
    assert "congested_corridors" in data
    assert data["total_cameras"] == 25

def test_corridor_congestion_calculation(client):
    res = client.get("/api/traffic/congestion?minutes=30")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10
    for item in data:
        assert item["congestion_level"] in ["LOW", "MODERATE", "HIGH", "SEVERE"]
        assert 0.0 <= item["congestion_score"] <= 1.0

def test_speed_analytics_percentiles(client):
    res = client.get("/api/traffic/speed-analytics?hours=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 10
    for item in data:
        assert "percentile_85_speed" in item
        assert "compliance_rate" in item
        assert 0.0 <= item["compliance_rate"] <= 100.0

def test_camera_flows_calculation(client):
    res = client.get("/api/traffic/flow?hours=2")
    assert res.status_code == 200
    flows = res.json()
    assert isinstance(flows, list)
    for f in flows:
        assert "source_camera" in f
        assert "destination_camera" in f
        assert f["vehicle_count"] >= 1

def test_dynamic_od_matrix(client):
    res = client.get("/api/traffic/od-matrix?hours=24")
    assert res.status_code == 200
    data = res.json()
    assert len(data["zones"]) == 5
    assert len(data["matrix"]) == 5
    assert len(data["matrix"][0]) == 5

def test_heatmap_geojson(client):
    res = client.get("/api/traffic/heatmap")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 25
    for feat in data["features"]:
        assert feat["geometry"]["type"] == "Point"
        assert 0.0 <= feat["properties"]["intensity"] <= 1.0
