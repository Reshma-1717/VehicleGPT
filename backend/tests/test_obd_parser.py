import pytest
from backend.app.ingestion.obd_parser import OBD2PIDDecoder


def test_decode_coolant_temp():
    # 0x05 Coolant Temp: A=125 -> 125 - 40 = 85 degC
    res = OBD2PIDDecoder.decode_pid(0x05, bytes([125]))
    assert res is not None
    assert res["signal"] == "coolant_temp_c"
    assert res["value"] == 85.0


def test_decode_rpm():
    # 0x0C RPM: A=0x1F (31), B=0x40 (64) -> ((31*256)+64)/4 = 8000/4 = 2000 RPM
    res = OBD2PIDDecoder.decode_pid(0x0C, bytes([0x1F, 0x40]))
    assert res is not None
    assert res["signal"] == "motor_speed_rpm"
    assert res["value"] == 2000.0


def test_decode_speed():
    # 0x0D Speed: A=65 km/h
    res = OBD2PIDDecoder.decode_pid(0x0D, bytes([65]))
    assert res is not None
    assert res["signal"] == "vehicle_speed_kmh"
    assert res["value"] == 65.0


def test_decode_soc():
    # 0x2F Fuel/SOC: A=204 -> (100/255)*204 = 80.0%
    res = OBD2PIDDecoder.decode_pid(0x2F, bytes([204]))
    assert res is not None
    assert res["signal"] == "battery_soc_percent"
    assert res["value"] == 80.0
