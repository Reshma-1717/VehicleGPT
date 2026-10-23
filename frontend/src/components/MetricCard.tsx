import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  icon: LucideIcon;
  subtext?: string;
  accentColor?: 'blue' | 'emerald' | 'amber' | 'red' | 'indigo';
  alert?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  unit,
  icon: Icon,
  subtext,
  accentColor = 'blue',
  alert = false
}) => {
  const colorMap = {
    blue: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
    emerald: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    amber: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
    red: 'text-red-400 bg-red-500/10 border-red-500/20',
    indigo: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
  };

  return (
    <div className={`glass-panel p-4 rounded-xl relative overflow-hidden transition-all duration-200 hover:border-slate-700 ${
      alert ? 'border-red-500/50 glow-red' : ''
    }`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 tracking-wider uppercase">{title}</span>
        <div className={`p-2 rounded-lg border ${colorMap[accentColor]}`}>
          <Icon className="h-4 w-4" />
        </div>
      </div>
      
      <div className="mt-3 flex items-baseline gap-1.5">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">{value}</span>
        {unit && <span className="text-xs font-medium text-slate-400">{unit}</span>}
      </div>

      {subtext && (
        <p className="mt-1 text-xs text-slate-400 font-sans flex items-center gap-1">
          {subtext}
        </p>
      )}
    </div>
  );
};
