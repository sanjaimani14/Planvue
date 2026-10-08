import React from 'react';
import { UnseenRegionItem, CompletionRegionItem } from '../../types';
import { EyeOff, CheckCircle2, AlertTriangle, ArrowRight, ShieldCheck } from 'lucide-react';

interface UnseenRegionOverlayProps {
  unseenRegions: UnseenRegionItem[];
  completionRegions: CompletionRegionItem[];
  selectedRegionId: string | null;
  onSelectRegion: (id: string | null) => void;
}

export const UnseenRegionOverlay: React.FC<UnseenRegionOverlayProps> = ({
  unseenRegions,
  completionRegions,
  selectedRegionId,
  onSelectRegion,
}) => {
  if (unseenRegions.length === 0) return null;

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <EyeOff className="w-4 h-4 text-rose-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Unseen Regions & Completion ({unseenRegions.length})
          </h4>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Explainable Evidence
        </span>
      </div>

      <div className="flex flex-col gap-2.5 max-h-72 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/10">
        {unseenRegions.map((reg) => {
          const isSelected = selectedRegionId === reg.region_id;
          const matchingComp = completionRegions.find(
            (c) => c.region_id.includes(reg.region_id) || reg.region_id.includes(c.region_id)
          );

          return (
            <div
              key={reg.region_id}
              onClick={() => onSelectRegion(isSelected ? null : reg.region_id)}
              className={`rounded-xl border p-3 cursor-pointer transition-all ${
                isSelected
                  ? 'border-rose-500 bg-rose-500/10 shadow-md shadow-rose-500/10'
                  : 'border-white/10 bg-slate-950/50 hover:border-white/20 hover:bg-white/[0.02]'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-rose-300 font-mono">
                    {reg.region_id}
                  </span>
                  <span className="text-xs text-slate-200 font-medium truncate max-w-[170px]">
                    {reg.label}
                  </span>
                </div>
                {matchingComp && (
                  <span
                    className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${
                      matchingComp.status === 'INFERRED'
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                        : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                    }`}
                  >
                    {matchingComp.status}
                  </span>
                )}
              </div>

              {/* Reason description */}
              <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                {reg.reason}
              </p>

              {/* Completion Action & Evidence */}
              {matchingComp && (
                <div className="mt-2 pt-2 border-t border-white/5 flex flex-col gap-1 text-[11px]">
                  <div className="flex items-center gap-1.5 text-slate-300">
                    <ArrowRight className="w-3 h-3 text-indigo-400" />
                    <span className="font-semibold text-slate-200">
                      {matchingComp.completion_level.replace(/_/g, ' ')}
                    </span>
                    <span className="text-[10px] text-slate-400">({matchingComp.confidence_level} confidence)</span>
                  </div>
                  <p className="text-[10px] text-slate-400 italic">
                    Reason: {matchingComp.reason}
                  </p>
                  {matchingComp.source_frames.length > 0 && (
                    <div className="flex items-center gap-1 mt-0.5 text-[9px] font-mono text-slate-400">
                      <span>Evidence Keyframes:</span>
                      {matchingComp.source_frames.map((fIdx) => (
                        <span key={fIdx} className="px-1 py-0.5 rounded bg-slate-800 text-slate-300">
                          KF{fIdx + 1}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
