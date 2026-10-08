import React, { useRef } from 'react';
import * as THREE from 'three';
import { Html } from '@react-three/drei';

interface FurnitureItem {
  id: string;
  name: string;
  type?: string;
  room_id?: string;
  room_label?: string;
  source?: string;
  status?: string;
  confidence?: number;
  dimensions?: {
    width_m: number;
    height_m: number;
    depth_m: number;
  };
  transform?: {
    position: [number, number, number];
    rotation?: [number, number, number];
  };
}

interface FurnitureMeshProps {
  item: FurnitureItem;
  isSelected: boolean;
  visible: boolean;
  onSelect: (item: any) => void;
}

export const FurnitureMesh: React.FC<FurnitureMeshProps> = ({
  item,
  isSelected,
  visible,
  onSelect,
}) => {
  const meshRef = useRef<THREE.Mesh | null>(null);

  if (!visible) return null;

  const dims = item.dimensions || { width_m: 1.0, height_m: 0.8, depth_m: 1.0 };
  const pos = item.transform?.position || [0, (dims.height_m || 0.8) / 2, 0];

  // Distinct color based on furniture name
  const isMedical = item.name.toLowerCase().includes('bed') || item.name.toLowerCase().includes('nurse') || item.name.toLowerCase().includes('dispenser') || item.name.toLowerCase().includes('clinic');
  const baseColor = isMedical ? '#38bdf8' : '#818cf8';

  return (
    <group position={pos}>
      <mesh
        ref={meshRef}
        onClick={(e) => {
          e.stopPropagation();
          onSelect({
            ...item,
            type: 'furniture',
            label: item.name,
            confidence: item.confidence ?? 0.88,
            status: item.status || 'INFERRED',
          });
        }}
        castShadow
        receiveShadow
      >
        <boxGeometry args={[dims.width_m, dims.height_m, dims.depth_m]} />
        <meshStandardMaterial
          color={isSelected ? '#f59e0b' : baseColor}
          roughness={0.4}
          metalness={0.2}
          transparent
          opacity={0.88}
        />
        <lineSegments>
          <edgesGeometry args={[new THREE.BoxGeometry(dims.width_m, dims.height_m, dims.depth_m)]} />
          <lineBasicMaterial color={isSelected ? '#ffffff' : '#e0e7ff'} linewidth={1.5} />
        </lineSegments>
      </mesh>

      {/* Floating 3D Label */}
      <Html
        position={[0, dims.height_m / 2 + 0.25, 0]}
        center
        distanceFactor={18}
        zIndexRange={[20, 0]}
      >
        <div
          onClick={(e) => {
            e.stopPropagation();
            onSelect({
              ...item,
              type: 'furniture',
              label: item.name,
              confidence: item.confidence ?? 0.88,
              status: item.status || 'INFERRED',
            });
          }}
          className={`cursor-pointer px-2 py-0.5 rounded text-[10px] font-mono font-bold whitespace-nowrap shadow-lg backdrop-blur-md transition-all select-none border ${
            isSelected
              ? 'bg-amber-500 text-slate-950 border-amber-300 ring-2 ring-amber-400 scale-105'
              : 'bg-slate-900/90 text-cyan-200 border-cyan-500/30 hover:border-cyan-400'
          }`}
        >
          <span>{item.name}</span>
          <span className="ml-1 text-[9px] opacity-75">
            ({Math.round((item.confidence ?? 0.88) * 100)}%)
          </span>
        </div>
      </Html>
    </group>
  );
};
