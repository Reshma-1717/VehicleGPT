import pytest
from backend.app.core.security import SecurityEnforcer

def test_security_valid_select_queries():
    valid, msg = SecurityEnforcer.validate_read_only_query("SELECT * FROM telemetry_records WHERE id = 1;")
    assert valid is True

    valid, msg = SecurityEnforcer.validate_read_only_query("WITH recent AS (SELECT * FROM trips) SELECT * FROM recent;")
    assert valid is True

def test_security_block_destructive_queries():
    invalid_queries = [
        "DELETE FROM telemetry_records;",
        "DROP TABLE vehicles;",
        "UPDATE vehicles SET vin = 'HACKED';",
        "INSERT INTO vehicles VALUES ('1', '2', '3', 2026, 'EV', 80.0, 'now');",
        "ALTER TABLE trips ADD COLUMN malware TEXT;",
        "PRAGMA writable_schema = 1;",
        "TRUNCATE TABLE vehicle_events;",
        "SELECT 1; DROP TABLE trips;"
    ]

    for q in invalid_queries:
        valid, msg = SecurityEnforcer.validate_read_only_query(q)
        assert valid is False, f"Expected '{q}' to be blocked!"

def test_security_block_actuator_commands():
    with pytest.raises(PermissionError) as exc_info:
        SecurityEnforcer.assert_vehicle_actuator_blocked("CAN_WRITE: STEERING_TORQUE_OVERRIDE")
    assert "SAFETY VIOLATION" in str(exc_info.value)
