from datetime import datetime
from backend.app.ingestion.normalizer import IngestionNormalizer
from backend.app.ingestion.daemon import ingestion_daemon

def test_normalizer_valid_record():
    raw = {
        "vehicle_id": "VIN-TATA-EV-2026-X01",
        "signal_name": "vehicle_speed_kmh",
        "value": 65.5,
        "unit": "km/h",
        "timestamp": datetime.utcnow().isoformat()
    }
    norm = IngestionNormalizer.normalize_record(raw)
    assert norm is not None
    assert norm["signal_name"] == "vehicle_speed_kmh"
    assert norm["value"] == 65.5
    assert norm["quality"] == "VALID"

def test_normalizer_out_of_bounds():
    raw = {
        "vehicle_id": "VIN-TATA-EV-2026-X01",
        "signal_name": "battery_soc_percent",
        "value": 150.0,  # Invalid SOC > 100%
        "unit": "%",
        "timestamp": datetime.utcnow().isoformat()
    }
    norm = IngestionNormalizer.normalize_record(raw)
    assert norm is not None
    assert norm["quality"] == "OUT_OF_BOUNDS"

def test_normalizer_malformed():
    raw = {
        "signal_name": "",  # Empty
        "value": "invalid_number"
    }
    norm = IngestionNormalizer.normalize_record(raw)
    assert norm is None

def test_retention_policy_execution():
    result = ingestion_daemon.enforce_retention_policy()
    assert "hot_to_warm" in result
    assert "warm_to_cold" in result
    assert "pruned_telemetry" in result
    assert "pruned_dtcs" in result
