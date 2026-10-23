import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.ingestion.normalizer import IngestionNormalizer
from backend.app.ingestion.adapters.simulator_adapter import SimulatorAdapter
from backend.app.repositories.telemetry_repo import TelemetryRepository

logger = logging.getLogger("vehiclegpt.ingestion.daemon")

class EdgeIngestionDaemon:
    """
    Edge Ingestion Daemon managing real-time vehicle streams, buffer queues,
    and multi-tier retention management (hot, warm, cold).
    """

    def __init__(self):
        self.is_running = False
        self.simulator_adapter = SimulatorAdapter(settings.SIMULATION_VEHICLE_ID)
        self._buffer: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def start(self):
        self.is_running = True
        self.simulator_adapter.connect()
        logger.info("Edge Ingestion Daemon started.")
        asyncio.create_task(self._ingestion_loop())
        asyncio.create_task(self._retention_cleanup_loop())

    async def stop(self):
        self.is_running = False
        self.simulator_adapter.disconnect()
        await self.flush()
        logger.info("Edge Ingestion Daemon stopped.")

    async def _ingestion_loop(self):
        while self.is_running:
            try:
                raw_records = self.simulator_adapter.poll_records(max_records=20)
                if raw_records:
                    normalized = []
                    for r in raw_records:
                        norm = IngestionNormalizer.normalize_record(r)
                        if norm:
                            normalized.append(norm)

                    async with self._lock:
                        self._buffer.extend(normalized)
                        if len(self._buffer) >= 20:
                            await self._flush_buffer_locked()
            except Exception as e:
                logger.error(f"Error in edge ingestion loop: {e}")

            await asyncio.sleep(settings.SIMULATION_INTERVAL_MS / 1000.0)

    async def flush(self):
        async with self._lock:
            await self._flush_buffer_locked()

    async def _flush_buffer_locked(self):
        if not self._buffer:
            return
        to_insert = list(self._buffer)
        self._buffer.clear()
        TelemetryRepository.insert_batch(to_insert)

    async def _retention_cleanup_loop(self):
        """Periodically enforces retention tiers: hot -> warm -> cold -> purge."""
        while self.is_running:
            try:
                self.enforce_retention_policy()
            except Exception as e:
                logger.error(f"Error during retention cleanup: {e}")
            # Run every 4 hours
            await asyncio.sleep(14400)

    def enforce_retention_policy(self) -> Dict[str, int]:
        """
        Executes tiered data aging:
        1. Downgrade hot raw telemetry older than 72 hours to warm.
        2. Downgrade warm telemetry older than 7 days to cold.
        3. Prune cold telemetry older than 12 weeks.
        4. Prune resolved DTCs older than 6 months.
        """
        now = datetime.utcnow()
        hot_threshold = (now - timedelta(hours=settings.RETENTION_HOT_HOURS)).isoformat()
        warm_threshold = (now - timedelta(days=settings.RETENTION_WARM_DAYS)).isoformat()
        cold_threshold = (now - timedelta(weeks=settings.RETENTION_COLD_WEEKS)).isoformat()
        dtc_threshold = (now - timedelta(days=settings.RETENTION_DTC_MONTHS * 30)).isoformat()

        with get_db() as conn:
            cursor = conn.cursor()

            # Hot -> Warm
            cursor.execute("""
            UPDATE telemetry_records
            SET tier = 'warm'
            WHERE tier = 'hot' AND timestamp < ?;
            """, (hot_threshold,))
            promoted_warm = cursor.rowcount

            # Warm -> Cold
            cursor.execute("""
            UPDATE telemetry_records
            SET tier = 'cold'
            WHERE tier = 'warm' AND timestamp < ?;
            """, (warm_threshold,))
            promoted_cold = cursor.rowcount

            # Delete cold older than 12 weeks
            cursor.execute("""
            DELETE FROM telemetry_records
            WHERE tier = 'cold' AND timestamp < ?;
            """, (cold_threshold,))
            pruned_telemetry = cursor.rowcount

            # Prune ancient resolved DTCs
            cursor.execute("""
            DELETE FROM diagnostic_codes
            WHERE status = 'RESOLVED' AND timestamp < ?;
            """, (dtc_threshold,))
            pruned_dtcs = cursor.rowcount

            logger.info(
                f"Retention policy applied: {promoted_warm} hot->warm, {promoted_cold} warm->cold, "
                f"{pruned_telemetry} cold purged, {pruned_dtcs} DTCs pruned."
            )

            return {
                "hot_to_warm": promoted_warm,
                "warm_to_cold": promoted_cold,
                "pruned_telemetry": pruned_telemetry,
                "pruned_dtcs": pruned_dtcs
            }

ingestion_daemon = EdgeIngestionDaemon()
