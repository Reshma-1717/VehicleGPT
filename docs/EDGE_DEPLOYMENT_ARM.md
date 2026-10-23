# Edge Deployment Guide: ARM64 & Constrained Profiles

This guide documents deploying **VehicleGPT** on resource-constrained embedded automotive hardware such as a **Raspberry Pi 5 / CM4**, **NXP i.MX8QuadMax**, or **NVIDIA Jetson Orin Nano**.

---

## 1. Hardware & Memory Budget Allocation (~2 GB Total RAM)

VehicleGPT is engineered to operate strictly within a **2.0 GB RAM / 2 ARM CPU Core** hardware profile:

```
+--------------------------------------------------------------+
|             TOTAL SYSTEM MEMORY BUDGET: 2048 MB              |
+--------------------------------------------------------------+
|  Component                                 | Footprint       |
| :----------------------------------------- | :-------------- |
|  Embedded Linux OS (Debian/Ubuntu Core)    | ~ 350 MB        |
|  VehicleGPT Backend Process (FastAPI)      | ~ 41 MB         |
|  SQLite Database & In-Memory WAL Cache     | ~ 64 MB         |
|  Local SLM Weights (Llama 3.2 1B Q4_K_M)   | ~ 1,100 MB      |
|  Available OS Buffer / Safety Margin       | ~ 493 MB        |
+--------------------------------------------------------------+
|  Total Peak Memory Under Full Load         | ~ 1,555 MB      |
+--------------------------------------------------------------+
```

---

## 2. Linux & OS Tuning for Embedded Automotive

### A. SQLite Optimization Pragmas
VehicleGPT automatically configures SQLite for high edge concurrency:
```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 15000;
PRAGMA cache_size = -64000; -- 64MB RAM cache
```

### B. Disable Unnecessary Background Daemons
```bash
# On Ubuntu/Debian ARM64, disable heavy desktop and cloud telemetry daemons
sudo systemctl disable cups.service bluetooth.service snapd.service
```

---

## 3. Deployment as a Systemd Edge Service

Create `/etc/systemd/system/vehiclegpt.service`:
```ini
[Unit]
Description=VehicleGPT On-Device Intelligence Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/opt/vehiclegpt
ExecStart=/opt/vehiclegpt/venv/bin/python backend/run.py
Restart=always
RestartSec=5
Environment=APP_ENV=production
Environment=HARDWARE_PROFILE=constrained
Environment=HOST=0.0.0.0
Environment=PORT=8000

# CPU and Memory Hard Limits
MemoryMax=1800M
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vehiclegpt.service
```

---

## 4. Docker Deployment on ARM64

To build and run natively on ARM64:
```bash
# Build multi-stage arm64 container
docker build -t vehiclegpt:arm64 .

# Run with resource constraints (2 Cores, 2GB RAM)
docker run -d \
  --name vehiclegpt-edge \
  --restart unless-stopped \
  --cpus="2.0" \
  --memory="2048m" \
  -p 8000:8000 \
  -v /opt/vehiclegpt/data:/app/data \
  vehiclegpt:arm64
```
