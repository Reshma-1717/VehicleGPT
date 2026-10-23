import logging
from typing import List, Dict, Any
from datetime import datetime
from backend.app.ingestion.adapters.base import BaseIngestionAdapter
from backend.app.simulation.generator import VehicleSimulator

logger = logging.getLogger("vehiclegpt.adapters.simulator")

class SimulatorAdapter(BaseIngestionAdapter):
    """
    Live streaming simulation adapter.
    Generates periodic synthetic CAN-FD signals while the vehicle is 'running'.
    """

    def __init__(self, vehicle_id: str = "VIN-TATA-EV-2026-X01"):
        super().__init__("SRC_SIMULATOR", "Edge High-Fidelity Vehicle Simulator")
        self.vehicle_id = vehicle_id
        self._sim = VehicleSimulator(vehicle_id=vehicle_id)

    def connect(self) -> bool:
        logger.info(f"Simulator Adapter connected for VIN: {self.vehicle_id}")
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("Simulator Adapter disconnected.")

    def poll_records(self, max_records: int = 10) -> List[Dict[str, Any]]:
        if not self.is_connected:
            return []
        
        now = datetime.utcnow()
        # Emit a pulse of live telemetry
        records = [
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "vehicle_speed_kmh", "value": 0.0, "unit": "km/h", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "battery_soc_percent", "value": 78.5, "unit": "%", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "battery_pack_temp_c", "value": 28.2, "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "range_estimate_km", "value": 348.0, "unit": "km", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            {"vehicle_id": self.vehicle_id, "trip_id": None, "timestamp": now.isoformat(), "signal_name": "ambient_temp_c", "value": 23.5, "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
        ]
        self.records_ingested += len(records)
        return records
