from datetime import datetime
from backend.app.schemas.telemetry import TelemetryRecordCreate, TelemetryOverview
from backend.app.schemas.events import VehicleEventBase, DiagnosticCodeBase
from backend.app.schemas.chat import ChatQueryRequest, ChatQueryResponse, ChatEvidence

def test_telemetry_schema_validation():
    now = datetime.utcnow()
    rec = TelemetryRecordCreate(
        vehicle_id="VIN-TATA-EV-2026-X01",
        timestamp=now,
        signal_name="vehicle_speed_kmh",
        value=85.4,
        unit="km/h",
        protocol="CAN_FD"
    )
    assert rec.signal_name == "vehicle_speed_kmh"
    assert rec.value == 85.4
    assert rec.protocol == "CAN_FD"

def test_telemetry_overview_defaults():
    now = datetime.utcnow()
    overview = TelemetryOverview(
        speed_kmh=0.0,
        soc_percent=80.0,
        battery_temp_c=25.0,
        range_km=400.0,
        energy_consumption_kwh_100km=15.0,
        last_updated=now
    )
    assert overview.soc_percent == 80.0
    assert overview.status == "PARKED"

def test_event_schema():
    now = datetime.utcnow()
    evt = VehicleEventBase(
        id="EVT-TEST-001",
        vehicle_id="VIN-TATA-EV-2026-X01",
        timestamp=now,
        event_type="ADAS_DISENGAGEMENT",
        severity="WARNING",
        source="ADAS",
        description="Lane centering disengaged"
    )
    assert evt.id == "EVT-TEST-001"
    assert evt.severity == "WARNING"

def test_chat_schema():
    req = ChatQueryRequest(query="Why did my range drop?")
    assert req.query == "Why did my range drop?"

    resp = ChatQueryResponse(
        answer="Range dropped due to cold weather.",
        intent="RANGE_REDUCTION_EXPLANATION",
        confidence=0.95,
        evidence=ChatEvidence(time_range="last 14 days", metrics={"drop": 20}),
        source="deterministic_fallback",
        latency_ms=12.5,
        simulated_data=True
    )
    assert resp.intent == "RANGE_REDUCTION_EXPLANATION"
    assert resp.latency_ms == 12.5
