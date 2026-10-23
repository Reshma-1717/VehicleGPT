import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.core.database import get_db

class TelemetryRepository:
    @staticmethod
    def insert_batch(records: List[Dict[str, Any]]) -> int:
        """Batch insert telemetry records for high edge throughput."""
        if not records:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
            INSERT INTO telemetry_records (
                vehicle_id, trip_id, timestamp, signal_name, value, unit, protocol, quality, tier
            ) VALUES (
                :vehicle_id, :trip_id, :timestamp, :signal_name, :value, :unit, :protocol, :quality, :tier
            );
            """, records)
            return len(records)

    @staticmethod
    def get_latest(vehicle_id: str) -> Dict[str, Any]:
        """Fetch the latest value for each primary vehicle signal."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT signal_name, value, unit, timestamp, trip_id
            FROM telemetry_records
            WHERE vehicle_id = ?
            GROUP BY signal_name
            HAVING timestamp = MAX(timestamp);
            """, (vehicle_id,))
            rows = cursor.fetchall()
            
            result = {}
            for r in rows:
                result[r["signal_name"]] = {
                    "value": r["value"],
                    "unit": r["unit"],
                    "timestamp": r["timestamp"],
                    "trip_id": r["trip_id"]
                }
            return result

    @staticmethod
    def get_time_series(
        vehicle_id: str,
        signal_names: Optional[List[str]] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        trip_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Fetch filtered time series records."""
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT id, trip_id, timestamp, signal_name, value, unit, tier FROM telemetry_records WHERE vehicle_id = ?"
            params: List[Any] = [vehicle_id]

            if trip_id:
                query += " AND trip_id = ?"
                params.append(trip_id)
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat() if isinstance(start_time, datetime) else str(start_time))
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat() if isinstance(end_time, datetime) else str(end_time))
            if signal_names:
                placeholders = ",".join(["?"] * len(signal_names))
                query += f" AND signal_name IN ({placeholders})"
                params.extend(signal_names)

            query += " ORDER BY timestamp ASC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_pre_event_window(
        vehicle_id: str,
        target_timestamp: datetime,
        seconds_before: int = 60,
        seconds_after: int = 15
    ) -> List[Dict[str, Any]]:
        """Retrieve high-resolution telemetry records strictly around an event timestamp."""
        if isinstance(target_timestamp, str):
            from dateutil import parser as date_parser
            target_timestamp = date_parser.parse(target_timestamp)

        from datetime import timedelta
        start_bound = (target_timestamp - timedelta(seconds=seconds_before)).isoformat()
        end_bound = (target_timestamp + timedelta(seconds=seconds_after)).isoformat()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, trip_id, timestamp, signal_name, value, unit
            FROM telemetry_records
            WHERE vehicle_id = ?
              AND timestamp >= ?
              AND timestamp <= ?
            ORDER BY timestamp ASC;
            """, (vehicle_id, start_bound, end_bound))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_storage_stats() -> Dict[str, Any]:
        """Return counts and historical time ranges."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) as count,
                MIN(timestamp) as earliest,
                MAX(timestamp) as latest
            FROM telemetry_records;
            """)
            row = cursor.fetchone()
            return {
                "count": row["count"] if row else 0,
                "earliest": row["earliest"] if row else None,
                "latest": row["latest"] if row else None
            }
