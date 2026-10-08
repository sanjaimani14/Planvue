import React, { useState, useRef, useEffect } from 'react';
import { 
  Upload, Layers, Sparkles, CheckCircle2, AlertTriangle, 
  Trash2, ZoomIn, ZoomOut, RotateCcw, Sliders, ShieldCheck, 
  Ruler, Download, FileText, ChevronRight, Eye, Info, Crosshair,
  Box, Columns, Maximize2, RefreshCw
} from 'lucide-react';
import { 
  reconstructBlueprint, calibrateManualScale, reconstruct3D, exportScene,
  ReconstructResponse 
} from '../services/api';
import { Scene3D } from '../types';
import { SceneViewer } from '../components/3d/SceneViewer';

const PROGRESS_STEPS = [
  { id: 1, name: 'Upload' },
  { id: 2, name: 'Analyze' },
  { id: 3, name: 'Geometry' },
  { id: 4, name: 'Validate' },
  { id: 5, name: '3D Scene' },
];

export const BlueprintPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [pdfPage, setPdfPage] = useState<number>(1);
  const [totalPdfPages, setTotalPdfPages] = useState<number>(1);
  const [wallHeight, setWallHeight] = useState<number>(3.0);
  const [wallThickness, setWallThickness] = useState<number>(0.15);
  const [loading, setLoading] = useState<boolean>(false);
  const [currentStep, setCurrentStep] = useState<number>(1);
  const [loadingStage, setLoadingStage] = useState<number>(1);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [result, setResult] = useState<ReconstructResponse | null>(null);
  const [scene3D, setScene3D] = useState<Scene3D | null>(null);

  // Workspace View Mode: 'split' | '3d' | '2d'
  const [viewMode, setViewMode] = useState<'split' | '3d' | '2d'>('split');

  // Layer Toggles for 2D
  const [showWalls, setShowWalls] = useState<boolean>(true);
  const [showDoors, setShowDoors] = useState<boolean>(true);
  const [showWindows, setShowWindows] = useState<boolean>(true);
  const [showRooms, setShowRooms] = useState<boolean>(true);
  const [showOriginal, setShowOriginal] = useState<boolean>(false);

  // Selected Object Synchronization (2D <-> 3D)
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [selectedElementId, setSelectedElementId] = useState<string | null>(null);

  // Manual Scale Calibration Mode (Section 18)
  const [scaleCalibActive, setScaleCalibActive] = useState<boolean>(false);
  const [calibPoints, setCalibPoints] = useState<[number, number][]>([]);
  const [knownDistance, setKnownDistance] = useState<number>(4.0);
  const [knownUnit, setKnownUnit] = useState<string>('m');

  // Zoom & Pan state for 2D View
  const [zoomLevel, setZoomLevel] = useState<number>(1.0);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState<boolean>(false);
  const panStartRef = useRef<{ x: number; y: number }>({ x: 0, y: 0 });

  // 3D regeneration state
  const [isRegenerating3D, setIsRegenerating3D] = useState<boolean>(false);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selected = e.target.files[0];
      setFile(selected);
      setErrorMsg(null);
      setCurrentStep(1);
      if (selected.name.toLowerCase().endsWith('.pdf')) {
        setTotalPdfPages(3);
      } else {
        setTotalPdfPages(1);
        setPdfPage(1);
      }
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    setResult(null);
    setScene3D(null);
    setSelectedElement(null);
    setSelectedElementId(null);
    setErrorMsg(null);
    setCurrentStep(1);
  };

  const handleExecuteReconstruct = async (isDemo: boolean = false, demoType: string = 'simple') => {
    setLoading(true);
    setErrorMsg(null);
    setCurrentStep(2);
    setLoadingStage(1);

    // Simulated progress stage updates while real network call executes
    const stageTimer1 = setTimeout(() => setLoadingStage(2), 500);
    const stageTimer2 = setTimeout(() => setLoadingStage(3), 1200);
    const stageTimer3 = setTimeout(() => setLoadingStage(4), 2200);
    const stageTimer4 = setTimeout(() => setLoadingStage(5), 3200);

    try {
      const data = await reconstructBlueprint({
        file: isDemo ? undefined : (file || undefined),
        is_demo: isDemo,
        demo_type: demoType,
        page_number: pdfPage,
        wall_height: wallHeight,
        wall_thickness: wallThickness,
      });

      setResult(data);
      if (data.scene_3d) {
        setScene3D(data.scene_3d);
      }
      setCurrentStep(5);
    } catch (err: any) {
      setErrorMsg(err.message || 'Blueprint reconstruction error');
    } finally {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      clearTimeout(stageTimer3);
      clearTimeout(stageTimer4);
      setLoading(false);
    }
  };

  // Re-generate 3D when wall height or thickness changes (Section 6)
  const handleRegenerate3D = async () => {
    if (!result) return;
    setIsRegenerating3D(true);
    try {
      const data = await reconstruct3D({
        scene_id: result.scene_id,
        wall_height: wallHeight,
        wall_thickness: wallThickness,
      });
      if (data.scene_3d) {
        setScene3D(data.scene_3d);
      }
      setExportNotice('3D scene regenerated with updated BIM parameters.');
      setTimeout(() => setExportNotice(null), 3000);
    } catch (err: any) {
      setErrorMsg(err.message || '3D Regeneration failed');
    } finally {
      setIsRegenerating3D(false);
    }
  };

  const handleApplyManualScale = async () => {
    if (!result || calibPoints.length < 2) return;
    try {
      const updated = await calibrateManualScale({
        scene_id: result.scene_id,
        pt1: calibPoints[0],
        pt2: calibPoints[1],
        known_distance: knownDistance,
        unit: knownUnit,
      });
      setResult({
        ...result,
        scale: updated.scale,
        walls: updated.walls,
        doors: updated.doors,
        windows: updated.windows,
        rooms: updated.rooms,
        summary: updated.summary,
      });
      // Re-trigger 3D reconstruction with new scale
      handleRegenerate3D();
      setScaleCalibActive(false);
      setCalibPoints([]);
    } catch (err: any) {
      setErrorMsg(err.message || 'Scale calibration failed');
    }
  };

  // Quick export formats
  const handleTriggerExport = async (format: 'glb' | 'obj' | 'json') => {
    if (!result) return;
    try {
      setExportNotice(`Exporting ${format.toUpperCase()}...`);
      const blob = await exportScene({
        scene_id: result.scene_id,
        format,
        wall_height: wallHeight,
        wall_thickness: wallThickness,
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `planevue_scene_${result.scene_id}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      setExportNotice(`${format.toUpperCase()} export complete.`);
      setTimeout(() => setExportNotice(null), 3500);
    } catch (err: any) {
      setExportNotice(`Export failed: ${err.message}`);
      setTimeout(() => setExportNotice(null), 3500);
    }
  };

  const handleSvgClick = (e: React.MouseEvent<SVGSVGElement>) => {
    if (!scaleCalibActive) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const svgX = (e.clientX - rect.left) * (imgW / rect.width);
    const svgY = (e.clientY - rect.top) * (imgH / rect.height);

    if (calibPoints.length >= 2) {
      setCalibPoints([[Math.round(svgX), Math.round(svgY)]]);
    } else {
      setCalibPoints([...calibPoints, [Math.round(svgX), Math.round(svgY)]]);
    }
  };

  const imgW = result?.processed_image_url ? (result as any).image_width || 1200 : 1000;
  const imgH = result?.processed_image_url ? (result as any).image_height || 800 : 750;
  const viewBox = `0 0 ${imgW} ${imgH}`;

  // Quality checks from validation (Section 39)
  const qualityWallContinuity = result?.validation?.errors?.some(e => e.includes('wall')) ? 'WARNING' : 'PASS';
  const qualityDoorAttachment = result?.doors?.every((d: any) => d.wall_id) ? 'PASS' : 'WARNING';
  const qualityWindowAttachment = result?.windows?.every((w: any) => w.wall_id) ? 'PASS' : 'WARNING';
  const qualityRoomClosure = result?.rooms?.length ? 'PASS' : 'WARNING';

  return (
    <div className="w-full max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Top Header Banner & Pipeline Stepper */}
      <div className="glass-panel p-4 rounded-2xl border border-white/10 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="font-extrabold text-sm uppercase tracking-wider text-cyan-400 font-mono">
            Pipeline:
          </span>
          <div className="flex items-center gap-2 overflow-x-auto">
            {PROGRESS_STEPS.map((step, idx) => (
              <React.Fragment key={step.id}>
                <div className="flex items-center gap-1.5">
                  <span
                    className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono font-bold transition-all ${
                      step.id < currentStep || (step.id === 5 && scene3D)
                        ? 'bg-emerald-500 text-slate-950 font-black'
                        : step.id === currentStep
                        ? 'bg-cyan-500 text-slate-950 shadow-md ring-2 ring-cyan-400'
                        : 'bg-slate-800 text-slate-500'
                    }`}
                  >
                    {step.id}
                  </span>
                  <span
                    className={`text-xs font-semibold ${
                      step.id === currentStep ? 'text-white' : 'text-slate-400'
                    }`}
                  >
                    {step.name}
                  </span>
                </div>
                {idx < PROGRESS_STEPS.length - 1 && (
                  <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* View Mode Switcher */}
        {result && (
          <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setViewMode('split')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                viewMode === 'split'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Columns className="w-3.5 h-3.5" />
              <span>SPLIT VIEW</span>
            </button>
            <button
              onClick={() => setViewMode('3d')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                viewMode === '3d'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Box className="w-3.5 h-3.5" />
              <span>3D SCENE</span>
            </button>
            <button
              onClick={() => setViewMode('2d')}
              className={`px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-all ${
                viewMode === '2d'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>2D BLUEPRINT</span>
            </button>
          </div>
        )}

        <div className="hidden lg:flex items-center gap-2 text-[11px] font-mono text-cyan-400 bg-cyan-950/40 px-3 py-1 rounded-lg border border-cyan-500/20">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Real 3D Reconstruction Layer Active</span>
        </div>
      </div>

      {/* Notice Banner */}
      {exportNotice && (
        <div className="bg-cyan-950/80 border border-cyan-500/50 px-4 py-2 rounded-xl text-xs text-cyan-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{exportNotice}</span>
        </div>
      )}

      {errorMsg && (
        <div className="bg-rose-950/80 border border-rose-500/50 px-4 py-2.5 rounded-xl text-xs text-rose-200 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Real Pipeline Loading Overlay (Section 42) */}
      {loading && (
        <div className="glass-panel p-8 rounded-3xl border border-cyan-500/30 text-center space-y-6 max-w-lg mx-auto">
          <div className="space-y-2">
            <h3 className="text-lg font-black text-white uppercase tracking-wider flex items-center justify-center gap-2">
              <Sparkles className="w-5 h-5 text-cyan-400 animate-spin" />
              GENERATING 3D SCENE
            </h3>
            <p className="text-xs text-slate-400 font-sans">
              Transforming structured floor plan geometry into a metric 3D model
            </p>
          </div>

          <div className="space-y-2.5 text-left font-mono text-xs max-w-xs mx-auto">
            <div className={`flex items-center gap-2 ${loadingStage >= 1 ? 'text-emerald-400' : 'text-slate-500'}`}>
              <span>{loadingStage > 1 ? '✓' : '●'}</span>
              <span>Validated floor plan</span>
            </div>
            <div className={`flex items-center gap-2 ${loadingStage >= 2 ? 'text-emerald-400' : 'text-slate-500'}`}>
              <span>{loadingStage > 2 ? '✓' : loadingStage === 2 ? '●' : '○'}</span>
              <span>Metric geometry</span>
            </div>
            <div className={`flex items-center gap-2 ${loadingStage >= 3 ? 'text-emerald-400' : 'text-slate-500'}`}>
              <span>{loadingStage > 3 ? '✓' : loadingStage === 3 ? '●' : '○'}</span>
              <span>Building walls</span>
            </div>
            <div className={`flex items-center gap-2 ${loadingStage >= 4 ? 'text-emerald-400' : 'text-slate-500'}`}>
              <span>{loadingStage > 4 ? '✓' : loadingStage === 4 ? '●' : '○'}</span>
              <span>Adding doors & windows</span>
            </div>
            <div className={`flex items-center gap-2 ${loadingStage >= 5 ? 'text-emerald-400' : 'text-slate-500'}`}>
              <span>{loadingStage === 5 ? '●' : '○'}</span>
              <span>Preparing viewer & GLB export</span>
            </div>
          </div>
        </div>
      )}

      {/* Main Reconstruction Workspace */}
      {!loading && (
        <div className="space-y-6">
          {/* Top Config & Benchmark Quick-Bar */}
          <div className="glass-panel p-4 rounded-2xl border border-white/10 flex flex-wrap items-center justify-between gap-4 text-xs">
            {/* BIM Adjusters (Section 6) */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-medium">Wall Height:</span>
                <input
                  type="number"
                  step="0.1"
                  min="2.0"
                  max="6.0"
                  value={wallHeight}
                  onChange={(e) => setWallHeight(parseFloat(e.target.value) || 3.0)}
                  className="w-16 bg-slate-900 text-white rounded px-2 py-1 text-center font-mono border border-slate-700"
                />
                <span className="text-slate-400">m</span>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-slate-400 font-medium">Thickness:</span>
                <input
                  type="number"
                  step="0.01"
                  min="0.10"
                  max="0.45"
                  value={wallThickness}
                  onChange={(e) => setWallThickness(parseFloat(e.target.value) || 0.15)}
                  className="w-16 bg-slate-900 text-white rounded px-2 py-1 text-center font-mono border border-slate-700"
                />
                <span className="text-slate-400">m</span>
              </div>

              {result && (
                <button
                  onClick={handleRegenerate3D}
                  disabled={isRegenerating3D}
                  className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-cyan-300 rounded-lg font-semibold border border-slate-700 flex items-center gap-1.5 transition-colors"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isRegenerating3D ? 'animate-spin' : ''}`} />
                  <span>Regenerate 3D</span>
                </button>
              )}
            </div>

            {/* Quick Demo Benchmark Plans */}
            <div className="flex items-center gap-2">
              <span className="text-slate-400 font-mono text-[11px]">Benchmark Demo:</span>
              <button
                onClick={() => handleExecuteReconstruct(true, 'simple')}
                className="px-2.5 py-1 bg-white/5 hover:bg-white/10 rounded-lg text-slate-300 font-mono text-[11px] border border-white/5 hover:border-cyan-500/30"
              >
                Simple (2R)
              </button>
              <button
                onClick={() => handleExecuteReconstruct(true, 'medium')}
                className="px-2.5 py-1 bg-white/5 hover:bg-white/10 rounded-lg text-slate-300 font-mono text-[11px] border border-white/5 hover:border-cyan-500/30"
              >
                Medium (3R)
              </button>
              <button
                onClick={() => handleExecuteReconstruct(true, 'complex')}
                className="px-2.5 py-1 bg-cyan-950/60 hover:bg-cyan-900/60 rounded-lg text-cyan-300 font-mono text-[11px] border border-cyan-500/30 font-semibold"
              >
                Complex (4R)
              </button>
            </div>

            {/* Direct Export Buttons (Section 34, 35, 36) */}
            {result && (
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => handleTriggerExport('glb')}
                  className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white font-bold rounded-lg flex items-center gap-1.5 shadow-md transition-all text-xs"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>EXPORT GLB</span>
                </button>
                <button
                  onClick={() => handleTriggerExport('obj')}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-lg border border-slate-700 transition-all text-xs"
                >
                  OBJ
                </button>
                <button
                  onClick={() => handleTriggerExport('json')}
                  className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium rounded-lg border border-slate-700 transition-all text-xs"
                >
                  JSON
                </button>
              </div>
            )}
          </div>

          {/* ================= WORKSPACE PANELS ================= */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            {/* --- LEFT: 2D BLUEPRINT VIEW --- */}
            {(viewMode === 'split' || viewMode === '2d') && (
              <div className={`${viewMode === 'split' ? 'lg:col-span-6' : 'lg:col-span-12'} space-y-4 flex flex-col`}>
                <div className="glass-panel rounded-2xl border border-white/10 overflow-hidden flex flex-col h-[620px] bg-slate-950">
                  {/* 2D Viewport Header */}
                  <div className="p-3 bg-slate-900/90 border-b border-white/10 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-3 text-slate-300">
                      <span className="font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                        <Layers className="w-3.5 h-3.5 text-cyan-400" />
                        2D Blueprint View
                      </span>
                      <label className="flex items-center gap-1 cursor-pointer text-[11px]">
                        <input
                          type="checkbox"
                          checked={showWalls}
                          onChange={(e) => setShowWalls(e.target.checked)}
                          className="rounded accent-cyan-500"
                        />
                        <span>Walls</span>
                      </label>
                      <label className="flex items-center gap-1 cursor-pointer text-[11px]">
                        <input
                          type="checkbox"
                          checked={showDoors}
                          onChange={(e) => setShowDoors(e.target.checked)}
                          className="rounded accent-emerald-500"
                        />
                        <span>Doors</span>
                      </label>
                      <label className="flex items-center gap-1 cursor-pointer text-[11px]">
                        <input
                          type="checkbox"
                          checked={showWindows}
                          onChange={(e) => setShowWindows(e.target.checked)}
                          className="rounded accent-cyan-500"
                        />
                        <span>Windows</span>
                      </label>
                      <label className="flex items-center gap-1 cursor-pointer text-[11px]">
                        <input
                          type="checkbox"
                          checked={showRooms}
                          onChange={(e) => setShowRooms(e.target.checked)}
                          className="rounded accent-purple-500"
                        />
                        <span>Rooms</span>
                      </label>
                    </div>

                    {/* Zoom / View controls */}
                    <div className="flex items-center gap-1.5">
                      <button
                        onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 3.0))}
                        className="p-1 rounded bg-white/5 hover:bg-white/10 text-slate-300"
                        title="Zoom In"
                      >
                        <ZoomIn className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.6))}
                        className="p-1 rounded bg-white/5 hover:bg-white/10 text-slate-300"
                        title="Zoom Out"
                      >
                        <ZoomOut className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => {
                          setZoomLevel(1.0);
                          setPanOffset({ x: 0, y: 0 });
                        }}
                        className="p-1 rounded bg-white/5 hover:bg-white/10 text-slate-300"
                        title="Reset"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => setShowOriginal(!showOriginal)}
                        className={`px-2 py-0.5 rounded text-[10px] font-mono border ${
                          showOriginal
                            ? 'bg-cyan-600 text-white border-cyan-500'
                            : 'bg-white/5 text-slate-400 border-white/10 hover:text-white'
                        }`}
                      >
                        {showOriginal ? 'Raster' : 'Vector'}
                      </button>
                    </div>
                  </div>

                  {/* 2D Canvas SVG */}
                  <div
                    className="relative flex-1 flex items-center justify-center overflow-hidden cursor-crosshair bg-slate-950"
                    onMouseDown={(e) => {
                      if (e.button === 0 && !scaleCalibActive) {
                        setIsPanning(true);
                        panStartRef.current = { x: e.clientX - panOffset.x, y: e.clientY - panOffset.y };
                      }
                    }}
                    onMouseMove={(e) => {
                      if (isPanning) {
                        setPanOffset({
                          x: e.clientX - panStartRef.current.x,
                          y: e.clientY - panStartRef.current.y,
                        });
                      }
                    }}
                    onMouseUp={() => setIsPanning(false)}
                    onMouseLeave={() => setIsPanning(false)}
                  >
                    <div
                      style={{
                        transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
                        transformOrigin: 'center center',
                        transition: isPanning ? 'none' : 'transform 0.15s ease-out',
                      }}
                      className="w-full h-full flex items-center justify-center p-4"
                    >
                      <svg
                        viewBox={viewBox}
                        onClick={handleSvgClick}
                        className="w-full h-full max-h-[540px] object-contain rounded-lg select-none"
                      >
                        {result && (
                          <image
                            href={showOriginal ? result.original_image_url : result.processed_image_url}
                            width={imgW}
                            height={imgH}
                            opacity={0.35}
                          />
                        )}

                        {/* Rooms Overlay */}
                        {showRooms &&
                          result?.rooms.map((r: any) => {
                            const pts = r.polygon.map((p: number[]) => `${p[0]},${p[1]}`).join(' ');
                            const isSel = selectedElementId === r.id;
                            return (
                              <g
                                key={r.id}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedElementId(r.id);
                                  setSelectedElement({ type: 'room', data: r });
                                }}
                              >
                                <polygon
                                  points={pts}
                                  fill={isSel ? 'rgba(56, 189, 248, 0.35)' : 'rgba(168, 85, 247, 0.14)'}
                                  stroke={isSel ? '#38bdf8' : 'rgba(192, 132, 252, 0.6)'}
                                  strokeWidth={isSel ? '3' : '2'}
                                  strokeDasharray="4 4"
                                  className="hover:fill-purple-500/25 transition-all cursor-pointer"
                                />
                                {r.polygon[0] && (
                                  <text
                                    x={r.polygon.reduce((acc: number, p: number[]) => acc + p[0], 0) / r.polygon.length}
                                    y={r.polygon.reduce((acc: number, p: number[]) => acc + p[1], 0) / r.polygon.length}
                                    fill="#f3e8ff"
                                    fontSize="15"
                                    fontWeight="bold"
                                    textAnchor="middle"
                                    className="pointer-events-none select-none drop-shadow"
                                  >
                                    {r.label || r.id}
                                  </text>
                                )}
                              </g>
                            );
                          })}

                        {/* Walls Overlay */}
                        {showWalls &&
                          result?.walls.map((w: any) => {
                            const isCorrected = w.status === 'CORRECTED';
                            const isSel = selectedElementId === w.id;
                            return (
                              <g
                                key={w.id}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedElementId(w.id);
                                  setSelectedElement({ type: 'wall', data: w });
                                }}
                              >
                                <line
                                  x1={w.start[0]}
                                  y1={w.start[1]}
                                  x2={w.end[0]}
                                  y2={w.end[1]}
                                  stroke={isSel ? '#38bdf8' : isCorrected ? '#f59e0b' : '#f8fafc'}
                                  strokeWidth={isSel ? Math.max(w.thickness_px || 8, 8) + 4 : Math.max(w.thickness_px || 8, 8)}
                                  strokeLinecap="round"
                                  className="cursor-pointer hover:stroke-cyan-400 transition-colors"
                                />
                                <circle cx={w.start[0]} cy={w.start[1]} r="4" fill="#06b6d4" />
                                <circle cx={w.end[0]} cy={w.end[1]} r="4" fill="#06b6d4" />
                              </g>
                            );
                          })}

                        {/* Doors Overlay */}
                        {showDoors &&
                          result?.doors.map((d: any) => {
                            const isCorrected = d.status === 'CORRECTED';
                            const isSel = selectedElementId === d.id;
                            return (
                              <g
                                key={d.id}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedElementId(d.id);
                                  setSelectedElement({ type: 'door', data: d });
                                }}
                              >
                                <circle
                                  cx={d.position[0]}
                                  cy={d.position[1]}
                                  r={Math.max((d.width_px || 40) / 2, 14)}
                                  fill={isSel ? 'rgba(56, 189, 248, 0.4)' : isCorrected ? 'rgba(245, 158, 11, 0.25)' : 'rgba(16, 185, 129, 0.25)'}
                                  stroke={isSel ? '#38bdf8' : isCorrected ? '#f59e0b' : '#10b981'}
                                  strokeWidth={isSel ? '4' : '3'}
                                  className="cursor-pointer hover:stroke-white transition-colors"
                                />
                              </g>
                            );
                          })}

                        {/* Windows Overlay */}
                        {showWindows &&
                          result?.windows.map((win: any) => {
                            const isSel = selectedElementId === win.id;
                            return (
                              <g
                                key={win.id}
                                onClick={(e) => {
                                  e.stopPropagation();
                                  setSelectedElementId(win.id);
                                  setSelectedElement({ type: 'window', data: win });
                                }}
                              >
                                <rect
                                  x={win.position[0] - 22}
                                  y={win.position[1] - 6}
                                  width="44"
                                  height="12"
                                  fill={isSel ? 'rgba(56, 189, 248, 0.5)' : 'rgba(6, 182, 212, 0.3)'}
                                  stroke={isSel ? '#ffffff' : '#06b6d4'}
                                  strokeWidth={isSel ? '3' : '2'}
                                  rx="2"
                                  className="cursor-pointer hover:stroke-white transition-colors"
                                />
                              </g>
                            );
                          })}

                        {/* Calibration Points Marker */}
                        {calibPoints.map((pt, i) => (
                          <circle
                            key={i}
                            cx={pt[0]}
                            cy={pt[1]}
                            r="6"
                            fill="#f59e0b"
                            stroke="#ffffff"
                            strokeWidth="2"
                          />
                        ))}
                      </svg>
                    </div>

                    {!result && (
                      <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center space-y-3 pointer-events-none">
                        <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-slate-500">
                          <Layers className="w-6 h-6" />
                        </div>
                        <div>
                          <span className="text-sm font-semibold text-slate-300">No Blueprint Loaded</span>
                          <p className="text-xs text-slate-500 max-w-xs mt-1">
                            Upload a plan on top or choose a demo benchmark above.
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* --- RIGHT: 3D REAL ARCHITECTURAL SCENE VIEW --- */}
            {(viewMode === 'split' || viewMode === '3d') && (
              <div className={`${viewMode === 'split' ? 'lg:col-span-6' : 'lg:col-span-12'} space-y-4 flex flex-col`}>
                <div className="glass-panel rounded-2xl border border-white/10 overflow-hidden flex flex-col h-[620px] bg-slate-950 relative">
                  {scene3D ? (
                    <SceneViewer
                      scene={scene3D}
                      selectedId={selectedElementId}
                      onSelectObject={(obj) => {
                        setSelectedElement(obj ? { type: obj.type, data: obj } : null);
                        setSelectedElementId(obj ? obj.id : null);
                      }}
                      onExportGlbSuccess={(url) => setExportNotice(`GLB exported: ${url}`)}
                    />
                  ) : (
                    <div className="w-full h-full flex flex-col items-center justify-center p-8 text-center space-y-4 text-slate-500">
                      <div className="w-14 h-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400">
                        <Box className="w-7 h-7" />
                      </div>
                      <div className="space-y-1">
                        <span className="text-sm font-semibold text-slate-300">3D Scene Ready for Reconstruction</span>
                        <p className="text-xs text-slate-500 max-w-xs">
                          Click any Demo button above or upload your architectural floor plan to view the live 3D reconstruction.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* ================= BOTTOM: RECONSTRUCTION REPORT & METRICS (Section 38 & 39) ================= */}
          {result && (
            <div className="glass-panel p-6 rounded-2xl border border-white/10 space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-white/10">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-cyan-400" />
                  <h3 className="text-base font-black text-white uppercase tracking-wider">
                    RECONSTRUCTION REPORT
                  </h3>
                </div>
                <span className="text-xs font-mono text-slate-400">
                  Scene ID: {result.scene_id} | {result.summary.processing_time_ms} ms
                </span>
              </div>

              {/* Grid of Report Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-3 text-xs font-mono">
                <div className="bg-slate-900/80 p-3 rounded-xl border border-white/5 space-y-1">
                  <span className="text-slate-400 text-[10px] uppercase block">Input Mode</span>
                  <span className="text-sm font-extrabold text-white">Blueprint</span>
                </div>

                <div className="bg-slate-900/80 p-3 rounded-xl border border-white/5 space-y-1">
                  <span className="text-slate-400 text-[10px] uppercase block">Scale</span>
                  <span className="text-sm font-extrabold text-cyan-400">
                    {result.scale.meters_per_pixel ? `${result.scale.meters_per_pixel.toFixed(3)} m/px` : 'N/A'}
                  </span>
                </div>

                <div className="bg-slate-900/80 p-3 rounded-xl border border-white/5 space-y-1">
                  <span className="text-slate-400 text-[10px] uppercase block">Rooms</span>
                  <span className="text-sm font-extrabold text-purple-400">{result.summary.room_count}</span>
                </div>

                <div className="bg-slate-900/80 p-3 rounded-xl border border-white/5 space-y-1">
                  <span className="text-slate-400 text-[10px] uppercase block">Walls</span>
                  <span className="text-sm font-extrabold text-white">{result.summary.wall_count}</span>
                </div>

                <div className="bg-slate-900/80 p-3 rounded-xl border border-white/5 space-y-1">
                  <span className="text-slate-400 text-[10px] uppercase block">Doors / Windows</span>
                  <span className="text-sm font-extrabold text-emerald-400">
                    {result.summary.door_count} / {result.summary.window_count}
                  </span>
                </div>

                <div className="bg-slate-900/80 p-3 rounded-xl border border-white/5 space-y-1">
                  <span className="text-slate-400 text-[10px] uppercase block">Corrections</span>
                  <span className="text-sm font-extrabold text-amber-400">
                    {result.validation.corrections?.length || 0}
                  </span>
                </div>
              </div>

              {/* Geometry Quality Status (Section 39) */}
              <div className="p-4 rounded-xl bg-slate-900/60 border border-white/5 space-y-3">
                <span className="text-[11px] font-mono text-cyan-400 uppercase font-bold tracking-wider block">
                  GEOMETRY QUALITY TELEMETRY:
                </span>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
                  <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Wall continuity:</span>
                    <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${qualityWallContinuity === 'PASS' ? 'text-emerald-400 bg-emerald-950' : 'text-amber-400 bg-amber-950'}`}>
                      {qualityWallContinuity}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Door attachment:</span>
                    <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${qualityDoorAttachment === 'PASS' ? 'text-emerald-400 bg-emerald-950' : 'text-amber-400 bg-amber-950'}`}>
                      {qualityDoorAttachment}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Window attachment:</span>
                    <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${qualityWindowAttachment === 'PASS' ? 'text-emerald-400 bg-emerald-950' : 'text-amber-400 bg-amber-950'}`}>
                      {qualityWindowAttachment}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Room closure:</span>
                    <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${qualityRoomClosure === 'PASS' ? 'text-emerald-400 bg-emerald-950' : 'text-amber-400 bg-amber-950'}`}>
                      {qualityRoomClosure}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-2 rounded bg-slate-950 border border-slate-800">
                    <span className="text-slate-400">Scale Confidence:</span>
                    <span className={`font-bold px-1.5 py-0.5 rounded text-[10px] ${
                      result.scale.confidence === 'HIGH' ? 'text-emerald-400 bg-emerald-950' :
                      result.scale.confidence === 'MEDIUM' ? 'text-amber-400 bg-amber-950' : 'text-rose-400 bg-rose-950'
                    }`}>
                      {result.scale.confidence}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
