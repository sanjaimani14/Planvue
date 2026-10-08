import React from 'react';
import { 
  Box, Layers, Video, ArrowRight, ShieldCheck, 
  Ruler, Sparkles, CheckCircle2, Compass, Download, Eye, Zap 
} from 'lucide-react';

interface HomeViewProps {
  onSelectMode: (mode: 'A' | 'B') => void;
  onRunDemo: (mode: 'A' | 'B') => void;
}

export const HomeView: React.FC<HomeViewProps> = ({ onSelectMode, onRunDemo }) => {
  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-12 space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-6 max-w-3xl mx-auto relative">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-bold uppercase shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          AI-Powered Spatial Reconstruction Platform
        </div>

        <h1 className="text-5xl sm:text-6xl font-black text-white tracking-tight leading-none">
          PLANE VUE
        </h1>

        <p className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-indigo-300 via-indigo-200 to-violet-300 bg-clip-text text-transparent">
          "See the space. Reconstruct the unseen."
        </p>

        <p className="text-sm sm:text-base text-slate-300 leading-relaxed max-w-2xl mx-auto font-normal">
          An AI-powered spatial reconstruction platform that transforms architectural blueprints and static room videos into measurable, navigable 3D environments with honest uncertainty attribution.
        </p>

        {/* 1-Click Quick Demo Buttons */}
        <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={() => onRunDemo('A')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/30 transition-all hover:scale-105"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Try Demo Blueprint (Mode A)
          </button>

          <button
            onClick={() => onRunDemo('B')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-semibold text-xs shadow-lg shadow-purple-600/30 transition-all hover:scale-105"
          >
            <Video className="w-3.5 h-3.5" />
            Try Demo Room Video (Mode B)
          </button>
        </div>
      </div>

      {/* TWO PRIMARY MODE CARDS */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* MODE A CARD */}
        <div className="group glass-panel-glow p-8 rounded-3xl border border-indigo-500/30 flex flex-col justify-between space-y-6 hover:border-indigo-500/60 transition-all duration-300">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                Input Mode A
              </span>
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 group-hover:scale-110 transition-transform">
                <Layers className="w-5 h-5" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-white group-hover:text-indigo-200 transition-colors">
              Blueprint → Metric 3D Building
            </h3>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Convert architectural floor plans (PNG, JPG, PDF) into metrically scaled, BIM-compatible 3D buildings. Features automated wall extraction, door snapping, topological polygon verification, and lintel opening cutouts.
            </p>

            <div className="grid grid-cols-2 gap-2.5 pt-2 text-xs font-mono text-slate-300">
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Metric Calibration</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Door / Window Snapping</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Room Cycle Closures</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Binary GLB Export</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onSelectMode('A')}
            className="w-full py-3.5 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/30 group-hover:shadow-indigo-600/50 transition-all"
          >
            <span>Start Blueprint Reconstruction</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        {/* MODE B CARD */}
        <div className="group glass-panel p-8 rounded-3xl border border-white/10 flex flex-col justify-between space-y-6 hover:border-purple-500/50 transition-all duration-300">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 uppercase">
                Input Mode B
              </span>
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 group-hover:scale-110 transition-transform">
                <Video className="w-5 h-5" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-white group-hover:text-purple-200 transition-colors">
              Room Video → 3D Scene + Unseen Completion
            </h3>

            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Reconstruct a static room from a walkthrough video (MP4, MOV) and synthesize unseen regions the camera never observed. Computes 3D camera coverage raycasting and labels completed geometry with honest uncertainty attribution.
            </p>

            <div className="grid grid-cols-2 gap-2.5 pt-2 text-xs font-mono text-slate-300">
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />
                <span>Keyframe Selection</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />
                <span>Camera Pose SfM</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />
                <span>Coverage Raycasting</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-purple-400" />
                <span>Unseen Procedural Wall</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => onSelectMode('B')}
            className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-bold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl shadow-purple-600/30 group-hover:shadow-purple-600/50 transition-all"
          >
            <span>Start Video Reconstruction</span>
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      {/* FEATURE PILL HIGHLIGHTS */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 pt-4">
        {[
          { label: 'Metric Reconstruction', icon: Ruler },
          { label: 'Geometry Validation', icon: ShieldCheck },
          { label: 'Unseen Completion', icon: Sparkles },
          { label: 'Confidence View', icon: Eye },
          { label: 'Interactive 3D Viewer', icon: Box },
          { label: 'GLB BIM Export', icon: Download },
        ].map((feat, i) => {
          const Icon = feat.icon;
          return (
            <div
              key={i}
              className="glass-panel p-3.5 rounded-xl border border-white/5 text-center flex flex-col items-center justify-center gap-2 hover:border-white/20 transition-colors"
            >
              <Icon className="w-4 h-4 text-indigo-400" />
              <span className="text-[11px] font-semibold text-slate-300">{feat.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
