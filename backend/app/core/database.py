import sqlite3
import logging
from contextlib import contextmanager
from typing import Generator
from datetime import datetime
from backend.app.core.config import settings

logger = logging.getLogger("vehiclegpt.database")

from dateutil import parser as date_parser

def adapt_timestamp(val):
    if isinstance(val, datetime):
        return val.isoformat()
    return str(val)

def convert_timestamp(val: bytes):
    try:
        return date_parser.parse(val.decode("utf-8"))
    except Exception:
        return val.decode("utf-8")

sqlite3.register_adapter(datetime, adapt_timestamp)
sqlite3.register_converter("timestamp", convert_timestamp)
sqlite3.register_converter("TIMESTAMP", convert_timestamp)

def get_connection(timeout: float = 15.0) -> sqlite3.Connection:
    """Create a configured SQLite connection with WAL mode and row factory."""
    conn = sqlite3.connect(
        settings.DATABASE_PATH,
        timeout=timeout,
        detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
    )
    conn.row_factory = sqlite3.Row
    
    # Configure pragmas for high edge performance and concurrency
    cursor = conn.cursor()
    if settings.DB_ENABLE_WAL:
        cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("PRAGMA busy_timeout = 15000;")
    cursor.execute("PRAGMA cache_size = -64000;")  # ~64MB cache
    cursor.close()
    
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections with automatic commit/rollback."""
    conn = get_connection(timeout=settings.DB_TIMEOUT_SECONDS)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        conn.close()

def init_db() -> None:
    """Initialize database tables, full-text FTS5 search tables, and performance indexes."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # 1. Vehicles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id TEXT PRIMARY KEY,
            vin TEXT UNIQUE NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            powertrain_type TEXT NOT NULL DEFAULT 'BEV',
            battery_capacity_kwh REAL NOT NULL DEFAULT 75.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 2. Trips
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            trip_type TEXT NOT NULL DEFAULT 'mixed', -- 'city', 'highway', 'mixed'
            distance_km REAL NOT NULL DEFAULT 0.0,
            avg_speed_kmh REAL NOT NULL DEFAULT 0.0,
            avg_consumption REAL NOT NULL DEFAULT 0.0, -- kWh/100km
            ambient_temp_c REAL NOT NULL DEFAULT 22.0,
            status TEXT NOT NULL DEFAULT 'COMPLETED' -- 'ACTIVE', 'COMPLETED'
        );
        """)

        # 3. Telemetry Records
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            trip_id TEXT REFERENCES trips(id) ON DELETE SET NULL,
            timestamp TIMESTAMP NOT NULL,
            signal_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            protocol TEXT NOT NULL DEFAULT 'CAN_FD',
            quality TEXT NOT NULL DEFAULT 'VALID',
            tier TEXT NOT NULL DEFAULT 'hot' -- 'hot', 'warm', 'cold'
        );
        """)

        # 4. Vehicle Events
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_events (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            trip_id TEXT REFERENCES trips(id) ON DELETE SET NULL,
            timestamp TIMESTAMP NOT NULL,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL, -- 'INFO', 'WARNING', 'CRITICAL'
            source TEXT NOT NULL,   -- 'ADAS', 'BMS', 'POWERTRAIN', 'THERMAL', 'CHASSIS'
            description TEXT NOT NULL,
            metadata_json TEXT DEFAULT '{}'
        );
        """)

        # 5. Diagnostic Codes (DTCs)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diagnostic_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id TEXT NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
            trip_id TEXT REFERENCES trips(id) ON DELETE SET NULL,
            timestamp TIMESTAMP NOT NULL,
            dtc_code TEXT NOT NULL,
            ecu_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'PENDING', 'RESOLVED'
            description TEXT NOT NULL,
            severity TEXT NOT NULL DEFAULT 'WARNING'
        );
        """)

        # 6. Ingestion Sources
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingestion_sources (
            id TEXT PRIMARY KEY,
            protocol_name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ONLINE',
            last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            error_count INTEGER DEFAULT 0,
            records_ingested INTEGER DEFAULT 0
        );
        """)

        # 7. Query Audit Record
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS query_audits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            query_text TEXT NOT NULL,
            intent TEXT NOT NULL,
            latency_ms REAL NOT NULL,
            source TEXT NOT NULL, -- 'local_slm', 'deterministic_fallback'
            success INTEGER NOT NULL DEFAULT 1,
            response_preview TEXT
        );
        """)

        # B-Tree Performance Indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_ts ON telemetry_records(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_sig_ts ON telemetry_records(signal_name, timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_trip ON telemetry_records(trip_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_tier ON telemetry_records(tier);")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_ts ON vehicle_events(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON vehicle_events(event_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_severity ON vehicle_events(severity);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_trip ON vehicle_events(trip_id);")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dtc_ts ON diagnostic_codes(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_dtc_code ON diagnostic_codes(dtc_code);")

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trips_ts ON trips(start_time, end_time);")

        # Full-Text Search (FTS5) for fast natural-language searches over events and DTCs
        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS events_fts USING fts5(
            event_id UNINDEXED,
            event_type,
            severity,
            source,
            description,
            tokenize = 'porter unicode61'
        );
        """)

        cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS dtc_fts USING fts5(
            dtc_code,
            ecu_name,
            description,
            tokenize = 'porter unicode61'
        );
        """)

        # Default vehicle insertion if empty
        cursor.execute("SELECT COUNT(*) as cnt FROM vehicles WHERE id = ?;", (settings.SIMULATION_VEHICLE_ID,))
        row = cursor.fetchone()
        if row and row["cnt"] == 0:
            cursor.execute("""
            INSERT INTO vehicles (id, vin, model, year, powertrain_type, battery_capacity_kwh)
            VALUES (?, ?, ?, ?, ?, ?);
            """, (
                settings.SIMULATION_VEHICLE_ID,
                "MAT67890123456789",
                "TATA Harrier.ev Concept AWD",
                2026,
                "BEV",
                80.0
            ))

        # Default ingestion sources
        protocols = [
            ("SRC_CAN_FD", "CAN/CAN-FD Bus via SocketCAN (DBC)"),
            ("SRC_SOMEIP", "SOME/IP Subscribe-Only Interface"),
            ("SRC_VHAL", "Android Vehicle HAL (Properties)"),
            ("SRC_SYSLOG", "QNX slog2 / Linux Syslog"),
            ("SRC_UDS", "UDS/DoIP Diagnostic Services"),
            ("SRC_SIMULATOR", "Edge High-Fidelity Vehicle Simulator")
        ]
        for src_id, name in protocols:
            cursor.execute("""
            INSERT OR IGNORE INTO ingestion_sources (id, protocol_name, status, last_heartbeat, error_count, records_ingested)
            VALUES (?, ?, 'ONLINE', CURRENT_TIMESTAMP, 0, 0);
            """, (src_id, name))

        cursor.close()
        logger.info("Database initialized successfully with WAL mode, tables, and FTS5 indexes.")
