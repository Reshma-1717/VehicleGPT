from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime
from backend.app.core.config import settings
from backend.app.schemas.telemetry import TelemetryOverview
from backend.app.repositories.telemetry_repo import TelemetryRepository
from backend.app.repositories.event_repo import EventRepository
from backend.app.repositories.trip_repo import TripRepository

router = APIRouter(prefix="/api/vehicle", tags=["Vehicle"])

@router.get("/overview", response_model=TelemetryOverview)
async def get_vehicle_overview(vehicle_id: str = settings.SIMULATION_VEHICLE_ID):
    latest = TelemetryRepository.get_latest(vehicle_id)
    now = datetime.utcnow()

    # Synthesize cohesive overview
    speed = latest.get("vehicle_speed_kmh", {}).get("value", 0.0)
    soc = latest.get("battery_soc_percent", {}).get("value", 78.5)
    temp = latest.get("battery_pack_temp_c", {}).get("value", 28.2)
    range_val = latest.get("range_estimate_km", {}).get("value", 348.0)
    eff = latest.get("energy_consumption_kwh_100km", {}).get("value", 16.4)
    ambient = latest.get("ambient_temp_c", {}).get("value", 23.5)

    return TelemetryOverview(
        speed_kmh=speed,
        soc_percent=soc,
        battery_temp_c=temp,
        range_km=range_val,
        energy_consumption_kwh_100km=eff,
        motor_power_kw=0.0,
        cabin_temp_c=22.0,
        ambient_temp_c=ambient,
        tire_pressure_front_left_bar=latest.get("tire_pressure_fl_bar", {}).get("value", 2.2),
        tire_pressure_front_right_bar=latest.get("tire_pressure_fl_bar", {}).get("value", 2.2),
        tire_pressure_rear_left_bar=2.1,
        tire_pressure_rear_right_bar=2.1,
        cooling_pump_duty_percent=25.0,
        last_updated=now,
        status="PARKED" if speed == 0 else "DRIVING"
    )

@router.get("/telemetry")
async def get_telemetry(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    signals: Optional[str] = Query(None, description="Comma-separated signal names"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    trip_id: Optional[str] = None,
    limit: int = Query(500, le=2000)
):
    sig_list = [s.strip() for s in signals.split(",")] if signals else None
    records = TelemetryRepository.get_time_series(
        vehicle_id=vehicle_id,
        signal_names=sig_list,
        start_time=start_time,
        end_time=end_time,
        trip_id=trip_id,
        limit=limit
    )
    return {"count": len(records), "records": records}

@router.get("/trips")
async def get_trips(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    trip_type: Optional[str] = Query(None),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(50, le=200)
):
    trips = TripRepository.get_trips(
        vehicle_id=vehicle_id,
        start_time=start_time,
        end_time=end_time,
        trip_type=trip_type,
        limit=limit
    )
    return {"count": len(trips), "trips": trips}

@router.get("/events")
async def get_events(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    trip_id: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0
):
    if search:
        events = EventRepository.search_fts(search, limit=limit)
    else:
        events = EventRepository.get_events(
            vehicle_id=vehicle_id,
            event_type=event_type,
            severity=severity,
            trip_id=trip_id,
            limit=limit,
            offset=offset
        )
    return {"count": len(events), "events": events}

@router.get("/events/{event_id}")
async def get_event_detail(event_id: str):
    evt = EventRepository.get_event_by_id(event_id)
    if not evt:
        raise HTTPException(status_code=404, detail="Vehicle event not found")
    return evt

@router.get("/diagnostics")
async def get_diagnostics(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(50, le=200)
):
    dtcs = EventRepository.get_dtcs(vehicle_id=vehicle_id, start_time=start_time, end_time=end_time, limit=limit)
    return {"count": len(dtcs), "diagnostic_codes": dtcs}
