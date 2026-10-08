import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Grid, Line, Box, Cone } from '@react-three/drei';
import * as THREE from 'three';
import { VideoSceneItem, CameraPoseItem, Point3DItem, UnseenRegionItem } from '../../types';
import { ProvenanceFilter } from './CompletionControls';
import { Compass, RotateCcw, Eye, Maximize, Info, X } from 'lucide-react';

interface VideoSceneViewerProps {
  scene: VideoSceneItem;
  provenanceFilter: ProvenanceFilter;
  showCameras: boolean;
  showPointCloud: boolean;
  showUnseenVolumes: boolean;
  selectedKeyframeIndex: number | null;
  selectedRegionId: string | null;
  onSelectElement?: (elem: any | null) => void;
}

// Subcomponent: Wall Prism Mesh
const VideoWallMesh: React.FC<{
  wall: any;
  isVisible: boolean;
  isSelected: boolean;
  onClick: () => void;
}> = ({ wall, isVisible, isSelected, onClick }) => {
  if (!isVisible) return null;

  const s = wall.geometry.start || [0, 0, 0];
  const e = wall.geometry.end || [1, 0, 1];
  const h = wall.geometry.height || 2.8;
  const th = wall.geometry.thickness || 0.18;

  const dx = e[0] - s[0];
  const dz = e[2] - s[2];
  const length = Math.hypot(dx, dz);
  const angle = Math.atan2(dz, dx);
  const midX = (s[0] + e[0]) / 2;
  const midZ = (s[2] + e[2]) / 2;

  // Determine color based on provenance
  let color = '#94a3b8'; // OBSERVED (slate)
  if (wall.status === 'INFERRED') color = '#06b6d4'; // INFERRED (cyan)
  if (wall.status === 'GENERATED') color = '#f59e0b'; // GENERATED (amber)
  if (isSelected) color = '#ec4899'; // Selected (pink)

  return (
    <group position={[midX, h / 2, midZ]} rotation={[0, -angle, 0]} onClick={(evt) => { evt.stopPropagation(); onClick(); }}>
      <mesh castShadow receiveShadow>
        <boxGeometry args={[length, h, th]} />
        <meshStandardMaterial
          color={color}
          roughness={0.4}
          metalness={0.1}
          wireframe={false}
          transparent={wall.status !== 'OBSERVED'}
          opacity={wall.status === 'GENERATED' ? 0.75 : 0.90}
        />
      </mesh>
    </group>
  );
};

// Subcomponent: Floor Slab
const VideoFloorMesh: React.FC<{ bounds: any }> = ({ bounds }) => {
  const minX = bounds.min[0];
  const maxX = bounds.max[0];
  const minZ = bounds.min[2];
  const maxZ = bounds.max[2];

  const w = Math.max(1, maxX - minX);
  const d = Math.max(1, maxZ - minZ);
  const midX = (minX + maxX) / 2;
  const midZ = (minZ + maxZ) / 2;

  return (
    <mesh position={[midX, -0.02, midZ]} receiveShadow>
      <boxGeometry args={[w, 0.04, d]} />
      <meshStandardMaterial color="#1e293b" roughness={0.7} />
    </mesh>
  );
};

// Subcomponent: Camera Path and Frustums
const CameraTrajectory: React.FC<{
  poses: CameraPoseItem[];
  selectedKeyframeIndex: number | null;
}> = ({ poses, selectedKeyframeIndex }) => {
  const points = useMemo(() => {
    return poses.map((p) => new THREE.Vector3(p.position[0], p.position[1], p.position[2]));
  }, [poses]);

  if (poses.length === 0) return null;

  return (
    <group>
      {/* Trajectory Polyline */}
      {points.length >= 2 && (
        <Line points={points} color="#6366f1" lineWidth={2.5} dashed={false} />
      )}

      {/* Camera Pose Markers */}
      {poses.map((p) => {
        const isSelected = selectedKeyframeIndex === p.frame_index;
        return (
          <group
            key={p.frame_index}
            position={[p.position[0], p.position[1], p.position[2]]}
          >
            <mesh>
              <coneGeometry args={[0.08, 0.16, 4]} />
              <meshStandardMaterial
                color={isSelected ? '#f43f5e' : '#818cf8'}
                emissive={isSelected ? '#f43f5e' : '#4f46e5'}
                emissiveIntensity={isSelected ? 0.6 : 0.2}
              />
            </mesh>
          </group>
        );
      })}
    </group>
  );
};

// Subcomponent: Sparse 3D Point Cloud
const SparsePointCloud: React.FC<{ points: Point3DItem[] }> = ({ points }) => {
  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(points.length * 3);
    const col = new Float32Array(points.length * 3);
    for (let i = 0; i < points.length; i++) {
      pos[i * 3] = points[i].position[0];
      pos[i * 3 + 1] = points[i].position[1];
      pos[i * 3 + 2] = points[i].position[2];

      col[i * 3] = points[i].color[0] / 255.0;
      col[i * 3 + 1] = points[i].color[1] / 255.0;
      col[i * 3 + 2] = points[i].color[2] / 255.0;
    }
    return [pos, col];
  }, [points]);

  if (points.length === 0) return null;

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
      <pointsMaterial
        size={0.06}
        vertexColors
        transparent
        opacity={0.85}
        sizeAttenuation
      />
    </points>
  );
};

// Subcomponent: Unseen Region Bounding Volumes
const UnseenVolumeBox: React.FC<{
  region: UnseenRegionItem;
  isSelected: boolean;
  onClick: () => void;
}> = ({ region, isSelected, onClick }) => {
  const min = region.boundary_min;
  const max = region.boundary_max;
  const w = Math.max(0.2, max[0] - min[0]);
  const h = Math.max(0.2, max[1] - min[1]);
  const d = Math.max(0.2, max[2] - min[2]);
  const midX = (min[0] + max[0]) / 2;
  const midY = (min[1] + max[1]) / 2;
  const midZ = (min[2] + max[2]) / 2;

  return (
    <group position={[midX, midY, midZ]} onClick={(e) => { e.stopPropagation(); onClick(); }}>
      <Box args={[w, h, d]}>
        <meshStandardMaterial
          color={isSelected ? '#ec4899' : '#f43f5e'}
          transparent
          opacity={isSelected ? 0.35 : 0.20}
          wireframe={false}
        />
      </Box>
    </group>
  );
};

export const VideoSceneViewer: React.FC<VideoSceneViewerProps> = ({
  scene,
  provenanceFilter,
  showCameras,
  showPointCloud,
  showUnseenVolumes,
  selectedKeyframeIndex,
  selectedRegionId,
  onSelectElement,
}) => {
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [cameraView, setCameraView] = useState<'persp' | 'top' | 'front'>('persp');
  const controlsRef = useRef<any>(null);

  const handleSelectItem = (item: any) => {
    setSelectedItem(item);
    if (onSelectElement) onSelectElement(item);
  };

  const handleCameraPreset = (view: 'persp' | 'top' | 'front') => {
    setCameraView(view);
    if (!controlsRef.current) return;
    if (view === 'top') {
      controlsRef.current.object.position.set(0, 10, 0);
      controlsRef.current.target.set(0, 0, 0);
    } else if (view === 'front') {
      controlsRef.current.object.position.set(0, 2, 8);
      controlsRef.current.target.set(0, 1.4, 0);
    } else {
      controlsRef.current.object.position.set(5, 5, 6);
      controlsRef.current.target.set(0, 1, 0);
    }
    controlsRef.current.update();
  };

  // Filter objects based on provenance toggle
  const visibleWalls = useMemo(() => {
    const wallObjs = scene.objects.filter((o) => o.type === 'wall');
    if (provenanceFilter === 'ALL') return wallObjs;
    return wallObjs.filter((o) => o.status === provenanceFilter);
  }, [scene.objects, provenanceFilter]);

  return (
    <div className="relative w-full h-[540px] bg-slate-950 rounded-2xl border border-white/10 overflow-hidden shadow-2xl">
      {/* 3D Scene Toolbar */}
      <div className="absolute top-3 left-3 z-10 flex items-center gap-1.5 p-1 rounded-xl bg-slate-900/90 border border-white/10 backdrop-blur-md shadow-lg text-xs">
        <button
          onClick={() => handleCameraPreset('persp')}
          className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
            cameraView === 'persp' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Persp
        </button>
        <button
          onClick={() => handleCameraPreset('top')}
          className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
            cameraView === 'top' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Top View
        </button>
        <button
          onClick={() => handleCameraPreset('front')}
          className={`px-2.5 py-1 rounded-lg font-medium transition-all ${
            cameraView === 'front' ? 'bg-indigo-600 text-white shadow' : 'text-slate-400 hover:text-white'
          }`}
        >
          Front
        </button>
      </div>

      {/* Provenance Color Legend */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-2 p-1.5 rounded-xl bg-slate-900/90 border border-white/10 backdrop-blur-md text-[11px] shadow-lg">
        <span className="flex items-center gap-1 text-slate-300 font-medium">
          <span className="w-2.5 h-2.5 rounded-sm bg-slate-400" /> Observed
        </span>
        <span className="flex items-center gap-1 text-cyan-300 font-medium">
          <span className="w-2.5 h-2.5 rounded-sm bg-cyan-400" /> Inferred
        </span>
        <span className="flex items-center gap-1 text-amber-300 font-medium">
          <span className="w-2.5 h-2.5 rounded-sm bg-amber-400" /> Generated
        </span>
        <span className="flex items-center gap-1 text-rose-300 font-medium">
          <span className="w-2.5 h-2.5 rounded-sm bg-rose-500" /> Unseen
        </span>
      </div>

      {/* Three.js Canvas */}
      <Canvas
        shadows
        camera={{ position: [5, 5, 6], fov: 50 }}
        className="w-full h-full cursor-grab active:cursor-grabbing"
        onPointerDown={(e) => {
          if (e.target === e.currentTarget) setSelectedItem(null);
        }}
      >
        <ambientLight intensity={0.65} />
        <directionalLight position={[10, 15, 10]} intensity={1.1} castShadow />
        <pointLight position={[-8, 6, -5]} intensity={0.5} />

        <Grid
          args={[20, 20]}
          cellSize={0.5}
          cellThickness={0.6}
          cellColor="#334155"
          sectionSize={2.0}
          sectionThickness={1.2}
          sectionColor="#475569"
          fadeDistance={25}
          fadeStrength={1}
          position={[0, -0.01, 0]}
        />

        {/* Floor */}
        <VideoFloorMesh bounds={scene.bounds} />

        {/* Walls */}
        {visibleWalls.map((w) => (
          <VideoWallMesh
            key={w.id}
            wall={w}
            isVisible={true}
            isSelected={selectedItem?.id === w.id}
            onClick={() => handleSelectItem(w)}
          />
        ))}

        {/* Cameras */}
        {showCameras && (
          <CameraTrajectory
            poses={scene.camera_poses}
            selectedKeyframeIndex={selectedKeyframeIndex}
          />
        )}

        {/* Point Cloud */}
        {showPointCloud && <SparsePointCloud points={scene.point_cloud} />}

        {/* Unseen Volumes */}
        {showUnseenVolumes &&
          scene.unseen_regions.map((reg) => (
            <UnseenVolumeBox
              key={reg.region_id}
              region={reg}
              isSelected={selectedRegionId === reg.region_id}
              onClick={() => handleSelectItem(reg)}
            />
          ))}

        <OrbitControls ref={controlsRef} makeDefault dampingFactor={0.08} />
      </Canvas>

      {/* Selected Element Inspector Overlay */}
      {selectedItem && (
        <div className="absolute bottom-4 left-4 z-10 w-80 p-3.5 rounded-xl bg-slate-900/95 border border-white/15 backdrop-blur-xl shadow-2xl text-xs flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <span className="font-bold text-white font-mono text-xs flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-indigo-400" />
              {selectedItem.id || selectedItem.region_id}
            </span>
            <div className="flex items-center gap-1.5">
              <span
                className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border ${
                  selectedItem.status === 'OBSERVED'
                    ? 'bg-slate-700/80 text-slate-200 border-slate-600'
                    : selectedItem.status === 'INFERRED'
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30'
                    : selectedItem.status === 'GENERATED'
                    ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                    : 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                }`}
              >
                {selectedItem.status}
              </span>
              <button
                onClick={() => setSelectedItem(null)}
                className="text-slate-400 hover:text-white p-0.5 rounded"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
          <p className="text-[11px] text-slate-300 leading-tight">
            {selectedItem.provenance_note || selectedItem.reason || 'Observed 3D architectural element'}
          </p>
          {selectedItem.geometry && selectedItem.geometry.length && (
            <div className="text-[10px] text-slate-400 font-mono">
              Dimensions: {selectedItem.geometry.length}m L × {selectedItem.geometry.height}m H × {selectedItem.geometry.thickness}m T
            </div>
          )}
        </div>
      )}
    </div>
  );
};
