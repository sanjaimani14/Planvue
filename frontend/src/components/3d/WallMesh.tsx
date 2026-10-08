import React from 'react';
import { Wall3D } from '../../types';

interface WallMeshProps {
  wall: Wall3D;
  isSelected: boolean;
  displayMode: 'solid' | 'wireframe' | 'xray';
  confidenceFilter: 'ALL' | 'OBSERVED' | 'INFERRED' | 'CORRECTED';
  showDimensions: boolean;
  onSelect: (item: Wall3D) => void;
}

export const WallMesh: React.FC<WallMeshProps> = ({
  wall,
  isSelected,
  displayMode,
  confidenceFilter,
  showDimensions,
  onSelect,
}) => {
  const { length_m, thickness_m, height_m } = wall.dimensions;
  const [posX, posY, posZ] = wall.transform.position;
  const rotY = wall.transform.rotation_y;

  // Filter visibility logic
  const isMatchFilter =
    confidenceFilter === 'ALL' || wall.status === confidenceFilter;

  // Determine material color based on status or selection
  let baseColor = '#e2e8f0'; // Clean matte architectural off-white (OBSERVED)
  if (wall.status === 'CORRECTED') baseColor = '#f59e0b'; // Amber
  if (wall.status === 'INFERRED') baseColor = '#8b5cf6'; // Violet

  const color = isSelected ? '#38bdf8' : baseColor;
  const opacity = !isMatchFilter
    ? 0.12
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
        onSelect(wall);
      }}
    >
      <mesh castShadow receiveShadow>
        <boxGeometry args={[length_m, height_m, thickness_m]} />
        <meshStandardMaterial
          color={color}
          roughness={0.7}
          metalness={0.05}
          wireframe={wireframe}
          transparent={transparent}
          opacity={opacity}
          emissive={isSelected ? '#0284c7' : '#000000'}
          emissiveIntensity={isSelected ? 0.35 : 0}
        />
      </mesh>

      {/* Live Dimension helper */}
      {showDimensions && (
        <group position={[0, height_m / 2 + 0.15, 0]}>
          <mesh>
            <boxGeometry args={[length_m * 0.9, 0.02, 0.02]} />
            <meshBasicMaterial color="#38bdf8" />
          </mesh>
        </group>
      )}
    </group>
  );
};
