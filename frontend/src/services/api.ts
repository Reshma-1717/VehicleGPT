import {
  TelemetryOverview,
  TelemetryRecord,
  VehicleEvent,
  DiagnosticCode,
  Trip,
  ChatResponse,
  SystemStatus,
  PreEventWindow
} from '../types';

const API_BASE = '/api';

export const api = {
  // Health & Status
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    return res.json();
  },

  async getSystemStatus(): Promise<SystemStatus> {
    const res = await fetch(`${API_BASE}/system/status`);
    if (!res.ok) throw new Error('Failed to fetch system status');
    return res.json();
  },

  async getStorageStats() {
    const res = await fetch(`${API_BASE}/system/storage/stats`);
    if (!res.ok) throw new Error('Failed to fetch storage stats');
    return res.json();
  },

  // Vehicle
  async getOverview(): Promise<TelemetryOverview> {
    const res = await fetch(`${API_BASE}/vehicle/overview`);
    if (!res.ok) throw new Error('Failed to fetch vehicle overview');
    return res.json();
  },

  async getTelemetry(params?: { signals?: string; limit?: number; trip_id?: string; start_time?: string; end_time?: string }): Promise<{ count: number; records: TelemetryRecord[] }> {
    const query = new URLSearchParams();
    if (params?.signals) query.append('signals', params.signals);
    if (params?.limit) query.append('limit', params.limit.toString());
    if (params?.trip_id) query.append('trip_id', params.trip_id);
    if (params?.start_time) query.append('start_time', params.start_time);
    if (params?.end_time) query.append('end_time', params.end_time);

    const res = await fetch(`${API_BASE}/vehicle/telemetry?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch telemetry records');
    return res.json();
  },

  async getTrips(trip_type?: string, limit: number = 50): Promise<{ count: number; trips: Trip[] }> {
    const query = new URLSearchParams();
    if (trip_type && trip_type !== 'all') query.append('trip_type', trip_type);
    query.append('limit', limit.toString());

    const res = await fetch(`${API_BASE}/vehicle/trips?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch trips');
    return res.json();
  },

  async getEvents(params?: { event_type?: string; severity?: string; search?: string; limit?: number }): Promise<{ count: number; events: VehicleEvent[] }> {
    const query = new URLSearchParams();
    if (params?.event_type) query.append('event_type', params.event_type);
    if (params?.severity && params.severity !== 'ALL') query.append('severity', params.severity);
    if (params?.search) query.append('search', params.search);
    if (params?.limit) query.append('limit', params.limit.toString());

    const res = await fetch(`${API_BASE}/vehicle/events?${query.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch events');
    return res.json();
  },

  async getDiagnostics(): Promise<{ count: number; diagnostic_codes: DiagnosticCode[] }> {
    const res = await fetch(`${API_BASE}/vehicle/diagnostics`);
    if (!res.ok) throw new Error('Failed to fetch diagnostic codes');
    return res.json();
  },

  // Analytics
  async getRangeAnalytics(days: number = 14) {
    const res = await fetch(`${API_BASE}/analytics/range?days=${days}`);
    if (!res.ok) throw new Error('Failed to fetch range analytics');
    return res.json();
  },

  async getEfficiencyAnalytics() {
    const res = await fetch(`${API_BASE}/analytics/efficiency`);
    if (!res.ok) throw new Error('Failed to fetch efficiency analytics');
    return res.json();
  },

  async getBatteryAnalytics(days: number = 7) {
    const res = await fetch(`${API_BASE}/analytics/battery?days=${days}`);
    if (!res.ok) throw new Error('Failed to fetch battery analytics');
    return res.json();
  },

  async getPreEventTelemetry(eventId: string, secondsBefore: number = 60): Promise<PreEventWindow> {
    const res = await fetch(`${API_BASE}/analytics/preevent/${eventId}?seconds_before=${secondsBefore}`);
    if (!res.ok) throw new Error('Failed to fetch pre-event window telemetry');
    return res.json();
  },

  // Natural Language Chat
  async queryChat(queryText: string): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: queryText })
    });
    if (!res.ok) throw new Error('Failed to execute natural language query');
    return res.json();
  },

  // Simulation
  async startSimulation() {
    const res = await fetch(`${API_BASE}/simulation/start`, { method: 'POST' });
    return res.json();
  },

  async stopSimulation() {
    const res = await fetch(`${API_BASE}/simulation/stop`, { method: 'POST' });
    return res.json();
  },

  async resetSimulation() {
    const res = await fetch(`${API_BASE}/simulation/reset`, { method: 'POST' });
    return res.json();
  }
};
