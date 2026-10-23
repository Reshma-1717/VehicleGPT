import random
import math
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.repositories.telemetry_repo import TelemetryRepository
from backend.app.repositories.event_repo import EventRepository
from backend.app.repositories.trip_repo import TripRepository

logger = logging.getLogger("vehiclegpt.simulation.generator")

class VehicleSimulator:
    """
    Deterministic edge vehicle telemetry and scenario generator.
    Simulates multi-week driving profiles, battery overheating, ADAS disengagements,
    efficiency drops, cold starts, and diagnostic trouble codes (DTCs).
    """

    def __init__(self, vehicle_id: str = settings.SIMULATION_VEHICLE_ID, seed: int = settings.SIMULATION_SEED):
        self.vehicle_id = vehicle_id
        self.seed = seed
        random.seed(seed)

    def generate_comprehensive_dataset(self, reference_time: datetime = None) -> Dict[str, int]:
        """
        Generate complete historical data spanning 4 weeks leading up to reference_time.
        Guarantees ground-truth presence of:
        1. Range drop over the last 2 weeks (with cold weather & tire drop).
        2. Largest energy efficiency drop trip (Winter mountain pass climb).
        3. Yesterday's 3 distinct ADAS disengagement events.
        4. Battery Overheating warning event with 60-second high-rate pre-event telemetry.
        5. City vs. Highway distinct trip distributions.
        """
        if reference_time is None:
            reference_time = datetime.utcnow()

        logger.info(f"Generating comprehensive vehicle dataset for VIN {self.vehicle_id} (Seed: {self.seed})...")

        # Ensure vehicle exists to satisfy foreign key constraints
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT OR IGNORE INTO vehicles (id, vin, model, year, powertrain_type, battery_capacity_kwh)
            VALUES (?, ?, 'TATA Harrier.ev Concept AWD', 2026, 'BEV', 80.0);
            """, (self.vehicle_id, f"MAT{abs(hash(self.vehicle_id)) % 100000000000000:014d}"))

        trips: List[Dict[str, Any]] = []
        events: List[Dict[str, Any]] = []
        dtcs: List[Dict[str, Any]] = []
        telemetry_records: List[Dict[str, Any]] = []

        # -------------------------------------------------------------
        # 1. Baseline Weeks (Weeks 3 & 4 ago): Normal Warm Weather
        # -------------------------------------------------------------
        base_start = reference_time - timedelta(days=28)
        trip_counter = 1

        for day in range(14):
            day_time = base_start + timedelta(days=day, hours=8, minutes=30)
            # Morning city commute
            t_id = f"TRIP-BASE-CITY-{trip_counter:03d}"
            dist = round(random.uniform(14.0, 22.0), 2)
            duration = int(dist / 32.0 * 60)
            avg_cons = round(random.uniform(13.8, 14.8), 2)
            trips.append({
                "id": t_id,
                "vehicle_id": self.vehicle_id,
                "start_time": day_time.isoformat(),
                "end_time": (day_time + timedelta(minutes=duration)).isoformat(),
                "trip_type": "city",
                "distance_km": dist,
                "avg_speed_kmh": round(random.uniform(30.0, 36.0), 1),
                "avg_consumption": avg_cons,
                "ambient_temp_c": round(random.uniform(25.0, 29.0), 1),
                "status": "COMPLETED"
            })
            self._generate_trip_telemetry(telemetry_records, t_id, day_time, duration, "city", 27.0, avg_cons, tier="cold")
            trip_counter += 1

            # Alternate afternoon highway trip
            if day % 2 == 0:
                day_time_pm = base_start + timedelta(days=day, hours=17, minutes=15)
                t_id_hw = f"TRIP-BASE-HWY-{trip_counter:03d}"
                dist_hw = round(random.uniform(45.0, 75.0), 2)
                dur_hw = int(dist_hw / 90.0 * 60)
                avg_cons_hw = round(random.uniform(18.2, 19.4), 2)
                trips.append({
                    "id": t_id_hw,
                    "vehicle_id": self.vehicle_id,
                    "start_time": day_time_pm.isoformat(),
                    "end_time": (day_time_pm + timedelta(minutes=dur_hw)).isoformat(),
                    "trip_type": "highway",
                    "distance_km": dist_hw,
                    "avg_speed_kmh": round(random.uniform(86.0, 98.0), 1),
                    "avg_consumption": avg_cons_hw,
                    "ambient_temp_c": round(random.uniform(26.0, 30.0), 1),
                    "status": "COMPLETED"
                })
                self._generate_trip_telemetry(telemetry_records, t_id_hw, day_time_pm, dur_hw, "highway", 28.0, avg_cons_hw, tier="cold")
                trip_counter += 1

        # -------------------------------------------------------------
        # 2. Weeks 1 & 2 ago (Recent period): Cold Weather, Under-inflated Tires, Range Drop
        # -------------------------------------------------------------
        recent_start = reference_time - timedelta(days=14)
        for day in range(12):  # up to 2 days ago
            day_time = recent_start + timedelta(days=day, hours=8, minutes=45)
            t_id = f"TRIP-REC-CITY-{trip_counter:03d}"
            dist = round(random.uniform(15.0, 25.0), 2)
            duration = int(dist / 29.0 * 60)
            # Notice higher consumption due to cold weather (12C) and cabin heating
            avg_cons = round(random.uniform(18.5, 20.8), 2)
            trips.append({
                "id": t_id,
                "vehicle_id": self.vehicle_id,
                "start_time": day_time.isoformat(),
                "end_time": (day_time + timedelta(minutes=duration)).isoformat(),
                "trip_type": "city",
                "distance_km": dist,
                "avg_speed_kmh": round(random.uniform(27.0, 32.0), 1),
                "avg_consumption": avg_cons,
                "ambient_temp_c": round(random.uniform(10.0, 14.0), 1),
                "status": "COMPLETED"
            })
            self._generate_trip_telemetry(telemetry_records, t_id, day_time, duration, "city", 12.0, avg_cons, tire_bar=2.1, tier="warm")
            trip_counter += 1

        # -------------------------------------------------------------
        # 3. Largest Efficiency Drop Trip (12 days ago, High mountain ascent in freezing fog)
        # -------------------------------------------------------------
        drop_time = reference_time - timedelta(days=12, hours=14, minutes=10)
        t_id_drop = "TRIP-2026-DROP01"
        dur_drop = 85
        drop_consumption = 33.8  # Huge drop in efficiency (33.8 kWh/100km vs normal ~18.5)
        trips.append({
            "id": t_id_drop,
            "vehicle_id": self.vehicle_id,
            "start_time": drop_time.isoformat(),
            "end_time": (drop_time + timedelta(minutes=dur_drop)).isoformat(),
            "trip_type": "highway",
            "distance_km": 68.4,
            "avg_speed_kmh": 48.3,
            "avg_consumption": drop_consumption,
            "ambient_temp_c": 1.5,
            "status": "COMPLETED"
        })
        self._generate_trip_telemetry(telemetry_records, t_id_drop, drop_time, dur_drop, "highway", 1.5, drop_consumption, tier="warm")

        events.append({
            "id": "EVT-EFF-DROP-01",
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_drop,
            "timestamp": (drop_time + timedelta(minutes=45)).isoformat(),
            "event_type": "EFFICIENCY_ANOMALY_WARNING",
            "severity": "WARNING",
            "source": "POWERTRAIN",
            "description": "Critical efficiency drop detected: 33.8 kWh/100km (+82% higher than baseline). Inverter thermal throttling active.",
            "metadata_json": '{"trip_id": "TRIP-2026-DROP01", "avg_consumption": 33.8, "ambient_temp_c": 1.5, "elevation_gain_m": 1240}'
        })

        dtcs.append({
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_drop,
            "timestamp": (drop_time + timedelta(minutes=46)).isoformat(),
            "dtc_code": "P0A78",
            "ecu_name": "INVERTER_ECU",
            "status": "ACTIVE",
            "description": "Drive Motor 'A' Inverter Performance - High Current / Low Efficiency Throttling",
            "severity": "WARNING"
        })

        # -------------------------------------------------------------
        # 4. Battery Overheating Warning Event (5 days ago) + 60s High Frequency Pre-Event
        # -------------------------------------------------------------
        overheat_time = reference_time - timedelta(days=5, hours=15, minutes=24, seconds=30)
        t_id_overheat = "TRIP-THERMAL-STRESS-01"
        trips.append({
            "id": t_id_overheat,
            "vehicle_id": self.vehicle_id,
            "start_time": (overheat_time - timedelta(minutes=25)).isoformat(),
            "end_time": (overheat_time + timedelta(minutes=15)).isoformat(),
            "trip_type": "highway",
            "distance_km": 52.0,
            "avg_speed_kmh": 105.0,
            "avg_consumption": 24.2,
            "ambient_temp_c": 38.5,
            "status": "COMPLETED"
        })

        # 60 seconds of high-rate telemetry leading up to overheat_time
        pre_start = overheat_time - timedelta(seconds=60)
        for s in range(75): # 60 seconds before, 15 seconds after
            curr_s = pre_start + timedelta(seconds=s)
            ratio = min(1.0, s / 60.0)
            speed = 95.0 + ratio * 32.0  # accelerate to 127 km/h
            current = 140.0 + ratio * 165.0 # 305 A discharge
            temp = 41.0 + ratio * 17.5    # climbs up to 58.5 C!
            pump = 40.0 + ratio * 60.0    # pump duty maxes out at 100%

            telemetry_records.extend([
                {"vehicle_id": self.vehicle_id, "trip_id": t_id_overheat, "timestamp": curr_s.isoformat(), "signal_name": "vehicle_speed_kmh", "value": round(speed, 1), "unit": "km/h", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
                {"vehicle_id": self.vehicle_id, "trip_id": t_id_overheat, "timestamp": curr_s.isoformat(), "signal_name": "battery_pack_temp_c", "value": round(temp, 2), "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
                {"vehicle_id": self.vehicle_id, "trip_id": t_id_overheat, "timestamp": curr_s.isoformat(), "signal_name": "battery_current_a", "value": round(current, 1), "unit": "A", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
                {"vehicle_id": self.vehicle_id, "trip_id": t_id_overheat, "timestamp": curr_s.isoformat(), "signal_name": "coolant_pump_duty_percent", "value": round(pump, 1), "unit": "%", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
                {"vehicle_id": self.vehicle_id, "trip_id": t_id_overheat, "timestamp": curr_s.isoformat(), "signal_name": "motor_power_kw", "value": round(speed * current * 0.003, 1), "unit": "kW", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
                {"vehicle_id": self.vehicle_id, "trip_id": t_id_overheat, "timestamp": curr_s.isoformat(), "signal_name": "inverter_temp_c", "value": round(45.0 + ratio * 28.0, 1), "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": "hot"},
            ])

        events.append({
            "id": "EVT-BATT-OVERHEAT",
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_overheat,
            "timestamp": overheat_time.isoformat(),
            "event_type": "BATTERY_OVERHEATING_WARNING",
            "severity": "CRITICAL",
            "source": "BMS",
            "description": "High-voltage battery pack temperature exceeded critical limit (58.4°C > 55.0°C). Thermal power derating initiated by BMS.",
            "metadata_json": '{"peak_temp_c": 58.4, "threshold_c": 55.0, "pump_duty": 100.0, "peak_current_a": 305.0}'
        })

        dtcs.append({
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_overheat,
            "timestamp": overheat_time.isoformat(),
            "dtc_code": "P0A7E",
            "ecu_name": "BMS_MASTER",
            "status": "ACTIVE",
            "description": "Hybrid/EV Battery Pack Over Temperature Detected",
            "severity": "CRITICAL"
        })

        # -------------------------------------------------------------
        # 5. Yesterday's ADAS Disengagement Events (Exactly 1 day ago)
        # -------------------------------------------------------------
        yesterday_base = reference_time - timedelta(days=1)
        t_id_adas = "TRIP-ADAS-YEST-01"
        trips.append({
            "id": t_id_adas,
            "vehicle_id": self.vehicle_id,
            "start_time": (yesterday_base.replace(hour=8, minute=15, second=0)).isoformat(),
            "end_time": (yesterday_base.replace(hour=9, minute=45, second=0)).isoformat(),
            "trip_type": "highway",
            "distance_km": 84.2,
            "avg_speed_kmh": 78.4,
            "avg_consumption": 19.1,
            "ambient_temp_c": 21.0,
            "status": "COMPLETED"
        })

        # Event 1: Morning glare camera blinding
        evt1_ts = yesterday_base.replace(hour=8, minute=42, second=15)
        events.append({
            "id": "EVT-ADAS-001",
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_adas,
            "timestamp": evt1_ts.isoformat(),
            "event_type": "ADAS_DISENGAGEMENT",
            "severity": "WARNING",
            "source": "ADAS",
            "description": "Lane Centering disengaged: Forward-facing camera blinding caused by direct low-angle solar glare (optical saturation).",
            "metadata_json": '{"speed_kmh": 78.2, "confidence": 0.22, "mode": "Lane_Centering", "reason": "CAMERA_SOLAR_GLARE"}'
        })

        # Event 2: Driver override
        evt2_ts = yesterday_base.replace(hour=9, minute=14, second=22)
        events.append({
            "id": "EVT-ADAS-002",
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_adas,
            "timestamp": evt2_ts.isoformat(),
            "event_type": "ADAS_DISENGAGEMENT",
            "severity": "INFO",
            "source": "ADAS",
            "description": "Adaptive Cruise Control (ACC) disengaged: Manual brake pedal applied by driver (override request).",
            "metadata_json": '{"speed_kmh": 92.5, "override_type": "BRAKE_PEDAL", "mode": "ACC"}'
        })

        # Evening commute trip yesterday with Event 3: Faded lane markings
        t_id_adas_pm = "TRIP-ADAS-YEST-02"
        trips.append({
            "id": t_id_adas_pm,
            "vehicle_id": self.vehicle_id,
            "start_time": (yesterday_base.replace(hour=18, minute=10, second=0)).isoformat(),
            "end_time": (yesterday_base.replace(hour=19, minute=10, second=0)).isoformat(),
            "trip_type": "city",
            "distance_km": 31.0,
            "avg_speed_kmh": 42.0,
            "avg_consumption": 15.6,
            "ambient_temp_c": 19.5,
            "status": "COMPLETED"
        })

        evt3_ts = yesterday_base.replace(hour=18, minute=35, second=10)
        events.append({
            "id": "EVT-ADAS-003",
            "vehicle_id": self.vehicle_id,
            "trip_id": t_id_adas_pm,
            "timestamp": evt3_ts.isoformat(),
            "event_type": "ADAS_DISENGAGEMENT",
            "severity": "WARNING",
            "source": "ADAS",
            "description": "Lane Keep Assist disengaged: Missing/faded lane markings detected in road construction bypass zone.",
            "metadata_json": '{"speed_kmh": 54.0, "confidence": 0.18, "mode": "LKA", "reason": "LANE_MARKINGS_UNAVAILABLE"}'
        })

        # -------------------------------------------------------------
        # 6. Today's Live Telemetry Overview Records
        # -------------------------------------------------------------
        live_ts = reference_time
        latest_signals = [
            ("vehicle_speed_kmh", 0.0, "km/h"),
            ("battery_soc_percent", 78.5, "%"),
            ("battery_pack_temp_c", 28.2, "C"),
            ("range_estimate_km", 348.0, "km"),
            ("energy_consumption_kwh_100km", 16.4, "kWh/100km"),
            ("motor_power_kw", 0.0, "kW"),
            ("cabin_temp_c", 22.0, "C"),
            ("ambient_temp_c", 23.5, "C"),
            ("tire_pressure_fl_bar", 2.2, "bar"),
            ("tire_pressure_fr_bar", 2.2, "bar"),
            ("tire_pressure_rl_bar", 2.1, "bar"),
            ("tire_pressure_rr_bar", 2.1, "bar"),
            ("coolant_pump_duty_percent", 25.0, "%"),
        ]
        for sig, val, unit in latest_signals:
            telemetry_records.append({
                "vehicle_id": self.vehicle_id,
                "trip_id": None,
                "timestamp": live_ts.isoformat(),
                "signal_name": sig,
                "value": val,
                "unit": unit,
                "protocol": "CAN_FD",
                "quality": "VALID",
                "tier": "hot"
            })

        # Insert into repositories
        inserted_trips = TripRepository.insert_trips_batch(trips)
        inserted_events = EventRepository.insert_events_batch(events)
        for dtc in dtcs:
            EventRepository.insert_dtc(dtc)
        inserted_telemetry = TelemetryRepository.insert_batch(telemetry_records)

        logger.info(
            f"Dataset generated: {inserted_trips} trips, {inserted_events} events, "
            f"{len(dtcs)} DTCs, {inserted_telemetry} telemetry records."
        )

        return {
            "trips": inserted_trips,
            "events": inserted_events,
            "dtcs": len(dtcs),
            "telemetry": inserted_telemetry
        }

    def _generate_trip_telemetry(
        self,
        target_list: List[Dict[str, Any]],
        trip_id: str,
        start_time: datetime,
        duration_minutes: int,
        trip_type: str,
        ambient_temp: float,
        avg_consumption: float,
        tire_bar: float = 2.4,
        tier: str = "warm"
    ) -> None:
        """Synthesize downsampled telemetry samples for a given trip."""
        points = min(15, duration_minutes)  # Sample every few minutes to keep database light & fast
        step_minutes = max(1, duration_minutes // points)

        base_speed = 32.0 if trip_type == "city" else 92.0
        base_soc = random.uniform(85.0, 95.0)

        for i in range(points):
            t = start_time + timedelta(minutes=i * step_minutes)
            spd = max(0.0, base_speed + math.sin(i) * (18.0 if trip_type == "city" else 8.0))
            soc = max(15.0, base_soc - (i / points) * (duration_minutes * 0.35))
            batt_temp = ambient_temp + (spd / 20.0) + (4.0 if avg_consumption > 22.0 else 1.5)

            target_list.extend([
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "vehicle_speed_kmh", "value": round(spd, 1), "unit": "km/h", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "battery_soc_percent", "value": round(soc, 1), "unit": "%", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "battery_pack_temp_c", "value": round(batt_temp, 1), "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "energy_consumption_kwh_100km", "value": round(avg_consumption + math.sin(i * 1.5) * 1.8, 1), "unit": "kWh/100km", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "range_estimate_km", "value": round(soc * (4.2 if ambient_temp > 20 else 3.4), 1), "unit": "km", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "ambient_temp_c", "value": round(ambient_temp, 1), "unit": "C", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
                {"vehicle_id": self.vehicle_id, "trip_id": trip_id, "timestamp": t.isoformat(), "signal_name": "tire_pressure_fl_bar", "value": round(tire_bar, 2), "unit": "bar", "protocol": "CAN_FD", "quality": "VALID", "tier": tier},
            ])
