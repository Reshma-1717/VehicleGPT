import React, { useEffect, useState } from 'react';
import { X, AlertTriangle, Activity, Flame, ShieldAlert, Cpu } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts';
import { PreEventWindow } from '../types';
import { api } from '../services/api';

interface PreEventModalProps {
  eventId: string;
  onClose: () => void;
}

export const PreEventModal: React.FC<PreEventModalProps> = ({ eventId, onClose }) => {
  const [data, setData] = useState<PreEventWindow | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;
    api.getPreEventTelemetry(eventId, 60)
      .then((res) => {
        if (isMounted) {
          setData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error(err);
        if (isMounted) setLoading(false);
      });
    return () => { isMounted = false; };
  }, [eventId]);

  // Transform records into timestamp-grouped objects for Recharts
  const chartData = React.useMemo(() => {
    if (!data || !data.telemetry) return [];
    const grouped: { [ts: string]: any } = {};

    data.telemetry.forEach((r) => {
      const timeStr = r.timestamp.slice(11, 19);
      if (!grouped[timeStr]) {
        grouped[timeStr] = { time: timeStr };
      }
      if (r.signal_name === 'vehicle_speed_kmh') grouped[timeStr].speed = r.value;
      if (r.signal_name === 'battery_pack_temp_c') grouped[timeStr].temp = r.value;
      if (r.signal_name === 'battery_current_a') grouped[timeStr].current = r.value;
      if (r.signal_name === 'coolant_pump_duty_percent') grouped[timeStr].pump = r.value;
    });

    return Object.values(grouped).sort((a, b) => a.time.localeCompare(b.time));
  }, [data]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="glass-panel w-full max-w-4xl rounded-2xl border border-slate-700 bg-slate-900/95 overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-4 sm:p-6 border-b border-slate-800 flex items-center justify-between bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 text-amber-400 border border-amber-500/30">
              <ShieldAlert className="h-6 w-6" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-lg font-bold text-white tracking-tight">Pre-Event Telemetry Investigation</h3>
                <span className="px-2 py-0.5 rounded text-xs bg-red-950 text-red-300 border border-red-800/40 font-mono">
                  T - 60 Seconds Window
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">Event ID: {eventId}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-4 sm:p-6 overflow-y-auto space-y-6">
          {loading ? (
            <div className="h-64 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            </div>
          ) : !data ? (
            <p className="text-center text-slate-400 py-12">No pre-event telemetry window found for this event.</p>
          ) : (
            <>
              {/* Key Observations Box */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                  <Activity className="h-4 w-4 text-blue-400" />
                  Forensic Telemetry Findings (T-60s to Trigger)
                </span>
                <ul className="space-y-1.5 text-sm text-slate-300">
                  {data.key_findings.map((f, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="text-amber-400 mt-1">•</span>
                      <span>{f}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Multi-Signal Chart */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-3">
                  High-Frequency Signal Progression
                </span>
                <div className="h-64 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                      <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                      <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }} />
                      <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                      <Line type="monotone" dataKey="temp" name="Battery Temp (°C)" stroke="#ef4444" strokeWidth={2} dot={false} />
                      <Line type="monotone" dataKey="speed" name="Speed (km/h)" stroke="#3b82f6" strokeWidth={1.5} dot={false} />
                      <Line type="monotone" dataKey="current" name="Current (A)" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
                      <Line type="monotone" dataKey="pump" name="Pump Duty (%)" stroke="#10b981" strokeWidth={1.5} strokeDasharray="3 3" dot={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Signals summary footer */}
              <div className="flex flex-wrap items-center justify-between gap-3 text-xs text-slate-400 bg-slate-950/40 p-3 rounded-lg border border-slate-800">
                <div>
                  <span className="text-slate-500">Root-cause signals identified: </span>
                  <span className="font-mono text-amber-300">{data.root_cause_signals.join(', ')}</span>
                </div>
                <div className="font-mono text-slate-400">
                  Total Samples: {data.telemetry.length}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
