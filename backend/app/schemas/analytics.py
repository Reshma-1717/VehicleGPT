from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class FactorAttribution(BaseModel):
    factor: str
    impact_percentage: float
    description: str
    evidence: str

class RangeReductionAnalysis(BaseModel):
    baseline_period: str
    current_period: str
    baseline_avg_range_km: float
    current_avg_range_km: float
    range_delta_km: float
    range_drop_percent: float
    factors: List[FactorAttribution]
    trip_count_analyzed: int
    data_points: int
    notes: str

class EfficiencyChangePoint(BaseModel):
    trip_id: str
    timestamp: datetime
    previous_efficiency: float
    dropped_efficiency: float
    drop_percentage: float
    drop_magnitude: float
    trip_type: str
    possible_causes: List[str]
    dtc_references: List[str]

class CityHighwayComparison(BaseModel):
    city_trip_count: int
    city_avg_consumption_kwh_100km: float
    city_avg_speed_kmh: float
    city_total_distance_km: float
    highway_trip_count: int
    highway_avg_consumption_kwh_100km: float
    highway_avg_speed_kmh: float
    highway_total_distance_km: float
    efficiency_difference_percent: float
    explanation: str

class PreEventWindow(BaseModel):
    event_id: str
    event_type: str
    event_timestamp: datetime
    window_duration_seconds: int
    telemetry: List[Dict[str, Any]]
    key_findings: List[str]
    root_cause_signals: List[str]

class BatteryTemperatureTrend(BaseModel):
    timeframe: str
    avg_temp_c: float
    max_temp_c: float
    min_temp_c: float
    overheat_events_count: int
    thermal_stress_level: str
    daily_stats: List[Dict[str, Any]]
