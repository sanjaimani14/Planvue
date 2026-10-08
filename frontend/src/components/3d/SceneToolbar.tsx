import React, { useState } from 'react';
import { 
  Rotate3d, Compass, Maximize2, Grid, Tag, Ruler, 
  Eye, Box, Download, Camera, Keyboard, Sparkles, HelpCircle,
  Armchair, Square, DoorOpen, LayoutGrid
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
  showWalls?: boolean;
  onToggleWalls?: () => void;
  showDoors?: boolean;
  onToggleDoors?: () => void;
  showWindows?: boolean;
  onToggleWindows?: () => void;
  showFurniture?: boolean;
  onToggleFurniture?: () => void;
  onToggleFullscreen?: () => void;
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
  showWalls = true,
  onToggleWalls,
  showDoors = true,
  onToggleDoors,
  showWindows = true,
  onToggleWindows,
  showFurniture = true,
  onToggleFurniture,
  onToggleFullscreen,
}) => {
  const [showShortcuts, setShowShortcuts] = useState<boolean>(false);

  return (
    <div className="bg-slate-900/95 backdrop-blur-md border border-slate-800 p-1.5 rounded-xl shadow-2xl flex flex-wrap items-center gap-1.5 text-xs max-w-full">
      {/* 1. Camera View Presets */}
      <div className="flex items-center gap-0.5 bg-slate-950/80 p-0.5 rounded-lg border border-slate-800">
        {(['ORBIT', 'TOP', 'FRONT', 'WALK'] as CameraViewMode[]).map((mode) => (
          <button
            key={mode}
            onClick={() => onSelectCameraMode(mode)}
            className={`px-2 py-0.5 rounded text-[10px] font-semibold tracking-wider transition-all ${
              cameraMode === mode
                ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/80'
            }`}
            title={mode === 'ORBIT' ? 'Perspective View' : `${mode} View`}
          >
            {mode === 'ORBIT' ? 'PERSPECTIVE' : mode}
          </button>
        ))}
      </div>

      <div className="h-4 w-px bg-slate-800 hidden sm:block" />

      {/* 2. Scene Layer Toggles */}
      <div className="flex items-center gap-1">
        {/* ROOM LABELS */}
        <button
          onClick={onToggleLabels}
          className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
            showLabels
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle Room Labels"
        >
          <Tag className="w-3 h-3" />
          <span>Labels</span>
        </button>

        {/* WALLS */}
        {onToggleWalls && (
          <button
            onClick={onToggleWalls}
            className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
              showWalls
                ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
                : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
            }`}
            title="Toggle Walls"
          >
            <Square className="w-3 h-3" />
            <span>Walls</span>
          </button>
        )}

        {/* DOORS */}
        {onToggleDoors && (
          <button
            onClick={onToggleDoors}
            className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
              showDoors
                ? 'bg-emerald-950/80 text-emerald-300 border-emerald-500/50'
                : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
            }`}
            title="Toggle Doors"
          >
            <DoorOpen className="w-3 h-3" />
            <span>Doors</span>
          </button>
        )}

        {/* WINDOWS */}
        {onToggleWindows && (
          <button
            onClick={onToggleWindows}
            className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
              showWindows
                ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
                : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
            }`}
            title="Toggle Windows"
          >
            <LayoutGrid className="w-3 h-3" />
            <span>Windows</span>
          </button>
        )}

        {/* FURNITURE */}
        {onToggleFurniture && (
          <button
            onClick={onToggleFurniture}
            className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
              showFurniture
                ? 'bg-indigo-950/80 text-indigo-300 border-indigo-500/50'
                : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
            }`}
            title="Toggle AI-Inferred Furniture"
          >
            <Armchair className="w-3 h-3" />
            <span>Furniture</span>
          </button>
        )}

        {/* DIMENSIONS */}
        <button
          onClick={onToggleDimensions}
          className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
            showDimensions
              ? 'bg-cyan-950/80 text-cyan-300 border-cyan-500/50'
              : 'bg-slate-850 text-slate-400 border-slate-800 hover:text-slate-200 hover:bg-slate-800'
          }`}
          title="Toggle Wall Dimension Helpers"
        >
          <Ruler className="w-3 h-3" />
          <span>Dimensions</span>
        </button>

        {/* GRID */}
        <button
          onClick={onToggleGrid}
          className={`px-2 py-1 rounded-md text-[10px] font-medium border flex items-center gap-1 transition-all ${
            showGrid
              ? 'bg-slate-800 text-slate-300 border-slate-700'
              : 'bg-slate-850 text-slate-500 border-slate-800 hover:text-slate-300'
          }`}
          title="Toggle 1m Metric Grid (G)"
        >
          <Grid className="w-3 h-3" />
          <span>Grid</span>
        </button>
      </div>

      <div className="h-4 w-px bg-slate-800 hidden sm:block" />

      {/* 3. Actions: RESET | FULLSCREEN | EXPORT GLB */}
      <div className="flex items-center gap-1.5 ml-auto">
        <button
          onClick={onResetCamera}
          className="px-2 py-1 rounded-md text-[10px] font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 transition-all"
          title="Reset View to Bounds (R)"
        >
          RESET
        </button>

        {onToggleFullscreen && (
          <button
            onClick={onToggleFullscreen}
            className="p-1 rounded-md text-slate-400 hover:text-white hover:bg-slate-800 transition-colors border border-slate-800"
            title="Toggle Fullscreen"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        )}

        <button
          onClick={onExportGlb}
          disabled={isExportingGlb}
          className="px-2.5 py-1 rounded-md text-[10px] font-bold bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-800 text-white shadow-md transition-all flex items-center gap-1"
          title="Export GLB 3D Model"
        >
          <Download className="w-3 h-3" />
          <span>{isExportingGlb ? '...' : 'GLB'}</span>
        </button>

        {/* Shortcuts popover toggle */}
        <button
          onClick={() => setShowShortcuts(!showShortcuts)}
          className="p-1 rounded-md text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-colors"
          title="View Keyboard Shortcuts"
        >
          <Keyboard className="w-3.5 h-3.5" />
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
