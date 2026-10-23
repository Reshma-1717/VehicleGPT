from fastapi import APIRouter
from datetime import datetime

router = APIRouter(tags=["Health"])

@router.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "VehicleGPT Edge Service",
        "timestamp": datetime.utcnow().isoformat(),
        "offline_ready": True
    }
