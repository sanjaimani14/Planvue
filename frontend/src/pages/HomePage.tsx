import React, { useState } from 'react';
import { Layers, Video, ArrowRight, ShieldCheck, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

interface HomePageProps {
  onStartBlueprint: () => void;
  onStartVideo: () => void;
}

export const HomePage: React.FC<HomePageProps> = ({ onStartBlueprint, onStartVideo }) => {
  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-16 space-y-16">
      {/* Hero Section */}
      <div className="text-center space-y-6 max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-300 text-xs font-mono font-bold uppercase shadow-sm">
          <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          AI Spatial Reconstruction
        </div>

        <h1 className="text-5xl sm:text-6xl font-black text-white tracking-tight leading-none space-y-2">
          <span className="block">See the space.</span>
          <span className="block bg-gradient-to-r from-indigo-300 via-indigo-200 to-violet-300 bg-clip-text text-transparent">
            Reconstruct the unseen.
          </span>
        </h1>

        <p className="text-base text-slate-300 leading-relaxed max-w-2xl mx-auto font-normal">
          PLANE VUE transforms architectural floor plans and static room walkthrough videos into measurable, navigable 3D environments with explicit provenance.
        </p>
      </div>

      {/* Two Mode Cards (Section 5) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* MODE A CARD — Working Mode */}
        <div className="glass-panel-glow p-8 rounded-3xl border border-indigo-500/30 flex flex-col justify-between space-y-6 hover:border-indigo-500/60 transition-all">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 uppercase">
                Mode A — Active
              </span>
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
                <Layers className="w-5 h-5" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-white">
              Blueprint → 3D
            </h3>

            <p className="text-sm text-slate-300 leading-relaxed">
              Convert architectural floor plans into metrically scaled 3D buildings. Features automated wall extraction, door snapping, topological polygon verification, and BIM metric normalization.
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2">
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Metric Calibration</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Constraint Snapping</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>Room Cycle Closure</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-indigo-400" />
                <span>scene.json Export</span>
              </div>
            </div>
          </div>

          <button
            onClick={onStartBlueprint}
            className="w-full py-4 px-6 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl shadow-indigo-600/30 transition-all hover:scale-[1.02]"
          >
            <span>START BLUEPRINT MODE</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* MODE B CARD — Room Video */}
        <div className="glass-panel-glow p-8 rounded-3xl border border-cyan-500/30 flex flex-col justify-between space-y-6 hover:border-cyan-500/60 transition-all">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 uppercase">
                Mode B — Active
              </span>
              <div className="w-10 h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                <Video className="w-5 h-5" />
              </div>
            </div>

            <h3 className="text-2xl font-bold text-white">
              Room Video → 3D + Unseen Completion
            </h3>

            <p className="text-sm text-slate-300 leading-relaxed">
              Reconstruct static rooms from walkthrough video and complete unseen occluded regions. Features 6-DOF camera tracking, 3D spatial coverage analysis, and conservative hierarchical completion.
            </p>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono text-slate-300 pt-2">
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>6-DOF Camera Tracking</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Sparse Triangulation</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Frustum Coverage Map</span>
              </div>
              <div className="flex items-center gap-2 bg-slate-900/60 p-2 rounded-lg border border-white/5">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Unseen Completion</span>
              </div>
            </div>
          </div>

          <button
            onClick={onStartVideo}
            className="w-full py-4 px-6 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-extrabold text-xs uppercase tracking-wider flex items-center justify-center gap-2 shadow-xl shadow-cyan-600/30 transition-all hover:scale-[1.02]"
          >
            <span>START VIDEO MODE</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

