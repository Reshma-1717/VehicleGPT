from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TelemetryRecordBase(BaseModel):
    vehicle_id: str
    trip_id: Optional[str] = None
    timestamp: datetime
    signal_name: str
    value: float
    unit: str
    protocol: str = "CAN_FD"
    quality: str = "VALID"
    tier: str = "hot"

class TelemetryRecordCreate(TelemetryRecordBase):
    pass

class TelemetryRecordResponse(TelemetryRecordBase):
    id: int

    class Config:
        from_attributes = True

class TelemetryOverview(BaseModel):
    vehicle_model: Optional[str] = None
    vin: Optional[str] = None
    powertrain_type: Optional[str] = None
    battery_capacity_kwh: Optional[float] = None
    speed_kmh: float = 0.0
    soc_percent: float = 0.0
    battery_temp_c: float = 0.0
    range_km: float = 0.0
    energy_consumption_kwh_100km: float = 0.0
    motor_power_kw: float = 0.0
    cabin_temp_c: float = 0.0
    ambient_temp_c: float = 0.0
    tire_pressure_front_left_bar: float = 0.0
    tire_pressure_front_right_bar: float = 0.0
    tire_pressure_rear_left_bar: float = 0.0
    tire_pressure_rear_right_bar: float = 0.0
    cooling_pump_duty_percent: float = 0.0
    last_updated: datetime
    current_trip_id: Optional[str] = None
    status: str = "PARKED"
