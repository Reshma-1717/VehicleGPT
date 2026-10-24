import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db
from backend.app.core.logging import setup_logging
from backend.app.simulation.generator import VehicleSimulator
from backend.app.ingestion.daemon import ingestion_daemon
from backend.app.api import (
    routes_health,
    routes_vehicle,
    routes_analytics,
    routes_chat,
    routes_simulation,
    routes_system,
    routes_diagnostics
)

setup_logging()
logger = logging.getLogger("vehiclegpt.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing VehicleGPT On-Device Intelligence Platform...")
    init_db()

    # Seed baseline multi-week dataset if empty
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM telemetry_records;")
        count = cursor.fetchone()["count"]
        if count == 0:
            logger.info("Database is empty. Seeding initial multi-week automotive dataset...")
            sim = VehicleSimulator(vehicle_id=settings.SIMULATION_VEHICLE_ID, seed=settings.SIMULATION_SEED)
            sim.generate_comprehensive_dataset()

    # Start live simulation stream if configured
    if settings.SIMULATION_AUTO_START:
        await ingestion_daemon.start()

    yield

    logger.info("Shutting down VehicleGPT Edge Service...")
    if ingestion_daemon.is_running:
        await ingestion_daemon.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Natural Language Vehicle Information Using an On-Device SLM/LLM - TATA TELIPORT Case Study 5",
    lifespan=lifespan
)

# Enable CORS for frontend Vite dev server & embedded dashboards
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(routes_health.router)
app.include_router(routes_vehicle.router)
app.include_router(routes_analytics.router)
app.include_router(routes_chat.router)
app.include_router(routes_simulation.router)
app.include_router(routes_system.router)
app.include_router(routes_diagnostics.router)


@app.get("/")
async def root():
    return {
        "message": "VehicleGPT: Natural Language Vehicle Information System is operational.",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "health_url": "/api/health"
    }
