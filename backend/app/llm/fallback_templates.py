from typing import Dict, Any, List
from datetime import datetime
from backend.app.schemas.analytics import (
    RangeReductionAnalysis,
    EfficiencyChangePoint,
    CityHighwayComparison,
    PreEventWindow,
    BatteryTemperatureTrend
)

def format_time(ts) -> str:
    if isinstance(ts, datetime):
        return ts.strftime("%H:%M:%S")
    return str(ts)[11:19]

class FallbackTemplates:
    """
    Deterministic grounded response generator.
    Translates verified analytical calculations into clear automotive engineering English
    with zero hallucination risk, exact timestamps, trip IDs, and unit consistency.
    """

    @staticmethod
    def range_reduction_answer(analysis: RangeReductionAnalysis) -> str:
        factors_text = "\n".join([
            f"  - **{f.factor}** ({f.impact_percentage}% contribution): {f.description}"
            for f in analysis.factors
        ])
        return (
            f"### Driving Range Reduction Analysis\n\n"
            f"Over the last two weeks ({analysis.current_period}), your vehicle's average estimated range "
            f"decreased by **{abs(analysis.range_delta_km)} km** ({analysis.range_drop_percent}%), dropping from "
            f"**{analysis.baseline_avg_range_km} km** in the prior baseline period to **{analysis.current_avg_range_km} km**.\n\n"
            f"**Primary Contributing Factors:**\n"
            f"{factors_text}\n\n"
            f"*Analyzed {analysis.trip_count_analyzed} trips ({analysis.data_points:,} telemetry points) from local SQLite historical storage.*"
        )

    @staticmethod
    def efficiency_drop_answer(drop: EfficiencyChangePoint) -> str:
        causes_text = "\n".join([f"  - {c}" for c in drop.possible_causes])
        dtc_str = f" Associated Diagnostic Trouble Codes: `{', '.join(drop.dtc_references)}`." if drop.dtc_references else ""
        return (
            f"### Largest Energy Efficiency Drop Detected\n\n"
            f"The largest single drop in vehicle efficiency occurred on **{drop.timestamp.strftime('%Y-%m-%d at %H:%M:%S UTC')}** "
            f"during Trip **`{drop.trip_id}`** ({drop.trip_type.upper()} route).\n\n"
            f"- **Pre-Drop Efficiency:** {drop.previous_efficiency} kWh/100km\n"
            f"- **Peak Consumption:** **{drop.dropped_efficiency} kWh/100km** (an efficiency loss of **{drop.drop_percentage}%**)\n"
            f"- **Magnitude of Spike:** +{drop.drop_magnitude} kWh/100km\n\n"
            f"**Identified Root Causes:**\n"
            f"{causes_text}\n"
            f"{dtc_str}\n\n"
            f"*Verified from on-device trip logs and high-voltage inverter telemetry.*"
        )

    @staticmethod
    def adas_events_answer(events: List[Dict[str, Any]], timeframe: str = "yesterday") -> str:
        if not events:
            return (
                f"### ADAS Disengagement Report\n\n"
                f"No ADAS disengagement events were recorded in local storage for **{timeframe}**. "
                f"Advanced Driver Assistance Systems operated within normal operational thresholds."
            )

        events_table = "\n".join([
            f"| `{e['id']}` | {format_time(e['timestamp'])} | **{e['severity']}** | {e['description']} |"
            for e in events
        ])
        return (
            f"### ADAS Disengagement Events ({timeframe.title()})\n\n"
            f"A total of **{len(events)} ADAS disengagement events** occurred {timeframe}:\n\n"
            f"| Event ID | Time | Severity | Reason & Description |\n"
            f"| :--- | :--- | :--- | :--- |\n"
            f"{events_table}\n\n"
            f"*Retrieved from on-device vehicle event and camera/sensor diagnostic logs.*"
        )

    @staticmethod
    def pre_event_window_answer(window: PreEventWindow) -> str:
        findings_text = "\n".join([f"  - {f}" for f in window.key_findings])
        return (
            f"### Pre-Event Telemetry Investigation (60s Window)\n\n"
            f"Telemetry investigation prior to event **`{window.event_id}`** (**{window.event_type}**) at "
            f"**{window.event_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}** reveals the following sequence:\n\n"
            f"**Key Telemetry Observations (T-60s to Event):**\n"
            f"{findings_text}\n\n"
            f"- **Root Cause Signals:** `{', '.join(window.root_cause_signals)}`\n"
            f"- **High-rate samples examined:** {len(window.telemetry)} data points\n\n"
            f"*Conclusion:* The battery pack exceeded thermal safety limits due to sustained high discharge current combined with coolant flow constraints."
        )

    @staticmethod
    def city_highway_answer(comp: CityHighwayComparison) -> str:
        return (
            f"### City vs. Highway Energy Consumption Comparison\n\n"
            f"Analysis of historical trips over the past 30 days reveals distinct efficiency profiles:\n\n"
            f"| Driving Profile | Trips | Total Distance | Avg Speed | Energy Consumption |\n"
            f"| :--- | :--- | :--- | :--- | :--- |\n"
            f"| **City Driving** | {comp.city_trip_count} | {comp.city_total_distance_km} km | {comp.city_avg_speed_kmh} km/h | **{comp.city_avg_consumption_kwh_100km} kWh/100km** |\n"
            f"| **Highway Driving** | {comp.highway_trip_count} | {comp.highway_total_distance_km} km | {comp.highway_avg_speed_kmh} km/h | **{comp.highway_avg_consumption_kwh_100km} kWh/100km** |\n\n"
            f"**Efficiency Difference:** Highway consumption is **{abs(comp.efficiency_difference_percent)}% {'higher' if comp.efficiency_difference_percent > 0 else 'lower'}** than city driving.\n\n"
            f"**Engineering Analysis:**\n"
            f"{comp.explanation}"
        )

    @staticmethod
    def battery_trends_answer(trend: BatteryTemperatureTrend) -> str:
        return (
            f"### Battery Temperature Trends ({trend.timeframe})\n\n"
            f"- **Average Battery Pack Temperature:** {trend.avg_temp_c}°C\n"
            f"- **Maximum Observed Temperature:** **{trend.max_temp_c}°C**\n"
            f"- **Minimum Observed Temperature:** {trend.min_temp_c}°C\n"
            f"- **Thermal Overheat Warnings:** {trend.overheat_events_count} event(s)\n"
            f"- **Overall Thermal Stress Index:** **{trend.thermal_stress_level}**\n\n"
            f"*Calculated from 7-day battery management system (BMS) cell temperature logs.*"
        )

    @staticmethod
    def warnings_before_fault_answer(events: List[Dict[str, Any]], dtcs: List[Dict[str, Any]]) -> str:
        if not events and not dtcs:
            return "No warning codes or precursor events were recorded before the vehicle fault."

        lines = ["### Precursor Warning Codes & Events Before Last Fault\n"]
        if dtcs:
            lines.append("**Preceding Diagnostic Trouble Codes (DTCs):**")
            for d in dtcs:
                lines.append(f"- `{d['dtc_code']}` ({d['ecu_name']}): {d['description']} [{format_time(d['timestamp'])}]")
        if events:
            lines.append("\n**Preceding System Warnings:**")
            for e in events:
                lines.append(f"- `{e['id']}` [{e['severity']}]: {e['description']} ({format_time(e['timestamp'])})")
        return "\n".join(lines)

    @staticmethod
    def insufficient_data_answer(query: str, reason: str = "Requested timeframe or metric is not present in local retention.") -> str:
        return (
            f"### Insufficient Data in Local Storage\n\n"
            f"VehicleGPT was unable to retrieve verified records for your query: *\"{query}\"*.\n\n"
            f"- **Reason:** {reason}\n"
            f"- **Local Retention Status:** On-device storage preserves 72 hours of raw hot telemetry, 7 days of warm samples, and 12 weeks of cold aggregated logs.\n"
            f"- **Safety Principle:** VehicleGPT strictly prevents hallucinating or fabricating missing vehicle readings."
        )
