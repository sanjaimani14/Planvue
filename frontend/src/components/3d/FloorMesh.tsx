import React, { useMemo } from 'react';
import * as THREE from 'three';
import { Floor3D } from '../../types';

interface FloorMeshProps {
  room: Floor3D;
  isSelected: boolean;
  displayMode: 'solid' | 'wireframe' | 'xray';
  onSelect: (item: Floor3D) => void;
}

export const FloorMesh: React.FC<FloorMeshProps> = ({
  room,
  isSelected,
  displayMode,
  onSelect,
}) => {
  const shape = useMemo(() => {
    if (!room.polygon_3d || room.polygon_3d.length < 3) return null;
    const s = new THREE.Shape();
    s.moveTo(room.polygon_3d[0][0], room.polygon_3d[0][2]);
    for (let i = 1; i < room.polygon_3d.length; i++) {
      s.lineTo(room.polygon_3d[i][0], room.polygon_3d[i][2]);
    }
    s.closePath();
    return s;
  }, [room.polygon_3d]);

  if (!shape) return null;

  const wireframe = displayMode === 'wireframe';
  const transparent = displayMode === 'xray';
  const opacity = displayMode === 'xray' ? 0.35 : 0.95;

  return (
    <group
      onClick={(e) => {
        e.stopPropagation();
        onSelect(room);
      }}
    >
      {/* Floor surface polygon at Y=0.005 */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.005, 0]}
        receiveShadow
      >
        <shapeGeometry args={[shape]} />
        <meshStandardMaterial
          color={isSelected ? '#38bdf8' : '#f1f5f9'}
          roughness={0.8}
          metalness={0.05}
          side={THREE.DoubleSide}
          wireframe={wireframe}
          transparent={transparent}
          opacity={opacity}
          emissive={isSelected ? '#0284c7' : '#000000'}
          emissiveIntensity={isSelected ? 0.25 : 0}
        />
      </mesh>
    </group>
  );
};
