import re
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from backend.app.schemas.chat import ChatEvidence

logger = logging.getLogger("vehiclegpt.retrieval.intent_router")

class IntentRouter:
    """
    Deterministic intent routing and relative timeframe resolver.
    Translates colloquial user queries into whitelisted analytical tool plans.
    """

    INTENT_RANGE_DROP = "RANGE_REDUCTION_EXPLANATION"
    INTENT_EFFICIENCY_DROP = "EFFICIENCY_DROP_CHANGEPOINT"
    INTENT_ADAS_DISENGAGE = "ADAS_DISENGAGEMENTS"
    INTENT_PRE_EVENT = "PRE_EVENT_INVESTIGATION"
    INTENT_CITY_VS_HIGHWAY = "CITY_VS_HIGHWAY_EFFICIENCY"
    INTENT_BATTERY_TRENDS = "BATTERY_TEMP_TRENDS"
    INTENT_WARNINGS_BEFORE_FAULT = "WARNINGS_BEFORE_FAULT"
    INTENT_INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

    @classmethod
    def resolve_relative_timeframe(cls, query: str) -> Dict[str, Any]:
        """
        Extract and resolve relative date phrases like 'yesterday', 'last two weeks', 'last 7 days'.
        """
        q = query.lower()
        now = datetime.utcnow()

        if "yesterday" in q:
            start = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = (now - timedelta(days=1)).replace(hour=23, minute=59, second=59, microsecond=999999)
            return {"label": "yesterday", "start": start, "end": end}
        elif "two weeks" in q or "2 weeks" in q or "last 14 days" in q:
            return {"label": "last two weeks", "start": now - timedelta(days=14), "end": now}
        elif "seven days" in q or "7 days" in q or "last week" in q:
            return {"label": "last seven days", "start": now - timedelta(days=7), "end": now}
        elif "month" in q or "30 days" in q:
            return {"label": "last 30 days", "start": now - timedelta(days=30), "end": now}
        elif "year 2021" in q or "5 years ago" in q or "10 years ago" in q or "last year" in q:
            return {"label": "out_of_retention", "start": now - timedelta(days=365*2), "end": now - timedelta(days=365)}
        else:
            return {"label": "recent_history", "start": now - timedelta(days=14), "end": now}

    @classmethod
    def classify_intent(cls, query: str) -> Tuple[str, float]:
        """
        Classifies incoming query into a supported analytical intent with confidence score.
        """
        q = query.lower()

        # Check for out-of-bounds/insufficient data requests
        if any(term in q for term in ["2021", "2020", "5 years ago", "10 years ago", "last century", "ancient"]):
            return cls.INTENT_INSUFFICIENT_DATA, 0.99

        # 1. Range drop / factor attribution
        if any(term in q for term in ["range reduced", "range drop", "driving range", "range drop", "loss in range"]):
            return cls.INTENT_RANGE_DROP, 0.95
        if "factors contributed" in q or "factor attribution" in q or "contributed most" in q:
            return cls.INTENT_RANGE_DROP, 0.92

        # 2. Largest efficiency drop
        if "largest drop" in q and ("efficiency" in q or "fuel" in q or "consumption" in q or "energy" in q):
            return cls.INTENT_EFFICIENCY_DROP, 0.98
        if "when did" in q and ("efficiency" in q or "fuel" in q) and "drop" in q:
            return cls.INTENT_EFFICIENCY_DROP, 0.95

        # 3. ADAS disengagements
        if "adas" in q and ("disengage" in q or "event" in q or "yesterday" in q):
            return cls.INTENT_ADAS_DISENGAGE, 0.98

        # 4. Warnings and codes before vehicle fault
        if ("warning" in q or "dtc" in q or "code" in q) and ("fault" in q or "failure" in q):
            return cls.INTENT_WARNINGS_BEFORE_FAULT, 0.98

        # 5. Pre-event investigation (e.g. before battery overheat warning)
        if ("before" in q or "prior to" in q or "what happened" in q) and ("overheat" in q or "thermal" in q or "battery warning" in q):
            return cls.INTENT_PRE_EVENT, 0.96

        # 6. City vs. Highway comparison
        if ("city" in q and "highway" in q) or ("city versus highway" in q) or ("compare" in q and ("efficiency" in q or "consumption" in q)):
            return cls.INTENT_CITY_VS_HIGHWAY, 0.97

        # 7. Battery temperature trends
        if ("battery" in q or "pack" in q) and ("temp" in q or "temperature" in q) and ("trend" in q or "days" in q or "week" in q):
            return cls.INTENT_BATTERY_TRENDS, 0.95

        # Keyword fallbacks
        if "adas" in q:
            return cls.INTENT_ADAS_DISENGAGE, 0.80
        if "range" in q:
            return cls.INTENT_RANGE_DROP, 0.80
        if "highway" in q or "city" in q:
            return cls.INTENT_CITY_VS_HIGHWAY, 0.80
        if "temperature" in q:
            return cls.INTENT_BATTERY_TRENDS, 0.80

        return cls.INTENT_INSUFFICIENT_DATA, 0.50
