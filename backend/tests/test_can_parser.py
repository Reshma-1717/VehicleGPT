import pytest
import struct
from backend.app.ingestion.can_parser import CANFrameParser


def test_decode_bms_frame():
    # 400.0V (4000), 12.5A (125), 85.0% (170), 28 degC
    payload = struct.pack(">HhBb", 4000, 125, 170, 28) + b'\x00\x00'
    signals = CANFrameParser.decode_frame(0x100, payload)

    assert signals["battery_voltage_v"] == 400.0
    assert signals["battery_current_a"] == 12.5
    assert signals["battery_soc_percent"] == 85.0
    assert signals["battery_pack_temp_c"] == 28.0


def test_decode_vcu_frame():
    # 72.50 km/h (7250), 45% pedal (112), 0 bar brake, Drive gear (4)
    payload = struct.pack(">HBBB", 7250, 112, 0, 4) + b'\x00\x00\x00'
    signals = CANFrameParser.decode_frame(0x200, payload)

    assert signals["vehicle_speed_kmh"] == 72.5
    assert signals["accelerator_pedal_percent"] == 44.8
    assert signals["brake_pressure_bar"] == 0.0
    assert signals["gear_position"] == 4.0


def test_decode_tpms_frame():
    # 2.40 bar (120), 2.40 bar (120), 2.30 bar (115), 2.30 bar (115)
    payload = struct.pack("BBBB", 120, 120, 115, 115) + b'\x00\x00\x00\x00'
    signals = CANFrameParser.decode_frame(0x300, payload)

    assert signals["tire_pressure_fl_bar"] == 2.40
    assert signals["tire_pressure_fr_bar"] == 2.40
    assert signals["tire_pressure_rl_bar"] == 2.30
    assert signals["tire_pressure_rr_bar"] == 2.30


def test_parse_log_line():
    line = "(1719234812.123456) can0 300#7878737300000000"
    res = CANFrameParser.parse_log_line(line)
    assert res is not None
    assert res["can_id"] == "0x300"
    assert res["signals"]["tire_pressure_fl_bar"] == 2.40
