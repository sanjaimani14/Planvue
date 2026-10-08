import React from 'react';
import { 
  Box, ShieldCheck, Cpu, Layers, Sparkles, CheckCircle2, 
  HelpCircle, Eye, Compass, Terminal, FileCode2 
} from 'lucide-react';

export const AboutView: React.FC = () => {
  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Research Contribution Hero */}
      <div className="glass-panel p-8 rounded-2xl border border-white/10 space-y-6 relative overflow-hidden">
        <div className="absolute -right-20 -bottom-20 w-80 h-80 rounded-full bg-indigo-600/10 blur-3xl pointer-events-none" />

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-bold uppercase">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          Primary Research Contribution
        </div>

        <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
          Constraint-Aware Metric Reconstruction
        </h2>

        <blockquote className="border-l-4 border-indigo-500 pl-4 py-1 text-slate-300 text-sm sm:text-base leading-relaxed italic bg-indigo-950/20 rounded-r-xl">
          "Traditional reconstruction systems primarily reproduce what the camera or blueprint explicitly provides.
          PLANE VUE goes one step further. It converts symbolic architectural information or visual observations into a metric 3D scene, validates the geometry, and explicitly distinguishes what is observed from what is inferred or generated.
          For video reconstruction, PLANE VUE completes spatial regions that were never directly observed while remaining transparent about that uncertainty."
        </blockquote>
      </div>

      {/* Two Pillars Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Pillar 1: Mode A */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <Layers className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white">MODE A — Blueprint → Metric 3D Building</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Eliminates floating openings and topological errors inherent in naive computer vision. Enforces architectural priors:
          </p>

          <ul className="space-y-2.5 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Metric Scale Calibration:</strong> Resolves true physical dimensions via OCR witness lines, door leaf widths (0.90m standard), and structural wall thicknesses.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Geometry Constraint Engine:</strong> Audits collinear overlaps, corner gaps, floating doors, and invalid polygons, snapping elements to true wall axes.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Physical BIM Cutouts:</strong> Generates real 3D wall lintels, sills, and jambs for standard GLB / BIM export.</span>
            </li>
          </ul>
        </div>

        {/* Pillar 2: Mode B */}
        <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <Eye className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-bold text-white">MODE B — Room Video → Unseen Completion</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Transparently completes blind spots without disguising hallucinated geometry as sensor reality:
          </p>

          <ul className="space-y-2.5 text-xs text-slate-300">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
              <span><strong>Camera Trajectory & SfM:</strong> Tracks essential matrix camera poses and triangulates photometric 3D point clouds.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
              <span><strong>3D Spatial Frustum Coverage:</strong> Classifies the entire room volume into OBSERVED, PARTIALLY OBSERVED, and UNSEEN voxels.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-purple-400 shrink-0 mt-0.5" />
              <span><strong>Honest Unseen Completion:</strong> Synthesizes unobserved boundary walls and ceilings based on structural continuity while explicitly tagging status as GENERATED.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Architectural Pipeline Diagram Card */}
      <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Cpu className="w-5 h-5 text-indigo-400" />
          End-to-End System Pipeline
        </h3>

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-3 pt-2 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1">
            <span className="text-[10px] text-indigo-400 font-bold">STAGE 01</span>
            <div className="font-bold text-white">Sensory Ingestion</div>
            <p className="text-[11px] text-slate-400 font-sans">Adaptive binarization, CLAHE, Laplacian variance filtering</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1">
            <span className="text-[10px] text-indigo-400 font-bold">STAGE 02</span>
            <div className="font-bold text-white">Feature Extraction</div>
            <p className="text-[11px] text-slate-400 font-sans">Directional wall kernels, door arcs, ORB multi-scale tracking</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1">
            <span className="text-[10px] text-indigo-400 font-bold">STAGE 03</span>
            <div className="font-bold text-white">Metric Calibration</div>
            <p className="text-[11px] text-slate-400 font-sans">Multi-source confidence scoring, pixel-to-meter resolution</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1">
            <span className="text-[10px] text-indigo-400 font-bold">STAGE 04</span>
            <div className="font-bold text-white">Constraint Engine</div>
            <p className="text-[11px] text-slate-400 font-sans">Topological snapping, duplicate pruning, polygon certification</p>
          </div>

          <div className="p-3.5 rounded-xl bg-slate-900/80 border border-white/5 space-y-1">
            <span className="text-[10px] text-indigo-400 font-bold">STAGE 05</span>
            <div className="font-bold text-white">BIM 3D Synthesis</div>
            <p className="text-[11px] text-slate-400 font-sans">Trimesh GLB compilation, confidence color-coding, audit report</p>
          </div>
        </div>
      </div>

      {/* System Engineering Details */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-white/10 space-y-1">
          <span className="text-xs font-mono text-indigo-400 font-bold">OFFLINE-FIRST</span>
          <h4 className="text-sm font-bold text-white">Zero Cloud Lock-In</h4>
          <p className="text-xs text-slate-400">
            Executes 100% locally on a Windows laptop without requiring proprietary cloud AI API keys.
          </p>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-white/10 space-y-1">
          <span className="text-xs font-mono text-emerald-400 font-bold">HONESTY FIRST</span>
          <h4 className="text-sm font-bold text-white">Transparent Attribution</h4>
          <p className="text-xs text-slate-400">
            Never fakes evaluation scores or disguises procedural completions as sensor observations.
          </p>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-white/10 space-y-1">
          <span className="text-xs font-mono text-purple-400 font-bold">INTEROPERABLE</span>
          <h4 className="text-sm font-bold text-white">Standard GLTF / GLB</h4>
          <p className="text-xs text-slate-400">
            Directly viewable in WebGL Three.js and importable into Blender, Unreal Engine, and Unity.
          </p>
        </div>
      </div>
    </div>
  );
};
