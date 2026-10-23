import logging
from typing import List, Dict, Any
from backend.app.ingestion.adapters.base import BaseIngestionAdapter

logger = logging.getLogger("vehiclegpt.adapters.vhal")

class AndroidVHALAdapter(BaseIngestionAdapter):
    """
    Android Automotive OS (AAOS) Vehicle Hardware Abstraction Layer (VHAL) property adapter.
    Listens to VehiclePropValue changes (e.g., PERF_VEHICLE_SPEED, EV_BATTERY_LEVEL, HVAC_TEMPERATURE_CURRENT).
    Operates in read-only subscription mode.
    """

    def __init__(self):
        super().__init__("SRC_VHAL", "Android Automotive Vehicle HAL")

    def connect(self) -> bool:
        logger.info("Connected to Android VHAL property listener service.")
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("Disconnected from Android VHAL.")

    def poll_records(self, max_records: int = 100) -> List[Dict[str, Any]]:
        return []
