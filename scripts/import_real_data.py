import os
import sys
import argparse
import logging

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db
from backend.app.ingestion.real_data_loader import RealDataLoader

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("import_real_data")

def main():
    parser = argparse.ArgumentParser(description="Import real-world vehicle telemetry logs into VehicleGPT SQLite database.")
    parser.add_argument("--file", "-f", required=True, help="Path to real vehicle CSV / CAN log file")
    parser.add_argument("--vehicle-id", "-v", default=settings.SIMULATION_VEHICLE_ID, help="Target Vehicle ID / VIN")
    parser.add_argument("--clear-synthetic", "-c", action="store_true", help="Purge synthetic records before importing real data")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        logger.error(f"File not found: {args.file}")
        sys.exit(1)

    init_db()

    if args.clear_synthetic:
        logger.info("Purging synthetic records from SQLite database to ensure 100% real data...")
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM telemetry_records;")
            cursor.execute("DELETE FROM trips;")
            cursor.execute("DELETE FROM vehicle_events;")
            cursor.execute("DELETE FROM diagnostic_codes;")
            conn.commit()
        logger.info("Database cleared.")

    logger.info(f"Reading real telemetry log from: {args.file}")
    with open(args.file, "r", encoding="utf-8") as f:
        csv_text = f.read()

    result = RealDataLoader.load_csv_content(
        csv_text=csv_text,
        vehicle_id=args.vehicle_id
    )

    print("\n" + "=" * 60)
    print("REAL VEHICLE TELEMETRY IMPORT SUCCESSFUL")
    print("=" * 60)
    print(f"  • Vehicle ID:        {result['vehicle_id']}")
    print(f"  • Imported Records:  {result['imported_records']:,}")
    print(f"  • Trips Detected:    {result['trips_detected']}")
    print(f"  • Time Range:        {result['time_range']}")
    print(f"  • Signals Detected:  {', '.join(result['signals_detected'])}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
