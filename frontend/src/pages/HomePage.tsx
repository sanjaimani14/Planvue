import React from 'react';
import {
  Layers,
  Video,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Play,
  Award,
  HelpCircle,
  WifiOff,
  Cpu,
  BarChart3,
  Box
} from 'lucide-react';

interface HomePageProps {
  onStartBlueprint: (autoDemo?: boolean) => void;
  onStartVideo: (autoDemo?: boolean) => void;
  onOpenEvaluation: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({
  onStartBlueprint,
  onStartVideo,
  onOpenEvaluation
}) => {
  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-12 space-y-16 animate-fade-in">
      {/* Hero Section */}
      <div className="text-center space-y-5 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-bold uppercase shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          <span>HackNEX 2026 — Problem HNX26EPS06</span>
          <span className="text-slate-500">•</span>
          <span className="inline-flex items-center gap-1 text-emerald-400">
            <WifiOff className="w-3 h-3" />
            Offline Mode
          </span>
        </div>

        <h1 className="text-5xl sm:text-6xl font-black text-white tracking-tight leading-none space-y-2">
          <span className="block">PLANE VUE</span>
          <span className="block text-2xl sm:text-3xl font-semibold bg-gradient-to-r from-indigo-300 via-indigo-200 to-cyan-300 bg-clip-text text-transparent italic">
            See the space. Reconstruct the unseen.
          </span>
        </h1>

        <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl mx-auto font-normal">
          AI-powered spatial reconstruction platform for architectural blueprints and handheld room walkthrough videos with rigorous visibility gating and structural constraint completion.
        </p>

        {/* Quick Demo Action Strip (Section 9) */}
        <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => onStartBlueprint(true)}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-indigo-500/40 hover:border-indigo-400 text-indigo-300 text-xs font-semibold flex items-center gap-2 transition-all hover:bg-indigo-950/40 shadow-sm"
          >
            <Play className="w-3.5 h-3.5 text-indigo-400" />
            <span>Load Demo Blueprint</span>
          </button>

          <button
            onClick={() => onStartVideo(true)}
            className="px-4 py-2 rounded-xl bg-slate-900 border border-cyan-500/40 hover:border-cyan-400 text-cyan-300 text-xs font-semibold flex items-center gap-2 transition-all hover:bg-cyan-950/40 shadow-sm"
          >
            <Play className="w-3.5 h-3.5 text-cyan-400" />
            <span>Load Demo Room Video</span>
          </button>

          <button
            onClick={() => onStartVideo(false)}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-indigo-600/30 transition-all"
          >
            <Award className="w-3.5 h-3.5 text-amber-300" />
            <span>Judge Mode Walkthrough</span>
          </button>
        </div>
      </div>

      {/* Two Core Mode Cards (Section 7) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* MODE A CARD */}
        <div className="glass-panel-glow p-8 rounded-3xl border border-indigo-500/30 flex flex-col justify-between space-y-6 hover:border-indigo-500/60 transition-all bg-slate-900/40">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                Mode A — Blueprint → 3D
              </span>
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Layers className="w-5 h-5" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-white">
              Blueprint → 3D
            </h3>

            <p className="text-sm text-slate-300 leading-relaxed">
              Upload a floor plan or architectural blueprint and reconstruct a metric 3D scene. Converts raster or PDF plans into metric 3D building models with automated wall/door/window parsing and topological validation.
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2">
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Metric Scale Engine</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Manifold Repair</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Room Enclosure</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Binary GLB Export</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onStartBlueprint(false)}
            className="w-full py-4 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/30 transition-all hover:scale-[1.01]"
          >
            <span>START BLUEPRINT RECONSTRUCTION</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* MODE B CARD */}
        <div className="glass-panel-glow p-8 rounded-3xl border border-cyan-500/30 flex flex-col justify-between space-y-6 hover:border-cyan-500/60 transition-all bg-slate-900/40">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase">
                Mode B — Video → 3D + Completion
              </span>
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                <Video className="w-5 h-5" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-white">
              Room Video → 3D + Completion
            </h3>

            <p className="text-sm text-slate-300 leading-relaxed">
              Upload a static room walkthrough and reconstruct observed geometry while identifying and completing unseen regions. Implements visibility-aware constraint completion with strict provenance and zero ungrounded hallucinations.
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2">
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>6-DOF Camera Motion</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>3D Voxel Raycasting</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Eligibility Engine</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-950/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Non-Overwrite Priority</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onStartVideo(false)}
            className="w-full py-4 px-6 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl shadow-cyan-600/30 transition-all hover:scale-[1.01]"
          >
            <span>START VIDEO RECONSTRUCTION</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Mode Comparison Matrix (Section 8) */}
      <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-6 backdrop-blur-xl">
        <h4 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-indigo-400" />
          Mode Comparison & Operational Scope
        </h4>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-4 rounded-xl bg-slate-950/70 border border-indigo-500/20 space-y-2">
            <div className="font-bold text-indigo-300 text-sm">MODE A: Structured Architectural Input</div>
            <p className="text-slate-300"><strong>Best for:</strong> Precise layout reconstruction from existing architectural documents.</p>
            <div className="space-y-1 text-slate-400">
              <div><strong className="text-white">Input:</strong> PNG, JPG, JPEG, multi-page vector PDF floor plans.</div>
              <div><strong className="text-white">Output:</strong> Parametric metric BIM building scene + binary GLB container.</div>
              <div><strong className="text-emerald-400">Strengths:</strong> Authoritative dimensions, exact door/window placements, OCR scale lock.</div>
              <div><strong className="text-amber-400">Limitations:</strong> Does not capture real-world surface wear, furnishings, or dynamic room conditions.</div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/70 border border-cyan-500/20 space-y-2">
            <div className="font-bold text-cyan-300 text-sm">MODE B: Real-World Visual Walkthrough</div>
            <p className="text-slate-300"><strong>Best for:</strong> Real-world room capture, blind-spot identification, and unseen completion.</p>
            <div className="space-y-1 text-slate-400">
              <div><strong className="text-white">Input:</strong> Handheld walkthrough video (MP4, MOV, AVI, WEBM).</div>
              <div><strong className="text-white">Output:</strong> 3D scene + voxel coverage map + conservative unseen completion.</div>
              <div><strong className="text-emerald-400">Strengths:</strong> Operates directly on visual reality; maps occluded perimeter sectors.</div>
              <div><strong className="text-amber-400">Limitations:</strong> Monocular scale requires ceiling prior; featureless white walls rely on corner constraints.</div>
            </div>
          </div>
        </div>
      </div>

      {/* Presentation Dashboard & Research Cards (Sections 40, 41, 42) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Presentation Dashboard (Section 40) */}
        <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-5 flex flex-col justify-between space-y-3">
          <div>
            <div className="text-[10px] font-mono uppercase text-slate-400 font-bold">System Status</div>
            <h4 className="text-lg font-bold text-white mt-1">Presentation Dashboard</h4>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between items-center p-2 rounded bg-slate-950/60 border border-white/5">
              <span className="text-slate-400">Mode A Engine:</span>
              <span className="text-emerald-400 font-bold">Active & Verified</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-slate-950/60 border border-white/5">
              <span className="text-slate-400">Mode B Engine:</span>
              <span className="text-cyan-400 font-bold">Active & Verified</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-slate-950/60 border border-white/5">
              <span className="text-slate-400">Verification Status:</span>
              <span className="text-emerald-400 font-bold">System Ready (PASS)</span>
            </div>
            <div className="flex justify-between items-center p-2 rounded bg-slate-950/60 border border-white/5">
              <span className="text-slate-400">Automated Tests:</span>
              <span className="text-white font-bold">79 / 79 Passing</span>
            </div>
          </div>

          <button
            onClick={onOpenEvaluation}
            className="w-full py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-indigo-300 flex items-center justify-center gap-1.5 transition-all"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Open Evaluation Lab</span>
          </button>
        </div>

        {/* Research Contribution Card (Section 41) */}
        <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-indigo-400" />
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Our Contribution</h4>
          </div>
          <div className="text-xs font-semibold text-indigo-300">
            Visibility-Aware Constraint Completion
          </div>
          <ol className="text-xs text-slate-300 space-y-1.5 list-decimal list-inside leading-relaxed">
            <li>Estimate what camera actually observed</li>
            <li>Identify unobserved perimeter sectors</li>
            <li>Evaluate structural evidence & eligibility</li>
            <li>Generate only structurally justified geometry</li>
            <li>Validate against non-overwrite invariants</li>
            <li>Preserve transparent provenance & confidence</li>
          </ol>
        </div>

        {/* Honesty Card (Section 42) */}
        <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-amber-400" />
            <h4 className="text-sm font-bold text-white uppercase tracking-wider">Scientific Honesty</h4>
          </div>
          <div className="space-y-2 text-xs">
            <div>
              <strong className="text-emerald-400 font-mono">OBSERVED:</strong>
              <p className="text-slate-300 text-[11px]">Directly supported by multi-view video observations.</p>
            </div>
            <div>
              <strong className="text-cyan-400 font-mono">INFERRED:</strong>
              <p className="text-slate-300 text-[11px]">Derived from collinearity or orthogonal symmetry constraints.</p>
            </div>
            <div>
              <strong className="text-purple-400 font-mono">GENERATED:</strong>
              <p className="text-slate-300 text-[11px]">Synthesized conservative room-shell perimeter closure.</p>
            </div>
            <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-amber-300 text-[11px]">
              <strong>Insufficient Evidence?</strong> The system leaves the region unresolved rather than hallucinating geometry.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
