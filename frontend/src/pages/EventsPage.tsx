import React, { useState, useEffect } from 'react';
import { 
  AlertTriangle, 
  Search, 
  Filter, 
  ShieldAlert, 
  History, 
  Activity, 
  ExternalLink,
  Flame,
  CheckCircle2
} from 'lucide-react';
import { VehicleEvent, DiagnosticCode } from '../types';
import { api } from '../services/api';
import { PreEventModal } from '../components/PreEventModal';

export const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<VehicleEvent[]>([]);
  const [dtcs, setDtcs] = useState<DiagnosticCode[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [inspectEventId, setInspectEventId] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [evRes, dtcRes] = await Promise.all([
        api.getEvents({
          severity: selectedSeverity !== 'ALL' ? selectedSeverity : undefined,
          search: searchTerm.trim() || undefined,
          limit: 100
        }),
        api.getDiagnostics()
      ]);
      setEvents(evRes.events);
      setDtcs(dtcRes.diagnostic_codes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSeverity]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="space-y-6">
      {/* Pre-Event Forensics Modal */}
      {inspectEventId && (
        <PreEventModal
          eventId={inspectEventId}
          onClose={() => setInspectEventId(null)}
        />
      )}

      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 text-amber-400" />
            Events & Diagnostic Timeline
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Search vehicle events, ADAS disengagements, thermal thresholds, and UDS DTC fault codes.
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearchSubmit} className="flex items-center gap-2">
          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search events (e.g. 'ADAS', 'overheat')..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 w-64"
            />
          </div>
          <button
            type="submit"
            className="px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-medium transition-colors"
          >
            Search
          </button>
        </form>
      </div>

      {/* Severity Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-slate-500 font-medium shrink-0">Severity Filter:</span>
        {['ALL', 'CRITICAL', 'WARNING', 'INFO'].map((sev) => (
          <button
            key={sev}
            onClick={() => setSelectedSeverity(sev)}
            className={`px-3 py-1 rounded-lg font-mono uppercase tracking-wider transition-colors ${
              selectedSeverity === sev
                ? sev === 'CRITICAL' ? 'bg-red-600 text-white font-bold' :
                  sev === 'WARNING' ? 'bg-amber-600 text-white font-bold' :
                  'bg-blue-600 text-white font-bold'
                : 'bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800'
            }`}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Main Grid: Events Timeline & Diagnostic DTCs */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Events Timeline (2 cols) */}
        <div className="lg:col-span-2 space-y-3">
          {loading ? (
            <div className="glass-panel p-12 rounded-2xl flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            </div>
          ) : events.length === 0 ? (
            <div className="glass-panel p-12 rounded-2xl text-center text-slate-400 text-xs">
              No vehicle events matching current filter or search criteria.
            </div>
          ) : (
            events.map((evt) => {
              const isThermalOrOverheat = evt.event_type.includes('OVERHEAT') || evt.event_type.includes('THERMAL') || evt.event_type.includes('DROP');
              return (
                <div
                  key={evt.id}
                  className="glass-panel p-4 rounded-xl border border-slate-800 hover:border-slate-700 transition-all space-y-2 relative"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold text-blue-300">{evt.id}</span>
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-400 bg-slate-900 border border-slate-800">
                        {evt.source}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        evt.severity === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800/50' :
                        evt.severity === 'WARNING' ? 'bg-amber-950 text-amber-400 border border-amber-800/50' :
                        'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}>
                        {evt.severity}
                      </span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-200 font-medium leading-relaxed">
                    {evt.description}
                  </p>

                  <div className="flex flex-wrap items-center justify-between pt-2 border-t border-slate-800/80 text-[11px] text-slate-400">
                    <div className="flex items-center gap-2 font-mono">
                      <span>{evt.timestamp.slice(0, 19).replace('T', ' ')}</span>
                      {evt.trip_id && (
                        <span className="text-slate-500">• Trip: {evt.trip_id}</span>
                      )}
                    </div>

                    {/* Pre-Event Investigation Trigger Button */}
                    {isThermalOrOverheat && (
                      <button
                        onClick={() => setInspectEventId(evt.id)}
                        className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-950/40 hover:bg-amber-900/60 text-amber-400 border border-amber-800/40 text-[11px] font-medium transition-colors"
                      >
                        <Activity className="h-3 w-3" />
                        <span>Investigate T-60s Pre-Event</span>
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Diagnostic Trouble Codes (DTCs) */}
        <div className="space-y-4">
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <span className="text-sm font-bold text-white flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 text-red-400" />
                Active & Logged DTCs
              </span>
              <span className="text-xs font-mono text-slate-400">({dtcs.length})</span>
            </div>

            <div className="space-y-3">
              {dtcs.length === 0 ? (
                <p className="text-xs text-slate-400 py-6 text-center">No diagnostic trouble codes logged.</p>
              ) : (
                dtcs.map((d, i) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-red-400 px-1.5 py-0.5 rounded bg-red-950/80 border border-red-900/60">
                        {d.dtc_code}
                      </span>
                      <span className="text-[10px] font-mono text-slate-400">{d.ecu_name}</span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium">{d.description}</p>
                    <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono pt-1">
                      <span>Status: {d.status}</span>
                      <span>{d.timestamp.slice(0, 19).replace('T', ' ')}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
