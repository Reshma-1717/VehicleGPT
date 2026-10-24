import pytest
from backend.app.analytics.tire_monitor import TirePressureMonitor


def test_temperature_compensation():
    # 2.40 bar measured at 20 degC (293.15 K) should remain 2.40 bar
    p = TirePressureMonitor.temperature_compensate(raw_pressure_bar=2.40, tire_temp_c=20.0)
    assert p == 2.40

    # Cold day: 2.20 bar at -5 degC (268.15 K) -> compensated pressure is higher (~2.40 bar)
    p_cold = TirePressureMonitor.temperature_compensate(raw_pressure_bar=2.20, tire_temp_c=-5.0)
    assert p_cold > 2.20


def test_puncture_detection():
    # RL is 1.7 bar at 20 degC (critical drop)
    res = TirePressureMonitor.evaluate_tires(
        fl_bar=2.40,
        fr_bar=2.40,
        rl_bar=1.70,
        rr_bar=2.40,
        ambient_temp_c=20.0,
        nominal_bar=2.40
    )
    assert res["safe_to_drive"] is False
    assert any("CRITICAL_LOW_PRESSURE_REAR_LEFT" in w for w in res["warnings"])
    assert res["rolling_resistance_penalty_pct"] > 4.0
