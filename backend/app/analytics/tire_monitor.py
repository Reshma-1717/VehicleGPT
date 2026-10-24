"""
Automotive Tire Pressure Temperature Compensation and Leakage Monitor.
Applies Gay-Lussac gas law (P1/T1 = P2/T2 in Kelvin) to distinguish thermal pressure changes
from physical structural tire deflation and puncture leaks.
"""

from typing import Dict, Any, List


class TirePressureMonitor:
    """
    Normalizes tire pressure against 20 degC (293.15 K) baseline.
    """

    T_BASELINE_K = 293.15  # 20 degC

    @classmethod
    def temperature_compensate(cls, raw_pressure_bar: float, tire_temp_c: float) -> float:
        """
        P_comp = P_raw * (T_baseline / T_current)
        """
        t_kelvin = max(233.15, tire_temp_c + 273.15)  # clamp to >= -40 degC
        compensated = raw_pressure_bar * (cls.T_BASELINE_K / t_kelvin)
        return round(compensated, 2)

    @classmethod
    def evaluate_tires(
        cls,
        fl_bar: float,
        fr_bar: float,
        rl_bar: float,
        rr_bar: float,
        ambient_temp_c: float = 20.0,
        nominal_bar: float = 2.40
    ) -> Dict[str, Any]:
        tires = {
            "front_left": cls.temperature_compensate(fl_bar, ambient_temp_c),
            "front_right": cls.temperature_compensate(fr_bar, ambient_temp_c),
            "rear_left": cls.temperature_compensate(rl_bar, ambient_temp_c),
            "rear_right": cls.temperature_compensate(rr_bar, ambient_temp_c)
        }

        warnings = []
        rolling_resistance_penalty_pct = 0.0

        for wheel, p_comp in tires.items():
            delta = p_comp - nominal_bar
            if delta < -0.40:
                warnings.append(f"CRITICAL_LOW_PRESSURE_{wheel.upper()}: {p_comp} bar (nominal {nominal_bar})")
                rolling_resistance_penalty_pct += 4.5
            elif delta < -0.20:
                warnings.append(f"UNDER_INFLATED_{wheel.upper()}: {p_comp} bar")
                rolling_resistance_penalty_pct += 2.0
            elif delta > 0.40:
                warnings.append(f"OVER_INFLATED_{wheel.upper()}: {p_comp} bar")

        return {
            "compensated_pressures_bar": tires,
            "warnings": warnings,
            "rolling_resistance_penalty_pct": round(rolling_resistance_penalty_pct, 1),
            "safe_to_drive": len([w for w in warnings if "CRITICAL" in w]) == 0
        }
