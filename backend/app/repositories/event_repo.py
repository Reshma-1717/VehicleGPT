from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.core.database import get_db

class EventRepository:
    @staticmethod
    def insert_event(event_dict: Dict[str, Any]) -> None:
        """Insert a vehicle event and index it in FTS5."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO vehicle_events (
                id, vehicle_id, trip_id, timestamp, event_type, severity, source, description, metadata_json
            ) VALUES (
                :id, :vehicle_id, :trip_id, :timestamp, :event_type, :severity, :source, :description, :metadata_json
            );
            """, event_dict)

            # Insert into FTS5 index
            cursor.execute("""
            INSERT INTO events_fts (event_id, event_type, severity, source, description)
            VALUES (?, ?, ?, ?, ?);
            """, (
                event_dict["id"],
                event_dict["event_type"],
                event_dict["severity"],
                event_dict["source"],
                event_dict["description"]
            ))

    @staticmethod
    def insert_events_batch(events: List[Dict[str, Any]]) -> int:
        """Batch insert vehicle events with FTS indexing."""
        if not events:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
            INSERT OR REPLACE INTO vehicle_events (
                id, vehicle_id, trip_id, timestamp, event_type, severity, source, description, metadata_json
            ) VALUES (
                :id, :vehicle_id, :trip_id, :timestamp, :event_type, :severity, :source, :description, :metadata_json
            );
            """, events)

            fts_records = [
                (e["id"], e["event_type"], e["severity"], e["source"], e["description"])
                for e in events
            ]
            cursor.executemany("""
            INSERT INTO events_fts (event_id, event_type, severity, source, description)
            VALUES (?, ?, ?, ?, ?);
            """, fts_records)
            return len(events)

    @staticmethod
    def get_events(
        vehicle_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        trip_id: Optional[str] = None,
        limit: int = 200,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Fetch filtered vehicle events sorted newest first."""
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM vehicle_events WHERE vehicle_id = ?"
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
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type)
            if severity:
                query += " AND severity = ?"
                params.append(severity)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def search_fts(search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Perform full-text search across indexed events using SQLite FTS5."""
        with get_db() as conn:
            cursor = conn.cursor()
            # Clean term for FTS5 syntax
            clean_term = "".join(c for c in search_term if c.isalnum() or c.isspace()).strip()
            if not clean_term:
                return []
            
            cursor.execute("""
            SELECT e.*
            FROM events_fts f
            JOIN vehicle_events e ON f.event_id = e.id
            WHERE events_fts MATCH ?
            ORDER BY rank
            LIMIT ?;
            """, (f"{clean_term}*", limit))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM vehicle_events WHERE id = ?;", (event_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    @staticmethod
    def insert_dtc(dtc: Dict[str, Any]) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO diagnostic_codes (
                vehicle_id, trip_id, timestamp, dtc_code, ecu_name, status, description, severity
            ) VALUES (
                :vehicle_id, :trip_id, :timestamp, :dtc_code, :ecu_name, :status, :description, :severity
            );
            """, dtc)
            cursor.execute("""
            INSERT INTO dtc_fts (dtc_code, ecu_name, description)
            VALUES (?, ?, ?);
            """, (dtc["dtc_code"], dtc["ecu_name"], dtc["description"]))

    @staticmethod
    def get_dtcs(
        vehicle_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM diagnostic_codes WHERE vehicle_id = ?"
            params: List[Any] = [vehicle_id]

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.isoformat() if isinstance(start_time, datetime) else str(start_time))
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.isoformat() if isinstance(end_time, datetime) else str(end_time))

            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
