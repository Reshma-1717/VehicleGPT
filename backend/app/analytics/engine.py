import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from backend.app.core.database import get_db
from backend.app.repositories.telemetry_repo import TelemetryRepository
from backend.app.repositories.event_repo import EventRepository
from backend.app.repositories.trip_repo import TripRepository
from backend.app.schemas.analytics import (
    RangeReductionAnalysis,
    EfficiencyChangePoint,
    CityHighwayComparison,
    PreEventWindow,
    BatteryTemperatureTrend
)
from backend.app.analytics.factor_attribution import FactorAttributionEngine

from dateutil import parser as date_parser

logger = logging.getLogger("vehiclegpt.analytics.engine")

def to_datetime(val) -> datetime:
    if isinstance(val, datetime):
        return val
    return date_parser.parse(str(val))

class AnalyticsEngine:
    """
    Deterministic automotive analytics engine.
    Computes range degradation, efficiency change-points, city vs highway comparisons,
    thermal stress, and pre-event telemetry investigations from stored database records.
    """

    @staticmethod
    def analyze_range_reduction(vehicle_id: str, days: int = 14) -> Optional[RangeReductionAnalysis]:
        """
        Compare driving range and efficiency over the last 'days' (current period)
        versus the preceding period of equal length (baseline period).
        """
        now = datetime.utcnow()
        current_start = now - timedelta(days=days)
        baseline_start = current_start - timedelta(days=days)

        with get_db() as conn:
            cursor = conn.cursor()

            # Baseline telemetry metrics
            cursor.execute("""
            SELECT 
                AVG(CASE WHEN signal_name = 'range_estimate_km' THEN value END) as avg_range,
                AVG(CASE WHEN signal_name = 'ambient_temp_c' THEN value END) as avg_temp,
                AVG(CASE WHEN signal_name = 'vehicle_speed_kmh' THEN value END) as avg_speed,
                AVG(CASE WHEN signal_name = 'tire_pressure_fl_bar' THEN value END) as avg_tire,
                COUNT(*) as count
            FROM telemetry_records
            WHERE vehicle_id = ? AND timestamp >= ? AND timestamp < ?;
            """, (vehicle_id, baseline_start.isoformat(), current_start.isoformat()))
            baseline_row = cursor.fetchone()

            # Current telemetry metrics
            cursor.execute("""
            SELECT 
                AVG(CASE WHEN signal_name = 'range_estimate_km' THEN value END) as avg_range,
                AVG(CASE WHEN signal_name = 'ambient_temp_c' THEN value END) as avg_temp,
                AVG(CASE WHEN signal_name = 'vehicle_speed_kmh' THEN value END) as avg_speed,
                AVG(CASE WHEN signal_name = 'tire_pressure_fl_bar' THEN value END) as avg_tire,
                COUNT(*) as count
            FROM telemetry_records
            WHERE vehicle_id = ? AND timestamp >= ?;
            """, (vehicle_id, current_start.isoformat()))
            current_row = cursor.fetchone()

            # Trips count
            cursor.execute("""
            SELECT COUNT(*) as trip_count
            FROM trips
            WHERE vehicle_id = ? AND start_time >= ?;
            """, (vehicle_id, baseline_start.isoformat()))
            trip_count = cursor.fetchone()["trip_count"]

        if not baseline_row or not current_row or not baseline_row["avg_range"] or not current_row["avg_range"]:
            # Insufficient data
            return None

        base_range = float(baseline_row["avg_range"])
        curr_range = float(current_row["avg_range"])
        delta_range = curr_range - base_range
        drop_pct = abs(delta_range / base_range * 100.0) if base_range > 0 else 0.0

        base_temp = float(baseline_row["avg_temp"] or 25.0)
        curr_temp = float(current_row["avg_temp"] or 25.0)
        temp_delta = curr_temp - base_temp

        base_spd = float(baseline_row["avg_speed"] or 45.0)
        curr_spd = float(current_row["avg_speed"] or 45.0)
        spd_delta = curr_spd - base_spd

        base_tire = float(baseline_row["avg_tire"] or 2.4)
        curr_tire = float(current_row["avg_tire"] or 2.4)
        tire_delta = curr_tire - base_tire

        factors = FactorAttributionEngine.calculate_range_attribution(
            temp_delta_c=temp_delta,
            speed_delta_kmh=spd_delta,
            tire_pressure_delta_bar=tire_delta
        )

        return RangeReductionAnalysis(
            baseline_period=f"{baseline_start.strftime('%Y-%m-%d')} to {current_start.strftime('%Y-%m-%d')}",
            current_period=f"{current_start.strftime('%Y-%m-%d')} to {now.strftime('%Y-%m-%d')}",
            baseline_avg_range_km=round(base_range, 1),
            current_avg_range_km=round(curr_range, 1),
            range_delta_km=round(delta_range, 1),
            range_drop_percent=round(drop_pct, 1),
            factors=factors,
            trip_count_analyzed=trip_count,
            data_points=int(baseline_row["count"] + current_row["count"]),
            notes="Computed from actual on-device time-series records."
        )

    @staticmethod
    def detect_efficiency_change_point(vehicle_id: str) -> Optional[EfficiencyChangePoint]:
        """
        Locate the exact trip with the largest drop in energy efficiency (highest kWh/100km spike).
        """
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, start_time, trip_type, avg_consumption, ambient_temp_c, distance_km
            FROM trips
            WHERE vehicle_id = ?
            ORDER BY start_time ASC;
            """, (vehicle_id,))
            trips = [dict(r) for r in cursor.fetchall()]

        if len(trips) < 2:
            return None

        max_drop_magnitude = 0.0
        max_drop_trip = None
        prev_consumption = 0.0

        for i in range(1, len(trips)):
            prev = trips[i - 1]["avg_consumption"]
            curr = trips[i]["avg_consumption"]
            drop = curr - prev  # Higher consumption means lower efficiency
            if drop > max_drop_magnitude:
                max_drop_magnitude = drop
                max_drop_trip = trips[i]
                prev_consumption = prev

        if not max_drop_trip or max_drop_magnitude <= 0.0:
            return None

        # Fetch active DTCs around this trip
        trip_start = max_drop_trip["start_time"]
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT dtc_code, description
            FROM diagnostic_codes
            WHERE vehicle_id = ? AND trip_id = ?;
            """, (vehicle_id, max_drop_trip["id"]))
            dtc_rows = cursor.fetchall()
            dtcs = [f"{r['dtc_code']}: {r['description']}" for r in dtc_rows]

        drop_pct = (max_drop_magnitude / prev_consumption * 100.0) if prev_consumption > 0 else 0.0

        causes = [
            f"Cold weather thermal overhead (ambient temperature: {max_drop_trip['ambient_temp_c']}°C)",
            f"Extended high power demand on {max_drop_trip['trip_type']} segment"
        ]
        if dtcs:
            causes.append(f"Diagnostic code triggered: {dtcs[0]}")

        return EfficiencyChangePoint(
            trip_id=max_drop_trip["id"],
            timestamp=to_datetime(trip_start),
            previous_efficiency=round(prev_consumption, 1),
            dropped_efficiency=round(max_drop_trip["avg_consumption"], 1),
            drop_percentage=round(drop_pct, 1),
            drop_magnitude=round(max_drop_magnitude, 1),
            trip_type=max_drop_trip["trip_type"],
            possible_causes=causes,
            dtc_references=[r['dtc_code'] for r in dtc_rows]
        )

    @staticmethod
    def compare_city_highway_efficiency(vehicle_id: str, days: int = 30) -> Optional[CityHighwayComparison]:
        """Compare aggregate efficiency between city and highway driving trips."""
        start_ts = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                trip_type,
                COUNT(*) as trip_count,
                AVG(avg_consumption) as avg_consumption,
                AVG(avg_speed_kmh) as avg_speed,
                SUM(distance_km) as total_distance
            FROM trips
            WHERE vehicle_id = ? AND start_time >= ?
            GROUP BY trip_type;
            """, (vehicle_id, start_ts))
            rows = {r["trip_type"]: dict(r) for r in cursor.fetchall()}

        if "city" not in rows or "highway" not in rows:
            return None

        city = rows["city"]
        hwy = rows["highway"]

        city_cons = float(city["avg_consumption"] or 0.0)
        hwy_cons = float(hwy["avg_consumption"] or 0.0)
        diff_pct = round(((hwy_cons - city_cons) / city_cons * 100.0) if city_cons > 0 else 0.0, 1)

        explanation = (
            f"City driving averaged {round(city_cons, 1)} kWh/100km due to regenerative braking efficiency during stop-and-go. "
            f"Highway driving averaged {round(hwy_cons, 1)} kWh/100km ({abs(diff_pct)}% {'higher' if diff_pct > 0 else 'lower'}) "
            f"driven by aerodynamic drag at higher cruising speeds."
        )

        return CityHighwayComparison(
            city_trip_count=int(city["trip_count"]),
            city_avg_consumption_kwh_100km=round(city_cons, 1),
            city_avg_speed_kmh=round(float(city["avg_speed"] or 0.0), 1),
            city_total_distance_km=round(float(city["total_distance"] or 0.0), 1),
            highway_trip_count=int(hwy["trip_count"]),
            highway_avg_consumption_kwh_100km=round(hwy_cons, 1),
            highway_avg_speed_kmh=round(float(hwy["avg_speed"] or 0.0), 1),
            highway_total_distance_km=round(float(hwy["total_distance"] or 0.0), 1),
            efficiency_difference_percent=diff_pct,
            explanation=explanation
        )

    @staticmethod
    def investigate_pre_event_window(
        vehicle_id: str,
        event_id: Optional[str] = None,
        event_type: str = "BATTERY_OVERHEATING_WARNING",
        seconds_before: int = 60
    ) -> Optional[PreEventWindow]:
        """
        Analyze high-frequency telemetry in the 60-second window before a target event.
        """
        event = None
        if event_id:
            event = EventRepository.get_event_by_id(event_id)
        else:
            events = EventRepository.get_events(vehicle_id=vehicle_id, event_type=event_type, limit=1)
            if events:
                event = events[0]

        if not event:
            return None

        event_ts = to_datetime(event["timestamp"])
        records = TelemetryRepository.get_pre_event_window(
            vehicle_id=vehicle_id,
            target_timestamp=event_ts,
            seconds_before=seconds_before,
            seconds_after=15
        )

        # Extract root-cause signals dynamically across all recorded signals
        findings = []
        root_signals = []

        # Group values by signal
        signal_groups: Dict[str, List[float]] = {}
        for r in records:
            sig = r["signal_name"]
            val = float(r["value"])
            signal_groups.setdefault(sig, []).append(val)

        for sig, vals in signal_groups.items():
            if not vals:
                continue
            min_v = min(vals)
            max_v = max(vals)
            delta = max_v - min_v

            if sig == "battery_pack_temp_c" and (delta > 3.0 or max_v > 45.0):
                findings.append(f"Rapid thermal escalation in battery pack from {min_v:.1f}°C to {max_v:.1f}°C (peak: {max_v:.1f}°C).")
                root_signals.append(sig)
            elif sig == "battery_current_a" and max_v > 150.0:
                findings.append(f"High discharge current sustained (peaking at {max_v:.1f} A), driving I²R resistive heating.")
                root_signals.append(sig)
            elif sig == "vehicle_speed_kmh" and max_v > 90.0:
                findings.append(f"Vehicle sustained high cruising speed (peaking at {max_v:.1f} km/h) prior to alert.")
                root_signals.append(sig)
            elif sig == "coolant_pump_duty_percent" and max_v >= 80.0:
                findings.append(f"Cooling pump was commanded to {max_v:.0f}% duty cycle, indicating active thermal mitigation.")
                root_signals.append(sig)
            elif sig in ["tire_pressure_fl_bar", "tire_pressure_fr_bar", "tire_pressure_rl_bar", "tire_pressure_rr_bar"] and min_v < 2.0:
                findings.append(f"Low tire pressure detected on {sig} ({min_v:.2f} bar vs 2.4 bar placard).")
                root_signals.append(sig)
            elif delta > (abs(min_v) * 0.5) and abs(min_v) > 0.01:
                findings.append(f"Signal '{sig}' deviated significantly (range: {min_v:.1f} to {max_v:.1f}) in pre-event window.")
                if sig not in root_signals:
                    root_signals.append(sig)

        return PreEventWindow(
            event_id=event["id"],
            event_type=event["event_type"],
            event_timestamp=event_ts,
            window_duration_seconds=seconds_before,
            telemetry=records[:150],  # Bound for edge responsiveness
            key_findings=findings if findings else ["Telemetry parameters remained within standard operating bands."],
            root_cause_signals=root_signals
        )

    @staticmethod
    def analyze_battery_temperature_trends(vehicle_id: str, days: int = 7) -> Optional[BatteryTemperatureTrend]:
        """Compute battery temperature statistics and thermal stress across the last 7 days."""
        start_ts = (datetime.utcnow() - timedelta(days=days)).isoformat()

        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT 
                DATE(timestamp) as date_str,
                AVG(value) as avg_temp,
                MAX(value) as max_temp,
                MIN(value) as min_temp
            FROM telemetry_records
            WHERE vehicle_id = ? AND signal_name = 'battery_pack_temp_c' AND timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date_str ASC;
            """, (vehicle_id, start_ts))
            daily = [dict(r) for r in cursor.fetchall()]

            cursor.execute("""
            SELECT COUNT(*) as overheat_count
            FROM vehicle_events
            WHERE vehicle_id = ? AND event_type = 'BATTERY_OVERHEATING_WARNING' AND timestamp >= ?;
            """, (vehicle_id, start_ts))
            overheat_count = cursor.fetchone()["overheat_count"]

        if not daily:
            return None

        all_avgs = [r["avg_temp"] for r in daily if r["avg_temp"] is not None]
        all_maxs = [r["max_temp"] for r in daily if r["max_temp"] is not None]
        all_mins = [r["min_temp"] for r in daily if r["min_temp"] is not None]

        overall_avg = sum(all_avgs) / len(all_avgs) if all_avgs else 25.0
        overall_max = max(all_maxs) if all_maxs else 30.0
        overall_min = min(all_mins) if all_mins else 20.0

        stress = "LOW"
        if overheat_count > 0 or overall_max > 50.0:
            stress = "CRITICAL"
        elif overall_max > 42.0:
            stress = "MODERATE"

        return BatteryTemperatureTrend(
            timeframe=f"Last {days} days",
            avg_temp_c=round(overall_avg, 1),
            max_temp_c=round(overall_max, 1),
            min_temp_c=round(overall_min, 1),
            overheat_events_count=overheat_count,
            thermal_stress_level=stress,
            daily_stats=daily
        )
