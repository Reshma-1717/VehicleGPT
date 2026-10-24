# Case Study 1: Range Drop Attribution Analysis

## Problem Statement
The driver inquires: *"Why did my range drop by 40 km over the past 2 weeks?"*
The vehicle is an 80 kWh Tata Harrier.ev AWD operating in real ambient driving conditions.

## Mathematical Attribution Model
The range drop $\Delta R = 40.0\text{ km}$ is decomposed deterministically across physical contributors:

$$\Delta R = \Delta R_{\text{HVAC}} + \Delta R_{\text{Speed}} + \Delta R_{\text{Thermal}} + \Delta R_{\text{Tire}}$$

### 1. In-Cabin Climate & HVAC Auxiliary Draw ($\Delta R_{\text{HVAC}}$)
- **Sensor Evidence**: Ambient temperature dropped to 36.5°C; cabin climate setpoint maintained at 21.0°C.
- **Physical Power**: Compressor electrical load averaged 3.2 kW continuously.
- **Attributed Loss**: **18.2 km (45.5%)**

### 2. High-Speed Aerodynamic Drag ($\Delta R_{\text{Speed}}$)
- **Sensor Evidence**: Vehicle speed distribution shifted from 62 km/h average to 98 km/h expressway cruising.
- **Physical Drag Power**: $P_{\text{aero}} = \frac{1}{2} \rho C_d A v^3$ scaling cubically with velocity.
- **Attributed Loss**: **12.4 km (31.0%)**

### 3. Battery Pack Thermal Management ($\Delta R_{\text{Thermal}}$)
- **Sensor Evidence**: Active chiller coolant pump ran at 65% duty cycle to maintain pack temperature below 38°C.
- **Attributed Loss**: **6.2 km (15.5%)**

### 4. Low Tire Pressure Drag ($\Delta R_{\text{Tire}}$)
- **Sensor Evidence**: Rear-left TPMS registered 2.05 bar (nominal 2.40 bar).
- **Attributed Loss**: **3.2 km (8.0%)**

## Driver Recommendations
1. Utilize pre-conditioning while connected to AC charging to minimize on-road HVAC pull.
2. Maintain highway cruise speeds between 85-90 km/h for optimal aero-efficiency.
3. Inflate all tires to 2.40 bar cold pressure.
