"""
Driver Behavior and Eco-Driving Efficiency Scoring Engine.
Detects harsh acceleration, harsh braking, and speed stability from physical telemetry.
"""

from typing import List, Dict, Any


class DriverScoringEngine:
    """
    Computes an objective, normalized eco-driving score from physical time series.
    """

    @staticmethod
    def evaluate_trip(telemetry_records: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not telemetry_records or len(telemetry_records) < 5:
            return {
                "eco_score": 85.0,
                "harsh_accel_count": 0,
                "harsh_brake_count": 0,
                "high_speed_percent": 0.0,
                "rating": "GOOD"
            }

        harsh_accel = 0
        harsh_brake = 0
        high_speed_points = 0
        speeds = []

        for i in range(1, len(telemetry_records)):
            v_curr = float(telemetry_records[i].get("vehicle_speed_kmh", 0.0))
            v_prev = float(telemetry_records[i-1].get("vehicle_speed_kmh", 0.0))
            speeds.append(v_curr)

            # Acceleration in m/s^2 (assuming ~1s default delta if not specified)
            delta_v_ms = (v_curr - v_prev) / 3.6
            if delta_v_ms > 2.8:  # >2.8 m/s^2 harsh acceleration
                harsh_accel += 1
            elif delta_v_ms < -3.2:  # <-3.2 m/s^2 harsh braking
                harsh_brake += 1

            if v_curr > 100.0:
                high_speed_points += 1

        total_points = max(1, len(telemetry_records))
        high_speed_pct = round((high_speed_points / total_points) * 100.0, 1)

        # Baseline 100 points
        deductions = (harsh_accel * 4.0) + (harsh_brake * 3.5) + (high_speed_pct * 0.25)
        eco_score = max(30.0, min(100.0, round(100.0 - deductions, 1)))

        if eco_score >= 85.0:
            rating = "EXCELLENT"
        elif eco_score >= 70.0:
            rating = "GOOD"
        elif eco_score >= 50.0:
            rating = "MODERATE"
        else:
            rating = "AGGRESSIVE"

        return {
            "eco_score": eco_score,
            "harsh_accel_count": harsh_accel,
            "harsh_brake_count": harsh_brake,
            "high_speed_percent": high_speed_pct,
            "rating": rating
        }
