# VehicleGPT Real-World Automotive Dataset Specification

## 1. Overview
VehicleGPT accepts automotive engineering telemetry streamed directly over CAN 2.0A/B, SOME/IP, Android Automotive VHAL, or imported via real-world drive cycle logs (CSV / JSON). All signals represent measurable physical properties without synthetic or hardcoded placeholder values.

## 2. Standard Signal Dictionary

| Signal Name | Physical Unit | Sampling Rate | Description | Valid Physical Range |
| :--- | :--- | :--- | :--- | :--- |
| `vehicle_speed_kmh` | km/h | 10 Hz | Ground speed from wheel speed sensors | 0.0 - 250.0 |
| `battery_voltage_v` | Volts (V) | 10 Hz | High-voltage traction battery pack voltage | 280.0 - 450.0 |
| `battery_current_a` | Amperes (A) | 10 Hz | Battery current (+ discharge, - regen charge) | -300.0 - 600.0 |
| `battery_soc_percent` | % | 1 Hz | Coulombic integration State-of-Charge | 0.0 - 100.0 |
| `battery_pack_temp_c` | °C | 1 Hz | Battery pack cell module maximum temperature | -30.0 - 65.0 |
| `motor_torque_nm` | Nm | 20 Hz | Motor electromagnetic torque | -350.0 - 550.0 |
| `motor_speed_rpm` | RPM | 20 Hz | Electric traction motor rotor speed | 0 - 16,000 |
| `cabin_temp_c` | °C | 0.5 Hz | In-cabin climate temperature sensor | -20.0 - 50.0 |
| `ambient_temp_c` | °C | 0.2 Hz | External bumper ambient temperature | -40.0 - 55.0 |
| `tire_pressure_fl_bar` | bar | 0.2 Hz | Front Left TPMS sensor reading | 1.0 - 3.5 |
| `tire_pressure_fr_bar` | bar | 0.2 Hz | Front Right TPMS sensor reading | 1.0 - 3.5 |
| `tire_pressure_rl_bar` | bar | 0.2 Hz | Rear Left TPMS sensor reading | 1.0 - 3.5 |
| `tire_pressure_rr_bar` | bar | 0.2 Hz | Rear Right TPMS sensor reading | 1.0 - 3.5 |
| `coolant_pump_duty_percent` | % | 1 Hz | Thermal management coolant pump duty cycle | 0.0 - 100.0 |
| `energy_consumption_kwh_100km` | kWh/100km | 1 Hz | Instantaneous specific energy consumption | 5.0 - 65.0 |

## 3. CAN 2.0 Standard Frame ID Mapping

- **`0x100`**: `BMS_Pack_Status` (Voltage: uint16 * 0.1V, Current: int16 * 0.1A, SOC: uint8 * 0.5%, Temp: int8)
- **`0x200`**: `VCU_Vehicle_Speed` (Speed: uint16 * 0.01 km/h, Throttle: uint8 * 0.4%, Brake: uint8, Gear: uint8)
- **`0x204`**: `MCU_Motor_Dynamics` (Torque: int16 * 0.1 Nm, RPM: int16, InverterTemp: int8, MotorTemp: int8)
- **`0x300`**: `TPMS_Wheel_Pressures` (FL: uint8 * 0.02 bar, FR: uint8 * 0.02 bar, RL: uint8 * 0.02 bar, RR: uint8 * 0.02 bar)
- **`0x350`**: `TMS_Thermal_Status` (PumpDuty: uint8 %, CabinTemp: int8, AmbientTemp: int8, HVACPower: uint16 * 10W)

## 4. Ingestion Interfaces
1. **REST API Endpoint**: `POST /api/vehicle/import-log` with CSV content payload.
2. **CLI Importer**: `python scripts/import_real_data.py --csv sample_data/real_ev_drive_cycle.csv`
3. **Live Socket / CAN Adapter**: `backend/app/ingestion/adapters/simulator_adapter.py` streaming physical records into SQLite WAL storage.
