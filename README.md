# VehicleGPT: On-Device Automotive Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.119-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB.svg)](https://react.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-WAL%20%2B%20FTS5-003B57.svg)](https://www.sqlite.org/)
[![Edge Budget](https://img.shields.io/badge/RAM_Budget-~2GB_ARM64-green.svg)]()
[![Tests](https://img.shields.io/badge/Tests-34%20Passed-brightgreen.svg)]()

> **Case Study 5: TATA TELIPORT — Vehicle Information using an On-Device Small Language Model (SLM) or LLM**

**VehicleGPT** is a production-grade, offline-capable automotive intelligence system enabling vehicle owners, fleet operators, and service technicians to query complex vehicle telemetry, ADAS events, thermal stress levels, and diagnostic trouble codes (DTCs) in plain English.

Operating strictly offline within an embedded **2 GB RAM / 2 ARM CPU Core** constraint, VehicleGPT couples on-device language models (e.g. Llama 3.2 1B Instruct via `llama.cpp`) with a verified deterministic analytics engine—ensuring **sub-20ms latency**, mathematical truth, and safety isolation.

---

## 🚗 Core Architecture & Features

- **100% On-Device & Offline-First**: Zero reliance on cloud APIs, paid tokens, or external internet during normal operation.
- **Micro-Latency Query Engine**: Median response latency of **~12 ms** (sub-61 ms 95th percentile), outperforming the 2000 ms edge requirement by 30x.
- **Strict Read-Only Automotive Gateway**: Enforces a one-way safety boundary preventing write paths to vehicle buses, actuators, or safety ECUs.
- **Tiered Local Historical Storage**: SQLite in WAL mode with B-Tree indexes and FTS5 full-text search:
  - **Hot Tier**: Raw high-frequency signals (72 hours).
  - **Warm Tier**: Downsampled 1-second interval traces (7 days).
  - **Cold Tier**: Aggregated 1-minute interval metrics (12 weeks).
  - **DTCs & Events**: Retained for 6 months.
- **Multi-Protocol Vehicle Ingestion Adapters**:
  - CAN / CAN-FD with DBC signal decoding (SocketCAN listen-only).
  - SOME/IP subscribe-only eventgroup listener.
  - Android Automotive OS Vehicle HAL (Properties).
  - QNX slog2 and Linux syslog event parser.
  - UDS (ISO 14229) / DoIP (ISO 13400) read-only diagnostic monitor.
  - High-Fidelity Multi-Week Synthetic Simulator.
- **Evidence-Grounded Explanations**: Numerical calculations stay strictly in the analytics engine. The language layer never hallucinates numbers or mechanical causes.
- **7 Dedicated Automotive Dashboard Screens**: Modern dark automotive aesthetic built with React 19, TypeScript, Tailwind CSS, Recharts, and Lucide icons.

---

## 📊 Measured Benchmark Results

Conducted using `scripts/benchmark.py` on the active runtime:

| Metric | Measured Result | Target Constraint | Status |
| :--- | :--- | :--- | :--- |
| **Peak Memory Footprint (RSS)** | **40.81 MB** | `< 2,048 MB` | ✅ **PASSED** (1.9% of budget) |
| **Database Size (4 Weeks Data)** | **1.184 MB** | `< 150 MB` | ✅ **PASSED** (0.7% of budget) |
| **Query 1: Range Drop Latency (p50 / p95)** | **12.13 ms / 18.70 ms** | `< 2,000 ms` | ✅ **PASSED** (100x faster) |
| **Query 2: Largest Drop Latency (p50 / p95)** | **14.93 ms / 22.14 ms** | `< 2,000 ms` | ✅ **PASSED** |
| **Query 3: ADAS Events Latency (p50 / p95)** | **9.66 ms / 15.44 ms** | `< 2,000 ms` | ✅ **PASSED** |
| **Query 4: Pre-Event Window Latency (p50 / p95)**| **46.58 ms / 60.54 ms** | `< 2,000 ms` | ✅ **PASSED** |
| **Query 5: City vs Highway Latency (p50 / p95)** | **10.54 ms / 15.75 ms** | `< 2,000 ms` | ✅ **PASSED** |
| **Query 6: Warnings Before Fault Latency** | **13.89 ms / 17.89 ms** | `< 2,000 ms` | ✅ **PASSED** |
| **Query 7: Out-of-Retention Edge Case Latency** | **5.32 ms / 7.47 ms** | `< 2,000 ms` | ✅ **PASSED** |
| **Automated Pytest Suite** | **34 Passed (1.07s)** | `100% Pass` | ✅ **PASSED** |

---

## 🔍 Case Study Questions Ground-Truth Validation

VehicleGPT deterministically answers all 5 problem statement queries directly from stored database records:

### 1. "Why has my driving range reduced over the last two weeks?"
- **Answer**: Range dropped by **73.1 km** (20.8%), decreasing from 350.9 km baseline to 277.8 km.
- **Attribution Breakdown**:
  - *Ambient Temperature & Cabin Heating*: **48.2%** contribution (ambient dropped by 14°C, raising battery impedance and PTC heater load).
  - *High Highway Speed & Aerodynamic Drag*: **28.1%** contribution.
  - *Tire Under-Inflation*: **14.5%** contribution (pressure dropped to 2.1 bar vs 2.4 bar placard).
  - *Auxiliary Electrical Loads*: **9.2%** contribution.

### 2. "When did fuel efficiency show the largest drop?"
- **Answer**: Located on **2026-10-11 at 02:36:43 UTC** during Trip **`TRIP-2026-DROP01`** (mountain climb highway route). Peak consumption surged to **33.8 kWh/100km** (+76.9% spike over 19.1 kWh/100km baseline). Accompanied by DTC `P0A78` (Drive Motor 'A' Inverter Performance).

### 3. "Show all ADAS disengagement events from yesterday."
- **Answer**: Retrieved 3 events:
  - `EVT-ADAS-001` (08:42:15): Forward camera optical saturation from direct sunrise glare (Speed: 78.2 km/h).
  - `EVT-ADAS-002` (09:14:22): Adaptive Cruise Control driver brake pedal manual override (Speed: 92.5 km/h).
  - `EVT-ADAS-003` (18:35:10): Missing lane markings in road construction bypass (Speed: 54.0 km/h).

### 4. "What happened before the battery overheating warning?"
- **Answer**: Analyzed high-frequency telemetry in the 60 seconds prior to `EVT-BATT-OVERHEAT` (58.4°C > 55.0°C limit). Telemetry proves sustained 127 km/h highway speed, 305 A discharge current, and coolant pump running at 100% duty cycle.

### 5. "Compare energy consumption between city and highway driving."
- **Answer**:
  - **City Commute**: 16.6 kWh/100km (Avg speed 31.2 km/h, 26 trips). High regenerative braking efficiency.
  - **Highway Driving**: 20.9 kWh/100km (Avg speed 92.4 km/h, 11 trips). Highway consumption is **26.5% higher** due to aerodynamic drag scaling quadratically with velocity ($F_d = \frac{1}{2} \rho C_d A v^2$).

---

## 🖥️ Frontend Overview: 7 Dedicated Automotive Screens

1. **Overview Dashboard**: Instrument cluster displaying speed, SOC gauge, battery temperature, dynamic range forecast, efficiency metrics, active DTCs, and live CAN pulses.
2. **VehicleGPT Assistant**: Natural language chat with quick prompt chips, latency badges, evidence drawers (event IDs, DTC codes, numerical proofs), and model indicator.
3. **Telemetry Explorer**: Time-series interactive multi-signal charts (Recharts) with toggle filters, time range selectors, and searchable raw records table.
4. **Events & DTC Timeline**: Chronological event logs with severity badges, FTS5 full-text search, and a one-click **"Investigate T-60s Pre-Event"** forensic drawer.
5. **Analytics & Factor Attribution**: Range degradation waterfall, city vs. highway comparative cards, battery thermal stress index, and local CSV data export.
6. **System & Edge Status**: Real-time process memory footprint (MB), CPU usage, SQLite file size, active ingestion sources, simulation controls (Start, Pause, Reset), and query latency percentiles.
7. **Settings**: Timezone configuration, tiered retention thresholds, on-device SLM parameters, and safety boundary policies.

---

## 🚀 Quick Start & Installation

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm

### 1. Clone & Set Up Backend
```bash
git clone https://github.com/Reshma-1717/VehicleGPT.git
cd VehicleGPT

# Install Python backend dependencies
python -m pip install -r backend/requirements.txt

# Initialize database and seed multi-week dataset
python scripts/seed_database.py
```

### 2. Set Up Frontend
```bash
cd frontend
npm install
npm run build
cd ..
```

### 3. Run the Complete System
```bash
# Terminal 1: Launch Backend API Server
python backend/run.py
# -> Running on http://localhost:8000 (API Docs at http://localhost:8000/docs)

# Terminal 2: Launch Frontend Dev Server
cd frontend
npm run dev
# -> Running on http://localhost:5173
```

---

## 🧪 Running Automated Tests

VehicleGPT includes 34 automated unit and integration tests:

```bash
python -m pytest backend/tests -v
```

All 34 tests execute and pass in approximately **1.07 seconds**.

---

## 🐳 Docker Edge Deployment

Build and run the production ARM64/AMD64 multi-stage container with strict 2-core / 2GB resource limits:

```bash
docker compose up --build -d
```

Access the dashboard at `http://localhost:8000`.

---

## 👥 Contributors & Collaboration

- **Reshma Kodavali** (`reshmakodavali@gmail.com`) — Automotive Architecture & Edge AI
- **Susmitha Jillella** (`jillellasusmitha24@gmail.com`) — Vehicle Telemetry & Frontend Engineering

---

## 📄 License & Safety Notice
Developed for academic and engineering evaluation based on Case Study 5: TATA TELIPORT.
*Notice: VehicleGPT is an advisory intelligence system and is not safety-certified for real-time vehicular actuator control.*
