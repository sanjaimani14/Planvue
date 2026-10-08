import React, { useState } from 'react';
import { HomePage } from './pages/HomePage';
import { BlueprintPage } from './pages/BlueprintPage';
import { VideoReconstructionPage } from './pages/VideoReconstructionPage';
import { EvaluationPage } from './pages/EvaluationPage';
import { Box, Layers, Compass, ShieldCheck, BarChart3, Video } from 'lucide-react';

export function App() {
  const [activePage, setActivePage] = useState<'home' | 'blueprint' | 'video' | 'evaluation'>('home');

  return (
    <div className="min-h-screen bg-[#090b10] text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30 selection:text-indigo-200">
      {/* Background ambient lighting */}
      <div className="fixed inset-0 pointer-events-none radial-glow" />
      <div className="fixed inset-0 pointer-events-none grid-bg opacity-40" />

      {/* Global Header (Section 5) */}
      <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-3.5 flex items-center justify-between backdrop-blur-xl">
        <div 
          className="flex items-center gap-3.5 cursor-pointer group"
          onClick={() => setActivePage('home')}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-500 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:shadow-indigo-500/40 transition-all duration-300">
            <div className="w-full h-full bg-slate-950/80 rounded-[10px] flex items-center justify-center">
              <Box className="w-5 h-5 text-indigo-400 group-hover:scale-110 transition-transform" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-wider text-white">PLANE VUE</span>
              <span className="text-[10px] uppercase font-mono font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Mode A + B Active
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium tracking-tight">AI Spatial Reconstruction</p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-xl border border-white/5">
          <button
            onClick={() => setActivePage('home')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activePage === 'home'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Compass className="w-3.5 h-3.5" />
            Home
          </button>

          <button
            onClick={() => setActivePage('blueprint')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activePage === 'blueprint'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Mode A — Blueprint
          </button>

          <button
            onClick={() => setActivePage('video')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activePage === 'video'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <Video className="w-3.5 h-3.5" />
            Mode B — Room Video
          </button>

          <button
            onClick={() => setActivePage('evaluation')}
            className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activePage === 'evaluation'
                ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                : 'text-slate-400 hover:text-white hover:bg-white/5'
            }`}
          >
            <BarChart3 className="w-3.5 h-3.5" />
            Evaluation Lab
          </button>
        </nav>

        {/* Active Engine Badge */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>Constraint Engine Active</span>
        </div>
      </header>

      {/* Main Content View */}
      <main className="flex-1 relative z-10">
        {activePage === 'home' && (
          <HomePage
            onStartBlueprint={() => setActivePage('blueprint')}
            onStartVideo={() => setActivePage('video')}
          />
        )}

        {activePage === 'blueprint' && (
          <BlueprintPage />
        )}

        {activePage === 'video' && (
          <VideoReconstructionPage />
        )}

        {activePage === 'evaluation' && (
          <EvaluationPage />
        )}
      </main>

      {/* Technical Footer */}
      <footer className="relative z-10 glass-panel border-t border-white/10 px-6 py-5 mt-12 text-xs text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="font-bold text-white font-mono tracking-wider">PLANE VUE</span>
            <span>•</span>
            <span className="text-[11px] text-slate-400">"See the space. Reconstruct the unseen."</span>
          </div>

          <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
            <span>Mode A: Functional BIM Extraction</span>
            <span>•</span>
            <span>Mode B: Room Video 3D Active</span>
            <span>•</span>
            <span>Local Offline-First</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
