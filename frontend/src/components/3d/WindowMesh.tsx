import React from 'react';
import { Window3D } from '../../types';

interface WindowMeshProps {
  window: Window3D;
  isSelected: boolean;
  displayMode: 'solid' | 'wireframe' | 'xray';
  confidenceFilter: 'ALL' | 'OBSERVED' | 'INFERRED' | 'CORRECTED';
  onSelect: (item: Window3D) => void;
}

export const WindowMesh: React.FC<WindowMeshProps> = ({
  window: win,
  isSelected,
  displayMode,
  confidenceFilter,
  onSelect,
}) => {
  const { width_m, height_m } = win.dimensions;
  const [posX, posY, posZ] = win.transform.position;
  const rotY = win.transform.rotation_y;

  const isMatchFilter =
    confidenceFilter === 'ALL' || win.status === confidenceFilter;

  const opacity = !isMatchFilter
    ? 0.15
    : displayMode === 'xray'
    ? 0.35
    : 1.0;
  const transparent = displayMode === 'xray' || !isMatchFilter;
  const wireframe = displayMode === 'wireframe';

  return (
    <group
      position={[posX, posY, posZ]}
      rotation={[0, -rotY, 0]}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(win);
      }}
    >
      {/* Outer Window Frame */}
      <mesh castShadow receiveShadow>
        <boxGeometry args={[width_m, height_m, 0.06]} />
        <meshStandardMaterial
          color={isSelected ? '#38bdf8' : '#475569'}
          roughness={0.5}
          wireframe={wireframe}
          transparent={transparent}
          opacity={opacity}
        />
      </mesh>

      {/* Translucent Architectural Glass Pane */}
      <mesh>
        <boxGeometry args={[width_m * 0.92, height_m * 0.92, 0.02]} />
        <meshStandardMaterial
          color={isSelected ? '#0284c7' : '#93c5fd'}
          roughness={0.1}
          metalness={0.1}
          transparent={true}
          opacity={isMatchFilter ? 0.55 : 0.12}
          wireframe={wireframe}
          emissive={isSelected ? '#0369a1' : '#1e3a8a'}
          emissiveIntensity={isSelected ? 0.4 : 0.1}
        />
      </mesh>
    </group>
  );
};
