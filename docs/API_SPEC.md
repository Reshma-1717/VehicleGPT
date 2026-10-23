# VehicleGPT REST API Specification

All endpoints return JSON responses and support edge-optimized local querying.

---

## 1. System & Health

### `GET /api/health`
Health check endpoint verifying offline operational readiness.
- **Response 200**:
```json
{
  "status": "healthy",
  "service": "VehicleGPT Edge Service",
  "timestamp": "2026-10-23T16:00:00Z",
  "offline_ready": true
}
```

### `GET /api/system/status`
Comprehensive status of edge host metrics, process memory footprint, database size, and model availability.
- **Response 200**:
```json
{
  "app_name": "VehicleGPT",
  "version": "1.0.0",
  "status": "ONLINE",
  "hardware_profile": "constrained",
  "offline_mode": true,
  "model_loaded": false,
  "model_name": "Deterministic Analytical Fallback (Active)",
  "cpu_usage_percent": 12.4,
  "memory_usage_mb": 40.8,
  "database_size_bytes": 1241088,
  "database_size_mb": 1.184,
  "telemetry_records_count": 4033,
  "events_count": 5,
  "trips_count": 37,
  "active_sources": 6,
  "simulation_active": true,
  "safety_boundaries_enforced": true
}
```

---

## 2. Vehicle Telemetry & Events

### `GET /api/vehicle/overview`
Retrieves live vehicle instrument cluster metrics.

### `GET /api/vehicle/telemetry`
Query time-series telemetry records with signal and time filters.
- **Parameters**: `signals` (optional), `trip_id` (optional), `start_time`, `end_time`, `limit` (default: 500).

### `GET /api/vehicle/events`
Query vehicle events with FTS5 full-text search and severity filters.
- **Parameters**: `severity` (INFO, WARNING, CRITICAL), `search` (text search), `limit`, `offset`.

### `GET /api/vehicle/diagnostics`
Query active and historical UDS diagnostic trouble codes (DTCs).

---

## 3. Analytics Endpoints

### `GET /api/analytics/range`
Calculates range loss between baseline and current periods with factor attribution breakdown.

### `GET /api/analytics/efficiency`
Returns the largest energy efficiency drop change-point trip and city vs. highway comparative analytics.

### `GET /api/analytics/battery`
Returns 7-day battery pack temperature trends and BMS thermal stress levels.

### `GET /api/analytics/preevent/{event_id}`
Extracts high-resolution telemetry records in the 60-second window leading right up to the specified event.

---

## 4. Natural Language Engine

### `POST /api/chat/query`
Primary natural language vehicle intelligence query interface.
- **Request**:
```json
{
  "query": "Why has my driving range reduced over the last two weeks?",
  "vehicle_id": "VIN-TATA-EV-2026-X01"
}
```
- **Response 200**:
```json
{
  "answer": "### Driving Range Reduction Analysis\n\nOver the last two weeks...",
  "intent": "RANGE_REDUCTION_EXPLANATION",
  "confidence": 0.95,
  "evidence": {
    "event_ids": [],
    "dtc_codes": [],
    "trip_ids": [],
    "time_range": "last two weeks",
    "metrics": {
      "baseline_avg_range_km": 350.9,
      "current_avg_range_km": 277.8,
      "range_drop_percent": 20.8,
      "range_delta_km": -73.1,
      "top_factor": "Ambient Temperature & Cabin Heating"
    },
    "data_points_examined": 1820
  },
  "source": "deterministic_fallback",
  "latency_ms": 12.13,
  "simulated_data": true,
  "model_name": "Deterministic Analytical Engine"
}
```
