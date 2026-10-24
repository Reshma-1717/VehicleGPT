import pytest
from backend.app.analytics.regen_braking import RegenBrakingModel


def test_standard_regen_deceleration():
    model = RegenBrakingModel(vehicle_mass_kg=2200.0)
    # 80 km/h to 20 km/h in 6 seconds, normal battery (25 C, 60% SOC)
    res = model.calculate_recovered_energy(
        v_start_kmh=80.0,
        v_end_kmh=20.0,
        brake_duration_sec=6.0,
        battery_soc_percent=60.0,
        battery_temp_c=25.0
    )
    assert res["recovered_kwh"] > 0.05
    assert res["recovery_efficiency_percent"] > 70.0
    assert res["regen_curtailed_reason"] is None


def test_curtailed_regen_high_soc():
    model = RegenBrakingModel(vehicle_mass_kg=2200.0)
    # 80 km/h to 0 km/h with battery at 98% SOC -> curtailed
    res = model.calculate_recovered_energy(
        v_start_kmh=80.0,
        v_end_kmh=0.0,
        brake_duration_sec=5.0,
        battery_soc_percent=98.0,
        battery_temp_c=25.0
    )
    assert res["regen_curtailed_reason"] == "BATTERY_FULL_HIGH_SOC_PROTECTION"
    assert res["recovery_efficiency_percent"] < 20.0


def test_curtailed_regen_cold_battery():
    model = RegenBrakingModel(vehicle_mass_kg=2200.0)
    # 70 km/h to 10 km/h with battery at -2 degC -> curtailed
    res = model.calculate_recovered_energy(
        v_start_kmh=70.0,
        v_end_kmh=10.0,
        brake_duration_sec=4.0,
        battery_soc_percent=50.0,
        battery_temp_c=-2.0
    )
    assert res["regen_curtailed_reason"] == "COLD_CELL_LITHIUM_PLATING_PROTECTION"
