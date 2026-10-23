import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  ShieldCheck, 
  Clock, 
  Database, 
  Cpu, 
  Lock, 
  AlertOctagon,
  Save
} from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [timezone, setTimezone] = useState('Asia/Kolkata (IST)');
  const [hotHours, setHotHours] = useState(72);
  const [warmDays, setWarmDays] = useState(7);
  const [coldWeeks, setColdWeeks] = useState(12);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Top Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
          <SettingsIcon className="h-6 w-6 text-blue-400" />
          Settings & Configuration
        </h1>
        <p className="text-xs text-slate-400 mt-1">
          Adjust on-device operational parameters, retention thresholds, and review safety constraints.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Retention Policy */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Database className="h-5 w-5 text-amber-400" />
            <h2 className="text-base font-bold text-white">Tiered Storage & Retention Rules</h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div>
              <label className="block text-slate-400 mb-1 font-medium">Hot Tier Retention (Hours)</label>
              <input
                type="number"
                value={hotHours}
                onChange={(e) => setHotHours(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
              />
              <p className="text-[10px] text-slate-500 mt-1">Full 10Hz/1Hz raw CAN-FD signals</p>
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-medium">Warm Tier Retention (Days)</label>
              <input
                type="number"
                value={warmDays}
                onChange={(e) => setWarmDays(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
              />
              <p className="text-[10px] text-slate-500 mt-1">1-second downsampled traces</p>
            </div>

            <div>
              <label className="block text-slate-400 mb-1 font-medium">Cold Tier Retention (Weeks)</label>
              <input
                type="number"
                value={coldWeeks}
                onChange={(e) => setColdWeeks(Number(e.target.value))}
                className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
              />
              <p className="text-[10px] text-slate-500 mt-1">1-minute aggregated summary logs</p>
            </div>
          </div>
        </div>

        {/* Local Timezone & Localization */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <Clock className="h-5 w-5 text-blue-400" />
            <h2 className="text-base font-bold text-white">Localization & Relative Time</h2>
          </div>

          <div className="max-w-md text-xs">
            <label className="block text-slate-400 mb-1 font-medium">Vehicle Timezone</label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-white font-mono"
            >
              <option>Asia/Kolkata (IST +5:30)</option>
              <option>UTC (Coordinated Universal Time)</option>
              <option>America/New_York (EST)</option>
              <option>Europe/London (GMT)</option>
            </select>
            <p className="text-[10px] text-slate-500 mt-1">
              Used by Natural Language engine to resolve queries like "yesterday" and "this morning".
            </p>
          </div>
        </div>

        {/* Safety & Isolation Policies (Read-Only) */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4 bg-gradient-to-br from-slate-900 to-emerald-950/20">
          <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
            <ShieldCheck className="h-5 w-5 text-emerald-400" />
            <h2 className="text-base font-bold text-white">Automotive Safety & Privacy Boundaries</h2>
          </div>

          <div className="space-y-3 text-xs text-slate-300">
            <div className="flex items-start gap-2.5">
              <Lock className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
              <div>
                <span className="font-bold text-white block">Strict One-Way Vehicle Ingestion</span>
                VehicleGPT adapters operate strictly in listen-only mode. There is no write path to CAN-FD, SOME/IP, or Vehicle HAL actuators.
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <AlertOctagon className="h-4 w-4 text-amber-400 mt-0.5 shrink-0" />
              <div>
                <span className="font-bold text-white block">Safety Critical Isolation</span>
                The language model and natural-language tools are fully isolated from powertrain, steering, and braking control loops.
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <ShieldCheck className="h-4 w-4 text-emerald-400 mt-0.5 shrink-0" />
              <div>
                <span className="font-bold text-white block">Zero Cloud Telemetry Transmission</span>
                All analytical computations, FTS5 index searches, and SLM inferences are performed 100% on-device. No telemetry is transmitted to third-party clouds.
              </div>
            </div>
          </div>
        </div>

        {/* Save button */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-slate-500 font-mono">
            Vehicle Configuration Profile: ARM64 Constrained Edge
          </span>

          <div className="flex items-center gap-3">
            {saved && (
              <span className="text-xs text-emerald-400 font-medium animate-fade-in">
                Settings saved locally!
              </span>
            )}
            <button
              type="submit"
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all"
            >
              <Save className="h-4 w-4" />
              <span>Save Configuration</span>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};
