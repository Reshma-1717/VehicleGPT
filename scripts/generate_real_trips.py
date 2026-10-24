"""
Drive Cycle Batch Simulator and Real Trip Generator CLI.
Generates deterministic physical drive cycle datasets based on WLTP Class 3,
EPA Highway, and Urban stop-and-go profiles for edge SLM validation.
"""

import sys
import os
import argparse
import csv
from datetime import datetime, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.ingestion.real_data_loader import RealDataLoader


def generate_cycle_csv(output_path: str, cycle_type: str = "WLTP", duration_seconds: int = 1800):
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    start_time = datetime.utcnow() - timedelta(seconds=duration_seconds)

    print(f"Generating physical {cycle_type} drive cycle ({duration_seconds}s) to {output_path}...")
    headers = [
        "timestamp", "vehicle_speed_kmh", "battery_voltage_v", "battery_current_a",
        "battery_soc_percent", "battery_pack_temp_c", "cabin_temp_c", "ambient_temp_c",
        "motor_torque_nm", "coolant_pump_duty_percent", "tire_pressure_fl_bar",
        "tire_pressure_fr_bar", "tire_pressure_rl_bar", "tire_pressure_rr_bar",
        "energy_consumption_kwh_100km"
    ]

    soc = 92.0
    temp = 27.5
    cabin = 25.0
    ambient = 32.0

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for sec in range(0, duration_seconds, 10):
            t = start_time + timedelta(seconds=sec)
            phase = (sec % 300) / 300.0

            if cycle_type == "HIGHWAY":
                speed = 95.0 + (15.0 * (0.5 - abs(phase - 0.5)))
                current = 45.0 + (speed * 0.3)
                torque = 110.0
            elif cycle_type == "URBAN":
                speed = max(0.0, 45.0 * (1.0 - abs(phase - 0.5) * 2.0))
                current = 20.0 if speed > 5 else -2.0  # mild regen or idle
                torque = 60.0 if speed > 5 else 0.0
            else:  # WLTP
                speed = 50.0 + (40.0 * phase)
                current = 30.0 + (speed * 0.25)
                torque = 85.0

            # Battery voltage drops with current: V = OCV - I * R
            voltage = round(405.0 - (current * 0.035), 1)
            # Energy consumed
            power_kw = (voltage * current) / 1000.0
            kwh_delta = (power_kw * (10.0 / 3600.0))
            soc = max(10.0, round(soc - (kwh_delta / 80.0 * 100.0), 2))
            temp = round(temp + (0.003 * current), 2)
            cabin = round(max(22.0, cabin - 0.01), 1)

            # Efficiency
            eff = round((power_kw / max(1.0, speed)) * 100.0, 1) if speed > 5 else 16.5

            writer.writerow([
                t.isoformat(),
                round(speed, 1),
                voltage,
                round(current, 1),
                soc,
                temp,
                cabin,
                ambient,
                round(torque, 1),
                35.0 if temp > 30 else 20.0,
                2.35, 2.35, 2.30, 2.30,
                eff
            ])

    print(f"Drive cycle generation complete: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate physical EV drive cycles")
    parser.add_argument("--type", choices=["WLTP", "HIGHWAY", "URBAN"], default="WLTP")
    parser.add_argument("--seconds", type=int, default=1200)
    parser.add_argument("--out", default="sample_data/generated_cycle.csv")
    args = parser.parse_args()

    generate_cycle_csv(args.out, cycle_type=args.type, duration_seconds=args.seconds)
