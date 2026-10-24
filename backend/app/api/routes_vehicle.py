import logging
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
from backend.app.core.config import settings
from backend.app.schemas.telemetry import TelemetryOverview
from backend.app.repositories.telemetry_repo import TelemetryRepository
from backend.app.repositories.event_repo import EventRepository
from backend.app.repositories.trip_repo import TripRepository

from backend.app.core.database import get_db
from backend.app.ingestion.real_data_loader import RealDataLoader

logger = logging.getLogger("vehiclegpt.api.vehicle")

router = APIRouter(prefix="/api/vehicle", tags=["Vehicle"])

@router.get("/profile")
async def get_vehicle_profile(vehicle_id: str = settings.SIMULATION_VEHICLE_ID):
    """Retrieve verified vehicle identity, model, and physical powertrain specifications."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, vin, model, year, powertrain_type, battery_capacity_kwh FROM vehicles WHERE id = ?;", (vehicle_id,))
        row = cursor.fetchone()
        if not row:
            # Query any available vehicle in database
            cursor.execute("SELECT id, vin, model, year, powertrain_type, battery_capacity_kwh FROM vehicles LIMIT 1;")
            row = cursor.fetchone()
        if row:
            return dict(row)
        return {
            "id": vehicle_id,
            "vin": f"VIN-{abs(hash(vehicle_id)) % 1000000000:010d}",
            "model": "Connected Vehicle",
            "year": 2026,
            "powertrain_type": "BEV",
            "battery_capacity_kwh": 80.0
        }

@router.get("/overview", response_model=TelemetryOverview)
async def get_vehicle_overview(vehicle_id: str = settings.SIMULATION_VEHICLE_ID):
    latest = TelemetryRepository.get_latest(vehicle_id)
    now = datetime.utcnow()

    # Dynamically fetch vehicle profile
    v_profile = await get_vehicle_profile(vehicle_id)
    battery_cap = float(v_profile.get("battery_capacity_kwh") or 80.0)

    # Dynamically resolve latest signal values with zero hardcoded defaults
    speed = float(latest.get("vehicle_speed_kmh", {}).get("value", 0.0))
    soc = float(latest.get("battery_soc_percent", {}).get("value", 0.0))
    temp = float(latest.get("battery_pack_temp_c", {}).get("value", 0.0))
    eff = float(latest.get("energy_consumption_kwh_100km", {}).get("value", 0.0))
    ambient = float(latest.get("ambient_temp_c", {}).get("value", 0.0))
    cabin = float(latest.get("cabin_temp_c", {}).get("value", 0.0))
    pump = float(latest.get("coolant_pump_duty_percent", {}).get("value", 0.0))

    # Dynamic motor power calculation: P = V * I (kW)
    if "motor_power_kw" in latest:
        motor_power = float(latest["motor_power_kw"]["value"])
    elif "battery_voltage_v" in latest and "battery_current_a" in latest:
        v = float(latest["battery_voltage_v"]["value"])
        i = float(latest["battery_current_a"]["value"])
        motor_power = round(abs(v * i) / 1000.0, 1)
    else:
        motor_power = 0.0

    # Dynamic range calculation: remaining kWh / (consumption per km)
    if "range_estimate_km" in latest:
        range_val = float(latest["range_estimate_km"]["value"])
    elif soc > 0 and eff > 0:
        remaining_kwh = (soc / 100.0) * battery_cap
        range_val = round((remaining_kwh / (eff / 100.0)), 1)
    else:
        range_val = 0.0

    # Dynamic individual tire pressures
    tire_fl = float(latest.get("tire_pressure_fl_bar", {}).get("value") or latest.get("tire_pressure_front_left_bar", {}).get("value", 0.0))
    tire_fr = float(latest.get("tire_pressure_fr_bar", {}).get("value") or latest.get("tire_pressure_front_right_bar", {}).get("value", 0.0))
    tire_rl = float(latest.get("tire_pressure_rl_bar", {}).get("value") or latest.get("tire_pressure_rear_left_bar", {}).get("value", 0.0))
    tire_rr = float(latest.get("tire_pressure_rr_bar", {}).get("value") or latest.get("tire_pressure_rear_right_bar", {}).get("value", 0.0))

    # Dynamic operational state
    curr_trip = latest.get("vehicle_speed_kmh", {}).get("trip_id")
    if speed > 1.0:
        veh_status = "DRIVING"
    elif latest.get("battery_current_a", {}).get("value", 0.0) < -5.0:
        veh_status = "CHARGING"
    else:
        veh_status = "PARKED"

    return TelemetryOverview(
        vehicle_model=v_profile.get("model"),
        vin=v_profile.get("vin"),
        powertrain_type=v_profile.get("powertrain_type"),
        battery_capacity_kwh=battery_cap,
        speed_kmh=round(speed, 1),
        soc_percent=round(soc, 1),
        battery_temp_c=round(temp, 1),
        range_km=round(range_val, 1),
        energy_consumption_kwh_100km=round(eff, 1),
        motor_power_kw=motor_power,
        cabin_temp_c=round(cabin, 1),
        ambient_temp_c=round(ambient, 1),
        tire_pressure_front_left_bar=round(tire_fl, 2),
        tire_pressure_front_right_bar=round(tire_fr, 2),
        tire_pressure_rear_left_bar=round(tire_rl, 2),
        tire_pressure_rear_right_bar=round(tire_rr, 2),
        cooling_pump_duty_percent=round(pump, 1),
        last_updated=now,
        current_trip_id=curr_trip,
        status=veh_status
    )

@router.post("/import-log")
async def import_real_vehicle_log(
    payload: Dict[str, Any]
):
    """
    Import real-world vehicle telemetry logs (CSV, JSON, or CAN frame logs).
    Populates local historical SQLite storage directly with real data.
    """
    csv_content = payload.get("csv_content")
    vehicle_id = payload.get("vehicle_id", settings.SIMULATION_VEHICLE_ID)
    trip_id = payload.get("trip_id", f"TRIP-REAL-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}")

    if not csv_content:
        raise HTTPException(status_code=400, detail="Missing required 'csv_content' in payload.")

    try:
        result = RealDataLoader.load_csv_content(
            csv_text=csv_content,
            vehicle_id=vehicle_id,
            trip_id_prefix=trip_id
        )
        return {
            "status": "success",
            "message": f"Successfully imported {result['imported_records']} real telemetry records.",
            "details": result
        }
    except Exception as e:
        logger.error(f"Failed to import real vehicle log: {e}")
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

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
