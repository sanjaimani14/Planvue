import React, { useState } from 'react';
import * as THREE from 'three';
import { Html } from '@react-three/drei';

interface MeasurementToolProps {
  active: boolean;
  onExit: () => void;
}

export const MeasurementTool: React.FC<MeasurementToolProps> = ({
  active,
  onExit,
}) => {
  const [pointA, setPointA] = useState<[number, number, number] | null>(null);
  const [pointB, setPointB] = useState<[number, number, number] | null>(null);

  if (!active) return null;

  const handlePointerDown = (e: any) => {
    e.stopPropagation();
    const point = e.point;
    if (!pointA) {
      setPointA([point.x, point.y, point.z]);
    } else if (!pointB) {
      setPointB([point.x, point.y, point.z]);
    } else {
      // Start a new measurement
      setPointA([point.x, point.y, point.z]);
      setPointB(null);
    }
  };

  const distanceMeters =
    pointA && pointB
      ? Math.sqrt(
          (pointB[0] - pointA[0]) ** 2 +
            (pointB[1] - pointA[1]) ** 2 +
            (pointB[2] - pointA[2]) ** 2
        )
      : null;

  const midPoint =
    pointA && pointB
      ? [
          (pointA[0] + pointB[0]) / 2,
          (pointA[1] + pointB[1]) / 2 + 0.15,
          (pointA[2] + pointB[2]) / 2,
        ]
      : null;

  return (
    <group>
      {/* Invisible raycast interceptor plane spanning the floor */}
      <mesh
        rotation={[-Math.PI / 2, 0, 0]}
        position={[0, 0.01, 0]}
        onPointerDown={handlePointerDown}
        visible={false}
      >
        <planeGeometry args={[100, 100]} />
        <meshBasicMaterial transparent opacity={0} />
      </mesh>

      {/* Point A Marker */}
      {pointA && (
        <mesh position={pointA}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
      )}

      {/* Point B Marker */}
      {pointB && (
        <mesh position={pointB}>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshBasicMaterial color="#38bdf8" />
        </mesh>
      )}

      {/* Dimension Line between Point A & Point B */}
      {pointA && pointB && (
        <line>
          <bufferGeometry>
            <bufferAttribute
              attach="attributes-position"
              args={[
                new Float32Array([
                  pointA[0],
                  pointA[1] + 0.05,
                  pointA[2],
                  pointB[0],
                  pointB[1] + 0.05,
                  pointB[2],
                ]),
                3,
              ]}
            />
          </bufferGeometry>
          <lineBasicMaterial color="#38bdf8" linewidth={3} />
        </line>
      )}

      {/* Dimension Distance Badge in 3D Scene */}
      {midPoint && distanceMeters !== null && (
        <group position={midPoint as [number, number, number]}>
          <Html center distanceFactor={12}>
            <div className="bg-cyan-950/90 border border-cyan-400 text-cyan-200 px-3 py-1 rounded-full shadow-2xl text-xs font-bold tracking-wider backdrop-blur-md whitespace-nowrap">
              {distanceMeters.toFixed(2)} m
            </div>
          </Html>
        </group>
      )}

      {/* Floating HUD Instructions */}
      <Html position={[0, 0, 0]} style={{ pointerEvents: 'auto' }}>
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-slate-900/95 border border-cyan-500/50 px-5 py-2.5 rounded-xl shadow-2xl backdrop-blur-lg flex items-center gap-4 text-xs z-50">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-slate-200 font-medium">
              {!pointA
                ? 'Click anywhere to place Point A'
                : !pointB
                ? 'Click second location to place Point B'
                : `Measured: ${distanceMeters?.toFixed(2)} m (Click again to measure another distance)`}
            </span>
          </div>

          <button
            onClick={() => {
              setPointA(null);
              setPointB(null);
              onExit();
            }}
            className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-md text-xs font-semibold border border-slate-700 transition-colors"
          >
            EXIT MEASURE (Esc)
          </button>
        </div>
      </Html>
    </group>
  );
};
