import pytest
from backend.app.analytics.thermal_model import EVThermalModel


def test_joule_heating():
    model = EVThermalModel()
    # 100A with 0.035 Ohm -> 100^2 * 0.035 = 350 W = 0.35 kW
    p = model.calculate_joule_heating(current_a=100.0, internal_resistance_ohm=0.035)
    assert p == 0.35


def test_cooling_mode_hvac():
    model = EVThermalModel()
    # Hot day: 38 degC ambient, 32 degC cabin -> should trigger COOLING
    res = model.calculate_thermal_loads(
        ambient_temp_c=38.0,
        cabin_temp_c=32.0,
        target_cabin_temp_c=22.0,
        battery_pack_temp_c=36.0,
        target_battery_temp_c=25.0,
        battery_current_a=80.0
    )
    assert res["hvac_mode"] == "COOLING"
    assert res["cabin_electrical_kw"] > 1.0
    assert res["bms_thermal_state"] == "ACTIVE_CHILLING"
    assert res["total_aux_thermal_kw"] > 2.0


def test_mild_ambient_ventilation():
    model = EVThermalModel()
    # Mild day: 20 degC ambient, 22 degC cabin
    res = model.calculate_thermal_loads(
        ambient_temp_c=20.0,
        cabin_temp_c=22.0,
        target_cabin_temp_c=22.0,
        battery_pack_temp_c=26.0,
        target_battery_temp_c=25.0,
        battery_current_a=15.0
    )
    assert res["hvac_mode"] == "VENTILATION"
    assert res["bms_thermal_state"] == "PASSIVE_MONITORING"
