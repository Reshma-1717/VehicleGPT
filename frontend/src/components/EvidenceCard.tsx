import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Database, Clock, Tag, Cpu } from 'lucide-react';
import { ChatEvidence } from '../types';

interface EvidenceCardProps {
  evidence: ChatEvidence;
  source: string;
  latencyMs: number;
  confidence: number;
  modelName?: string;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({
  evidence,
  source,
  latencyMs,
  confidence,
  modelName
}) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-3 rounded-lg border border-slate-800 bg-slate-900/60 overflow-hidden text-xs">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full px-3 py-2 flex items-center justify-between text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Database className="h-3.5 w-3.5 text-blue-400" />
          <span className="font-semibold text-slate-300">Ground-Truth Verification & Evidence</span>
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-blue-950 text-blue-400 border border-blue-800/40 font-mono">
            {source === 'local_slm' ? 'Local SLM' : 'Analytical Engine'}
          </span>
          <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800/40 font-mono">
            {latencyMs} ms
          </span>
        </div>
        {expanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
      </button>

      {expanded && (
        <div className="p-3 border-t border-slate-800/80 bg-slate-950/40 space-y-2.5">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Time Range</span>
              <span className="font-mono text-slate-200">{evidence.time_range}</span>
            </div>
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Telemetry Points</span>
              <span className="font-mono text-slate-200">{evidence.data_points_examined.toLocaleString()}</span>
            </div>
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Confidence</span>
              <span className="font-mono text-emerald-400">{(confidence * 100).toFixed(0)}%</span>
            </div>
            <div className="bg-slate-900/80 p-2 rounded border border-slate-800">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block">Model Profile</span>
              <span className="font-mono text-blue-300 truncate block">{modelName || 'Deterministic Engine'}</span>
            </div>
          </div>

          {evidence.event_ids && evidence.event_ids.length > 0 && (
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Referenced Events</span>
              <div className="flex flex-wrap gap-1">
                {evidence.event_ids.map((id) => (
                  <span key={id} className="px-1.5 py-0.5 rounded bg-slate-800 text-amber-300 font-mono text-[11px] border border-slate-700">
                    {id}
                  </span>
                ))}
              </div>
            </div>
          )}

          {evidence.dtc_codes && evidence.dtc_codes.length > 0 && (
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Active Diagnostic Codes</span>
              <div className="flex flex-wrap gap-1">
                {evidence.dtc_codes.map((code) => (
                  <span key={code} className="px-1.5 py-0.5 rounded bg-red-950/60 text-red-300 font-mono text-[11px] border border-red-800/50">
                    {code}
                  </span>
                ))}
              </div>
            </div>
          )}

          {evidence.metrics && Object.keys(evidence.metrics).length > 0 && (
            <div>
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block mb-1">Calculated Numerical Proof</span>
              <div className="bg-slate-900/90 rounded p-2 border border-slate-800 font-mono text-[11px] text-slate-300">
                <pre className="overflow-x-auto whitespace-pre-wrap">
                  {JSON.stringify(evidence.metrics, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
