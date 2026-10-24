import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_diagnostic_trouble_codes(client):
    res = client.get("/api/diagnostics/dtc")
    assert res.status_code == 200
    data = res.json()
    assert "active_dtc_count" in data
    assert "dtcs" in data


def test_get_battery_certificate(client):
    res = client.get("/api/diagnostics/battery-certificate?odometer_km=50000")
    assert res.status_code == 200
    data = res.json()
    assert "certificate_id" in data
    assert "battery_soh_percent" in data
    assert data["nominal_capacity_kwh"] == 80.0
    assert data["warranty_compliance"] == "NORMAL"
    assert "tamper_proof_checksum" in data
