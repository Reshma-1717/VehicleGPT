# VehicleGPT System Architecture

## Executive Overview
**VehicleGPT** is an on-device automotive intelligence platform based on **Case Study 5: TATA TELIPORT — Vehicle Information using an On-Device SLM or LLM**. It allows vehicle owners, fleet managers, and service engineers to interrogate complex vehicle telemetry, ADAS events, thermal stress conditions, and diagnostic trouble codes (DTCs) in natural English.

Operating strictly offline under edge constraints (~2 GB RAM, 2 ARM cores), VehicleGPT bridges raw high-frequency vehicle signals with evidence-grounded natural-language answers.

---

## High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------------+
|                                    VEHICLE BUS / ECUs                                   |
|   CAN / CAN-FD (DBC)   |   SOME/IP Subscribe   |   Android VHAL   |   UDS/DoIP (ISO 14229)  |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼ [ONE-WAY READ-ONLY OBSERVATION BOUNDARY]
+-----------------------------------------------------------------------------------------+
|                                 EDGE INGESTION DAEMON                                   |
|   - Physical Range & Boundary Validation (Pydantic / SENSOR_BOUNDS)                     |
|   - Out-of-Order & Quality Flagging (VALID, OUT_OF_BOUNDS, MALFORMED)                   |
|   - Dynamic Tiered Aging (Hot: 72h raw, Warm: 7d 1s, Cold: 12w 1m, DTCs: 6mo)           |
+-----------------------------------------------------------------------------------------+
                                             │
                                             ▼
+-----------------------------------------------------------------------------------------+
|                                 LOCAL HISTORICAL STORAGE                                |
|   - SQLite 3.40+ in Write-Ahead Logging (WAL) Mode, PRAGMA synchronous = NORMAL         |
|   - Tables: vehicles, trips, telemetry_records, vehicle_events, diagnostic_codes        |
|   - B-Tree Performance Indexes: timestamp, signal_name, trip_id, event_type, severity   |
|   - Full-Text Search: SQLite FTS5 index on events & diagnostic descriptions             |
+-----------------------------------------------------------------------------------------+
                          │                                           │
                          ▼                                           ▼
+-----------------------------------------+     +-----------------------------------------+
|            ANALYTICS ENGINE             |     |         NATURAL LANGUAGE ENGINE         |
| - Range Degradation & Factor Attrib     |     | - Deterministic Intent Router           |
| - Efficiency Drop Change-Point Detect   |     | - Relative Timeframe Resolver           |
| - City vs. Highway Consumption Comp     |     | - Read-Only Whitelisted Query Tools     |
| - Pre-Event 60s Telemetry Investigation |     | - Local SLM (llama.cpp INT4 GGUF)       |
| - Battery Temperature Trends (BMS)      |     | - Deterministic Grounded Templates      |
+-----------------------------------------+     +-----------------------------------------+
                          │                                           │
                          └─────────────────────┬─────────────────────┘
                                                ▼
+-----------------------------------------------------------------------------------------+
|                                  FASTAPI BACKEND SERVICE                                |
|   Endpoints: /api/health, /api/vehicle/*, /api/analytics/*, /api/chat/query, /api/system|
+-----------------------------------------------------------------------------------------+
                                                │
                                                ▼
+-----------------------------------------------------------------------------------------+
|                              REACT + VITE DASHBOARD & CHAT                              |
|   Dark Automotive UI • Tailwind CSS • Recharts Time-Series • Lucide Icons               |
|   Screens: Overview, Assistant, Telemetry Explorer, Events, Analytics, System, Settings |
+-----------------------------------------------------------------------------------------+
```

---

## Core System Modules

### 1. Read-Only Vehicle Ingestion Gateway
All vehicle interfaces are architected with a strict one-way boundary:
- **SocketCAN Adapter**: Promiscuous listen-only mode parsing CAN/CAN-FD frames via DBC signals.
- **SOME/IP Adapter**: Subscribe-only eventgroup consumer; no SOME/IP Method Call or Field Set is exposed.
- **Android VHAL Adapter**: Listens to AAOS `VehiclePropValue` updates.
- **UDS/DoIP Adapter**: Polls `ReadDTCInformation` (0x19) and `ReadDataByIdentifier` (0x22); blocks diagnostic flashing (`RequestDownload` 0x34) or actuator routines (`RoutineControl` 0x31).
- **High-Fidelity Vehicle Simulator**: Deterministically synthesizes multi-week city, highway, cold weather, mountain climb, thermal stress, and ADAS scenarios.

### 2. Multi-Tier Retention Engine
To operate comfortably under the 0.15 GB / 12-week edge storage estimate:
- **Hot Tier**: Full raw high-rate records preserved for **72 hours**.
- **Warm Tier**: Downsampled 1-second records preserved for **7 days**.
- **Cold Tier**: Downsampled 1-minute records preserved for **12 weeks**.
- **Diagnostic Trouble Codes (DTCs)**: Retained for **6 months**.

### 3. Grounded Natural Language & SLM Architecture
VehicleGPT guarantees sub-2-second edge latency and mathematical reliability:
1. **Deterministic Intent Routing**: Classifies queries (Range Drop, Efficiency Drop, ADAS, Overheating Pre-Event, City vs. Highway) in < 1 ms.
2. **Deterministic Mathematical Execution**: Numerical facts are calculated strictly in Python, guaranteeing 0% hallucination risk.
3. **Evidence Linking**: Every response is accompanied by referenced Event IDs, Trip IDs, DTC codes, timestamps, and confidence scores.
4. **Local SLM Integration**: If on-device GGUF weights are loaded (e.g. Llama 3.2 1B Instruct via `llama.cpp`), the model articulates the verified facts. If absent, the built-in deterministic templates synthesize the response with zero latency.
