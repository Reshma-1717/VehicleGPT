from backend.app.llm.explanation import GroundedExplanationLayer

def test_query_1_range_reduction():
    q = "Why has my driving range reduced over the last two weeks?"
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "RANGE_REDUCTION_EXPLANATION"
    assert res.confidence >= 0.8
    assert "baseline_avg_range_km" in res.evidence.metrics
    assert "current_avg_range_km" in res.evidence.metrics
    assert res.evidence.metrics["range_delta_km"] < 0
    assert "Driving Range Reduction Analysis" in res.answer
    assert "Ambient Temperature" in res.answer
    assert res.latency_ms < 2000.0  # Must be well below 2.0s

def test_query_2_largest_efficiency_drop():
    q = "When did fuel efficiency show the largest drop?"
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "EFFICIENCY_DROP_CHANGEPOINT"
    assert "TRIP-2026-DROP01" in res.evidence.trip_ids
    assert res.evidence.metrics["peak_consumption"] > 30.0
    assert "Largest Energy Efficiency Drop" in res.answer
    assert res.latency_ms < 2000.0

def test_query_3_yesterday_adas_disengagements():
    q = "Show all ADAS disengagement events from yesterday."
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "ADAS_DISENGAGEMENTS"
    assert res.evidence.metrics["disengagement_count"] == 3
    assert len(res.evidence.event_ids) == 3
    assert "EVT-ADAS-001" in res.evidence.event_ids
    assert "EVT-ADAS-002" in res.evidence.event_ids
    assert "EVT-ADAS-003" in res.evidence.event_ids
    assert "ADAS Disengagement Events" in res.answer
    assert res.latency_ms < 2000.0

def test_query_4_pre_battery_overheat_window():
    q = "What happened before the battery overheating warning?"
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "PRE_EVENT_INVESTIGATION"
    assert "EVT-BATT-OVERHEAT" in res.evidence.event_ids
    assert res.evidence.metrics["data_points"] > 0
    assert "Pre-Event Telemetry Investigation" in res.answer
    assert "battery_pack_temp_c" in res.evidence.metrics["root_signals"]
    assert res.latency_ms < 2000.0

def test_query_5_city_vs_highway_comparison():
    q = "Compare energy consumption between city and highway driving."
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "CITY_VS_HIGHWAY_EFFICIENCY"
    assert "city_consumption_kwh_100km" in res.evidence.metrics
    assert "highway_consumption_kwh_100km" in res.evidence.metrics
    assert "City vs. Highway Energy Consumption Comparison" in res.answer
    assert res.latency_ms < 2000.0

def test_query_6_warnings_before_fault():
    q = "What were the warning codes before the last vehicle fault?"
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "WARNINGS_BEFORE_FAULT"
    assert len(res.evidence.dtc_codes) > 0
    assert "Precursor Warning Codes" in res.answer
    assert res.latency_ms < 2000.0

def test_query_7_insufficient_data_boundary():
    q = "Show telemetry from the year 2021."
    res = GroundedExplanationLayer.process_query(q)
    assert res.intent == "INSUFFICIENT_DATA"
    assert "Insufficient Data in Local Storage" in res.answer
    assert "Reason:" in res.answer
    assert res.latency_ms < 2000.0
