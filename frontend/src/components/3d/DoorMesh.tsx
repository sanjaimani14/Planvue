import React from 'react';
import { Door3D } from '../../types';

interface DoorMeshProps {
  door: Door3D;
  isSelected: boolean;
  displayMode: 'solid' | 'wireframe' | 'xray';
  confidenceFilter: 'ALL' | 'OBSERVED' | 'INFERRED' | 'CORRECTED';
  onSelect: (item: Door3D) => void;
}

export const DoorMesh: React.FC<DoorMeshProps> = ({
  door,
  isSelected,
  displayMode,
  confidenceFilter,
  onSelect,
}) => {
  const { width_m, height_m } = door.dimensions;
  const [posX, posY, posZ] = door.transform.position;
  const rotY = door.transform.rotation_y;

  const isMatchFilter =
    confidenceFilter === 'ALL' || door.status === confidenceFilter;

  const opacity = !isMatchFilter
    ? 0.15
    : displayMode === 'xray'
    ? 0.4
    : 1.0;
  const transparent = displayMode === 'xray' || !isMatchFilter;
  const wireframe = displayMode === 'wireframe';

  return (
    <group
      position={[posX, posY, posZ]}
      rotation={[0, -rotY, 0]}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(door);
      }}
    >
      {/* Outer Door Frame */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[width_m, height_m, 0.08]} />
        <meshStandardMaterial
          color={isSelected ? '#38bdf8' : '#334155'}
          roughness={0.6}
          wireframe={wireframe}
          transparent={transparent}
          opacity={opacity}
        />
      </mesh>

      {/* Door Leaf Panel (Warm Architectural Timber) */}
      <mesh castShadow receiveShadow position={[0, 0, 0.01]}>
        <boxGeometry args={[width_m * 0.94, height_m * 0.96, 0.04]} />
        <meshStandardMaterial
          color={isSelected ? '#0284c7' : '#b45309'}
          roughness={0.4}
          metalness={0.1}
          wireframe={wireframe}
          transparent={transparent}
          opacity={opacity}
          emissive={isSelected ? '#0369a1' : '#000000'}
          emissiveIntensity={isSelected ? 0.3 : 0}
        />
      </mesh>
    </group>
  );
};
