from fastapi import APIRouter
from backend.app.core.config import settings
from backend.app.ingestion.daemon import ingestion_daemon
from backend.app.simulation.generator import VehicleSimulator

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

@router.post("/start")
async def start_simulation():
    if not ingestion_daemon.is_running:
        await ingestion_daemon.start()
    return {"status": "started", "active": True}

@router.post("/stop")
async def stop_simulation():
    if ingestion_daemon.is_running:
        await ingestion_daemon.stop()
    return {"status": "stopped", "active": False}

@router.post("/reset")
async def reset_simulation():
    sim = VehicleSimulator(vehicle_id=settings.SIMULATION_VEHICLE_ID)
    counts = sim.generate_comprehensive_dataset()
    return {
        "status": "reset_completed",
        "records_generated": counts
    }

@router.get("/status")
async def get_simulation_status():
    return {
        "vehicle_id": settings.SIMULATION_VEHICLE_ID,
        "is_active": ingestion_daemon.is_running,
        "interval_ms": settings.SIMULATION_INTERVAL_MS,
        "seed": settings.SIMULATION_SEED
    }
