import pytest
from backend.app.analytics.soh_estimator import BatterySOHEstimator


def test_internal_resistance_calculation():
    estimator = BatterySOHEstimator(nominal_capacity_kwh=80.0, nominal_voltage_v=400.0)
    # 400V rest, 395V load at 100A -> delta 5V / 100A = 0.05 Ohm (50 mOhm)
    r_int = estimator.estimate_internal_resistance(v_rest=400.0, v_load=395.0, current_a=100.0)
    assert r_int == 0.05


def test_soh_degradation_fresh_battery():
    estimator = BatterySOHEstimator(nominal_capacity_kwh=80.0)
    # Low throughput (e.g. 100 kWh throughput)
    result = estimator.calculate_cycle_degradation(total_kwh_throughput=100.0)
    assert result["soh_percent"] >= 99.0
    assert result["warranty_health_status"] == "NORMAL"
    assert result["equivalent_full_cycles"] < 1.0


def test_soh_degradation_aged_battery():
    estimator = BatterySOHEstimator(nominal_capacity_kwh=80.0)
    # 400,000 kWh throughput -> 2500 EFC
    result = estimator.calculate_cycle_degradation(
        total_kwh_throughput=400000.0,
        fast_charge_ratio=0.5,
        avg_battery_temp_c=35.0
    )
    assert result["soh_percent"] < 80.0
    assert result["warranty_health_status"] == "WARRANTY_REVIEW_RECOMMENDED"
    assert result["resistance_rise_percent"] > 50.0
