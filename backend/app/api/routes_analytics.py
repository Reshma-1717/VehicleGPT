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
