"""
CAN Bus Raw Frame Decoder and Signal Extractor.
Parses standard automotive CAN 2.0A/B frames into engineering telemetry signals
without synthetic approximations.
"""

import struct
from typing import Dict, Any, Optional, List
from datetime import datetime


class CANFrameParser:
    """
    Decodes raw automotive Controller Area Network (CAN) frames into physical signals.
    Standard EV CAN message mappings:
      - 0x100: BMS High Voltage, Current, SOC
      - 0x102: BMS Min/Max Cell Voltage & Temp
      - 0x200: VCU Vehicle Speed, Accelerator, Brake, Gear
      - 0x204: MCU Motor Torque, Motor Speed, Inverter Temp
      - 0x300: TPMS Tire Pressures (FL, FR, RL, RR)
      - 0x350: Thermal Management (Coolant flow, HVAC power)
    """

    @staticmethod
    def decode_frame(can_id: int, payload: bytes) -> Dict[str, float]:
        signals: Dict[str, float] = {}
        if not payload or len(payload) < 8:
            payload = payload.ljust(8, b'\x00') if payload else b'\x00' * 8

        if can_id == 0x100:
            # BMS Main: [Voltage: uint16 * 0.1 V] [Current: int16 * 0.1 A] [SOC: uint8 * 0.5 %] [Pack Temp: int8]
            v_raw, i_raw, soc_raw, temp_raw = struct.unpack_from(">HhBb", payload, 0)
            signals["battery_voltage_v"] = round(v_raw * 0.1, 1)
            signals["battery_current_a"] = round(i_raw * 0.1, 1)
            signals["battery_soc_percent"] = round(min(100.0, max(0.0, soc_raw * 0.5)), 1)
            signals["battery_pack_temp_c"] = float(temp_raw)

        elif can_id == 0x200:
            # VCU Speed: [Speed: uint16 * 0.01 km/h] [AccelPedal: uint8 * 0.4 %] [Brake: uint8] [Gear: uint8]
            speed_raw, accel_raw, brake_raw, gear_raw = struct.unpack_from(">HBBB", payload, 0)
            signals["vehicle_speed_kmh"] = round(speed_raw * 0.01, 1)
            signals["accelerator_pedal_percent"] = round(accel_raw * 0.4, 1)
            signals["brake_pressure_bar"] = float(brake_raw)
            signals["gear_position"] = float(gear_raw)

        elif can_id == 0x204:
            # MCU Motor: [Torque: int16 * 0.1 Nm] [RPM: int16] [Inverter Temp: int8] [Motor Temp: int8]
            trq_raw, rpm_raw, inv_temp, mot_temp = struct.unpack_from(">hhbb", payload, 0)
            signals["motor_torque_nm"] = round(trq_raw * 0.1, 1)
            signals["motor_speed_rpm"] = float(rpm_raw)
            signals["inverter_temp_c"] = float(inv_temp)
            signals["motor_temp_c"] = float(mot_temp)

        elif can_id == 0x300:
            # TPMS: [FL: uint8 * 0.02 bar] [FR: uint8 * 0.02 bar] [RL: uint8 * 0.02 bar] [RR: uint8 * 0.02 bar]
            fl, fr, rl, rr = struct.unpack_from("BBBB", payload, 0)
            signals["tire_pressure_fl_bar"] = round(fl * 0.02, 2)
            signals["tire_pressure_fr_bar"] = round(fr * 0.02, 2)
            signals["tire_pressure_rl_bar"] = round(rl * 0.02, 2)
            signals["tire_pressure_rr_bar"] = round(rr * 0.02, 2)

        elif can_id == 0x350:
            # Thermal: [PumpDuty: uint8 %] [CabinTemp: int8] [AmbientTemp: int8] [HVACPower: uint16 * 10 W]
            pump, cabin, amb, hvac_w = struct.unpack_from("BbbH", payload, 0)
            signals["coolant_pump_duty_percent"] = float(pump)
            signals["cabin_temp_c"] = float(cabin)
            signals["ambient_temp_c"] = float(amb)
            signals["hvac_power_kw"] = round(hvac_w * 0.01, 2)

        return signals

    @classmethod
    def parse_log_line(cls, line: str) -> Optional[Dict[str, Any]]:
        """
        Parses standard candump log format:
        '(1719234812.123456) can0 100#01900014C81E0000'
        or '100#01900014C81E0000'
        """
        line = line.strip()
        if not line or line.startswith("#"):
            return None

        try:
            parts = line.split()
            frame_str = parts[-1] if "#" in parts[-1] else ""
            if "#" not in frame_str:
                return None

            can_id_hex, payload_hex = frame_str.split("#", 1)
            can_id = int(can_id_hex, 16)
            payload = bytes.fromhex(payload_hex)
            signals = cls.decode_frame(can_id, payload)

            return {
                "can_id": hex(can_id),
                "signals": signals,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception:
            return None
