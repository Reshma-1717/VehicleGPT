import os
import sys
import csv
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.core.database import get_db

def export_telemetry_csv(output_file: str = "exported_telemetry.csv"):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, vehicle_id, trip_id, timestamp, signal_name, value, unit, protocol, tier FROM telemetry_records LIMIT 5000;")
        rows = cursor.fetchall()
        
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "vehicle_id", "trip_id", "timestamp", "signal_name", "value", "unit", "protocol", "tier"])
            for r in rows:
                writer.writerow(list(r))
        print(f"Exported {len(rows)} telemetry records to {output_file}")

if __name__ == "__main__":
    export_telemetry_csv()
