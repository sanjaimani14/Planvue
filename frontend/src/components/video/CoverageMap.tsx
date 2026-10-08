import React from 'react';
import { CoverageReportItem } from '../../types';
import { Eye, ShieldAlert, Box, Layers } from 'lucide-react';

interface CoverageMapProps {
  coverage: CoverageReportItem | null;
}

export const CoverageMap: React.FC<CoverageMapProps> = ({ coverage }) => {
  if (!coverage) return null;

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Eye className="w-4 h-4 text-emerald-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Spatial Coverage Analysis
          </h4>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Volumetric Frustum Rays
        </span>
      </div>

      {/* Progress Bar Distribution */}
      <div className="w-full h-3 rounded-full bg-slate-950/80 overflow-hidden flex border border-white/5">
        <div
          style={{ width: `${coverage.observed_percentage}%` }}
          className="bg-emerald-500 h-full transition-all duration-500"
          title={`Observed: ${coverage.observed_percentage}%`}
        />
        <div
          style={{ width: `${coverage.weakly_observed_percentage}%` }}
          className="bg-amber-500 h-full transition-all duration-500"
          title={`Weakly Observed: ${coverage.weakly_observed_percentage}%`}
        />
        <div
          style={{ width: `${coverage.unseen_percentage}%` }}
          className="bg-rose-500 h-full transition-all duration-500"
          title={`Unseen: ${coverage.unseen_percentage}%`}
        />
      </div>

      {/* Legend & Stat Badges */}
      <div className="grid grid-cols-3 gap-2 text-center text-xs">
        <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-2">
          <div className="text-[10px] text-emerald-300 font-medium">Observed</div>
          <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">
            {coverage.observed_percentage}%
          </div>
        </div>

        <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-2">
          <div className="text-[10px] text-amber-300 font-medium">Weak View</div>
          <div className="text-sm font-bold text-amber-400 font-mono mt-0.5">
            {coverage.weakly_observed_percentage}%
          </div>
        </div>

        <div className="bg-rose-500/10 border border-rose-500/20 rounded-xl p-2">
          <div className="text-[10px] text-rose-300 font-medium">Unseen</div>
          <div className="text-sm font-bold text-rose-400 font-mono mt-0.5">
            {coverage.unseen_percentage}%
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-white/5">
        <span className="flex items-center gap-1">
          <Box className="w-3.5 h-3.5 text-slate-500" />
          Volume: <strong className="text-slate-200">{coverage.total_scene_volume_m3} m³</strong>
        </span>
        <span className="flex items-center gap-1">
          <Layers className="w-3.5 h-3.5 text-slate-500" />
          Rays Cast: <strong className="text-slate-200">{coverage.camera_visibility_rays_count}</strong>
        </span>
      </div>
    </div>
  );
};
