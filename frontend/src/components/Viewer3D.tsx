import React, { useRef, useState, useEffect, Suspense } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls, Grid, Center, useGLTF, Html } from '@react-three/drei';
import * as THREE from 'three';
import { 
  Eye, Compass, Maximize2, RotateCcw, 
  Ruler, CheckCircle2, ShieldAlert, Sparkles, Video, Box
} from 'lucide-react';
import { Point3D, CoverageVoxel, CameraPose } from '../types';

interface Viewer3DProps {
  glbUrl?: string;
  mode: 'BLUEPRINT' | 'ROOM_VIDEO';
  sparsePoints?: Point3D[];
  coverageVoxels?: CoverageVoxel[];
  cameraPoses?: CameraPose[];
}

// GLTF model renderer component
const ModelScene: React.FC<{ 
  url: string; 
  confidenceMode: boolean; 
  layerVisibility: { walls: boolean; doors: boolean; floors: boolean; generated: boolean };
  modeFilter: 'all' | 'observed' | 'generated';
}> = ({ url, confidenceMode, layerVisibility, modeFilter }) => {
  const { scene } = useGLTF(url);
  const clonedScene = React.useMemo(() => scene.clone(true), [scene]);

  useEffect(() => {
    clonedScene.traverse((child) => {
      if ((child as THREE.Mesh).isMesh) {
        const mesh = child as THREE.Mesh;
        // Material transparency handling
        if (mesh.material) {
          const mat = (mesh.material as THREE.Material).clone();
          mesh.material = mat;

          // Confidence color mapping override if enabled
          if (confidenceMode) {
            // Check if vertex colors exist, otherwise highlight
            if (mesh.geometry.attributes.color) {
              (mat as THREE.MeshStandardMaterial).vertexColors = true;
            }
          }
        }
      }
    });
  }, [clonedScene, confidenceMode, layerVisibility, modeFilter]);

  return <primitive object={clonedScene} />;
};

// Point Cloud Renderer for Mode B
const PointCloudScene: React.FC<{ points: Point3D[]; visible: boolean }> = ({ points, visible }) => {
  if (!visible || !points || points.length === 0) return null;

  const { positions, colors } = React.useMemo(() => {
    const pos = new Float32Array(points.length * 3);
    const col = new Float32Array(points.length * 3);
    points.forEach((p, i) => {
      pos[i * 3] = p.x;
      pos[i * 3 + 1] = p.y;
      pos[i * 3 + 2] = p.z;
      col[i * 3] = p.r / 255;
      col[i * 3 + 1] = p.g / 255;
      col[i * 3 + 2] = p.b / 255;
    });
    return { positions: pos, colors: col };
  }, [points]);

  return (
    <points>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-color"
          args={[colors, 3]}
        />
      </bufferGeometry>
      <pointsMaterial size={0.06} vertexColors sizeAttenuation />
    </points>
  );
};

// Camera Controller for View Presets
const CameraPresetController: React.FC<{ preset: string; onPresetDone: () => void }> = ({ preset, onPresetDone }) => {
  const { camera } = useThree();

  useEffect(() => {
    if (!preset) return;
    const duration = 0.5;
    if (preset === 'top') {
      camera.position.set(0, 18, 0.01);
      camera.lookAt(0, 0, 0);
    } else if (preset === 'front') {
      camera.position.set(0, 2, 14);
      camera.lookAt(0, 1.5, 0);
    } else if (preset === 'side') {
      camera.position.set(14, 2, 0);
      camera.lookAt(0, 1.5, 0);
    } else if (preset === 'isometric') {
      camera.position.set(12, 12, 12);
      camera.lookAt(0, 0, 0);
    } else if (preset === 'walk') {
      camera.position.set(0, 1.6, 3);
      camera.lookAt(0, 1.6, -5);
    } else if (preset === 'reset') {
      camera.position.set(8, 10, 12);
      camera.lookAt(0, 0, 0);
    }
    camera.updateProjectionMatrix();
    onPresetDone();
  }, [preset, camera, onPresetDone]);

  return null;
};

// Measurement Tool Click Handler
const MeasurementInteraction: React.FC<{ 
  active: boolean; 
  measurePoints: THREE.Vector3[]; 
  onAddPoint: (pt: THREE.Vector3) => void 
}> = ({ active, measurePoints, onAddPoint }) => {
  return (
    <>
      {active && (
        <mesh
          position={[0, 0, 0]}
          rotation={[-Math.PI / 2, 0, 0]}
          onClick={(e) => {
            e.stopPropagation();
            if (measurePoints.length >= 2) return;
            onAddPoint(e.point);
          }}
          visible={false}
        >
          <planeGeometry args={[100, 100]} />
          <meshBasicMaterial transparent opacity={0} />
        </mesh>
      )}

      {/* Render measured points and line */}
      {measurePoints.map((pt, idx) => (
        <mesh key={idx} position={[pt.x, pt.y, pt.z]}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshStandardMaterial color="#f59e0b" emissive="#f59e0b" emissiveIntensity={0.5} />
        </mesh>
      ))}

      {measurePoints.length === 2 && (
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[
                new Float32Array([
                  measurePoints[0].x, measurePoints[0].y, measurePoints[0].z,
                  measurePoints[1].x, measurePoints[1].y, measurePoints[1].z
                ]),
                3
              ]}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#f59e0b" linewidth={3} />
        </line>
      )}
    </>
  );
};

export const Viewer3D: React.FC<Viewer3DProps> = ({
  glbUrl,
  mode,
  sparsePoints = [],
  coverageVoxels = [],
  cameraPoses = []
}) => {
  const [cameraPreset, setCameraPreset] = useState<string>('reset');
  const [confidenceMode, setConfidenceMode] = useState<boolean>(true);
  const [measureMode, setMeasureMode] = useState<boolean>(false);
  const [measurePoints, setMeasurePoints] = useState<THREE.Vector3[]>([]);
  const [modeFilter, setModeFilter] = useState<'all' | 'observed' | 'generated'>('all');
  const [showPointCloud, setShowPointCloud] = useState<boolean>(true);
  const [showGrid, setShowGrid] = useState<boolean>(true);

  // Calculated distance between measurement points
  const measurementDistance = React.useMemo(() => {
    if (measurePoints.length === 2) {
      return measurePoints[0].distanceTo(measurePoints[1]);
    }
    return null;
  }, [measurePoints]);

  const handleAddMeasurePoint = (pt: THREE.Vector3) => {
    if (measurePoints.length >= 2) {
      setMeasurePoints([pt]);
    } else {
      setMeasurePoints([...measurePoints, pt]);
    }
  };

  return (
    <div className="relative w-full h-[620px] rounded-2xl overflow-hidden bg-slate-950 border border-white/10 shadow-2xl">
      {/* 3D Canvas */}
      <Canvas
        camera={{ position: [8, 10, 12], fov: 45 }}
        gl={{ antialias: true, alpha: false, preserveDrawingBuffer: true }}
      >
        <color attach="background" args={['#080a10']} />
        <ambientLight intensity={0.7} />
        <directionalLight position={[10, 15, 10]} intensity={1.1} castShadow />
        <directionalLight position={[-10, 10, -10]} intensity={0.5} />

        {showGrid && (
          <Grid
            infiniteGrid
            cellSize={1}
            sectionSize={5}
            sectionColor="#334155"
            cellColor="#1e293b"
            fadeDistance={30}
            fadeStrength={1.5}
          />
        )}

        <CameraPresetController
          preset={cameraPreset}
          onPresetDone={() => setCameraPreset('')}
        />

        <Suspense fallback={
          <Html center>
            <div className="flex items-center gap-3 bg-slate-900/90 border border-indigo-500/30 px-4 py-2.5 rounded-xl shadow-xl backdrop-blur-md">
              <div className="w-4 h-4 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin" />
              <span className="text-xs font-mono text-indigo-200">Synthesizing 3D Geometry...</span>
            </div>
          </Html>
        }>
          <Center top>
            {glbUrl && (
              <ModelScene
                url={glbUrl}
                confidenceMode={confidenceMode}
                layerVisibility={{ walls: true, doors: true, floors: true, generated: true }}
                modeFilter={modeFilter}
              />
            )}
            {mode === 'ROOM_VIDEO' && (
              <PointCloudScene points={sparsePoints} visible={showPointCloud} />
            )}
          </Center>
        </Suspense>

        <MeasurementInteraction
          active={measureMode}
          measurePoints={measurePoints}
          onAddPoint={handleAddMeasurePoint}
        />

        <OrbitControls
          makeDefault
          enableDamping
          dampingFactor={0.05}
          minDistance={1.0}
          maxDistance={45.0}
          maxPolarAngle={Math.PI / 2 + 0.05} // Prevent going below floor
        />
      </Canvas>

      {/* Top Floating Viewport HUD Controls */}
      <div className="absolute top-4 left-4 right-4 flex items-center justify-between pointer-events-none">
        {/* Preset View Switcher */}
        <div className="pointer-events-auto flex items-center gap-1 bg-slate-900/90 backdrop-blur-md p-1 rounded-xl border border-white/10 shadow-lg">
          <button
            onClick={() => setCameraPreset('reset')}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            title="3D Orbit Default"
          >
            3D Orbit
          </button>
          <button
            onClick={() => setCameraPreset('top')}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            title="Top-Down Plan View"
          >
            Top View
          </button>
          <button
            onClick={() => setCameraPreset('front')}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            title="Front Elevation"
          >
            Front
          </button>
          <button
            onClick={() => setCameraPreset('side')}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            title="Side Elevation"
          >
            Side
          </button>
          <button
            onClick={() => setCameraPreset('isometric')}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            title="Isometric Ortho"
          >
            Isometric
          </button>
          <button
            onClick={() => setCameraPreset('walk')}
            className="px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white hover:bg-white/10 transition-colors"
            title="Eye-Level Walkthrough"
          >
            Walk
          </button>
        </div>

        {/* Feature Toggles */}
        <div className="pointer-events-auto flex items-center gap-2">
          {/* Measurement Button */}
          <button
            onClick={() => {
              setMeasureMode(!measureMode);
              setMeasurePoints([]);
            }}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              measureMode
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-lg shadow-amber-500/20'
                : 'bg-slate-900/90 text-slate-300 border-white/10 hover:bg-white/10'
            }`}
          >
            <Ruler className="w-3.5 h-3.5" />
            {measureMode ? 'Measuring Active' : 'Measure Tool'}
          </button>

          {/* Confidence View Mode Toggle */}
          <button
            onClick={() => setConfidenceMode(!confidenceMode)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
              confidenceMode
                ? 'bg-indigo-600/30 text-indigo-300 border-indigo-500/50 shadow-lg shadow-indigo-600/20'
                : 'bg-slate-900/90 text-slate-400 border-white/10 hover:bg-white/10'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Confidence View
          </button>
        </div>
      </div>

      {/* Mode B Specific Coverage Switcher */}
      {mode === 'ROOM_VIDEO' && (
        <div className="absolute top-16 left-4 flex items-center gap-1.5 bg-slate-900/90 backdrop-blur-md p-1 rounded-xl border border-white/10 text-xs shadow-lg">
          <span className="text-slate-400 font-mono px-2 text-[11px]">Filter:</span>
          <button
            onClick={() => setModeFilter('all')}
            className={`px-2.5 py-1 rounded-lg transition-colors ${modeFilter === 'all' ? 'bg-indigo-600 text-white font-medium' : 'text-slate-300 hover:bg-white/5'}`}
          >
            Show All
          </button>
          <button
            onClick={() => setModeFilter('observed')}
            className={`px-2.5 py-1 rounded-lg transition-colors ${modeFilter === 'observed' ? 'bg-emerald-600 text-white font-medium' : 'text-slate-300 hover:bg-white/5'}`}
          >
            Observed Only
          </button>
          <button
            onClick={() => setModeFilter('generated')}
            className={`px-2.5 py-1 rounded-lg transition-colors ${modeFilter === 'generated' ? 'bg-purple-600 text-white font-medium' : 'text-slate-300 hover:bg-white/5'}`}
          >
            Generated Only
          </button>
        </div>
      )}

      {/* Active Measurement Distance Badge */}
      {measureMode && measurementDistance !== null && (
        <div className="absolute bottom-16 left-1/2 -translate-x-1/2 bg-amber-950/90 border border-amber-500/50 text-amber-200 px-4 py-2 rounded-xl text-xs font-mono shadow-2xl backdrop-blur-md flex items-center gap-2">
          <Ruler className="w-4 h-4 text-amber-400" />
          <span>Metric Distance:</span>
          <span className="font-bold text-amber-300 text-sm">{measurementDistance.toFixed(2)} m</span>
          <span className="text-amber-400/80">({(measurementDistance * 100).toFixed(0)} cm)</span>
        </div>
      )}

      {/* Bottom Color-Coded Confidence Legend HUD */}
      <div className="absolute bottom-4 left-4 right-4 flex items-center justify-between pointer-events-none">
        <div className="pointer-events-auto flex flex-wrap items-center gap-3 bg-slate-900/90 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10 text-xs">
          <span className="text-slate-400 font-mono text-[11px] uppercase font-semibold">Classification:</span>
          
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-slate-200 border border-white/30" />
            <span className="text-slate-300">Observed</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500 border border-amber-400" />
            <span className="text-amber-300">Corrected / Snapped</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-violet-400 border border-violet-300" />
            <span className="text-violet-300">Inferred</span>
          </div>

          {mode === 'ROOM_VIDEO' && (
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-purple-500 border border-purple-400" />
              <span className="text-purple-300">Generated (Unseen Region)</span>
            </div>
          )}
        </div>

        {/* Status / Metric scale HUD note */}
        <div className="pointer-events-auto hidden md:flex items-center gap-2 bg-slate-900/90 backdrop-blur-md px-3.5 py-2 rounded-xl border border-white/10 text-[11px] font-mono text-slate-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>True Metric BIM Scale (1 unit = 1.0 m)</span>
        </div>
      </div>
    </div>
  );
};
