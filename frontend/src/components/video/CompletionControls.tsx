import React from 'react';
import { Sliders, Camera, Dot, Sparkles, SplitSquareVertical, ToggleLeft, ToggleRight, ShieldCheck } from 'lucide-react';

export type ProvenanceFilter = 'ALL' | 'OBSERVED' | 'INFERRED' | 'GENERATED' | 'CORRECTED';
export type ComparisonViewMode = 'AFTER_COMPLETION' | 'BEFORE_COMPLETION' | 'SPLIT_VIEW';

interface CompletionControlsProps {
  provenanceFilter: ProvenanceFilter;
  onSetProvenanceFilter: (filter: ProvenanceFilter) => void;
  comparisonMode: ComparisonViewMode;
  onSetComparisonMode: (mode: ComparisonViewMode) => void;
  showCameras: boolean;
  onToggleCameras: () => void;
  showPointCloud: boolean;
  onTogglePointCloud: () => void;
  showUnseenVolumes: boolean;
  onToggleUnseenVolumes: () => void;
}

export const CompletionControls: React.FC<CompletionControlsProps> = ({
  provenanceFilter,
  onSetProvenanceFilter,
  comparisonMode,
  onSetComparisonMode,
  showCameras,
  onToggleCameras,
  showPointCloud,
  onTogglePointCloud,
  showUnseenVolumes,
  onToggleUnseenVolumes,
}) => {
  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-3.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Provenance & Comparison
          </h4>
        </div>
        <div className="flex items-center gap-1 text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
          <ShieldCheck className="w-3 h-3" />
          <span>Non-Hallucinatory</span>
        </div>
      </div>

      {/* Before / After / Split View Selector */}
      <div className="flex flex-col gap-1.5">
        <span className="text-[11px] font-semibold text-slate-300">
          Inspection Mode (Before / After Comparison):
        </span>
        <div className="grid grid-cols-3 gap-1.5 p-1 rounded-xl bg-slate-950/80 border border-white/5">
          <button
            onClick={() => onSetComparisonMode('BEFORE_COMPLETION')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all flex items-center justify-center gap-1 ${
              comparisonMode === 'BEFORE_COMPLETION'
                ? 'bg-slate-700 text-white shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ToggleLeft className="w-3.5 h-3.5" />
            <span>Observed Only</span>
          </button>
          <button
            onClick={() => onSetComparisonMode('AFTER_COMPLETION')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all flex items-center justify-center gap-1 ${
              comparisonMode === 'AFTER_COMPLETION'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <ToggleRight className="w-3.5 h-3.5" />
            <span>Completed</span>
          </button>
          <button
            onClick={() => onSetComparisonMode('SPLIT_VIEW')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all flex items-center justify-center gap-1 ${
              comparisonMode === 'SPLIT_VIEW'
                ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            <SplitSquareVertical className="w-3.5 h-3.5" />
            <span>Split View</span>
          </button>
        </div>
      </div>

      {/* Provenance Filter Pills */}
      <div className="flex flex-col gap-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-medium text-slate-400">
            Geometry Provenance Isolation:
          </span>
          <span className="text-[10px] text-slate-400 font-mono">
            {provenanceFilter}
          </span>
        </div>
        <div className="grid grid-cols-5 gap-1 p-1 rounded-xl bg-slate-950/80 border border-white/5">
          <button
            onClick={() => onSetProvenanceFilter('ALL')}
            className={`py-1.5 px-1.5 rounded-lg text-[10px] font-semibold transition-all text-center ${
              provenanceFilter === 'ALL'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All
          </button>
          <button
            onClick={() => onSetProvenanceFilter('OBSERVED')}
            className={`py-1.5 px-1.5 rounded-lg text-[10px] font-semibold transition-all text-center ${
              provenanceFilter === 'OBSERVED'
                ? 'bg-slate-700 text-slate-100 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Observed
          </button>
          <button
            onClick={() => onSetProvenanceFilter('INFERRED')}
            className={`py-1.5 px-1.5 rounded-lg text-[10px] font-semibold transition-all text-center ${
              provenanceFilter === 'INFERRED'
                ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Inferred
          </button>
          <button
            onClick={() => onSetProvenanceFilter('GENERATED')}
            className={`py-1.5 px-1.5 rounded-lg text-[10px] font-semibold transition-all text-center ${
              provenanceFilter === 'GENERATED'
                ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Generated
          </button>
          <button
            onClick={() => onSetProvenanceFilter('CORRECTED')}
            className={`py-1.5 px-1.5 rounded-lg text-[10px] font-semibold transition-all text-center ${
              provenanceFilter === 'CORRECTED'
                ? 'bg-purple-600 text-white shadow-md shadow-purple-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Corrected
          </button>
        </div>
      </div>

      {/* View Layer Checkboxes */}
      <div className="grid grid-cols-3 gap-2 pt-2 border-t border-white/5 text-xs">
        <button
          onClick={onToggleCameras}
          className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-xl border transition-all ${
            showCameras
              ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40'
              : 'bg-slate-950/40 text-slate-400 border-white/5 hover:text-slate-200'
          }`}
        >
          <Camera className="w-3.5 h-3.5" />
          <span>Cameras</span>
        </button>

        <button
          onClick={onTogglePointCloud}
          className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-xl border transition-all ${
            showPointCloud
              ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
              : 'bg-slate-950/40 text-slate-400 border-white/5 hover:text-slate-200'
          }`}
        >
          <Dot className="w-4 h-4" />
          <span>Point Cloud</span>
        </button>

        <button
          onClick={onToggleUnseenVolumes}
          className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-xl border transition-all ${
            showUnseenVolumes
              ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
              : 'bg-slate-950/40 text-slate-400 border-white/5 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Unseen</span>
        </button>
      </div>
    </div>
  );
};
