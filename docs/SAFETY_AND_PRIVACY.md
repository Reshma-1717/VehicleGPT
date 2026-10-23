# Automotive Safety & Privacy Mandate

## 1. Safety Isolation Principles

Modern Software Defined Vehicles (SDVs) operate under strict functional safety standards (ISO 26262 ASIL-D). AI assistants and language models must remain strictly outside safety-critical vehicle control loops.

### Safety Guarantees Enforced in VehicleGPT:
1. **One-Way Ingestion Gateway**: All adapters (CAN/CAN-FD, SOME/IP, Android VHAL, UDS) operate strictly in promiscuous listen-only or subscribe-only mode.
2. **Hard Control Block**: Any attempt to dispatch write frames or commands to vehicle buses, ECUs, actuators, steering racks, or braking hydraulics triggers an immediate `PermissionError` and is securely logged to security audits.
3. **Read-Only Database Queries**: The analytical query planner strictly accepts whitelisted `SELECT` or `WITH` queries. Commands containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, or `TRUNCATE` are blocked before execution.
4. **Advisory Prototype Classification**: VehicleGPT is an advisory diagnostics prototype and must not be presented as automotive safety-certified.

---

## 2. Privacy & Edge Data Governance

1. **100% On-Device Processing**: In normal operation, all telemetry ingestion, FTS5 index searches, database persistence, analytical math, and language model inference occur locally on the edge device.
2. **Default-Deny Outbound Telemetry**: No telemetry records, GPS locations, or user queries are automatically uploaded to external cloud endpoints.
3. **No External AI APIs**: VehicleGPT does not require external AI API keys or third-party cloud LLM infrastructure.
4. **Synthetic Vehicle & Driver Data**: All demonstration data uses synthetic VINs (e.g., `VIN-TATA-EV-2026-X01`), simulated route profiles, and synthetic DTC codes to avoid privacy infringement.
5. **Auditable User Exports**: Data export actions (such as CSV downloads) are initiated exclusively by explicit user action.
