import React from 'react';

interface GridSystemProps {
  visible: boolean;
  size?: number;
}

export const GridSystem: React.FC<GridSystemProps> = ({ visible, size = 30 }) => {
  if (!visible) return null;

  return (
    <group position={[0, -0.005, 0]}>
      {/* 1m metric grid (30m size with 30 divisions = exactly 1m per grid square) */}
      <gridHelper
        args={[size, size, '#38bdf8', '#334155']}
        position={[0, 0, 0]}
      />

      {/* Ground plane shadow catcher & background tone */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
        <planeGeometry args={[size * 1.5, size * 1.5]} />
        <meshStandardMaterial color="#0b1120" roughness={0.9} metalness={0.1} />
      </mesh>

      {/* Axis lines: X axis (red) from -size/2 to +size/2 */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array([-size / 2, 0.01, 0, size / 2, 0.01, 0]), 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#ef4444" linewidth={2} />
      </line>

      {/* Axis lines: Z axis (blue/cyan) from -size/2 to +size/2 */}
      <line>
        <bufferGeometry>
          <bufferAttribute
            attach="attributes-position"
            args={[new Float32Array([0, 0.01, -size / 2, 0, 0.01, size / 2]), 3]}
          />
        </bufferGeometry>
        <lineBasicMaterial color="#06b6d4" linewidth={2} />
      </line>
    </group>
  );
};
