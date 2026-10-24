from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.app.core.config import settings
from backend.app.analytics.engine import AnalyticsEngine
from backend.app.repositories.event_repo import EventRepository

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/range")
async def get_range_analytics(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    days: int = Query(14, ge=3, le=60)
):
    analysis = AnalyticsEngine.analyze_range_reduction(vehicle_id=vehicle_id, days=days)
    if not analysis:
        raise HTTPException(status_code=404, detail="Insufficient range history records.")
    return analysis

@router.get("/efficiency")
async def get_efficiency_analytics(vehicle_id: str = settings.SIMULATION_VEHICLE_ID):
    drop = AnalyticsEngine.detect_efficiency_change_point(vehicle_id=vehicle_id)
    comp = AnalyticsEngine.compare_city_highway_efficiency(vehicle_id=vehicle_id, days=30)
    return {
        "largest_drop": drop,
        "city_highway_comparison": comp
    }

@router.get("/battery")
async def get_battery_analytics(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    days: int = Query(7, ge=1, le=30)
):
    trend = AnalyticsEngine.analyze_battery_temperature_trends(vehicle_id=vehicle_id, days=days)
    if not trend:
        raise HTTPException(status_code=404, detail="Insufficient battery thermal records.")
    return trend

@router.get("/adas")
async def get_adas_analytics(vehicle_id: str = settings.SIMULATION_VEHICLE_ID):
    events = EventRepository.get_events(vehicle_id=vehicle_id, event_type="ADAS_DISENGAGEMENT", limit=20)
    return {
        "total_disengagements": len(events),
        "recent_events": events
    }

@router.get("/preevent/{event_id}")
async def get_pre_event_telemetry(
    event_id: str,
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    seconds_before: int = Query(60, ge=10, le=300)
):
    window = AnalyticsEngine.investigate_pre_event_window(
        vehicle_id=vehicle_id,
        event_id=event_id,
        seconds_before=seconds_before
    )
    if not window:
        raise HTTPException(status_code=404, detail="Target event or pre-window telemetry not found.")
    return window

@router.get("/soh")
async def get_battery_soh_analytics(
    vehicle_id: str = settings.SIMULATION_VEHICLE_ID,
    total_throughput_kwh: float = Query(12500.0, ge=0.0)
):
    from backend.app.analytics.soh_estimator import BatterySOHEstimator
    estimator = BatterySOHEstimator(nominal_capacity_kwh=80.0, nominal_voltage_v=400.0)
    return estimator.calculate_cycle_degradation(
        total_kwh_throughput=total_throughput_kwh,
        fast_charge_ratio=0.25,
        avg_battery_temp_c=29.0
    )

@router.get("/thermal-load")
async def get_thermal_load_breakdown(
    ambient_temp_c: float = Query(35.0, ge=-40.0, le=60.0),
    cabin_temp_c: float = Query(28.0, ge=-20.0, le=50.0),
    battery_temp_c: float = Query(32.0, ge=-20.0, le=70.0),
    current_a: float = Query(45.0, ge=-200.0, le=500.0)
):
    from backend.app.analytics.thermal_model import EVThermalModel
    model = EVThermalModel()
    return model.calculate_thermal_loads(
        ambient_temp_c=ambient_temp_c,
        cabin_temp_c=cabin_temp_c,
        battery_pack_temp_c=battery_temp_c,
        battery_current_a=current_a
    )

