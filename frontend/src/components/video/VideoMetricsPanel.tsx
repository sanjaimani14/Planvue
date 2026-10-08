import React from 'react';
import { VideoSceneMetrics } from '../../types';
import { Activity, Clock, Box, Layers, Camera, Dot, ShieldCheck, Ruler } from 'lucide-react';

interface VideoMetricsPanelProps {
  metrics: any;
  onExportGlb: () => void;
  onExportJson: () => void;
  isExporting: boolean;
}

export const VideoMetricsPanel: React.FC<VideoMetricsPanelProps> = ({
  metrics,
  onExportGlb,
  onExportJson,
  isExporting,
}) => {
  if (!metrics) return null;

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-5 backdrop-blur-xl shadow-xl flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Reconstruction Telemetry & Provenance Accounting
          </h4>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={onExportGlb}
            disabled={isExporting}
            className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition-all disabled:opacity-50 flex items-center gap-1.5"
          >
            <Box className="w-3.5 h-3.5" />
            Export GLB
          </button>
          <button
            onClick={onExportJson}
            disabled={isExporting}
            className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-white/10 transition-all disabled:opacity-50 flex items-center gap-1.5"
          >
            <Layers className="w-3.5 h-3.5" />
            JSON
          </button>
        </div>
      </div>

      {/* Grid of Key Telemetry Points */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3 flex flex-col">
          <span className="text-[10px] text-slate-400 font-medium">Video Processing Time</span>
          <span className="text-sm font-bold text-indigo-400 font-mono mt-1 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" />
            {metrics.total_processing_time_ms ? `${metrics.total_processing_time_ms} ms` : 'N/A'}
          </span>
        </div>

        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3 flex flex-col">
          <span className="text-[10px] text-slate-400 font-medium">Trajectory Poses</span>
          <span className="text-sm font-bold text-white font-mono mt-1 flex items-center gap-1">
            <Camera className="w-3.5 h-3.5 text-indigo-400" />
            {metrics.camera_poses_estimated || 0}
          </span>
        </div>

        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3 flex flex-col">
          <span className="text-[10px] text-slate-400 font-medium">3D Sparse Points</span>
          <span className="text-sm font-bold text-emerald-400 font-mono mt-1 flex items-center gap-1">
            <Dot className="w-4 h-4" />
            {metrics.sparse_points_triangulated || 0}
          </span>
        </div>

        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3 flex flex-col">
          <span className="text-[10px] text-slate-400 font-medium">Observed Elements</span>
          <span className="text-sm font-bold text-slate-200 font-mono mt-1">
            {metrics.observed_elements_count || 0}
          </span>
        </div>

        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3 flex flex-col">
          <span className="text-[10px] text-slate-400 font-medium">Inferred (L1/L2)</span>
          <span className="text-sm font-bold text-cyan-400 font-mono mt-1">
            {metrics.inferred_elements_count || 0}
          </span>
        </div>

        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3 flex flex-col">
          <span className="text-[10px] text-slate-400 font-medium">Generated (L3 Shell)</span>
          <span className="text-sm font-bold text-amber-400 font-mono mt-1">
            {metrics.generated_elements_count || 0}
          </span>
        </div>
      </div>

      {/* Scale Provenance Disclaimer */}
      <div className="bg-slate-950/80 border border-white/5 rounded-xl p-3 flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <Ruler className="w-4 h-4 text-indigo-400" />
          <span>
            Scale Mode: <strong className="text-white font-mono uppercase">{metrics.scale_mode || 'relative'}</strong>
            <span className="text-[11px] text-slate-500 ml-2">
              (Monocular video has unconstrained translation baseline; units shown in relative steps)
            </span>
          </span>
        </div>
        <span className="text-[10px] text-indigo-300 font-mono px-2 py-0.5 rounded bg-indigo-500/10 border border-indigo-500/20">
          Scale Calibration Active
        </span>
      </div>
    </div>
  );
};
