import json
import os
import logging
from typing import List, Dict, Any
from backend.app.ingestion.adapters.base import BaseIngestionAdapter

logger = logging.getLogger("vehiclegpt.adapters.replay")

class SampleFileReplayAdapter(BaseIngestionAdapter):
    """
    Adapter that replays pre-recorded vehicle trace files (JSON / CSV).
    Facilitates repeatable QA testing and offline demonstrations.
    """

    def __init__(self, file_path: str = "sample_data/sample_telemetry_replay.json"):
        super().__init__("SRC_FILE_REPLAY", "Recorded Sample File Replayer")
        self.file_path = file_path
        self._cached_records: List[Dict[str, Any]] = []
        self._index = 0

    def connect(self) -> bool:
        if not os.path.exists(self.file_path):
            logger.warning(f"Replay file '{self.file_path}' not found on disk.")
            return False

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self._cached_records = json.load(f)
            self._index = 0
            self.is_connected = True
            logger.info(f"Loaded {len(self._cached_records)} replay records from '{self.file_path}'")
            return True
        except Exception as e:
            logger.error(f"Failed to load replay file: {e}")
            self.error_count += 1
            return False

    def disconnect(self) -> None:
        self.is_connected = False
        self._cached_records.clear()
        self._index = 0

    def poll_records(self, max_records: int = 100) -> List[Dict[str, Any]]:
        if not self.is_connected or not self._cached_records:
            return []

        end_idx = min(len(self._cached_records), self._index + max_records)
        chunk = self._cached_records[self._index:end_idx]
        self._index = end_idx
        self.records_ingested += len(chunk)

        # Loop back if reaching end
        if self._index >= len(self._cached_records):
            self._index = 0

        return chunk
