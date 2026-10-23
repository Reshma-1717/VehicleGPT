from typing import List, Dict, Any
from backend.app.core.database import get_db

class AuditRepository:
    @staticmethod
    def log_query(
        query_text: str,
        intent: str,
        latency_ms: float,
        source: str,
        success: bool = True,
        response_preview: str = ""
    ) -> None:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO query_audits (
                query_text, intent, latency_ms, source, success, response_preview
            ) VALUES (?, ?, ?, ?, ?, ?);
            """, (
                query_text,
                intent,
                latency_ms,
                source,
                1 if success else 0,
                response_preview[:200]
            ))

    @staticmethod
    def get_recent_audits(limit: int = 50) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, timestamp, query_text, intent, latency_ms, source, success, response_preview
            FROM query_audits
            ORDER BY timestamp DESC
            LIMIT ?;
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def get_latency_stats() -> Dict[str, Any]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                COUNT(*) as total_queries,
                AVG(latency_ms) as avg_latency_ms,
                MIN(latency_ms) as min_latency_ms,
                MAX(latency_ms) as max_latency_ms
            FROM query_audits;
            """)
            row = cursor.fetchone()
            return dict(row) if row else {
                "total_queries": 0, "avg_latency_ms": 0.0, "min_latency_ms": 0.0, "max_latency_ms": 0.0
            }
