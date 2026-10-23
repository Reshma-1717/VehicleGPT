import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.core.config import settings
from backend.app.schemas.chat import ChatQueryResponse, ChatEvidence
from backend.app.retrieval.intent_router import IntentRouter
from backend.app.analytics.engine import AnalyticsEngine
from backend.app.repositories.event_repo import EventRepository
from backend.app.repositories.audit_repo import AuditRepository
from backend.app.llm.fallback_templates import FallbackTemplates
from backend.app.llm.local_slm import local_slm

logger = logging.getLogger("vehiclegpt.llm.explanation")

class GroundedExplanationLayer:
    """
    Coordinates Natural Language Understanding, Deterministic Analytics Execution,
    Evidence Extraction, and Model / Fallback explanation synthesis.
    """

    @classmethod
    def process_query(cls, query: str, vehicle_id: Optional[str] = None) -> ChatQueryResponse:
        start_time = time.perf_counter()
        target_vid = vehicle_id or settings.SIMULATION_VEHICLE_ID

        # 1. Classify intent & resolve timeframe
        intent, confidence = IntentRouter.classify_intent(query)
        timeframe = IntentRouter.resolve_relative_timeframe(query)

        evidence = ChatEvidence(time_range=timeframe["label"])
        answer = ""
        source = "deterministic_fallback"

        # 2. Route to appropriate deterministic analytical tool
        if intent == IntentRouter.INTENT_RANGE_DROP:
            analysis = AnalyticsEngine.analyze_range_reduction(target_vid, days=14)
            if analysis:
                answer = FallbackTemplates.range_reduction_answer(analysis)
                evidence.metrics = {
                    "baseline_avg_range_km": analysis.baseline_avg_range_km,
                    "current_avg_range_km": analysis.current_avg_range_km,
                    "range_drop_percent": analysis.range_drop_percent,
                    "range_delta_km": analysis.range_delta_km,
                    "top_factor": analysis.factors[0].factor if analysis.factors else "None"
                }
                evidence.data_points_examined = analysis.data_points
            else:
                answer = FallbackTemplates.insufficient_data_answer(query, "Insufficient baseline range records in database.")

        elif intent == IntentRouter.INTENT_EFFICIENCY_DROP:
            drop = AnalyticsEngine.detect_efficiency_change_point(target_vid)
            if drop:
                answer = FallbackTemplates.efficiency_drop_answer(drop)
                evidence.trip_ids = [drop.trip_id]
                evidence.dtc_codes = drop.dtc_references
                evidence.metrics = {
                    "peak_consumption": drop.dropped_efficiency,
                    "previous_consumption": drop.previous_efficiency,
                    "drop_percentage": drop.drop_percentage,
                    "trip_type": drop.trip_type
                }
            else:
                answer = FallbackTemplates.insufficient_data_answer(query, "No significant efficiency change point identified in trip history.")

        elif intent == IntentRouter.INTENT_ADAS_DISENGAGE:
            events = EventRepository.get_events(
                vehicle_id=target_vid,
                start_time=timeframe["start"],
                end_time=timeframe["end"],
                event_type="ADAS_DISENGAGEMENT"
            )
            answer = FallbackTemplates.adas_events_answer(events, timeframe=timeframe["label"])
            evidence.event_ids = [e["id"] for e in events]
            evidence.metrics = {"disengagement_count": len(events)}
            evidence.data_points_examined = len(events)

        elif intent == IntentRouter.INTENT_PRE_EVENT:
            window = AnalyticsEngine.investigate_pre_event_window(target_vid, seconds_before=60)
            if window:
                answer = FallbackTemplates.pre_event_window_answer(window)
                evidence.event_ids = [window.event_id]
                evidence.metrics = {
                    "pre_window_seconds": window.window_duration_seconds,
                    "root_signals": window.root_cause_signals,
                    "data_points": len(window.telemetry)
                }
                evidence.data_points_examined = len(window.telemetry)
            else:
                answer = FallbackTemplates.insufficient_data_answer(query, "No preceding battery overheating events located.")

        elif intent == IntentRouter.INTENT_CITY_VS_HIGHWAY:
            comp = AnalyticsEngine.compare_city_highway_efficiency(target_vid, days=30)
            if comp:
                answer = FallbackTemplates.city_highway_answer(comp)
                evidence.metrics = {
                    "city_consumption_kwh_100km": comp.city_avg_consumption_kwh_100km,
                    "highway_consumption_kwh_100km": comp.highway_avg_consumption_kwh_100km,
                    "difference_percent": comp.efficiency_difference_percent,
                    "total_trips": comp.city_trip_count + comp.highway_trip_count
                }
            else:
                answer = FallbackTemplates.insufficient_data_answer(query, "Need both city and highway trips recorded to perform comparison.")

        elif intent == IntentRouter.INTENT_BATTERY_TRENDS:
            trend = AnalyticsEngine.analyze_battery_temperature_trends(target_vid, days=7)
            if trend:
                answer = FallbackTemplates.battery_trends_answer(trend)
                evidence.metrics = {
                    "avg_temp_c": trend.avg_temp_c,
                    "max_temp_c": trend.max_temp_c,
                    "overheat_events": trend.overheat_events_count,
                    "thermal_stress": trend.thermal_stress_level
                }
            else:
                answer = FallbackTemplates.insufficient_data_answer(query, "No battery temperature telemetry found for the requested timeframe.")

        elif intent == IntentRouter.INTENT_WARNINGS_BEFORE_FAULT:
            events = EventRepository.get_events(vehicle_id=target_vid, severity="WARNING", limit=5)
            dtcs = EventRepository.get_dtcs(vehicle_id=target_vid, limit=5)
            answer = FallbackTemplates.warnings_before_fault_answer(events, dtcs)
            evidence.event_ids = [e["id"] for e in events]
            evidence.dtc_codes = [d["dtc_code"] for d in dtcs]

        else:
            # Insufficient or unknown data
            answer = FallbackTemplates.insufficient_data_answer(query)

        # 3. Optional local SLM re-articulation if model is active
        if local_slm.is_available() and intent != IntentRouter.INTENT_INSUFFICIENT_DATA:
            sys_prompt = (
                "You are VehicleGPT, an on-device automotive intelligence assistant. "
                "Explain the verified analytical findings in clear English. "
                "Never alter any numerical metrics or dates."
            )
            slm_out = local_slm.generate_explanation(f"User Query: {query}\nVerified Data:\n{answer}", system_prompt=sys_prompt)
            if slm_out:
                answer = slm_out
                source = "local_slm"

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        # 4. Audit query log
        AuditRepository.log_query(
            query_text=query,
            intent=intent,
            latency_ms=latency_ms,
            source=source,
            success=True,
            response_preview=answer[:100]
        )

        return ChatQueryResponse(
            answer=answer,
            intent=intent,
            confidence=round(confidence, 2),
            evidence=evidence,
            source=source,
            latency_ms=latency_ms,
            simulated_data=True,
            model_name="Llama-3.2-1B-Instruct-Q4_K_M" if source == "local_slm" else "Deterministic Analytical Engine"
        )
