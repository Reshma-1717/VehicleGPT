import logging
from typing import Dict, Any, Optional
from datetime import datetime
from dateutil import parser as date_parser

logger = logging.getLogger("vehiclegpt.ingestion.normalizer")

# Plausible physical bounds for automotive sensors
SENSOR_BOUNDS = {
    "vehicle_speed_kmh": (0.0, 300.0),
    "battery_soc_percent": (0.0, 100.0),
    "battery_pack_temp_c": (-40.0, 120.0),
    "battery_voltage_v": (200.0, 900.0),
    "battery_current_a": (-600.0, 600.0),
    "motor_power_kw": (-150.0, 450.0),
    "energy_consumption_kwh_100km": (0.0, 100.0),
    "range_estimate_km": (0.0, 1200.0),
    "cabin_temp_c": (-30.0, 70.0),
    "ambient_temp_c": (-50.0, 60.0),
    "coolant_pump_duty_percent": (0.0, 100.0),
    "tire_pressure_fl_bar": (0.0, 5.0),
    "tire_pressure_fr_bar": (0.0, 5.0),
    "tire_pressure_rl_bar": (0.0, 5.0),
    "tire_pressure_rr_bar": (0.0, 5.0),
}

class IngestionNormalizer:
    """
    Normalizes incoming vehicle signals from heterogeneous protocols (CAN, VHAL, SOME/IP).
    Handles missing values, unit conversions, and bounds validation.
    """

    @staticmethod
    def normalize_record(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            signal_name = str(raw.get("signal_name", "")).strip()
            if not signal_name:
                return None

            raw_val = float(raw.get("value", 0.0))
            unit = str(raw.get("unit", "")).strip()

            # Timestamp parsing
            raw_ts = raw.get("timestamp")
            if isinstance(raw_ts, datetime):
                parsed_ts = raw_ts
            elif isinstance(raw_ts, str):
                parsed_ts = date_parser.parse(raw_ts)
            else:
                parsed_ts = datetime.utcnow()

            # Physical boundary checks
            quality = "VALID"
            if signal_name in SENSOR_BOUNDS:
                min_b, max_b = SENSOR_BOUNDS[signal_name]
                if not (min_b <= raw_val <= max_b):
                    quality = "OUT_OF_BOUNDS"
                    logger.warning(f"Sensor '{signal_name}' reading {raw_val} out of bounds [{min_b}, {max_b}]")

            return {
                "vehicle_id": str(raw.get("vehicle_id", "VIN-TATA-EV-2026-X01")),
                "trip_id": raw.get("trip_id"),
                "timestamp": parsed_ts.isoformat(),
                "signal_name": signal_name,
                "value": round(raw_val, 3),
                "unit": unit,
                "protocol": str(raw.get("protocol", "CAN_FD")),
                "quality": quality,
                "tier": str(raw.get("tier", "hot"))
            }
        except (ValueError, TypeError) as e:
            logger.error(f"Malformed telemetry record discarded: {raw} - Error: {e}")
            return None
