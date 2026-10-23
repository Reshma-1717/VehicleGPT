from backend.app.analytics.engine import AnalyticsEngine
from backend.app.analytics.factor_attribution import FactorAttributionEngine

def test_factor_attribution_percentages_sum_to_100():
    factors = FactorAttributionEngine.calculate_range_attribution(
        temp_delta_c=-14.0,
        speed_delta_kmh=12.0,
        tire_pressure_delta_bar=-0.3,
        cabin_heat_active=True
    )
    assert len(factors) >= 2
    total_pct = sum(f.impact_percentage for f in factors)
    assert abs(total_pct - 100.0) < 0.5

def test_range_reduction_analytics():
    res = AnalyticsEngine.analyze_range_reduction("VIN-TATA-EV-2026-X01", days=14)
    assert res is not None
    assert res.baseline_avg_range_km > 0
    assert res.current_avg_range_km > 0
    assert res.range_delta_km < 0  # Range drop present
    assert res.range_drop_percent > 10.0
    assert len(res.factors) > 0

def test_efficiency_change_point():
    res = AnalyticsEngine.detect_efficiency_change_point("VIN-TATA-EV-2026-X01")
    assert res is not None
    assert res.trip_id == "TRIP-2026-DROP01"
    assert res.dropped_efficiency > res.previous_efficiency
    assert res.drop_magnitude > 10.0

def test_city_vs_highway_comparison():
    res = AnalyticsEngine.compare_city_highway_efficiency("VIN-TATA-EV-2026-X01", days=30)
    assert res is not None
    assert res.city_trip_count > 0
    assert res.highway_trip_count > 0
    assert res.highway_avg_consumption_kwh_100km > res.city_avg_consumption_kwh_100km

def test_pre_event_window():
    res = AnalyticsEngine.investigate_pre_event_window(
        vehicle_id="VIN-TATA-EV-2026-X01",
        event_type="BATTERY_OVERHEATING_WARNING",
        seconds_before=60
    )
    assert res is not None
    assert res.event_id == "EVT-BATT-OVERHEAT"
    assert len(res.telemetry) > 0
    assert "battery_pack_temp_c" in res.root_cause_signals

def test_battery_temperature_trends():
    res = AnalyticsEngine.analyze_battery_temperature_trends("VIN-TATA-EV-2026-X01", days=7)
    assert res is not None
    assert res.avg_temp_c > 0
    assert res.max_temp_c >= res.avg_temp_c
