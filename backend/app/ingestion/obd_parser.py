"""
SAE J1979 OBD-II Diagnostic Mode 01 PID Decoder.
Decodes standard standardized OBD-II telemetry signals from Mode $01 request/response frames.
"""

from typing import Dict, Any, Optional


class OBD2PIDDecoder:
    """
    Decodes standard SAE J1979 Mode 01 PID response payloads:
      Format: [Mode: 0x41] [PID: uint8] [Data Bytes A, B, C, D...]
    """

    @staticmethod
    def decode_pid(pid: int, data_bytes: bytes) -> Optional[Dict[str, Any]]:
        if not data_bytes:
            return None

        # Mode 01 PIDs
        if pid == 0x05:
            # Engine / Coolant Temperature: A - 40 (°C)
            temp_c = data_bytes[0] - 40
            return {"signal": "coolant_temp_c", "value": float(temp_c), "unit": "degC"}

        elif pid == 0x0C:
            # Engine / Motor RPM: ((A * 256) + B) / 4
            if len(data_bytes) < 2:
                return None
            rpm = ((data_bytes[0] * 256) + data_bytes[1]) / 4.0
            return {"signal": "motor_speed_rpm", "value": round(rpm, 1), "unit": "RPM"}

        elif pid == 0x0D:
            # Vehicle Speed: A (km/h)
            speed_kmh = float(data_bytes[0])
            return {"signal": "vehicle_speed_kmh", "value": speed_kmh, "unit": "km/h"}

        elif pid == 0x2F:
            # Fuel Level / State of Charge: (100 / 255) * A (%)
            soc = (100.0 / 255.0) * data_bytes[0]
            return {"signal": "battery_soc_percent", "value": round(soc, 1), "unit": "%"}

        elif pid == 0x42:
            # Control Module Voltage: ((A * 256) + B) / 1000 (V)
            if len(data_bytes) < 2:
                return None
            voltage = ((data_bytes[0] * 256) + data_bytes[1]) / 1000.0
            return {"signal": "control_module_voltage_v", "value": round(voltage, 2), "unit": "V"}

        elif pid == 0x5B:
            # Hybrid / EV Battery Pack Remaining Life: (100 / 255) * A (%)
            soh = (100.0 / 255.0) * data_bytes[0]
            return {"signal": "battery_soh_percent", "value": round(soh, 1), "unit": "%"}

        return None
