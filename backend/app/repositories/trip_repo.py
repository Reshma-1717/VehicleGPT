from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.core.database import get_db

class TripRepository:
    @staticmethod
    def insert_trip(trip: Dict[str, Any]) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR REPLACE INTO trips (
                id, vehicle_id, start_time, end_time, trip_type, distance_km, avg_speed_kmh, avg_consumption, ambient_temp_c, status
            ) VALUES (
                :id, :vehicle_id, :start_time, :end_time, :trip_type, :distance_km, :avg_speed_kmh, :avg_consumption, :ambient_temp_c, :status
            );
            """, trip)

    @staticmethod
    def insert_trips_batch(trips: List[Dict[str, Any]]) -> int:
        if not trips:
            return 0
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
            INSERT OR REPLACE INTO trips (
                id, vehicle_id, start_time, end_time, trip_type, distance_km, avg_speed_kmh, avg_consumption, ambient_temp_c, status
            ) VALUES (
                :id, :vehicle_id, :start_time, :end_time, :trip_type, :distance_km, :avg_speed_kmh, :avg_consumption, :ambient_temp_c, :status
            );
            """, trips)
            return len(trips)

    @staticmethod
    def get_trips(
        vehicle_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        trip_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM trips WHERE vehicle_id = ?"
            params: List[Any] = [vehicle_id]

            if start_time:
                query += " AND start_time >= ?"
                params.append(start_time.isoformat() if isinstance(start_time, datetime) else str(start_time))
            if end_time:
                query += " AND start_time <= ?"
                params.append(end_time.isoformat() if isinstance(end_time, datetime) else str(end_time))
            if trip_type and trip_type != "all":
                query += " AND trip_type = ?"
                params.append(trip_type)

            query += " ORDER BY start_time DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_trip_by_id(trip_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trips WHERE id = ?;", (trip_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
