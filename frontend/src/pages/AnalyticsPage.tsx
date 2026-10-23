import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  TrendingDown, 
  Zap, 
  Flame, 
  Car, 
  Download, 
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  Compass
} from 'lucide-react';
import { api } from '../services/api';

export const AnalyticsPage: React.FC = () => {
  const [rangeData, setRangeData] = useState<any>(null);
  const [efficiencyData, setEfficiencyData] = useState<any>(null);
  const [batteryData, setBatteryData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      setLoading(true);
      try {
        const [r, eff, batt] = await Promise.all([
          api.getRangeAnalytics(14),
          api.getEfficiencyAnalytics(),
          api.getBatteryAnalytics(7)
        ]);
        setRangeData(r);
        setEfficiencyData(eff);
        setBatteryData(batt);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  const handleExportCSV = async () => {
    try {
      const tripsRes = await api.getTrips(undefined, 100);
      const headers = ['Trip ID', 'Start Time', 'Trip Type', 'Distance (km)', 'Avg Speed (km/h)', 'Avg Consumption (kWh/100km)', 'Ambient Temp (°C)'];
      const rows = tripsRes.trips.map(t => [
        t.id,
        t.start_time,
        t.trip_type,
        t.distance_km,
        t.avg_speed_kmh,
        t.avg_consumption,
        t.ambient_temp_c
      ]);

      const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
      const encodedUri = encodeURI(csvContent);
      const link = document.createElement('a');
      link.setAttribute('href', encodedUri);
      link.setAttribute('download', `VehicleGPT_Trips_Export_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      alert('Failed to generate CSV export');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500" />
      </div>
    );
  }

  const largestDrop = efficiencyData?.largest_drop;
  const cityHwy = efficiencyData?.city_highway_comparison;

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-blue-400" />
            Deterministic Vehicle Analytics
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Grounded mathematical evaluations computed directly from local on-device records.
          </p>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 text-xs font-medium transition-colors"
        >
          <Download className="h-4 w-4 text-blue-400" />
          <span>Export Analytics CSV</span>
        </button>
      </div>

      {/* 1. Range Degradation & Factor Attribution */}
      {rangeData && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
            <div>
              <div className="flex items-center gap-2">
                <Compass className="h-5 w-5 text-indigo-400" />
                <h2 className="text-base font-bold text-white">Driving Range Degradation & Factor Attribution</h2>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Comparing current 14 days ({rangeData.current_period}) vs prior baseline ({rangeData.baseline_period})
              </p>
            </div>

            <div className="flex items-center gap-3 font-mono">
              <div className="text-right">
                <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Observed Range Drop</span>
                <span className="text-lg font-bold text-red-400">
                  {rangeData.range_delta_km} km ({rangeData.range_drop_percent}%)
                </span>
              </div>
            </div>
          </div>

          {/* Metric Comparison Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Baseline Range</span>
              <span className="text-base font-bold font-mono text-emerald-400">{rangeData.baseline_avg_range_km} km</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Current Range</span>
              <span className="text-base font-bold font-mono text-red-400">{rangeData.current_avg_range_km} km</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Analyzed Trips</span>
              <span className="text-base font-bold font-mono text-slate-200">{rangeData.trip_count_analyzed}</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Telemetry Points</span>
              <span className="text-base font-bold font-mono text-blue-400">{rangeData.data_points.toLocaleString()}</span>
            </div>
          </div>

          {/* Factor Attribution Cards */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3">
              Identified Root Physical Factors
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {rangeData.factors.map((f: any, i: number) => (
                <div key={i} className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-200">{f.factor}</span>
                    <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-blue-950 text-blue-300 border border-blue-800/40">
                      {f.impact_percentage}%
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{f.description}</p>
                  <p className="text-[10px] text-slate-500 font-mono pt-1 border-t border-slate-800/60">
                    Evidence: {f.evidence}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 2. City vs. Highway & Efficiency Change Point */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* City vs Highway Card */}
        {cityHwy && (
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-emerald-400" />
                <h2 className="text-base font-bold text-white">City vs. Highway Efficiency</h2>
              </div>
              <span className="text-xs font-mono text-slate-400">Past 30 Days</span>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <span className="text-xs font-bold text-slate-300 block">City Commute</span>
                <span className="text-xl font-bold font-mono text-emerald-400">
                  {cityHwy.city_avg_consumption_kwh_100km} <span className="text-xs font-normal">kWh/100km</span>
                </span>
                <p className="text-[11px] text-slate-400">
                  Avg Speed: {cityHwy.city_avg_speed_kmh} km/h • {cityHwy.city_trip_count} trips
                </p>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1">
                <span className="text-xs font-bold text-slate-300 block">Highway Driving</span>
                <span className="text-xl font-bold font-mono text-amber-400">
                  {cityHwy.highway_avg_consumption_kwh_100km} <span className="text-xs font-normal">kWh/100km</span>
                </span>
                <p className="text-[11px] text-slate-400">
                  Avg Speed: {cityHwy.highway_avg_speed_kmh} km/h • {cityHwy.highway_trip_count} trips
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/40 p-3 rounded-xl border border-slate-800">
              {cityHwy.explanation}
            </p>
          </div>
        )}

        {/* Largest Efficiency Drop Card */}
        {largestDrop && (
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <TrendingDown className="h-5 w-5 text-red-400" />
                <h2 className="text-base font-bold text-white">Largest Efficiency Drop Change-Point</h2>
              </div>
              <span className="font-mono text-xs text-red-400 bg-red-950/60 px-2 py-0.5 rounded border border-red-800/40">
                +{largestDrop.drop_magnitude} kWh/100km Spike
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Trip Identifier</span>
                <span className="font-mono text-blue-300 font-bold">{largestDrop.trip_id}</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Timestamp</span>
                <span className="font-mono text-slate-200">{largestDrop.timestamp.slice(0, 19).replace('T', ' ')}</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Baseline Efficiency</span>
                <span className="font-mono text-slate-200">{largestDrop.previous_efficiency} kWh/100km</span>
              </div>
              <div className="flex items-center justify-between py-1.5 border-b border-slate-800">
                <span className="text-slate-400">Spike Consumption</span>
                <span className="font-mono text-red-400 font-bold">{largestDrop.dropped_efficiency} kWh/100km</span>
              </div>
            </div>

            <div>
              <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-1">
                Root Cause Attribution
              </span>
              <ul className="text-xs text-slate-300 space-y-1">
                {largestDrop.possible_causes.map((c: string, i: number) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-red-400">•</span>
                    <span>{c}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* 3. Battery Temperature & Thermal Stress */}
      {batteryData && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <div className="flex items-center gap-2">
              <Flame className="h-5 w-5 text-amber-400" />
              <h2 className="text-base font-bold text-white">Battery Thermal Stress & Temperature Trends</h2>
            </div>
            <span className={`px-2 py-0.5 rounded text-xs font-mono font-bold ${
              batteryData.thermal_stress_level === 'CRITICAL' ? 'bg-red-950 text-red-400 border border-red-800/50' :
              'bg-emerald-950 text-emerald-400 border border-emerald-800/50'
            }`}>
              Stress Index: {batteryData.thermal_stress_level}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Average Temp</span>
              <span className="text-base font-bold font-mono text-slate-200">{batteryData.avg_temp_c}°C</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Max Observed Temp</span>
              <span className="text-base font-bold font-mono text-red-400">{batteryData.max_temp_c}°C</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Min Temp</span>
              <span className="text-base font-bold font-mono text-blue-400">{batteryData.min_temp_c}°C</span>
            </div>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Overheat Events</span>
              <span className="text-base font-bold font-mono text-amber-400">{batteryData.overheat_events_count}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
