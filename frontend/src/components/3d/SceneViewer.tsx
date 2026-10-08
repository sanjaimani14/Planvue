import React, { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { Scene3D, Wall3D, Door3D, Window3D, Floor3D } from '../../types';
import { WallMesh } from './WallMesh';
import { DoorMesh } from './DoorMesh';
import { WindowMesh } from './WindowMesh';
import { FloorMesh } from './FloorMesh';
import { RoomLabel } from './RoomLabel';
import { GridSystem } from './GridSystem';
import { MeasurementTool } from './MeasurementTool';
import { CameraControls, CameraViewMode } from './CameraControls';
import { ConfidenceOverlay, ConfidenceFilterType } from './ConfidenceOverlay';
import { SceneToolbar } from './SceneToolbar';
import { exportScene } from '../../services/api';
import { Info, X, Layers, Box, CheckCircle2 } from 'lucide-react';

interface SceneViewerProps {
  scene: Scene3D;
  selectedId?: string | null;
  onSelectObject?: (obj: any | null) => void;
  onExportGlbSuccess?: (url: string) => void;
}

export const SceneViewer: React.FC<SceneViewerProps> = ({
  scene,
  selectedId: externalSelectedId,
  onSelectObject,
  onExportGlbSuccess,
}) => {
  // Viewer state
  const [cameraMode, setCameraMode] = useState<CameraViewMode>('ORBIT');
  const [resetTrigger, setResetTrigger] = useState<number>(0);
  const [showGrid, setShowGrid] = useState<boolean>(true);
  const [showLabels, setShowLabels] = useState<boolean>(true);
  const [showDimensions, setShowDimensions] = useState<boolean>(false);
  const [displayMode, setDisplayMode] = useState<'solid' | 'wireframe' | 'xray'>('solid');
  const [showConfidence, setShowConfidence] = useState<boolean>(false);
  const [confidenceFilter, setConfidenceFilter] = useState<ConfidenceFilterType>('ALL');
  const [measureActive, setMeasureActive] = useState<boolean>(false);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [isExportingGlb, setIsExportingGlb] = useState<boolean>(false);
  const [exportNotice, setExportNotice] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Sync external selection (e.g. from 2D blueprint)
  useEffect(() => {
    if (externalSelectedId) {
      const match =
        scene.walls.find((w) => w.id === externalSelectedId) ||
        scene.doors.find((d) => d.id === externalSelectedId) ||
        scene.windows.find((win) => win.id === externalSelectedId) ||
        scene.floors.find((f) => f.id === externalSelectedId);
      if (match) setSelectedItem(match);
    }
  }, [externalSelectedId, scene]);

  const handleSelectItem = (item: any) => {
    setSelectedItem(item);
    if (onSelectObject) onSelectObject(item);
  };

  const handleResetCamera = () => {
    setResetTrigger((prev) => prev + 1);
  };

  // Keyboard shortcuts (Section 53)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input
      if (['INPUT', 'TEXTAREA'].includes((e.target as HTMLElement).tagName)) return;

      switch (e.key.toLowerCase()) {
        case 'r':
          handleResetCamera();
          break;
        case 't':
          setCameraMode('TOP');
          break;
        case 'f':
          setCameraMode('FRONT');
          break;
        case 'w':
          setCameraMode('WALK');
          break;
        case 'g':
          setShowGrid((prev) => !prev);
          break;
        case 'x':
          setDisplayMode((prev) => (prev === 'xray' ? 'solid' : 'xray'));
          break;
        case 'c':
          setShowConfidence((prev) => !prev);
          break;
        case 'm':
          setMeasureActive((prev) => !prev);
          break;
        case 'escape':
          setMeasureActive(false);
          setSelectedItem(null);
          if (onSelectObject) onSelectObject(null);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onSelectObject]);

  // GLB Export handler (Section 34)
  const handleExportGlb = async () => {
    try {
      setIsExportingGlb(true);
      setExportNotice('Exporting GLB 3D scene...');

      if (scene.glb_url) {
        // Direct download
        const link = document.createElement('a');
        link.href = scene.glb_url;
        link.download = `planevue_scene_${scene.scene_id}.glb`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } else {
        const blob = await exportScene({
          scene_id: scene.scene_id,
          format: 'glb',
          wall_height: scene.wall_height,
          wall_thickness: scene.wall_thickness,
        });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `planevue_scene_${scene.scene_id}.glb`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      }

      setExportNotice('Export complete. Download started.');
      setTimeout(() => setExportNotice(null), 3500);
      if (onExportGlbSuccess && scene.glb_url) onExportGlbSuccess(scene.glb_url);
    } catch (err: any) {
      setExportNotice(`Export failed: ${err.message || 'Error generating GLB'}`);
      setTimeout(() => setExportNotice(null), 4000);
    } finally {
      setIsExportingGlb(false);
    }
  };

  // View Capture handler (Section 37)
  const handleCaptureView = () => {
    const canvas = document.querySelector('canvas');
    if (!canvas) return;

    try {
      const dataUrl = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.href = dataUrl;
      link.download = `planevue_capture_${scene.scene_id}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setExportNotice('3D view snapshot captured.');
      setTimeout(() => setExportNotice(null), 3000);
    } catch (err) {
      console.error('Failed to capture canvas', err);
    }
  };

  // Stats for confidence breakdown
  const confidenceStats = React.useMemo(() => {
    const all = [
      ...scene.walls,
      ...scene.doors,
      ...scene.windows,
      ...scene.floors,
    ];
    const observed = all.filter((o) => o.status === 'OBSERVED').length;
    const inferred = all.filter((o) => o.status === 'INFERRED').length;
    const corrected = all.filter((o) => o.status === 'CORRECTED').length;
    const confs = all.map((o) => o.confidence).filter((c) => c !== undefined && c !== null);
    const mean = confs.length ? confs.reduce((a, b) => a + b, 0) / confs.length : undefined;

    return {
      observedCount: observed,
      inferredCount: inferred,
      correctedCount: corrected,
      meanConfidence: mean,
    };
  }, [scene]);

  return (
    <div className="relative w-full h-full flex flex-col bg-slate-950 select-none overflow-hidden rounded-xl border border-slate-800">
      {/* Top Floating Toolbar */}
      <div className="absolute top-3 left-3 right-3 z-30 pointer-events-auto">
        <SceneToolbar
          cameraMode={cameraMode}
          onSelectCameraMode={setCameraMode}
          showGrid={showGrid}
          onToggleGrid={() => setShowGrid(!showGrid)}
          showLabels={showLabels}
          onToggleLabels={() => setShowLabels(!showLabels)}
          showDimensions={showDimensions}
          onToggleDimensions={() => setShowDimensions(!showDimensions)}
          displayMode={displayMode}
          onChangeDisplayMode={setDisplayMode}
          showConfidence={showConfidence}
          onToggleConfidence={() => setShowConfidence(!showConfidence)}
          measureActive={measureActive}
          onToggleMeasure={() => setMeasureActive(!measureActive)}
          onResetCamera={handleResetCamera}
          onExportGlb={handleExportGlb}
          onCaptureView={handleCaptureView}
          isExportingGlb={isExportingGlb}
        />
      </div>

      {/* Confidence Overlay Bar */}
      {showConfidence && (
        <div className="absolute top-18 right-3 z-30 pointer-events-auto">
          <ConfidenceOverlay
            filter={confidenceFilter}
            onChangeFilter={setConfidenceFilter}
            stats={confidenceStats}
          />
        </div>
      )}

      {/* Export / Toast Banner */}
      {exportNotice && (
        <div className="absolute top-18 left-1/2 transform -translate-x-1/2 z-40 bg-cyan-950/95 border border-cyan-400 text-cyan-200 px-4 py-2 rounded-xl text-xs font-semibold shadow-2xl backdrop-blur-md flex items-center gap-2 animate-bounce">
          <CheckCircle2 className="w-4 h-4 text-cyan-400" />
          <span>{exportNotice}</span>
        </div>
      )}

      {/* 3D WebGL Canvas */}
      <div className="w-full h-full relative cursor-grab active:cursor-grabbing">
        <Canvas
          shadows
          gl={{ preserveDrawingBuffer: true, antialias: true }}
          camera={{ position: [10, 10, 10], fov: 45 }}
          onClick={() => {
            // Background click deselects
            setSelectedItem(null);
            if (onSelectObject) onSelectObject(null);
          }}
        >
          {/* Professional Lighting (Section 12) */}
          <ambientLight intensity={0.65} />
          <directionalLight
            position={[12, 20, 10]}
            intensity={1.1}
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
          />
          <hemisphereLight
            args={['#38bdf8', '#0f172a', 0.4]}
          />

          {/* Grid & Ground */}
          <GridSystem visible={showGrid} />

          {/* Camera Controls */}
          <CameraControls
            mode={cameraMode}
            bounds={scene.bounds}
            resetTrigger={resetTrigger}
          />

          {/* Scene Meshes */}
          <group>
            {/* 1. Floors */}
            {scene.floors.map((floor) => (
              <FloorMesh
                key={floor.id}
                room={floor}
                isSelected={selectedItem?.id === floor.id}
                displayMode={displayMode}
                onSelect={handleSelectItem}
              />
            ))}

            {/* 2. Room Labels */}
            {scene.floors.map((floor) => (
              <RoomLabel
                key={`label-${floor.id}`}
                room={floor}
                visible={showLabels}
              />
            ))}

            {/* 3. Walls */}
            {scene.walls.map((wall) => (
              <WallMesh
                key={wall.id}
                wall={wall}
                isSelected={selectedItem?.id === wall.id}
                displayMode={displayMode}
                confidenceFilter={confidenceFilter}
                showDimensions={showDimensions}
                onSelect={handleSelectItem}
              />
            ))}

            {/* 4. Doors */}
            {scene.doors.map((door) => (
              <DoorMesh
                key={door.id}
                door={door}
                isSelected={selectedItem?.id === door.id}
                displayMode={displayMode}
                confidenceFilter={confidenceFilter}
                onSelect={handleSelectItem}
              />
            ))}

            {/* 5. Windows */}
            {scene.windows.map((win) => (
              <WindowMesh
                key={win.id}
                window={win}
                isSelected={selectedItem?.id === win.id}
                displayMode={displayMode}
                confidenceFilter={confidenceFilter}
                onSelect={handleSelectItem}
              />
            ))}
          </group>

          {/* Real Euclidean Measurement Tool (Section 17) */}
          <MeasurementTool
            active={measureActive}
            onExit={() => setMeasureActive(false)}
          />
        </Canvas>
      </div>

      {/* Selected Object Inspector Panel (Section 16) */}
      {selectedItem && (
        <div className="absolute bottom-4 left-4 z-30 bg-slate-900/95 border border-cyan-500/40 p-4 rounded-xl shadow-2xl backdrop-blur-md w-72 text-xs">
          <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-800">
            <span className="font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Box className="w-4 h-4 text-cyan-400" />
              {selectedItem.type} {selectedItem.id}
            </span>
            <button
              onClick={() => setSelectedItem(null)}
              className="text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-1.5 text-slate-300">
            {selectedItem.dimensions?.length_m !== undefined && (
              <div className="flex justify-between">
                <span className="text-slate-400">Length:</span>
                <span className="font-mono font-semibold text-white">
                  {selectedItem.dimensions.length_m.toFixed(2)} m
                </span>
              </div>
            )}
            {selectedItem.dimensions?.width_m !== undefined && (
              <div className="flex justify-between">
                <span className="text-slate-400">Width:</span>
                <span className="font-mono font-semibold text-white">
                  {selectedItem.dimensions.width_m.toFixed(2)} m
                </span>
              </div>
            )}
            {selectedItem.dimensions?.thickness_m !== undefined && (
              <div className="flex justify-between">
                <span className="text-slate-400">Thickness:</span>
                <span className="font-mono font-semibold text-white">
                  {selectedItem.dimensions.thickness_m.toFixed(2)} m
                </span>
              </div>
            )}
            {selectedItem.dimensions?.height_m !== undefined && (
              <div className="flex justify-between">
                <span className="text-slate-400">Height:</span>
                <span className="font-mono font-semibold text-white">
                  {selectedItem.dimensions.height_m.toFixed(2)} m
                </span>
              </div>
            )}
            {selectedItem.area_m2 !== undefined && (
              <div className="flex justify-between">
                <span className="text-slate-400">Room Area:</span>
                <span className="font-mono font-semibold text-white">
                  {selectedItem.area_m2.toFixed(1)} m²
                </span>
              </div>
            )}
            {selectedItem.label && (
              <div className="flex justify-between">
                <span className="text-slate-400">Room Name:</span>
                <span className="font-bold text-cyan-300">{selectedItem.label}</span>
              </div>
            )}

            <div className="flex justify-between pt-1 border-t border-slate-800">
              <span className="text-slate-400">Confidence:</span>
              <span className="font-mono font-semibold text-emerald-400">
                {selectedItem.confidence !== undefined
                  ? `${(selectedItem.confidence * 100).toFixed(0)}%`
                  : 'Confidence unavailable'}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-400">Status:</span>
              <span
                className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                  selectedItem.status === 'OBSERVED'
                    ? 'bg-emerald-950 text-emerald-300'
                    : selectedItem.status === 'CORRECTED'
                    ? 'bg-amber-950 text-amber-300'
                    : 'bg-purple-950 text-purple-300'
                }`}
              >
                {selectedItem.status}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Scene Statistics & Bounding Box (Section 25 & 26) */}
      <div className="absolute bottom-3 right-3 z-20 pointer-events-none">
        <div className="bg-slate-900/85 backdrop-blur-md border border-slate-800 px-3 py-1.5 rounded-lg text-[10px] text-slate-400 flex items-center gap-3">
          <span>Rooms: <strong className="text-slate-200">{scene.metrics.room_count}</strong></span>
          <span>Walls: <strong className="text-slate-200">{scene.metrics.wall_count}</strong></span>
          <span>Doors: <strong className="text-slate-200">{scene.metrics.door_count}</strong></span>
          <span>Windows: <strong className="text-slate-200">{scene.metrics.window_count}</strong></span>
          <span className="text-slate-600">|</span>
          <span>
            Bounds: <strong className="text-cyan-300">{scene.bounds.width_m.toFixed(1)}m × {scene.bounds.depth_m.toFixed(1)}m × {scene.bounds.height_m.toFixed(1)}m</strong>
          </span>
        </div>
      </div>
    </div>
  );
};
