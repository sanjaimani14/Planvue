import React, { useState } from 'react';
import { 
  Rotate3d, Compass, Maximize2, Grid, Tag, Ruler, 
  Eye, Box, Download, Camera, Keyboard, Sparkles, HelpCircle 
} from 'lucide-react';
import { CameraViewMode } from './CameraControls';

interface SceneToolbarProps {
  cameraMode: CameraViewMode;
  onSelectCameraMode: (mode: CameraViewMode) => void;
  showGrid: boolean;
  onToggleGrid: () => void;
  showLabels: boolean;
  onToggleLabels: () => void;
  showDimensions: boolean;
  onToggleDimensions: () => void;
  displayMode: 'solid' | 'wireframe' | 'xray';
  onChangeDisplayMode: (mode: 'solid' | 'wireframe' | 'xray') => void;
  showConfidence: boolean;
  onToggleConfidence: () => void;
  measureActive: boolean;
  onToggleMeasure: () => void;
  onResetCamera: () => void;
  onExportGlb: () => void;
  onCaptureView: () => void;
  isExportingGlb?: boolean;
}

export const SceneToolbar: React.FC<SceneToolbarProps> = ({
  cameraMode,
  onSelectCameraMode,
  showGrid,
  onToggleGrid,
  showLabels,
  onToggleLabels,
  showDimensions,
  onToggleDimensions,
  displayMode,
  onChangeDisplayMode,
  showConfidence,
  onToggleConfidence,
  measureActive,
  onToggleMeasure,
  onResetCamera,
  onExportGlb,
  onCaptureView,
  isExportingGlb = false,
}) => {
  const [showShortcuts, setShowShortcuts] = useState<boolean>(false);

  return (
    <div className="bg-slate-900/95 backdrop-blur-md border border-slate-800 p-1.5 rounded-xl shadow-2xl flex flex-wrap items-center gap-1.5 text-xs max-w-full">
      {/* 1. Camera View Presets */}
      <div className="flex items-center gap-0.5 bg-slate-950/80 p-0.5 rounded-lg border border-slate-800">
        {(['ORBIT', 'TOP', 'FRONT', 'SIDE', 'WALK'] as CameraViewMode[]).map((mode) => (
          <button
            key={mode}
            onClick={() => onSelectCameraMode(mode)}
            className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider transition-all ${
              cameraMode === mode
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
            }`}
          >
            {mode}
          </button>
        ))}
      </div>

      <div className="h-4 w-px bg-slate-800 hidden sm:block" />

      {/* 2. Scene Feature Toggles */}
      <div className="flex items-center gap-1">
        {/* GRID */}
        <button
          onClick={onToggleGrid}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            showGrid
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle 1m Metric Grid (G)"
        >
          <Grid className="w-3.5 h-3.5" />
          <span>GRID</span>
        </button>

        {/* LABELS */}
        <button
          onClick={onToggleLabels}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            showLabels
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle Room Labels"
        >
          <Tag className="w-3.5 h-3.5" />
          <span>LABELS</span>
        </button>

        {/* DIMENSIONS */}
        <button
          onClick={onToggleDimensions}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            showDimensions
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle Wall Dimension Helpers"
        >
          <Ruler className="w-3.5 h-3.5" />
          <span>DIMENSIONS</span>
        </button>

        {/* X-RAY */}
        <button
          onClick={() => onChangeDisplayMode(displayMode === 'xray' ? 'solid' : 'xray')}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            displayMode === 'xray'
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle X-Ray Transparency (X)"
        >
          <Box className="w-3.5 h-3.5" />
          <span>X-RAY</span>
        </button>

        {/* WIREFRAME */}
        <button
          onClick={() => onChangeDisplayMode(displayMode === 'wireframe' ? 'solid' : 'wireframe')}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            displayMode === 'wireframe'
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle Wireframe Mode"
        >
          <span>WIREFRAME</span>
        </button>

        {/* CONFIDENCE */}
        <button
          onClick={onToggleConfidence}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            showConfidence
              ? 'bg-purple-950/80 text-purple-300 border-purple-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-purple-300 hover:bg-slate-800'
          }`}
          title="Toggle Confidence Inspector (C)"
        >
          <Eye className="w-3.5 h-3.5" />
          <span>CONFIDENCE</span>
        </button>

        {/* MEASURE */}
        <button
          onClick={onToggleMeasure}
          className={`px-2.5 py-1 rounded-md text-[11px] font-medium border flex items-center gap-1 transition-all ${
            measureActive
              ? 'bg-amber-950/80 text-amber-300 border-amber-500/60 ring-2 ring-amber-500/30'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-amber-300 hover:bg-slate-800'
          }`}
          title="Measure 3D Distance (M)"
        >
          <Ruler className="w-3.5 h-3.5" />
          <span>{measureActive ? 'EXIT MEASURE' : 'MEASURE'}</span>
        </button>
      </div>

      <div className="h-4 w-px bg-slate-800 hidden sm:block" />

      {/* 3. Actions: RESET | CAPTURE | EXPORT GLB */}
      <div className="flex items-center gap-1.5">
        <button
          onClick={onResetCamera}
          className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
          title="Reset View to Bounds (R)"
        >
          RESET
        </button>

        <button
          onClick={onCaptureView}
          className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all flex items-center gap-1"
          title="Capture Current 3D Canvas Image"
        >
          <Camera className="w-3.5 h-3.5" />
          <span>CAPTURE</span>
        </button>

        <button
          onClick={onExportGlb}
          disabled={isExportingGlb}
          className="px-3 py-1 rounded-md text-[11px] font-bold bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 text-white shadow-md transition-all flex items-center gap-1.5"
          title="Export GLB 3D Model"
        >
          <Download className="w-3.5 h-3.5" />
          <span>{isExportingGlb ? 'EXPORTING...' : 'EXPORT GLB'}</span>
        </button>

        {/* Shortcuts popover toggle */}
        <button
          onClick={() => setShowShortcuts(!showShortcuts)}
          className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          title="View Keyboard Shortcuts"
        >
          <Keyboard className="w-4 h-4" />
        </button>
      </div>

      {/* Keyboard Shortcuts Overlay Modal */}
      {showShortcuts && (
        <div className="absolute top-12 right-4 z-50 bg-slate-900 border border-slate-700 p-3 rounded-xl shadow-2xl w-64 text-slate-300">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800 font-semibold text-xs text-white">
            <span>Keyboard Shortcuts</span>
            <button
              onClick={() => setShowShortcuts(false)}
              className="text-slate-400 hover:text-white text-sm"
            >
              ×
            </button>
          </div>
          <div className="grid grid-cols-2 gap-y-1.5 gap-x-2 pt-2 text-[11px]">
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">R</kbd> Reset View</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">T</kbd> Top View</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">F</kbd> Front View</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">W</kbd> Walk Mode</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">G</kbd> Toggle Grid</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">X</kbd> Toggle X-Ray</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">C</kbd> Confidence</div>
            <div><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">M</kbd> Measure</div>
            <div className="col-span-2"><kbd className="px-1.5 py-0.5 bg-slate-800 rounded font-mono text-[10px] text-cyan-300">Esc</kbd> Exit Tool / Deselect</div>
          </div>
        </div>
      )}
    </div>
  );
};
