from typing import List, Dict, Any
from backend.app.schemas.analytics import FactorAttribution

class FactorAttributionEngine:
    """
    Decomposes observed driving range or energy efficiency reductions into
    evidence-based automotive engineering physical factors.
    """

    @staticmethod
    def calculate_range_attribution(
        temp_delta_c: float,
        speed_delta_kmh: float,
        tire_pressure_delta_bar: float,
        cabin_heat_active: bool = True
    ) -> List[FactorAttribution]:
        """
        Computes physical attribution shares.
        1. Low temperature: Battery electrochemical resistance rises, cabin PTC heater consumes 3-6 kW.
        2. High vehicle speed: Aerodynamic drag scales with velocity squared (0.5 * rho * Cd * A * v^2).
        3. Underinflated tires: Increases rolling resistance coefficient (Crr).
        """
        factors: List[FactorAttribution] = []

        # Temperature / Heating component
        temp_loss_weight = 0.0
        if temp_delta_c < 0:
            temp_loss_weight = min(60.0, abs(temp_delta_c) * 3.5 + (15.0 if cabin_heat_active else 0.0))
            factors.append(FactorAttribution(
                factor="Ambient Temperature & Cabin Heating",
                impact_percentage=round(temp_loss_weight, 1),
                description=f"Ambient temperature dropped by {abs(round(temp_delta_c, 1))}°C, increasing battery internal impedance and driving cabin PTC heater demand.",
                evidence=f"Average ambient temperature shift from warm baseline to cold period."
            ))

        # Aerodynamic speed component
        speed_loss_weight = 0.0
        if speed_delta_kmh > 0:
            speed_loss_weight = min(40.0, speed_delta_kmh * 2.8)
            factors.append(FactorAttribution(
                factor="Higher Highway Speed & Aerodynamic Drag",
                impact_percentage=round(speed_loss_weight, 1),
                description=f"Average cruising speed increased by {round(speed_delta_kmh, 1)} km/h, substantially increasing aerodynamic drag.",
                evidence=f"Speed telemetry across analyzed highway segments."
            ))

        # Tire rolling resistance component
        tire_loss_weight = 0.0
        if tire_pressure_delta_bar < 0:
            tire_loss_weight = min(25.0, abs(tire_pressure_delta_bar) * 35.0)
            factors.append(FactorAttribution(
                factor="Tire Under-Inflation",
                impact_percentage=round(tire_loss_weight, 1),
                description=f"Tire pressure was {abs(round(tire_pressure_delta_bar, 2))} bar below recommended 2.4 bar placard rating, elevating tire contact patch rolling drag.",
                evidence="TPMS telemetry records."
            ))

        # Normalize weights to sum to 100%
        total_w = sum(f.impact_percentage for f in factors)
        if total_w > 0:
            for f in factors:
                f.impact_percentage = round((f.impact_percentage / total_w) * 100.0, 1)
        else:
            factors.append(FactorAttribution(
                factor="Normal Driving Variability",
                impact_percentage=100.0,
                description="Minor routine variance within standard operational margins.",
                evidence="Consistent telemetry across periods."
            ))

        return factors
