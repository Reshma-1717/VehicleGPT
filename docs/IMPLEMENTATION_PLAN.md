# Implementation Plan - VehicleGPT (Edge Vehicle Intelligence System)

## Overview
VehicleGPT is an on-device automotive intelligence platform enabling drivers and service engineers to query complex vehicle telemetry, ADAS events, battery metrics, and diagnostic trouble codes (DTCs) in plain English. Operating under edge constraints (~2 GB RAM, 2 ARM cores, offline-first), it utilizes a local SLM (e.g., Llama 3.2 1B / Qwen 2.5 1.5B via llama.cpp) paired with a deterministic analytical fallback engine to guarantee sub-2-second queries, zero hallucinations, and absolute safety isolation (read-only vehicle interface).

---

## Architecture Components

```
+-----------------------------------------------------------------------------------+
|                              VehicleGPT System                                   |
+-----------------------------------------------------------------------------------+
|  [Vehicle Interfaces - Read-Only Gateway]                                        |
|  - CAN / CAN-FD DBC Parser     - Android Vehicle HAL      - UDS / DoIP DTCs       |
|  - SOME/IP (Subscribe Only)   - QNX slog2 / Syslog       - Multi-Week Simulator |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼ (One-way ingest boundary)
+-----------------------------------------------------------------------------------+
|  [Edge Ingestion Daemon & Retention Engine]                                       |
|  - Schema Normalization & Validation (Pydantic)                                   |
|  - Deduplication & Anomaly Detection                                              |
|  - Tiered Retention (Hot: 72h raw, Warm: 7d 1s, Cold: 12w 1m, DTC: 6mo)          |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  [Local Historical Storage - SQLite WAL + FTS5]                                   |
|  - vehicle, trip, telemetry_record, vehicle_event, diagnostic_code, query_audit   |
|  - B-Tree indexes on timestamp, trip_id, event_type, severity                     |
|  - FTS5 virtual tables for text search across event descriptions & DTC meanings    |
+-----------------------------------------------------------------------------------+
                                         │
                   ┌─────────────────────┴──────────────────────┐
                   ▼                                            ▼
+--------------------------------------+     +--------------------------------------+
|  [Analytics Engine]                  |     |  [Natural Language Engine]           |
|  - Range degradation & factor attrib |     |  - Deterministic Intent Router       |
|  - Efficiency drop (Change-Point)    |     |  - Relative Timeframe Resolver       |
|  - City vs. Highway efficiency       |     |  - Read-Only Whitelisted Query Tools |
|  - Pre-event 60s telemetry window    |     |  - Local SLM (llama.cpp GGUF)        |
|  - Battery thermal stress analysis   |     |  - Deterministic Fallback Templates  |
+--------------------------------------+     +--------------------------------------+
                   │                                            │
                   └─────────────────────┬──────────────────────┘
                                         ▼
+-----------------------------------------------------------------------------------+
|  [FastAPI Backend - REST API]                                                     |
|  /api/health, /api/vehicle/*, /api/analytics/*, /api/chat/query, /api/system/*   |
+-----------------------------------------------------------------------------------+
                                         │
                                         ▼
+-----------------------------------------------------------------------------------+
|  [React + Vite + TypeScript Frontend]                                            |
|  - Modern Dark Automotive UI (Tailwind CSS, Recharts, Lucide)                     |
|  - 7 Dedicated Screens: Overview, Assistant, Telemetry Explorer, Event Timeline,  |
|    Analytics, System & Edge Status, Settings                                     |
+-----------------------------------------------------------------------------------+
```

---

## Phased Execution Roadmap

### Phase 1: Repository Setup & Git Initial State
- Initialize git repo, configure `.gitignore`, set up multi-author commit attribution (Reshma & Susmitha Jillella).
- Create baseline documentation (`README.md`, `docs/ARCHITECTURE.md`).

### Phase 2: Core Backend, Schemas & SQLite Database
- Configure SQLite in WAL mode with busy timeout and foreign keys enabled.
- Create tables: `vehicles`, `trips`, `telemetry_records`, `vehicle_events`, `diagnostic_codes`, `ingestion_sources`, `query_audits`.
- Setup FTS5 full-text index on vehicle events and diagnostic codes.
- Implement Repository layer for high-throughput batch inserts and indexed time-range queries.

### Phase 3: Vehicle Simulator, Ingestion Adapters & Data Generation
- Build `VehicleSimulator` generating reproducible multi-week telemetry (city driving, highway cruising, cold starts, battery thermal runaway warning, ADAS disengagement, sudden efficiency drops, and DTC faults).
- Implement read-only adapter interfaces: CAN DBC decoder mock, SOME/IP listener mock, Android VHAL mock, QNX slog2 parser, UDS DTC reader, and sample replay adapter.
- Implement Edge Ingestion Daemon with hot/warm/cold downsampling and retention cleanup.

### Phase 4: Deterministic Analytics & Intent Routing
- Implement Deterministic Intent Router resolving natural language patterns and relative timeframes ("yesterday", "last 2 weeks", "before battery warning").
- Build Analytics Engine:
  1. Range drop analysis with multi-factor attribution (ambient temp/heater, high speed, aggressive throttle, low tire pressure).
  2. Efficiency change-point detection (identifying largest drop trip/timestamp).
  3. City vs. Highway efficiency comparison.
  4. Pre-event 60-second window extractor for root-cause telemetry.
  5. ADAS disengagement event aggregator.
  6. Battery temperature trends and overheating correlation.
- Enforce strict read-only query isolation.

### Phase 5: Local SLM Integration & Grounded Fallback
- Implement `LocalSLM` loader using `llama-cpp-python` / GGUF model runner with configurable context and temperature.
- Build robust deterministic fallback templates for all query classes when SLM is missing.
- Ensure all numerical figures originate strictly from verified analytics output, never generated hallucinated numbers.

### Phase 6: Modern Automotive React Frontend
- Build responsive, dark-mode automotive UI with Tailwind CSS, Recharts, and Lucide icons.
- Screen 1: Overview Dashboard (gauges, quick metrics, active trip, alerts).
- Screen 2: VehicleGPT Assistant (chat interface, quick question chips, latency badges, evidence drawers).
- Screen 3: Telemetry Explorer (multi-line charts, brush zoom, sensor selection, raw records table).
- Screen 4: Event Timeline (severity filters, pre-event 60s telemetry inspection modal).
- Screen 5: Analytics & Factor Attribution (waterfall chart, city vs highway comparisons, CSV download).
- Screen 6: System & Edge Status (memory, CPU, DB size, offline indicator, simulation controls).
- Screen 7: Settings (timezone, retention policy, model config, privacy policy).

### Phase 7: Verification, Pytest Suite & Benchmarking
- Write comprehensive test suite in `backend/tests/`:
  - Test all 5 primary case study questions against fixture data.
  - Test insufficient data handling.
  - Test schema validation, simulator reproducibility, ingestion, retention, analytics math, and safety boundaries.
- Build benchmark script `scripts/benchmark.py` testing latency (p50, p95), memory footprint, and storage metrics.
- Verify Docker configuration and document ARM edge deployment.
- Commit all changes and push to `https://github.com/Reshma-1717/VehicleGPT.git`.
