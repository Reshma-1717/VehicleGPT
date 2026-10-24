import pytest
from backend.app.analytics.driver_scoring import DriverScoringEngine


def test_smooth_trip_scoring():
    # Smooth progression: 20, 25, 30, 35, 40, 45, 50 km/h (gentle acceleration)
    records = [{"vehicle_speed_kmh": float(v)} for v in [20, 23, 26, 30, 34, 38, 42, 45]]
    res = DriverScoringEngine.evaluate_trip(records)
    assert res["eco_score"] >= 95.0
    assert res["harsh_accel_count"] == 0
    assert res["harsh_brake_count"] == 0
    assert res["rating"] == "EXCELLENT"


def test_aggressive_trip_scoring():
    # Aggressive: 0 to 60 km/h in 1s (~16.6 m/s^2), then 60 to 0 in 1s (-16.6 m/s^2)
    records = [{"vehicle_speed_kmh": float(v)} for v in [0, 60, 65, 0, 70, 0, 110]]
    res = DriverScoringEngine.evaluate_trip(records)
    assert res["harsh_accel_count"] >= 2
    assert res["harsh_brake_count"] >= 2
    assert res["eco_score"] < 80.0
