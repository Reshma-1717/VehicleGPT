def test_api_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["offline_ready"] is True

def test_api_system_status(client):
    res = client.get("/api/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["app_name"] == "VehicleGPT"
    assert data["offline_mode"] is True
    assert data["memory_usage_mb"] > 0
    assert data["database_size_bytes"] > 0

def test_api_vehicle_overview(client):
    res = client.get("/api/vehicle/overview")
    assert res.status_code == 200
    data = res.json()
    assert "soc_percent" in data
    assert "range_km" in data
    assert "battery_temp_c" in data

def test_api_vehicle_telemetry(client):
    res = client.get("/api/vehicle/telemetry?limit=50")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0
    assert len(data["records"]) > 0

def test_api_vehicle_events(client):
    res = client.get("/api/vehicle/events?limit=20")
    assert res.status_code == 200
    data = res.json()
    assert data["count"] > 0

def test_api_analytics_range(client):
    res = client.get("/api/analytics/range?days=14")
    assert res.status_code == 200
    data = res.json()
    assert "range_delta_km" in data
    assert len(data["factors"]) > 0

def test_api_chat_query(client):
    res = client.post("/api/chat/query", json={"query": "Why did my range drop?"})
    assert res.status_code == 200
    data = res.json()
    assert "answer" in data
    assert data["intent"] == "RANGE_REDUCTION_EXPLANATION"
    assert data["latency_ms"] < 2000.0

def test_api_simulation_lifecycle(client):
    res_status = client.get("/api/simulation/status")
    assert res_status.status_code == 200
    
    res_stop = client.post("/api/simulation/stop")
    assert res_stop.status_code == 200
    assert res_stop.json()["active"] is False

    res_start = client.post("/api/simulation/start")
    assert res_start.status_code == 200
    assert res_start.json()["active"] is True
