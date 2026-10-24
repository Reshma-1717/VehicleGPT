"""
Automotive Telemetry Dataset Exporter CLI.
Exports verified physical time-series records from SQLite into standardized CSV format.
"""

import sys
import os
import argparse
import csv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import get_db


def export_telemetry_to_csv(output_file: str, vehicle_id: str = "VIN-TATA-HARRIER-EV-001", limit: int = 10000):
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, signal_name, signal_value, physical_unit, source_bus, trip_id
            FROM telemetry_records
            WHERE vehicle_id = ?
            ORDER BY timestamp DESC
            LIMIT ?;
        """, (vehicle_id, limit))
        rows = cursor.fetchall()

    if not rows:
        print(f"No records found for vehicle {vehicle_id}.")
        return

    print(f"Exporting {len(rows)} telemetry records to {output_file}...")
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "signal_name", "signal_value", "physical_unit", "source_bus", "trip_id"])
        for r in rows:
            writer.writerow([r["timestamp"], r["signal_name"], r["signal_value"], r["physical_unit"], r["source_bus"], r["trip_id"]])

    print(f"Export completed: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export VehicleGPT telemetry to CSV")
    parser.add_argument("--out", default="sample_data/exported_telemetry.csv")
    parser.add_argument("--vehicle", default="VIN-TATA-HARRIER-EV-001")
    parser.add_argument("--limit", type=int, default=5000)
    args = parser.parse_args()

    export_telemetry_to_csv(args.out, vehicle_id=args.vehicle, limit=args.limit)
