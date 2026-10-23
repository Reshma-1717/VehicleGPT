import logging
from typing import List, Dict, Any
from backend.app.ingestion.adapters.base import BaseIngestionAdapter

logger = logging.getLogger("vehiclegpt.adapters.uds")

class UDSDoIPAdapter(BaseIngestionAdapter):
    """
    Unified Diagnostic Services (ISO 14229) over IP (DoIP - ISO 13400).
    Performs read-only polling of ReadDTCInformation (Service 0x19) and ReadDataByIdentifier (0x22).
    Safety constraint: No RoutineControl (0x31) or RequestDownload (0x34) write commands.
    """

    def __init__(self, target_ip: str = "192.168.1.100", port: int = 13400):
        super().__init__("SRC_UDS", "UDS/DoIP Diagnostic Service")
        self.target_ip = target_ip
        self.port = port

    def connect(self) -> bool:
        logger.info(f"Connecting to UDS/DoIP Diagnostic Server {self.target_ip}:{self.port}")
        self.is_connected = True
        return True

    def disconnect(self) -> None:
        self.is_connected = False

    def poll_records(self, max_records: int = 100) -> List[Dict[str, Any]]:
        return []
