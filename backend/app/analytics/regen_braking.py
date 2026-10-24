"""
Regenerative Braking Kinetic Energy Recovery Model.
Calculates kinetic energy dissipation, electrical power regenerated,
and round-trip charging efficiency without synthetic approximations.
"""

from typing import Dict, Any


class RegenBrakingModel:
    """
    Physical kinetic energy recovery calculator:
      E_kinetic = 0.5 * mass * (v_initial^2 - v_final^2) (Joules)
      E_recovered = E_kinetic * eta_drivetrain * eta_inverter * eta_bms_acceptance
    """

    def __init__(self, vehicle_mass_kg: float = 2200.0):
        self.mass_kg = vehicle_mass_kg

    def calculate_recovered_energy(
        self,
        v_start_kmh: float,
        v_end_kmh: float,
        brake_duration_sec: float,
        battery_soc_percent: float,
        battery_temp_c: float
    ) -> Dict[str, Any]:
        v1 = v_start_kmh / 3.6  # m/s
        v2 = max(0.0, v_end_kmh) / 3.6

        if v1 <= v2:
            return {
                "kinetic_energy_kwh": 0.0,
                "recovered_kwh": 0.0,
                "recovery_efficiency_percent": 0.0,
                "regen_curtailed_reason": None
            }

        delta_kinetic_j = 0.5 * self.mass_kg * (v1**2 - v2**2)
        kinetic_kwh = delta_kinetic_j / 3_600_000.0

        # Efficiency factors
        drivetrain_eff = 0.88
        inverter_eff = 0.94

        # Battery charge acceptance limits
        curtailed_reason = None
        if battery_soc_percent > 95.0:
            bms_acceptance = 0.15
            curtailed_reason = "BATTERY_FULL_HIGH_SOC_PROTECTION"
        elif battery_temp_c < 5.0:
            bms_acceptance = 0.30
            curtailed_reason = "COLD_CELL_LITHIUM_PLATING_PROTECTION"
        elif battery_temp_c > 45.0:
            bms_acceptance = 0.40
            curtailed_reason = "BATTERY_HIGH_TEMPERATURE_PROTECTION"
        else:
            bms_acceptance = 0.92

        overall_eff = drivetrain_eff * inverter_eff * bms_acceptance
        recovered_kwh = round(kinetic_kwh * overall_eff, 4)
        avg_regen_power_kw = round((recovered_kwh / max(0.1, brake_duration_sec)) * 3600.0, 1)

        return {
            "kinetic_energy_kwh": round(kinetic_kwh, 4),
            "recovered_kwh": recovered_kwh,
            "avg_regen_power_kw": avg_regen_power_kw,
            "recovery_efficiency_percent": round(overall_eff * 100.0, 1),
            "regen_curtailed_reason": curtailed_reason
        }
