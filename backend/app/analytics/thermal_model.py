"""
Automotive EV Thermal Management and Auxiliary Load Model.
Calculates battery pack heat generation (Joule heating), active chiller power,
and cabin HVAC heating/cooling electrical demand based on thermodynamic equations.
"""

from typing import Dict, Any


class EVThermalModel:
    """
    Thermodynamic modeling for EV battery pack and cabin thermal systems.
    """

    def __init__(self, pack_mass_kg: float = 450.0, specific_heat_j_kg_k: float = 900.0):
        self.pack_mass_kg = pack_mass_kg
        self.specific_heat = specific_heat_j_kg_k  # J / (kg * K)

    def calculate_joule_heating(self, current_a: float, internal_resistance_ohm: float = 0.035) -> float:
        """
        P = I^2 * R (Watts)
        """
        p_watts = (current_a ** 2) * internal_resistance_ohm
        return round(p_watts / 1000.0, 2)  # Return in kW

    def calculate_thermal_loads(
        self,
        ambient_temp_c: float,
        cabin_temp_c: float,
        target_cabin_temp_c: float = 22.0,
        battery_pack_temp_c: float = 28.0,
        target_battery_temp_c: float = 25.0,
        battery_current_a: float = 30.0
    ) -> Dict[str, Any]:
        """
        Computes electrical power required for cabin HVAC and battery chiller/heater.
        """
        # 1. Cabin HVAC load
        cabin_delta = abs(cabin_temp_c - target_cabin_temp_c)
        ambient_cabin_delta = abs(ambient_temp_c - target_cabin_temp_c)

        if ambient_temp_c > target_cabin_temp_c:
            # AC Cooling mode: COP ~2.8
            cop = 2.8
            thermal_kw = (ambient_cabin_delta * 0.25) + (cabin_delta * 0.35)
            cabin_electrical_kw = round(min(5.5, max(0.2, thermal_kw / cop)), 2)
            hvac_mode = "COOLING"
        elif ambient_temp_c < 15.0:
            # Heat Pump / PTC Heating mode: COP ~1.8 (or 1.0 for PTC)
            cop = 2.0 if ambient_temp_c > 0 else 1.2
            thermal_kw = (ambient_cabin_delta * 0.30) + (cabin_delta * 0.40)
            cabin_electrical_kw = round(min(6.5, max(0.3, thermal_kw / cop)), 2)
            hvac_mode = "HEATING"
        else:
            cabin_electrical_kw = 0.3  # Ventilation only
            hvac_mode = "VENTILATION"

        # 2. Battery pack thermal load
        joule_heat_kw = self.calculate_joule_heating(battery_current_a)
        battery_delta = battery_pack_temp_c - target_battery_temp_c

        if battery_delta > 3.0:
            # Battery active chiller cooling: COP ~2.5
            chiller_electrical_kw = round(min(4.0, max(0.4, (battery_delta * 0.4 + joule_heat_kw) / 2.5)), 2)
            bms_thermal_state = "ACTIVE_CHILLING"
        elif battery_pack_temp_c < 10.0:
            # Battery pre-heating
            chiller_electrical_kw = round(min(3.5, max(0.5, abs(battery_delta) * 0.3)), 2)
            bms_thermal_state = "PRE_HEATING"
        else:
            chiller_electrical_kw = 0.05  # Passive pump circulation
            bms_thermal_state = "PASSIVE_MONITORING"

        total_aux_thermal_kw = round(cabin_electrical_kw + chiller_electrical_kw, 2)

        return {
            "hvac_mode": hvac_mode,
            "cabin_electrical_kw": cabin_electrical_kw,
            "battery_joule_heat_kw": joule_heat_kw,
            "bms_thermal_state": bms_thermal_state,
            "chiller_electrical_kw": chiller_electrical_kw,
            "total_aux_thermal_kw": total_aux_thermal_kw
        }
