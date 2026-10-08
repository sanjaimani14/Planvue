import React, { useEffect, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

export type CameraViewMode = 'ORBIT' | 'TOP' | 'FRONT' | 'SIDE' | 'ISOMETRIC' | 'WALK';

interface CameraControlsProps {
  mode: CameraViewMode;
  bounds?: {
    min: [number, number, number];
    max: [number, number, number];
    width_m: number;
    depth_m: number;
    height_m: number;
  };
  resetTrigger: number;
}

export const CameraControls: React.FC<CameraControlsProps> = ({
  mode,
  bounds,
  resetTrigger,
}) => {
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  const width = bounds?.width_m || 10;
  const depth = bounds?.depth_m || 10;
  const height = bounds?.height_m || 3.0;
  const maxDim = Math.max(width, depth, 6);

  // Auto-frame / adjust camera based on mode
  useEffect(() => {
    if (!controlsRef.current) return;

    const center = new THREE.Vector3(0, height / 2, 0);

    switch (mode) {
      case 'TOP':
        camera.position.set(0, maxDim * 1.8, 0.001);
        controlsRef.current.target.set(0, 0, 0);
        break;

      case 'FRONT':
        camera.position.set(0, height / 2, maxDim * 1.5);
        controlsRef.current.target.copy(center);
        break;

      case 'SIDE':
        camera.position.set(maxDim * 1.5, height / 2, 0);
        controlsRef.current.target.copy(center);
        break;

      case 'ISOMETRIC':
        camera.position.set(maxDim * 1.2, maxDim * 1.1, maxDim * 1.2);
        controlsRef.current.target.copy(center);
        break;

      case 'WALK':
        // Eye level 1.7m inside the space
        camera.position.set(0, 1.7, maxDim * 0.4);
        controlsRef.current.target.set(0, 1.7, 0);
        break;

      case 'ORBIT':
      default:
        camera.position.set(maxDim * 1.2, maxDim * 0.9, maxDim * 1.2);
        controlsRef.current.target.copy(center);
        break;
    }

    controlsRef.current.update();
  }, [mode, resetTrigger, maxDim, height, camera]);

  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      enableDamping
      dampingFactor={0.08}
      minDistance={1}
      maxDistance={maxDim * 4}
      maxPolarAngle={mode === 'TOP' ? 0.05 : Math.PI / 2 + 0.05}
    />
  );
};
