export interface TelemetryOverview {
  speed_kmh: number;
  soc_percent: number;
  battery_temp_c: number;
  range_km: number;
  energy_consumption_kwh_100km: number;
  motor_power_kw: number;
  cabin_temp_c: number;
  ambient_temp_c: number;
  tire_pressure_front_left_bar: number;
  tire_pressure_front_right_bar: number;
  tire_pressure_rear_left_bar: number;
  tire_pressure_rear_right_bar: number;
  cooling_pump_duty_percent: number;
  last_updated: string;
  current_trip_id?: string;
  status: string;
}

export interface TelemetryRecord {
  id: number;
  vehicle_id: string;
  trip_id?: string;
  timestamp: string;
  signal_name: string;
  value: number;
  unit: string;
  protocol: string;
  quality: string;
  tier: string;
}

export interface VehicleEvent {
  id: string;
  vehicle_id: string;
  trip_id?: string;
  timestamp: string;
  event_type: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  source: string;
  description: string;
  metadata_json: string;
}

export interface DiagnosticCode {
  id?: number;
  vehicle_id: string;
  trip_id?: string;
  timestamp: string;
  dtc_code: string;
  ecu_name: string;
  status: string;
  description: string;
  severity: string;
}

export interface Trip {
  id: string;
  vehicle_id: string;
  start_time: string;
  end_time?: string;
  trip_type: 'city' | 'highway' | 'mixed';
  distance_km: number;
  avg_speed_kmh: number;
  avg_consumption: number;
  ambient_temp_c: number;
  status: string;
}

export interface ChatEvidence {
  event_ids: string[];
  dtc_codes: string[];
  trip_ids: string[];
  time_range: string;
  metrics: Record<string, any>;
  data_points_examined: number;
}

export interface ChatResponse {
  answer: string;
  intent: string;
  confidence: number;
  evidence: ChatEvidence;
  source: string;
  latency_ms: number;
  simulated_data: boolean;
  model_name?: string;
  timestamp: string;
}

export interface SystemStatus {
  app_name: string;
  version: string;
  status: string;
  hardware_profile: string;
  offline_mode: boolean;
  model_loaded: boolean;
  model_path?: string;
  model_name?: string;
  cpu_usage_percent: number;
  memory_usage_mb: number;
  database_size_bytes: number;
  database_size_mb: number;
  historical_time_range_start?: string;
  historical_time_range_end?: string;
  telemetry_records_count: number;
  events_count: number;
  trips_count: number;
  active_sources: number;
  simulation_active: boolean;
  safety_boundaries_enforced: boolean;
}

export interface PreEventWindow {
  event_id: string;
  event_type: string;
  event_timestamp: string;
  window_duration_seconds: number;
  telemetry: TelemetryRecord[];
  key_findings: string[];
  root_cause_signals: string[];
}
