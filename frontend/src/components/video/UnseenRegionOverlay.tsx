import React from 'react';
import { UnseenRegionItem, CompletionRegionItem } from '../../types';
import { EyeOff, ArrowRight, Info, CheckCircle2, AlertCircle } from 'lucide-react';

interface UnseenRegionOverlayProps {
  unseenRegions: UnseenRegionItem[];
  completionRegions: CompletionRegionItem[];
  selectedRegionId: string | null;
  onSelectRegion: (id: string | null) => void;
  onInspectRegion?: (region: UnseenRegionItem | CompletionRegionItem) => void;
}

export const UnseenRegionOverlay: React.FC<UnseenRegionOverlayProps> = ({
  unseenRegions,
  completionRegions,
  selectedRegionId,
  onSelectRegion,
  onInspectRegion,
}) => {
  if (unseenRegions.length === 0) return null;

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <EyeOff className="w-4 h-4 text-rose-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Unseen Sectors & Completion ({unseenRegions.length})
          </h4>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Eligibility Verified
        </span>
      </div>

      <div className="flex flex-col gap-2.5 max-h-72 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-white/10">
        {unseenRegions.map((reg) => {
          const isSelected = selectedRegionId === reg.region_id;
          const matchingComp = completionRegions.find(
            (c) => c.region_id.includes(reg.region_id) || reg.region_id.includes(c.region_id)
          );
          const isEligible = reg.completion_eligibility?.is_eligible !== false;

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
                <div className="flex items-center gap-1">
                  {matchingComp ? (
                    <span
                      className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${
                        matchingComp.status === 'INFERRED'
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                          : matchingComp.status === 'CORRECTED'
                          ? 'bg-purple-500/20 text-purple-300 border-purple-500/30'
                          : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                      }`}
                    >
                      {matchingComp.status}
                    </span>
                  ) : (
                    <span className="text-[9px] font-mono px-1.5 py-0.5 rounded border bg-slate-800 text-slate-400 border-white/5">
                      {isEligible ? 'UNSEEN' : 'UNRESOLVED'}
                    </span>
                  )}
                </div>
              </div>

              {/* Reason description */}
              <p className="text-[11px] text-slate-400 mt-1 leading-snug">
                {reg.reason}
              </p>

              {/* Completion Action & Evidence */}
              {matchingComp && (
                <div className="mt-2 pt-2 border-t border-white/5 flex flex-col gap-1 text-[11px]">
                  <div className="flex items-center justify-between text-slate-300">
                    <div className="flex items-center gap-1.5">
                      <ArrowRight className="w-3 h-3 text-indigo-400" />
                      <span className="font-semibold text-slate-200">
                        {matchingComp.completion_level.replace(/_/g, ' ')}
                      </span>
                      <span className="text-[10px] text-emerald-400 font-mono">
                        ({Math.round((matchingComp.confidence || 0.8) * 100)}% conf)
                      </span>
                    </div>
                    {onInspectRegion && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onInspectRegion(matchingComp);
                        }}
                        className="flex items-center gap-1 text-[10px] text-cyan-400 hover:text-cyan-300 font-medium underline transition-colors"
                      >
                        <Info className="w-3 h-3" />
                        <span>Inspect Reason</span>
                      </button>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400 italic">
                    Evidence: {matchingComp.evidence_category}
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
