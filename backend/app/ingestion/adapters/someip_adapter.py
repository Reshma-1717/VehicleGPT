import logging
from typing import List, Dict, Any
from backend.app.ingestion.adapters.base import BaseIngestionAdapter

logger = logging.getLogger("vehiclegpt.adapters.someip")

class SomeIPAdapter(BaseIngestionAdapter):
    """
    Scalable service-oriented middlewarE over IP (SOME/IP) Subscribe-Only interface.
    Subscribes to SOME/IP events (e.g., ADAS Camera Obstruction, High-Voltage Service).
    Strictly subscribe-only; no SOME/IP Method Call or Field Set is exposed.
    """

    def __init__(self, service_id: int = 0x1234, instance_id: int = 0x01):
        super().__init__("SRC_SOMEIP", "SOME/IP Subscribe-Only Service")
        self.service_id = service_id
        self.instance_id = instance_id

    def connect(self) -> bool:
        logger.info(f"Subscribing to SOME/IP Eventgroup (Service: {hex(self.service_id)}, Instance: {hex(self.instance_id)})")
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False
        logger.info("Unsubscribed from SOME/IP Eventgroup.")

    def poll_records(self, max_records: int = 100) -> List[Dict[str, Any]]:
        return []
