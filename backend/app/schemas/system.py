from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime

class SystemStatus(BaseModel):
    app_name: str
    version: str
    status: str
    hardware_profile: str
    offline_mode: bool
    model_loaded: bool
    model_path: Optional[str] = None
    model_name: Optional[str] = None
    cpu_usage_percent: float
    memory_usage_mb: float
    database_size_bytes: int
    database_size_mb: float
    historical_time_range_start: Optional[datetime] = None
    historical_time_range_end: Optional[datetime] = None
    telemetry_records_count: int
    events_count: int
    trips_count: int
    active_sources: int
    simulation_active: bool
    safety_boundaries_enforced: bool
