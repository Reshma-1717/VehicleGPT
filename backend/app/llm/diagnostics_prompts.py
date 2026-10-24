"""
Automotive Edge SLM System Prompts, Structured Output Schemas, and Diagnostic Directives.
Enforces strict zero-hallucination boundaries, numerical citation rules,
and CAN/DTC diagnostic reasoning guardrails for vehicle edge deployment.
"""

from typing import Dict, Any, List

SYSTEM_DIAGNOSTIC_DIRECTIVE = """You are VehicleGPT Edge Diagnostics, an on-device Small Language Model (SLM) running directly on the vehicle's compute unit.
Your function is to provide deterministic, grounded engineering explanations of vehicle telemetry, efficiency, range changes, and diagnostic trouble codes (DTCs).

OPERATIONAL RULES:
1. ONLY reference physical evidence provided in the verified telemetry and event context.
2. NEVER speculate, assume external variables, or guess missing parameters.
3. Quantify every root cause with exact numerical values and physical units (kW, kWh/100km, bar, °C).
4. Strictly reject requests that compromise vehicle safety or control bus writes (CAN injection, brake bypass, torque overrides).
5. If telemetry evidence is insufficient, explicitly state: 'INSUFFICIENT_TELEMETRY_EVIDENCE' and list the missing signals.
"""

SAFETY_BUS_WRITE_REFUSAL = (
    "SAFETY GUARD REFUSAL: Direct vehicle control commands and raw CAN bus write injections "
    "are blocked by hardware-enforced read-only Gateway boundaries (ISO 26262 ASIL-D)."
)

DIAGNOSTIC_PROMPT_TEMPLATES: Dict[str, str] = {
    "RANGE_DEGRADATION": """[CONTEXT]
Vehicle: {vehicle_model} (VIN: {vin})
Nominal Range: {nominal_range_km} km | Observed Range: {observed_range_km} km (Delta: -{range_drop_km} km)
Attribution Breakdown:
- HVAC Thermal Load: {hvac_loss_km} km ({hvac_pct}%)
- High Speed Aerodynamic Drag: {speed_loss_km} km ({speed_pct}%)
- Battery Thermal Conditioning: {thermal_loss_km} km ({thermal_pct}%)
- Low Tire Pressure Drag: {tire_loss_km} km ({tire_pct}%)

[QUERY]
{user_query}

[RESPONSE REQUIREMENTS]
Explain the exact engineering reasons for the range drop based on the physical attribution above. Include actionable driver recommendations.""",

    "THERMAL_ALERT": """[CONTEXT]
Vehicle: {vehicle_model}
Battery Pack Max Temp: {battery_temp_c}°C | Threshold: 42.0°C
Coolant Pump Duty: {pump_duty_percent}%
Inverter Temp: {inverter_temp_c}°C
Ambient Temp: {ambient_temp_c}°C

[QUERY]
{user_query}

[RESPONSE REQUIREMENTS]
Provide battery thermal status assessment and specify if fast charging or peak motor torque throttling is recommended.""",

    "ADAS_DISENGAGEMENT": """[CONTEXT]
Vehicle: {vehicle_model}
Event: ADAS Disengagement at {timestamp}
Trigger Reason: {trigger_reason}
Speed: {speed_kmh} km/h | Steering Angle: {steering_deg}°
Pre-Event Driver Torque: {driver_torque_nm} Nm

[QUERY]
{user_query}

[RESPONSE REQUIREMENTS]
Explain why the ADAS system disengaged, citing the driver torque override or camera/radar confidence degradation."""
}


def build_diagnostic_prompt(intent: str, context: Dict[str, Any], user_query: str) -> str:
    template = DIAGNOSTIC_PROMPT_TEMPLATES.get(intent)
    if not template:
        return f"{SYSTEM_DIAGNOSTIC_DIRECTIVE}\n\nContext: {context}\n\nUser Question: {user_query}"
    
    try:
        return f"{SYSTEM_DIAGNOSTIC_DIRECTIVE}\n\n" + template.format(user_query=user_query, **context)
    except KeyError:
        return f"{SYSTEM_DIAGNOSTIC_DIRECTIVE}\n\nContext: {context}\n\nUser Question: {user_query}"
