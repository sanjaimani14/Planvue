import React from 'react';
import { Eye, ShieldCheck, Sparkles, AlertCircle } from 'lucide-react';

export type ConfidenceFilterType = 'ALL' | 'OBSERVED' | 'INFERRED' | 'CORRECTED';

interface ConfidenceOverlayProps {
  filter: ConfidenceFilterType;
  onChangeFilter: (f: ConfidenceFilterType) => void;
  stats?: {
    observedCount: number;
    inferredCount: number;
    correctedCount: number;
    meanConfidence?: number;
  };
}

export const ConfidenceOverlay: React.FC<ConfidenceOverlayProps> = ({
  filter,
  onChangeFilter,
  stats,
}) => {
  return (
    <div className="bg-slate-900/90 backdrop-blur-md border border-slate-800 p-2.5 rounded-xl shadow-2xl flex flex-col gap-2">
      <div className="flex items-center justify-between gap-3 text-xs font-semibold text-slate-300">
        <span className="flex items-center gap-1.5 text-cyan-400">
          <Eye className="w-3.5 h-3.5" />
          CONFIDENCE VISUALIZATION
        </span>
        {stats?.meanConfidence !== undefined && (
          <span className="text-[10px] text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full font-mono">
            Avg: {(stats.meanConfidence * 100).toFixed(0)}%
          </span>
        )}
      </div>

      {/* Filter Category Buttons */}
      <div className="grid grid-cols-4 gap-1.5 text-[11px] font-medium">
        <button
          onClick={() => onChangeFilter('ALL')}
          className={`px-2.5 py-1 rounded-lg transition-all flex items-center justify-center gap-1 border ${
            filter === 'ALL'
              ? 'bg-slate-700 text-white border-slate-500 shadow-sm'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
        >
          <span>ALL</span>
        </button>

        <button
          onClick={() => onChangeFilter('OBSERVED')}
          className={`px-2 py-1 rounded-lg transition-all flex items-center justify-center gap-1 border ${
            filter === 'OBSERVED'
              ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/60 shadow-sm'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-emerald-400 hover:bg-slate-800'
          }`}
          title="Directly detected from input blueprint"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>OBSERVED</span>
          {stats && <span className="text-[9px] opacity-70">({stats.observedCount})</span>}
        </button>

        <button
          onClick={() => onChangeFilter('INFERRED')}
          className={`px-2 py-1 rounded-lg transition-all flex items-center justify-center gap-1 border ${
            filter === 'INFERRED'
              ? 'bg-purple-950/80 text-purple-300 border-purple-500/60 shadow-sm'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-purple-400 hover:bg-slate-800'
          }`}
          title="Derived from geometric enclosure or constraints"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-purple-400"></span>
          <span>INFERRED</span>
          {stats && <span className="text-[9px] opacity-70">({stats.inferredCount})</span>}
        </button>

        <button
          onClick={() => onChangeFilter('CORRECTED')}
          className={`px-2 py-1 rounded-lg transition-all flex items-center justify-center gap-1 border ${
            filter === 'CORRECTED'
              ? 'bg-amber-950/80 text-amber-300 border-amber-500/60 shadow-sm'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-amber-400 hover:bg-slate-800'
          }`}
          title="Refined/snapped by validation constraints engine"
        >
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          <span>CORRECTED</span>
          {stats && <span className="text-[9px] opacity-70">({stats.correctedCount})</span>}
        </button>
      </div>
    </div>
  );
};
