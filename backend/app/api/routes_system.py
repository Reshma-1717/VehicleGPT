import os
import psutil
from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.schemas.system import SystemStatus
from backend.app.repositories.telemetry_repo import TelemetryRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.llm.local_slm import local_slm
from backend.app.ingestion.daemon import ingestion_daemon

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    # Process & Hardware metrics
    process = psutil.Process()
    mem_info = process.memory_info()
    mem_mb = round(mem_info.rss / (1024 * 1024), 2)
    cpu_pct = round(psutil.cpu_percent(interval=None), 1)

    # Database file stats
    db_size = os.path.getsize(settings.DATABASE_PATH) if os.path.exists(settings.DATABASE_PATH) else 0

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as c, MIN(timestamp) as min_t, MAX(timestamp) as max_t FROM telemetry_records;")
        telem_row = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) as c FROM vehicle_events;")
        events_count = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM trips;")
        trips_count = cursor.fetchone()["c"]
        cursor.execute("SELECT COUNT(*) as c FROM ingestion_sources WHERE status = 'ONLINE';")
        active_sources = cursor.fetchone()["c"]

    return SystemStatus(
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        status="ONLINE",
        hardware_profile=settings.HARDWARE_PROFILE,
        offline_mode=True,
        model_loaded=local_slm.is_available(),
        model_path=settings.LLM_MODEL_PATH if local_slm.is_available() else None,
        model_name="Llama-3.2-1B-Instruct-Q4_K_M" if local_slm.is_available() else "Deterministic Analytical Fallback (Active)",
        cpu_usage_percent=cpu_pct,
        memory_usage_mb=mem_mb,
        database_size_bytes=db_size,
        database_size_mb=round(db_size / (1024 * 1024), 3),
        historical_time_range_start=telem_row["min_t"] if telem_row else None,
        historical_time_range_end=telem_row["max_t"] if telem_row else None,
        telemetry_records_count=telem_row["c"] if telem_row else 0,
        events_count=events_count,
        trips_count=trips_count,
        active_sources=active_sources,
        simulation_active=ingestion_daemon.is_running,
        safety_boundaries_enforced=settings.READ_ONLY_VEHICLE_BUS and settings.BLOCK_ACTUATOR_COMMANDS
    )

@router.get("/storage/stats")
async def get_storage_stats():
    telem = TelemetryRepository.get_storage_stats()
    latency = AuditRepository.get_latency_stats()
    db_size = os.path.getsize(settings.DATABASE_PATH) if os.path.exists(settings.DATABASE_PATH) else 0
    return {
        "database_size_mb": round(db_size / (1024 * 1024), 3),
        "telemetry_stats": telem,
        "query_latency_stats": latency,
        "retention_policy": {
            "hot_hours": settings.RETENTION_HOT_HOURS,
            "warm_days": settings.RETENTION_WARM_DAYS,
            "cold_weeks": settings.RETENTION_COLD_WEEKS,
            "dtc_months": settings.RETENTION_DTC_MONTHS
        }
    }
