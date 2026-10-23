import React, { useState, useEffect, useMemo } from 'react';
import { 
  Activity, 
  Search, 
  Filter, 
  Calendar, 
  Download, 
  RefreshCw,
  Table,
  LineChart as ChartIcon
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { TelemetryRecord } from '../types';
import { api } from '../services/api';

export const TelemetryPage: React.FC = () => {
  const [records, setRecords] = useState<TelemetryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRange, setSelectedRange] = useState<'all' | '14d' | '7d' | '24h'>('7d');
  const [activeSignals, setActiveSignals] = useState({
    speed: true,
    temp: true,
    soc: false,
    consumption: true
  });
  const [searchTable, setSearchTable] = useState('');
  const [page, setPage] = useState(0);
  const rowsPerPage = 15;

  const loadTelemetry = async () => {
    setLoading(true);
    try {
      const res = await api.getTelemetry({ limit: 1000 });
      setRecords(res.records);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
  }, []);

  // Filter records by time range
  const filteredRecords = useMemo(() => {
    if (selectedRange === 'all') return records;
    const now = new Date();
    const cutoff = new Date();
    if (selectedRange === '24h') cutoff.setHours(now.getHours() - 24);
    if (selectedRange === '7d') cutoff.setDate(now.getDate() - 7);
    if (selectedRange === '14d') cutoff.setDate(now.getDate() - 14);

    return records.filter((r) => new Date(r.timestamp) >= cutoff);
  }, [records, selectedRange]);

  // Aggregate for Recharts
  const chartData = useMemo(() => {
    const grouped: { [timeKey: string]: any } = {};

    filteredRecords.forEach((r) => {
      // Aggregate into 5-minute buckets for smooth visualization
      const ts = new Date(r.timestamp);
      const key = `${ts.getMonth() + 1}/${ts.getDate()} ${ts.getHours().toString().padStart(2, '0')}:${(Math.floor(ts.getMinutes() / 15) * 15).toString().padStart(2, '0')}`;
      
      if (!grouped[key]) {
        grouped[key] = { time: key };
      }

      if (r.signal_name === 'vehicle_speed_kmh') grouped[key].speed = r.value;
      if (r.signal_name === 'battery_pack_temp_c') grouped[key].temp = r.value;
      if (r.signal_name === 'battery_soc_percent') grouped[key].soc = r.value;
      if (r.signal_name === 'energy_consumption_kwh_100km') grouped[key].consumption = r.value;
    });

    return Object.values(grouped);
  }, [filteredRecords]);

  // Table filtering & pagination
  const searchedTableRecords = useMemo(() => {
    return filteredRecords.filter((r) => 
      r.signal_name.toLowerCase().includes(searchTable.toLowerCase()) ||
      r.protocol.toLowerCase().includes(searchTable.toLowerCase()) ||
      r.quality.toLowerCase().includes(searchTable.toLowerCase())
    );
  }, [filteredRecords, searchTable]);

  const pagedRecords = useMemo(() => {
    const start = page * rowsPerPage;
    return searchedTableRecords.slice(start, start + rowsPerPage);
  }, [searchedTableRecords, page]);

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <Activity className="h-6 w-6 text-blue-400" />
            Telemetry Explorer
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Explore time-series sensor traces, battery metrics, and normalized CAN-FD signals.
          </p>
        </div>

        {/* Range selectors & Refresh */}
        <div className="flex items-center gap-2">
          <div className="bg-slate-900 rounded-lg p-1 border border-slate-800 flex items-center gap-1 text-xs font-medium">
            {(['24h', '7d', '14d', 'all'] as const).map((r) => (
              <button
                key={r}
                onClick={() => setSelectedRange(r)}
                className={`px-2.5 py-1 rounded transition-colors ${
                  selectedRange === r ? 'bg-blue-600 text-white font-semibold' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                {r === '24h' ? '24 Hours' : r === '7d' ? '7 Days' : r === '14d' ? '14 Days' : 'Full History'}
              </button>
            ))}
          </div>

          <button
            onClick={loadTelemetry}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
            title="Refresh Telemetry"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Interactive Time-Series Chart */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
          <span className="text-sm font-bold text-white flex items-center gap-2">
            <ChartIcon className="h-4 w-4 text-blue-400" />
            Time-Series Signal Visualization
          </span>

          {/* Signal toggles */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={activeSignals.speed}
                onChange={(e) => setActiveSignals({ ...activeSignals, speed: e.target.checked })}
                className="rounded border-slate-700 text-blue-600 focus:ring-0"
              />
              <span className="text-blue-400 font-mono">Speed (km/h)</span>
            </label>

            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={activeSignals.temp}
                onChange={(e) => setActiveSignals({ ...activeSignals, temp: e.target.checked })}
                className="rounded border-slate-700 text-red-600 focus:ring-0"
              />
              <span className="text-red-400 font-mono">Battery Temp (°C)</span>
            </label>

            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={activeSignals.soc}
                onChange={(e) => setActiveSignals({ ...activeSignals, soc: e.target.checked })}
                className="rounded border-slate-700 text-emerald-600 focus:ring-0"
              />
              <span className="text-emerald-400 font-mono">SOC (%)</span>
            </label>

            <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input
                type="checkbox"
                checked={activeSignals.consumption}
                onChange={(e) => setActiveSignals({ ...activeSignals, consumption: e.target.checked })}
                className="rounded border-slate-700 text-amber-600 focus:ring-0"
              />
              <span className="text-amber-400 font-mono">Consumption (kWh/100km)</span>
            </label>
          </div>
        </div>

        {/* Chart Canvas */}
        <div className="mt-4 h-72 w-full">
          {loading ? (
            <div className="h-full flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
            </div>
          ) : chartData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-400 text-xs">
              No telemetry records found for the selected timeframe.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="time" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                {activeSignals.speed && (
                  <Line type="monotone" dataKey="speed" name="Speed (km/h)" stroke="#3b82f6" strokeWidth={1.5} dot={false} />
                )}
                {activeSignals.temp && (
                  <Line type="monotone" dataKey="temp" name="Battery Temp (°C)" stroke="#ef4444" strokeWidth={1.5} dot={false} />
                )}
                {activeSignals.soc && (
                  <Line type="monotone" dataKey="soc" name="SOC (%))" stroke="#10b981" strokeWidth={1.5} dot={false} />
                )}
                {activeSignals.consumption && (
                  <Line type="monotone" dataKey="consumption" name="Consumption (kWh/100km)" stroke="#f59e0b" strokeWidth={1.5} dot={false} />
                )}
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Raw Telemetry Records Table */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Table className="h-4 w-4 text-blue-400" />
            <span className="text-sm font-bold text-white">Stored Telemetry Records</span>
            <span className="text-xs text-slate-400 font-mono">({searchedTableRecords.length} records)</span>
          </div>

          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search signal or protocol..."
              value={searchTable}
              onChange={(e) => {
                setSearchTable(e.target.value);
                setPage(0);
              }}
              className="bg-slate-900 border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500 w-64"
            />
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-800">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-mono text-[10px] border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Signal Name</th>
                <th className="py-2.5 px-3">Value</th>
                <th className="py-2.5 px-3">Unit</th>
                <th className="py-2.5 px-3">Protocol</th>
                <th className="py-2.5 px-3">Tier</th>
                <th className="py-2.5 px-3">Quality</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {pagedRecords.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-6 text-center text-slate-500">
                    No matching telemetry records found.
                  </td>
                </tr>
              ) : (
                pagedRecords.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-2 px-3 text-slate-400">{r.timestamp.slice(0, 19).replace('T', ' ')}</td>
                    <td className="py-2 px-3 font-semibold text-blue-300">{r.signal_name}</td>
                    <td className="py-2 px-3 font-bold text-white">{r.value}</td>
                    <td className="py-2 px-3 text-slate-400">{r.unit}</td>
                    <td className="py-2 px-3 text-slate-400">{r.protocol}</td>
                    <td className="py-2 px-3">
                      <span className={`px-1.5 py-0.2 rounded text-[10px] ${
                        r.tier === 'hot' ? 'bg-red-950 text-red-300 border border-red-900' :
                        r.tier === 'warm' ? 'bg-amber-950 text-amber-300 border border-amber-900' :
                        'bg-blue-950 text-blue-300 border border-blue-900'
                      }`}>
                        {r.tier}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-emerald-400">{r.quality}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination controls */}
        <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
          <span>Page {page + 1} of {Math.max(1, Math.ceil(searchedTableRecords.length / rowsPerPage))}</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(Math.max(0, page - 1))}
              disabled={page === 0}
              className="px-3 py-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 border border-slate-800"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(page + 1)}
              disabled={(page + 1) * rowsPerPage >= searchedTableRecords.length}
              className="px-3 py-1 rounded bg-slate-900 hover:bg-slate-800 disabled:opacity-40 border border-slate-800"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
