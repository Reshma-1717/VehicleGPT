from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ChatQueryRequest(BaseModel):
    query: str
    vehicle_id: Optional[str] = None
    stream: bool = False

class ChatEvidence(BaseModel):
    event_ids: List[str] = []
    dtc_codes: List[str] = []
    trip_ids: List[str] = []
    time_range: str
    metrics: Dict[str, Any] = {}
    data_points_examined: int = 0

class ChatQueryResponse(BaseModel):
    answer: str
    intent: str
    confidence: float
    evidence: ChatEvidence
    source: str  # 'local_slm' or 'deterministic_fallback'
    latency_ms: float
    simulated_data: bool = True
    model_name: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
