from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime, timedelta

@dataclass
class SimulationScenario:
    name: str
    description: str
    trip_type: str
    duration_minutes: int
    ambient_temp_c: float
    avg_speed_kmh: float
    base_consumption: float
    events: List[Dict[str, Any]]
    dtcs: List[Dict[str, Any]]
