"""
Battery State-of-Health (SOH) and Degradation Dynamics Estimator.
Calculates battery capacity fade, equivalent full cycles (EFC), and internal resistance rise
using Ah integration and dynamic Ohm's law delta measurements.
"""

from typing import Dict, Any, List, Optional
import math


class BatterySOHEstimator:
    """
    Computes State of Health (SOH) and impedance degradation for lithium-ion packs.
    """

    def __init__(self, nominal_capacity_kwh: float = 80.0, nominal_voltage_v: float = 400.0):
        self.nominal_capacity_kwh = nominal_capacity_kwh
        self.nominal_voltage_v = nominal_voltage_v
        self.nominal_ah = (nominal_capacity_kwh * 1000.0) / nominal_voltage_v  # e.g. 200 Ah

    def estimate_internal_resistance(self, v_rest: float, v_load: float, current_a: float) -> float:
        """
        R_int = abs(V_rest - V_load) / abs(I_load) (Ohms)
        """
        if abs(current_a) < 1.0:
            return 0.025  # Nominal baseline ~25 mOhm
        r_int = abs(v_rest - v_load) / abs(current_a)
        return round(min(0.5, max(0.005, r_int)), 4)

    def calculate_cycle_degradation(
        self,
        total_kwh_throughput: float,
        fast_charge_ratio: float = 0.2,
        avg_battery_temp_c: float = 28.0
    ) -> Dict[str, Any]:
        """
        Computes SOH based on cumulative throughput and stress factors:
          - Equivalent Full Cycles (EFC) = Total Throughput / (2 * Nominal kWh)
          - Thermal acceleration factor: Arrhenius aging factor
          - Fast charge penalty multiplier
        """
        efc = total_kwh_throughput / (2.0 * max(1.0, self.nominal_capacity_kwh))

        # Arrhenius thermal factor relative to 25 degC
        temp_delta = max(0.0, avg_battery_temp_c - 25.0)
        thermal_multiplier = 1.0 + (temp_delta * 0.02)

        # C-rate / fast charge multiplier
        fast_charge_multiplier = 1.0 + (fast_charge_ratio * 0.3)

        # Base capacity loss: ~20% loss at 2500 EFC for automotive NMC/LFP cells
        # Capacity fade = 0.008 * sqrt(EFC) * thermal_multiplier * fast_charge_multiplier
        capacity_fade_percent = 0.008 * math.sqrt(max(0.0, efc)) * 100.0 * thermal_multiplier * fast_charge_multiplier
        soh_percent = round(max(50.0, 100.0 - capacity_fade_percent), 2)

        # Usable remaining capacity
        usable_capacity_kwh = round((soh_percent / 100.0) * self.nominal_capacity_kwh, 2)

        # Internal resistance rise: ~100% rise (2x) by end of life (80% SOH)
        resistance_rise_percent = round((100.0 - soh_percent) * 3.5, 1)

        return {
            "soh_percent": soh_percent,
            "usable_capacity_kwh": usable_capacity_kwh,
            "nominal_capacity_kwh": self.nominal_capacity_kwh,
            "equivalent_full_cycles": round(efc, 1),
            "resistance_rise_percent": resistance_rise_percent,
            "warranty_health_status": "NORMAL" if soh_percent >= 80.0 else "WARRANTY_REVIEW_RECOMMENDED"
        }
