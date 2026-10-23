import React, { useEffect, useState } from 'react';
import { 
  Gauge, 
  BatteryCharging, 
  Flame, 
  MapPin, 
  Zap, 
  Compass, 
  AlertOctagon, 
  CheckCircle2, 
  Clock, 
  ChevronRight,
  TrendingUp,
  ShieldAlert
} from 'lucide-react';
import { MetricCard } from '../components/MetricCard';
import { TelemetryOverview, VehicleEvent, DiagnosticCode } from '../types';
import { api } from '../services/api';

interface OverviewPageProps {
  onNavigateToAssistant: (initialQuery?: string) => void;
  onNavigateToEvents: () => void;
}

export const OverviewPage: React.FC<OverviewPageProps> = ({
  onNavigateToAssistant,
  onNavigateToEvents
}) => {
  const [overview, setOverview] = useState<TelemetryOverview | null>(null);
  const [recentEvents, setRecentEvents] = useState<VehicleEvent[]>([]);
  const [recentDtcs, setRecentDtcs] = useState<DiagnosticCode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [ov, evRes, dtcRes] = await Promise.all([
          api.getOverview(),
          api.getEvents({ limit: 4 }),
          api.getDiagnostics()
        ]);
        setOverview(ov);
        setRecentEvents(evRes.events);
        setRecentDtcs(dtcRes.diagnostic_codes.slice(0, 3));
      } catch (err) {
        console.error('Failed to load overview data', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 4000); // 4s periodic update
    return () => clearInterval(interval);
  }, []);

  if (loading && !overview) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
      </div>
    );
  }

  const isBatteryHot = (overview?.battery_temp_c || 0) > 45.0;

  return (
    <div className="space-y-6">
      {/* Top Hero Banner */}
      <div className="glass-panel p-6 rounded-2xl relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900/90 to-blue-950/40 border border-slate-800">
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase bg-emerald-950 text-emerald-400 border border-emerald-800/40">
                Vehicle Online
              </span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono text-slate-400 bg-slate-800 border border-slate-700">
                Powertrain: Dual-Motor AWD
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mt-1.5">
              TATA Harrier.ev Concept AWD
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              On-board edge intelligence active. Monitoring 32 vehicle ECUs and continuous CAN-FD telemetry.
            </p>
          </div>

          <button
            onClick={() => onNavigateToAssistant()}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium text-sm transition-all shadow-lg shadow-blue-600/25 hover:shadow-blue-500/35"
          >
            <span>Ask VehicleGPT</span>
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Main Metric Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Vehicle Speed"
          value={overview?.speed_kmh?.toFixed(0) || '0'}
          unit="km/h"
          icon={Gauge}
          subtext={`Status: ${overview?.status || 'PARKED'}`}
          accentColor="blue"
        />

        <MetricCard
          title="Battery State of Charge"
          value={overview?.soc_percent?.toFixed(1) || '0'}
          unit="%"
          icon={BatteryCharging}
          subtext="Usable Capacity: 80 kWh"
          accentColor="emerald"
        />

        <MetricCard
          title="Driving Range Estimate"
          value={overview?.range_km?.toFixed(0) || '0'}
          unit="km"
          icon={Compass}
          subtext="Dynamic terrain forecast"
          accentColor="indigo"
        />

        <MetricCard
          title="Battery Pack Temperature"
          value={overview?.battery_temp_c?.toFixed(1) || '0'}
          unit="°C"
          icon={Flame}
          subtext={isBatteryHot ? 'High Thermal Stress Alert' : 'Nominal Thermal Band'}
          accentColor={isBatteryHot ? 'red' : 'amber'}
          alert={isBatteryHot}
        />
      </div>

      {/* Secondary Gauges & Energy Efficiency */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          title="Energy Consumption"
          value={overview?.energy_consumption_kwh_100km?.toFixed(1) || '16.4'}
          unit="kWh/100km"
          icon={Zap}
          subtext="Rolling 100km trip average"
          accentColor="emerald"
        />
        <MetricCard
          title="Ambient Temperature"
          value={overview?.ambient_temp_c?.toFixed(1) || '24.0'}
          unit="°C"
          icon={TrendingUp}
          subtext={`Cabin target: ${overview?.cabin_temp_c || 22}°C`}
          accentColor="blue"
        />
        <MetricCard
          title="Average Tire Pressure"
          value={overview?.tire_pressure_front_left_bar?.toFixed(2) || '2.20'}
          unit="bar"
          icon={AlertOctagon}
          subtext="TPMS Placed Placard: 2.4 bar"
          accentColor="amber"
        />
      </div>

      {/* Bottom Section: Recent Events & Active Fault Codes */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Events Card */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 text-amber-400" />
              <h2 className="text-base font-bold text-white">Recent Vehicle Events</h2>
            </div>
            <button
              onClick={onNavigateToEvents}
              className="text-xs text-blue-400 hover:text-blue-300 font-medium"
            >
              View All Events →
            </button>
          </div>

          <div className="mt-4 space-y-3">
            {recentEvents.length === 0 ? (
              <p className="text-xs text-slate-400 py-4 text-center">No recent vehicle events logged.</p>
            ) : (
              recentEvents.map((evt) => (
                <div
                  key={evt.id}
                  className="p-3 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-semibold text-slate-300">{evt.id}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      evt.severity === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800/40' :
                      evt.severity === 'WARNING' ? 'bg-amber-950 text-amber-400 border border-amber-800/40' :
                      'bg-slate-800 text-slate-300'
                    }`}>
                      {evt.severity}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 mt-1 line-clamp-2">{evt.description}</p>
                  <div className="mt-2 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="font-mono">{evt.source}</span>
                    <span>{evt.timestamp.slice(0, 19).replace('T', ' ')}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Diagnostic Codes & Ask Chips */}
        <div className="space-y-6">
          {/* Active DTCs */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <AlertOctagon className="h-4 w-4 text-red-400" />
                <h2 className="text-base font-bold text-white">Diagnostic Trouble Codes (DTC)</h2>
              </div>
              <span className="text-xs font-mono text-slate-400">UDS ISO 14229</span>
            </div>

            <div className="mt-4 space-y-2.5">
              {recentDtcs.length === 0 ? (
                <p className="text-xs text-slate-400 py-4 text-center">All ECUs reporting clean diagnostic state (0 DTCs).</p>
              ) : (
                recentDtcs.map((dtc, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-red-950/20 border border-red-900/30 flex items-start gap-3">
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-red-950 text-red-300 border border-red-800/50 mt-0.5">
                      {dtc.dtc_code}
                    </span>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-slate-200 font-medium truncate">{dtc.description}</p>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">ECU: {dtc.ecu_name} • Status: {dtc.status}</p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Quick AI Questions Card */}
          <div className="glass-panel p-5 rounded-2xl border border-slate-800 bg-gradient-to-br from-slate-900/90 to-blue-950/20">
            <h2 className="text-sm font-bold text-white tracking-tight mb-2">Explore with Natural Language</h2>
            <p className="text-xs text-slate-400 mb-3">Ask questions derived directly from local database records:</p>
            <div className="flex flex-wrap gap-2">
              {[
                "Why has my driving range reduced over the last two weeks?",
                "When did fuel efficiency show the largest drop?",
                "Show all ADAS disengagement events from yesterday.",
                "What happened before the battery overheating warning?",
                "Compare energy consumption between city and highway driving."
              ].map((q, i) => (
                <button
                  key={i}
                  onClick={() => onNavigateToAssistant(q)}
                  className="text-left text-xs px-3 py-1.5 rounded-lg bg-slate-800/80 hover:bg-blue-600/20 hover:text-blue-300 text-slate-300 border border-slate-700/80 transition-colors"
                >
                  "{q}"
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
