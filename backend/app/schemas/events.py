from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class VehicleEventBase(BaseModel):
    id: str
    vehicle_id: str
    trip_id: Optional[str] = None
    timestamp: datetime
    event_type: str
    severity: str  # INFO, WARNING, CRITICAL
    source: str    # ADAS, BMS, POWERTRAIN, THERMAL, CHASSIS
    description: str
    metadata_json: Optional[str] = "{}"

class VehicleEventResponse(VehicleEventBase):
    pass

class DiagnosticCodeBase(BaseModel):
    id: Optional[int] = None
    vehicle_id: str
    trip_id: Optional[str] = None
    timestamp: datetime
    dtc_code: str
    ecu_name: str
    status: str = "ACTIVE"
    description: str
    severity: str = "WARNING"

class DiagnosticCodeResponse(DiagnosticCodeBase):
    pass

class TripBase(BaseModel):
    id: str
    vehicle_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    trip_type: str = "mixed"  # city, highway, mixed
    distance_km: float = 0.0
    avg_speed_kmh: float = 0.0
    avg_consumption: float = 0.0
    ambient_temp_c: float = 22.0
    status: str = "COMPLETED"

class TripResponse(TripBase):
    pass
