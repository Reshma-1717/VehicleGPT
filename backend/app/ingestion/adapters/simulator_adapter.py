import logging
from typing import List, Dict, Any
from datetime import datetime
from backend.app.ingestion.adapters.base import BaseIngestionAdapter
from backend.app.simulation.generator import VehicleSimulator

from backend.app.repositories.telemetry_repo import TelemetryRepository
import math

logger = logging.getLogger("vehiclegpt.adapters.simulator")

class SimulatorAdapter(BaseIngestionAdapter):
    """
    Live streaming telemetry adapter.
    Dynamically generates live telemetry signals based on the active vehicle state
    and actual historical database values.
    """

    def __init__(self, vehicle_id: str = "VIN-TATA-EV-2026-X01"):
        super().__init__("SRC_STREAMING", "Edge Vehicle Live Stream")
        self.vehicle_id = vehicle_id
        self._step = 0

    def connect(self) -> bool:
        logger.info(f"Live Streaming Adapter connected for vehicle: {self.vehicle_id}")
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("Live Streaming Adapter disconnected.")

    def poll_records(self, max_records: int = 10) -> List[Dict[str, Any]]:
        if not self.is_connected:
            return []
        
        now = datetime.utcnow()
        self._step += 1

        # Retrieve actual baseline state from database if available
        latest = TelemetryRepository.get_latest(self.vehicle_id)
        
        base_soc = float(latest.get("battery_soc_percent", {}).get("value", 80.0))
        base_temp = float(latest.get("battery_pack_temp_c", {}).get("value", 25.0))
        base_ambient = float(latest.get("ambient_temp_c", {}).get("value", 22.0))
        base_eff = float(latest.get("energy_consumption_kwh_100km", {}).get("value", 16.5))

        # Dynamic physical variation (smooth sinusoidal driving dynamics)
        sim_speed = max(0.0, round(45.0 + 20.0 * math.sin(self._step * 0.1), 1))
        sim_current = round(sim_speed * 1.8 + (10.0 if sim_speed > 0 else 0.5), 1)
        sim_temp = round(base_temp + (sim_current * 0.02 * math.sin(self._step * 0.05)), 1)
        sim_range = round((base_soc / 100.0) * 80.0 / (base_eff / 100.0), 1)

        records = [
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "vehicle_speed_kmh", "value": sim_speed, "unit": "km/h", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "battery_soc_percent", "value": round(base_soc, 2), "unit": "%", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "battery_pack_temp_c", "value": sim_temp, "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "battery_current_a", "value": sim_current, "unit": "A", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "range_estimate_km", "value": sim_range, "unit": "km", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "ambient_temp_c", "value": round(base_ambient, 1), "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
        ]
        self.records_ingested += len(records)
        return records
