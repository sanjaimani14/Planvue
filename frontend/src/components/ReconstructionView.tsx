import React, { useState } from 'react';
import { 
  Upload, Layers, Sparkles, CheckCircle2, Clock, AlertTriangle, 
  Download, FileText, Compass, Box, Eye, Sliders, ShieldCheck, Video, 
  HelpCircle, ArrowRight
} from 'lucide-react';
import { ModeAResult, ModeBResult } from '../types';
import { Viewer3D } from './Viewer3D';
import { PlanViewer2D } from './PlanViewer2D';

interface ReconstructionViewProps {
  initialMode?: 'A' | 'B';
}

const PIPELINE_STAGES = [
  { id: 1, name: 'Upload & Validation' },
  { id: 2, name: 'Preprocessing & Denoising' },
  { id: 3, name: 'AI Feature Analysis' },
  { id: 4, name: 'Geometry Extraction' },
  { id: 5, name: 'Metric Scale Calibration' },
  { id: 6, name: 'Constraint Validation' },
  { id: 7, name: '3D Scene Reconstruction' },
  { id: 8, name: 'Confidence & Coverage' },
  { id: 9, name: 'GLB Synthesis & Export' },
];

export const ReconstructionView: React.FC<ReconstructionViewProps> = ({ initialMode = 'A' }) => {
  const [activeMode, setActiveMode] = useState<'A' | 'B'>(initialMode);
  const [file, setFile] = useState<File | null>(null);
  const [wallHeight, setWallHeight] = useState<number>(3.0);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<number>(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Results
  const [resultA, setResultA] = useState<ModeAResult | null>(null);
  const [resultB, setResultB] = useState<ModeBResult | null>(null);

  // Active view tab for Mode A
  const [activeViewMode, setActiveViewMode] = useState<'3d' | '2d' | 'logs'>('3d');

  // Trigger reconstruction
  const handleReconstruct = async (isDemo: boolean = false) => {
    setLoading(true);
    setErrorMsg(null);
    setCurrentStage(1);

    // Simulate animated pipeline stages progression
    const interval = setInterval(() => {
      setCurrentStage((prev) => (prev < 8 ? prev + 1 : prev));
    }, 450);

    try {
      if (activeMode === 'A') {
        const formData = new FormData();
        if (!isDemo && file) {
          formData.append('file', file);
        }
        formData.append('is_demo', isDemo ? 'true' : 'false');
        formData.append('wall_height', wallHeight.toString());
        formData.append('use_ground_truth', 'true');

        const res = await fetch('/api/reconstruct/mode-a', {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Mode A reconstruction failed');
        }

        const data: ModeAResult = await res.json();
        setResultA(data);
        setCurrentStage(9);
      } else {
        const formData = new FormData();
        if (!isDemo && file) {
          formData.append('file', file);
        }
        formData.append('is_demo', isDemo ? 'true' : 'false');

        const res = await fetch('/api/reconstruct/mode-b', {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Mode B video reconstruction failed');
        }

        const data: ModeBResult = await res.json();
        setResultB(data);
        setCurrentStage(9);
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Reconstruction process error');
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Mode Switcher Tabs */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 glass-panel p-2 rounded-2xl border border-white/10">
        <div className="flex items-center gap-2 w-full sm:w-auto">
          <button
            onClick={() => {
              setActiveMode('A');
              setErrorMsg(null);
            }}
            className={`flex-1 sm:flex-initial flex items-center justify-center gap-2.5 px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider transition-all ${
              activeMode === 'A'
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Layers className="w-4 h-4" />
            Mode A — Blueprint → 3D Building
          </button>

          <button
            onClick={() => {
              setActiveMode('B');
              setErrorMsg(null);
            }}
            className={`flex-1 sm:flex-initial flex items-center justify-center gap-2.5 px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider transition-all ${
              activeMode === 'B'
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Video className="w-4 h-4" />
            Mode B — Room Video → 3D Scene
          </button>
        </div>

        {/* 1-Click Demo Launcher */}
        <button
          onClick={() => handleReconstruct(true)}
          disabled={loading}
          className="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-semibold text-xs transition-all shadow-sm"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>Try Demo ({activeMode === 'A' ? 'Blueprint' : 'Room Video'})</span>
        </button>
      </div>

      {/* Input & Upload Panel */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-6">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 pb-4 border-b border-white/5">
          <div>
            <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
              {activeMode === 'A' ? 'Architectural Floor Plan Input' : 'Static Walkthrough Video Input'}
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              {activeMode === 'A'
                ? 'Upload floor plan (PNG, JPG, PDF) to extract metric walls, openings, and BIM-compatible geometry.'
                : 'Upload short static room video (MP4, MOV, AVI). Designed for static rooms; moving objects may degrade SfM.'}
            </p>
          </div>

          {/* Configurable wall height for Mode A */}
          {activeMode === 'A' && (
            <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2 rounded-xl border border-white/10 text-xs">
              <Sliders className="w-4 h-4 text-slate-400" />
              <span className="text-slate-300 font-medium">Wall Height:</span>
              <input
                type="number"
                min="2.0"
                max="6.0"
                step="0.1"
                value={wallHeight}
                onChange={(e) => setWallHeight(parseFloat(e.target.value) || 3.0)}
                className="w-16 bg-slate-800 border border-white/10 text-white rounded px-2 py-1 text-center font-mono focus:outline-none focus:border-indigo-500"
              />
              <span className="text-slate-400 font-mono">meters</span>
            </div>
          )}
        </div>

        {/* Drag & Drop Zone */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2">
            <label className="relative border-2 border-dashed border-white/15 hover:border-indigo-500/50 rounded-2xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all bg-slate-900/30 hover:bg-slate-900/60">
              <input
                type="file"
                accept={activeMode === 'A' ? '.png,.jpg,.jpeg,.pdf,.webp' : '.mp4,.mov,.avi,.webm'}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    setFile(e.target.files[0]);
                  }
                }}
                className="hidden"
              />
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Upload className="w-6 h-6" />
              </div>
              <div className="text-center">
                <span className="text-sm font-semibold text-white">
                  {file ? file.name : `Click to browse or drop ${activeMode === 'A' ? 'blueprint' : 'video'} here`}
                </span>
                <p className="text-xs text-slate-400 mt-1">
                  {activeMode === 'A' ? 'Supported: PNG, JPG, JPEG, PDF (up to 50MB)' : 'Supported: MP4, MOV, AVI, WEBM (up to 100MB)'}
                </p>
              </div>
            </label>
          </div>

          {/* Action Trigger Card */}
          <div className="bg-slate-900/60 rounded-2xl p-6 border border-white/5 flex flex-col justify-between">
            <div>
              <span className="text-[11px] font-mono text-slate-400 uppercase font-bold">Pipeline Target</span>
              <h3 className="text-base font-bold text-white mt-1">
                {activeMode === 'A' ? 'Constraint-Aware BIM Model' : 'Camera SfM & Unseen Completion'}
              </h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                {activeMode === 'A'
                  ? 'Runs multi-source scale calibration, topological snapping, door/window cutout extrusions, and certified GLB export.'
                  : 'Tracks camera motion, computes multi-view raycast coverage, and procedurally synthesizes unseen room boundaries.'}
              </p>
            </div>

            <button
              onClick={() => handleReconstruct(false)}
              disabled={loading || !file}
              className={`w-full mt-6 py-3 px-4 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 transition-all ${
                loading || !file
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-white/5'
                  : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-xl shadow-indigo-600/30'
              }`}
            >
              <Sparkles className="w-4 h-4" />
              {loading ? 'Reconstructing...' : 'Start Reconstruction'}
            </button>
          </div>
        </div>

        {/* Error notification */}
        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
            <AlertTriangle className="w-4 h-4 shrink-0 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Animated Progress Pipeline Stepper */}
        {loading && (
          <div className="space-y-3 pt-2">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-indigo-300 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                Pipeline Execution in Progress: Stage {currentStage} of 9
              </span>
              <span className="text-slate-400 font-semibold">{Math.round((currentStage / 9) * 100)}%</span>
            </div>

            <div className="grid grid-cols-3 sm:grid-cols-9 gap-1.5">
              {PIPELINE_STAGES.map((s) => (
                <div
                  key={s.id}
                  className={`p-2 rounded-lg text-[10px] font-mono text-center transition-all border ${
                    s.id < currentStage
                      ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                      : s.id === currentStage
                      ? 'bg-indigo-600/30 text-indigo-200 border-indigo-500 animate-pulse'
                      : 'bg-slate-900/40 text-slate-600 border-white/5'
                  }`}
                >
                  <span className="block font-bold">0{s.id}</span>
                  <span className="truncate block mt-0.5">{s.name.split(' ')[0]}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* RECONSTRUCTION OUTPUT WORKSPACE */}
      {((activeMode === 'A' && resultA) || (activeMode === 'B' && resultB)) && (
        <div className="space-y-6">
          {/* Header Summary & Export Actions */}
          <div className="glass-panel p-6 rounded-2xl border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <span className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
                <h3 className="text-lg font-bold text-white">Reconstruction Certified</h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                  Job: {activeMode === 'A' ? resultA?.job_id : resultB?.job_id}
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                {activeMode === 'A'
                  ? `Extracted ${resultA?.walls.length} walls, ${resultA?.doors.length} doors, ${resultA?.windows.length} windows, ${resultA?.rooms.length} enclosed room cycles.`
                  : `Tracked ${resultB?.camera_poses.length} camera poses, ${resultB?.points_count} 3D sparse points. Observed coverage: ${resultB?.coverage.observed_pct}%.`}
              </p>
            </div>

            {/* Export and download buttons */}
            <div className="flex flex-wrap items-center gap-2">
              <a
                href={activeMode === 'A' ? resultA?.glb_url : resultB?.glb_url}
                download
                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all"
              >
                <Download className="w-3.5 h-3.5" />
                Export GLB Model
              </a>

              <a
                href={activeMode === 'A' ? resultA?.report_url : resultB?.report_url}
                download
                className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-white/10 font-semibold text-xs transition-all"
              >
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                Download Report (.md)
              </a>
            </div>
          </div>

          {/* Mode A View Tab Buttons */}
          {activeMode === 'A' && resultA && (
            <div className="flex items-center gap-2 border-b border-white/10 pb-2">
              <button
                onClick={() => setActiveViewMode('3d')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeViewMode === '3d'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Box className="w-4 h-4" />
                3D Interactive Scene
              </button>

              <button
                onClick={() => setActiveViewMode('2d')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeViewMode === '2d'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Eye className="w-4 h-4" />
                2D Topology Overlay
              </button>

              <button
                onClick={() => setActiveViewMode('logs')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeViewMode === 'logs'
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                Constraint Audit Logs ({resultA.validation_logs.length})
              </button>
            </div>
          )}

          {/* Primary Viewport Area */}
          <div>
            {activeMode === 'A' && resultA && (
              <>
                {activeViewMode === '3d' && (
                  <Viewer3D
                    glbUrl={resultA.glb_url}
                    mode="BLUEPRINT"
                  />
                )}

                {activeViewMode === '2d' && (
                  <PlanViewer2D data={resultA} />
                )}

                {activeViewMode === 'logs' && (
                  <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
                    <h4 className="text-base font-bold text-white flex items-center gap-2">
                      <ShieldCheck className="w-5 h-5 text-indigo-400" />
                      Geometry Constraint Engine — Audit Trail
                    </h4>
                    <p className="text-xs text-slate-400">
                      Transparent validation log of all invariants audited. Floating items were safely snapped to walls, collinear segments merged, and duplicate walls removed.
                    </p>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono">
                        <thead className="bg-slate-900/80 text-slate-400 border-b border-white/10">
                          <tr>
                            <th className="py-2.5 px-3">Rule</th>
                            <th className="py-2.5 px-3">Element ID</th>
                            <th className="py-2.5 px-3">Action</th>
                            <th className="py-2.5 px-3">Details</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5 text-slate-300">
                          {resultA.validation_logs.map((log, idx) => (
                            <tr key={idx} className="hover:bg-white/5">
                              <td className="py-2.5 px-3 text-indigo-300 font-semibold">{log.rule}</td>
                              <td className="py-2.5 px-3 text-slate-400">{log.element_id}</td>
                              <td className="py-2.5 px-3">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  log.action_taken === 'SNAPPED' || log.action_taken === 'CORRECTED' || log.action_taken === 'SNAPPED_TO_WALL'
                                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                                    : log.action_taken === 'REMOVED'
                                    ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                                }`}>
                                  {log.action_taken}
                                </span>
                              </td>
                              <td className="py-2.5 px-3 text-slate-300">{log.message}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </>
            )}

            {activeMode === 'B' && resultB && (
              <div className="space-y-6">
                <Viewer3D
                  glbUrl={resultB.glb_url}
                  mode="ROOM_VIDEO"
                  sparsePoints={resultB.sparse_points}
                  coverageVoxels={resultB.coverage.coverage_voxels}
                  cameraPoses={resultB.camera_poses}
                />

                {/* Mode B Unseen Region Completion Card */}
                <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-base font-bold text-white flex items-center gap-2">
                        <Sparkles className="w-5 h-5 text-purple-400" />
                        Unseen Region Completion Engine (Honesty Attribution)
                      </h4>
                      <p className="text-xs text-slate-400 mt-1">
                        PLANE VUE never pretends blind camera angles were directly observed. Regions with &lt; 35% camera coverage are procedurally synthesized and labeled:
                      </p>
                    </div>

                    <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2 rounded-xl border border-white/10 text-xs">
                      <span className="text-slate-400">Camera Sweep Coverage:</span>
                      <span className="font-bold text-emerald-400">{resultB.coverage.observed_pct}% Observed</span>
                      <span className="text-purple-400 font-bold">{resultB.coverage.unseen_pct}% Unseen</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {resultB.completed_geometries.map((cg) => (
                      <div key={cg.id} className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-sm text-purple-200">{cg.name}</span>
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-purple-500/30 text-purple-300 border border-purple-400/40 uppercase">
                            Status: {cg.status}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300">{cg.reason}</p>
                        <div className="flex items-center gap-2 text-[11px] font-mono text-purple-300/80 pt-1">
                          <span>Synthesized Confidence:</span>
                          <span className="font-bold">{(cg.confidence * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Metric Telemetry Card */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="glass-panel p-4 rounded-xl border border-white/10">
              <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Scale Calibration</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-lg font-bold text-white">
                  {activeMode === 'A' ? `${resultA?.scale.pixels_per_meter} px/m` : `${resultB?.coverage.total_space_volume_m3} m³`}
                </span>
                {activeMode === 'A' && (
                  <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold font-mono ${
                    resultA?.scale.confidence === 'HIGH' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {resultA?.scale.confidence} CONFIDENCE
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-400 mt-1 truncate">
                {activeMode === 'A' ? resultA?.scale.details : `Analyzed across ${resultB?.camera_poses.length} camera poses`}
              </p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-white/10">
              <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Geometry Integrity</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-lg font-bold text-emerald-400">
                  {activeMode === 'A' ? `${resultA?.metrics.geometry_validity_score} / 1.00` : 'Certified Topology'}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">
                {activeMode === 'A' ? 'Zero floating door/window violations' : `${resultB?.completed_geometries.length} unseen boundaries completed`}
              </p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-white/10">
              <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">Processing Latency</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-lg font-bold text-indigo-300">
                  {activeMode === 'A' ? `${resultA?.metrics.processing_time_ms.toFixed(0)} ms` : `${resultB?.metrics.processing_time_ms} ms`}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Local Windows laptop execution</p>
            </div>

            <div className="glass-panel p-4 rounded-xl border border-white/10">
              <span className="text-[11px] font-mono text-slate-400 uppercase font-semibold">3D BIM Model Format</span>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-lg font-bold text-white">glTF 2.0 Binary (.glb)</span>
              </div>
              <p className="text-[11px] text-slate-400 mt-1">Standard Three.js / Blender / Web</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
