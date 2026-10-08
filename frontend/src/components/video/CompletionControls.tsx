import React from 'react';
import { Filter, Eye, Camera, Dot, Sparkles, Sliders } from 'lucide-react';

export type ProvenanceFilter = 'ALL' | 'OBSERVED' | 'INFERRED' | 'GENERATED';

interface CompletionControlsProps {
  provenanceFilter: ProvenanceFilter;
  onSetProvenanceFilter: (filter: ProvenanceFilter) => void;
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
  showCameras,
  onToggleCameras,
  showPointCloud,
  onTogglePointCloud,
  showUnseenVolumes,
  onToggleUnseenVolumes,
}) => {
  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Provenance & Layer Toggles
          </h4>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Honest Reconstruction
        </span>
      </div>

      {/* Provenance Filter Pills */}
      <div className="flex flex-col gap-1.5">
        <span className="text-[11px] font-medium text-slate-400">
          Geometry Provenance Isolation:
        </span>
        <div className="grid grid-cols-4 gap-1.5 p-1 rounded-xl bg-slate-950/80 border border-white/5">
          <button
            onClick={() => onSetProvenanceFilter('ALL')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all ${
              provenanceFilter === 'ALL'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All
          </button>
          <button
            onClick={() => onSetProvenanceFilter('OBSERVED')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all ${
              provenanceFilter === 'OBSERVED'
                ? 'bg-slate-700 text-slate-100 shadow-md'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Observed
          </button>
          <button
            onClick={() => onSetProvenanceFilter('INFERRED')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all ${
              provenanceFilter === 'INFERRED'
                ? 'bg-cyan-600 text-white shadow-md shadow-cyan-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Inferred
          </button>
          <button
            onClick={() => onSetProvenanceFilter('GENERATED')}
            className={`py-1.5 px-2 rounded-lg text-[11px] font-semibold transition-all ${
              provenanceFilter === 'GENERATED'
                ? 'bg-amber-600 text-white shadow-md shadow-amber-600/30'
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Generated
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
