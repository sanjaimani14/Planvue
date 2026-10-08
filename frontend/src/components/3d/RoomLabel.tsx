import React from 'react';
import { Html } from '@react-three/drei';
import { Floor3D } from '../../types';

interface RoomLabelProps {
  room: Floor3D;
  visible: boolean;
}

export const RoomLabel: React.FC<RoomLabelProps> = ({ room, visible }) => {
  if (!visible) return null;

  const [cx, , cz] = room.centroid || [0, 0.2, 0];
  const displayName = room.label ? room.label.toUpperCase() : `ROOM ${room.id}`;

  return (
    <group position={[cx, 0.25, cz]}>
      <Html
        center
        distanceFactor={15}
        zIndexRange={[100, 0]}
        style={{
          pointerEvents: 'none',
          userSelect: 'none',
          whiteSpace: 'nowrap',
        }}
      >
        <div className="flex flex-col items-center bg-slate-900/85 backdrop-blur-md border border-cyan-500/30 px-3 py-1.5 rounded-lg shadow-xl text-center transform -translate-y-2">
          <span className="text-[11px] font-bold tracking-wider text-cyan-300">
            {displayName}
          </span>
          {room.area_m2 > 0 && (
            <span className="text-[9px] font-medium text-slate-400">
              {room.area_m2.toFixed(1)} m²
            </span>
          )}
        </div>
      </Html>
    </group>
  );
};
