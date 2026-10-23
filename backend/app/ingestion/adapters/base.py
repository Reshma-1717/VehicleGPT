from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generator

class BaseIngestionAdapter(ABC):
    """
    Abstract base class for all vehicle telemetry ingestion adapters.
    Mandatory safety constraint: All adapters are strictly read-only or subscribe-only.
    No adapter implements or allows any write path to vehicle buses or actuators.
    """

    def __init__(self, source_id: str, protocol_name: str):
        self.source_id = source_id
        self.protocol_name = protocol_name
        self.is_connected = False
        self.records_ingested = 0
        self.error_count = 0

    @abstractmethod
    def connect(self) -> bool:
        """Establish read-only connection or subscriber channel to vehicle data source."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect and release resources."""
        pass

    @abstractmethod
    def poll_records(self, max_records: int = 100) -> List[Dict[str, Any]]:
        """Fetch normalized incoming telemetry records."""
        pass

    def is_healthy(self) -> bool:
        return self.is_connected and self.error_count < 50
