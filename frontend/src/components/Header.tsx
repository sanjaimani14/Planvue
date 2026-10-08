import React from 'react';
import { Box, Layers, BarChart2, Info, Compass, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  currentTab: 'home' | 'reconstruction' | 'evaluation' | 'about';
  setTab: (tab: 'home' | 'reconstruction' | 'evaluation' | 'about') => void;
  activeMode?: 'A' | 'B';
}

export const Header: React.FC<HeaderProps> = ({ currentTab, setTab, activeMode }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/10 px-6 py-3.5 flex items-center justify-between backdrop-blur-xl">
      {/* Brand logo & tagline */}
      <div 
        className="flex items-center gap-3.5 cursor-pointer group"
        onClick={() => setTab('home')}
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
              v1.0
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium tracking-tight">AI Spatial Reconstruction Platform</p>
        </div>
      </div>

      {/* Navigation tabs */}
      <nav className="flex items-center gap-1.5 bg-slate-900/80 p-1 rounded-xl border border-white/5">
        <button
          onClick={() => setTab('home')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
            currentTab === 'home'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Compass className="w-3.5 h-3.5" />
          Home
        </button>

        <button
          onClick={() => setTab('reconstruction')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
            currentTab === 'reconstruction'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Reconstruction
          {activeMode && (
            <span className="px-1.5 py-0.2 rounded text-[9px] font-mono bg-white/20 text-white uppercase">
              Mode {activeMode}
            </span>
          )}
        </button>

        <button
          onClick={() => setTab('evaluation')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
            currentTab === 'evaluation'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <BarChart2 className="w-3.5 h-3.5" />
          Evaluation & Ablation
        </button>

        <button
          onClick={() => setTab('about')}
          className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
            currentTab === 'about'
              ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
              : 'text-slate-400 hover:text-white hover:bg-white/5'
          }`}
        >
          <Info className="w-3.5 h-3.5" />
          Research Contribution
        </button>
      </nav>

      {/* Honesty / Reliability Assurance Badge */}
      <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>Constraint-Aware Engine Active</span>
      </div>
    </header>
  );
};
