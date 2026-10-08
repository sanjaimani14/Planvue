import React, { useState } from 'react';
import { ModeAResult, WallItem, OpeningItem, RoomPolygon } from '../types';
import { Layers, CheckCircle2, AlertTriangle, Eye, ShieldCheck } from 'lucide-react';

interface PlanViewer2DProps {
  data: ModeAResult;
}

export const PlanViewer2D: React.FC<PlanViewer2DProps> = ({ data }) => {
  const [selectedElement, setSelectedElement] = useState<any>(null);
  const [showOriginal, setShowOriginal] = useState<boolean>(false);
  const [showWalls, setShowWalls] = useState<boolean>(true);
  const [showDoors, setShowDoors] = useState<boolean>(true);
  const [showWindows, setShowWindows] = useState<boolean>(true);
  const [showRooms, setShowRooms] = useState<boolean>(true);

  const { image_width, image_height, walls, doors, windows, rooms, scale } = data;
  const viewBox = `0 0 ${image_width || 1200} ${image_height || 900}`;

  return (
    <div className="relative w-full h-[620px] rounded-2xl overflow-hidden bg-slate-950 border border-white/10 shadow-2xl flex flex-col">
      {/* 2D Toolbar */}
      <div className="p-3 bg-slate-900/90 border-b border-white/10 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-300 font-mono">2D TOPOLOGY HUD:</span>
          <button
            onClick={() => setShowOriginal(!showOriginal)}
            className={`px-2.5 py-1 rounded-lg border transition-colors ${
              showOriginal 
                ? 'bg-indigo-600 text-white border-indigo-500 font-medium' 
                : 'bg-white/5 text-slate-300 border-white/10 hover:bg-white/10'
            }`}
          >
            {showOriginal ? 'Showing Blueprint Raster' : 'Showing Binary Topology'}
          </button>
        </div>

        {/* Layer Filters */}
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={showWalls}
              onChange={(e) => setShowWalls(e.target.checked)}
              className="rounded accent-indigo-500"
            />
            <span>Walls ({walls.length})</span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={showDoors}
              onChange={(e) => setShowDoors(e.target.checked)}
              className="rounded accent-amber-500"
            />
            <span>Doors ({doors.length})</span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={showWindows}
              onChange={(e) => setShowWindows(e.target.checked)}
              className="rounded accent-cyan-500"
            />
            <span>Windows ({windows.length})</span>
          </label>

          <label className="flex items-center gap-1.5 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={showRooms}
              onChange={(e) => setShowRooms(e.target.checked)}
              className="rounded accent-emerald-500"
            />
            <span>Rooms ({rooms.length})</span>
          </label>
        </div>
      </div>

      {/* SVG Canvas & Image Overlay */}
      <div className="relative flex-1 bg-slate-950 flex items-center justify-center overflow-auto p-4">
        <svg
          viewBox={viewBox}
          className="w-full h-full max-h-[540px] object-contain rounded-lg border border-white/5 shadow-inner"
        >
          {/* Background image */}
          <image
            href={showOriginal ? (data.original_image_url || data.processed_image_url) : data.processed_image_url}
            width={image_width}
            height={image_height}
            opacity={0.35}
          />

          {/* Room polygons */}
          {showRooms &&
            rooms.map((r, i) => {
              const pts = r.vertices.map((v) => `${v.x},${v.y}`).join(' ');
              return (
                <g key={r.id}>
                  <polygon
                    points={pts}
                    fill="rgba(99, 102, 241, 0.12)"
                    stroke="rgba(129, 140, 248, 0.5)"
                    strokeWidth="2"
                    strokeDasharray="4 4"
                    className="cursor-pointer hover:fill-indigo-500/25 transition-all"
                    onClick={() => setSelectedElement({ type: 'room', data: r })}
                  />
                  {r.vertices[0] && (
                    <text
                      x={r.vertices.reduce((acc, v) => acc + v.x, 0) / r.vertices.length}
                      y={r.vertices.reduce((acc, v) => acc + v.y, 0) / r.vertices.length}
                      fill="#e0e7ff"
                      fontSize="18"
                      fontWeight="bold"
                      textAnchor="middle"
                      className="pointer-events-none select-none drop-shadow"
                    >
                      {r.name} ({r.area_sqm} m²)
                    </text>
                  )}
                </g>
              );
            })}

          {/* Walls */}
          {showWalls &&
            walls.map((w) => {
              const isCorrected = w.status === 'CORRECTED';
              const strokeColor = isCorrected ? '#f59e0b' : '#f8fafc';
              return (
                <g key={w.id} onClick={() => setSelectedElement({ type: 'wall', data: w })}>
                  <line
                    x1={w.start.x}
                    y1={w.start.y}
                    x2={w.end.x}
                    y2={w.end.y}
                    stroke={strokeColor}
                    strokeWidth={Math.max(w.thickness || 8, 8)}
                    strokeLinecap="round"
                    className="cursor-pointer hover:stroke-indigo-400 transition-colors"
                  />
                  {/* Endpoint markers */}
                  <circle cx={w.start.x} cy={w.start.y} r="4" fill="#6366f1" />
                  <circle cx={w.end.x} cy={w.end.y} r="4" fill="#6366f1" />
                </g>
              );
            })}

          {/* Doors */}
          {showDoors &&
            doors.map((d) => {
              const isCorrected = d.status === 'CORRECTED';
              return (
                <g key={d.id} onClick={() => setSelectedElement({ type: 'door', data: d })}>
                  <circle
                    cx={d.position.x}
                    cy={d.position.y}
                    r={Math.max((d.width_m ? d.width_m * scale.pixels_per_meter : 35) / 2, 14)}
                    fill={isCorrected ? 'rgba(245, 158, 11, 0.25)' : 'rgba(16, 185, 129, 0.25)'}
                    stroke={isCorrected ? '#f59e0b' : '#10b981'}
                    strokeWidth="3"
                    className="cursor-pointer hover:stroke-white transition-colors"
                  />
                  <line
                    x1={d.position.x}
                    y1={d.position.y}
                    x2={d.position.x + 20}
                    y2={d.position.y - 20}
                    stroke={isCorrected ? '#f59e0b' : '#10b981'}
                    strokeWidth="3"
                  />
                </g>
              );
            })}

          {/* Windows */}
          {showWindows &&
            windows.map((win) => {
              return (
                <g key={win.id} onClick={() => setSelectedElement({ type: 'window', data: win })}>
                  <rect
                    x={win.position.x - 25}
                    y={win.position.y - 6}
                    width="50"
                    height="12"
                    fill="rgba(6, 182, 212, 0.3)"
                    stroke="#06b6d4"
                    strokeWidth="2"
                    rx="2"
                    className="cursor-pointer hover:stroke-white transition-colors"
                  />
                </g>
              );
            })}
        </svg>
      </div>

      {/* Selected Element Inspector HUD */}
      {selectedElement && (
        <div className="absolute bottom-4 left-4 right-4 bg-slate-900/95 border border-indigo-500/40 rounded-xl p-3 shadow-2xl backdrop-blur-md flex items-center justify-between text-xs">
          <div className="flex items-center gap-4">
            <span className="font-mono text-indigo-400 font-bold uppercase">
              Selected {selectedElement.type}:
            </span>
            <span className="text-white font-semibold">{selectedElement.data.id || selectedElement.data.name}</span>
            <div className="flex items-center gap-1.5">
              <span className="text-slate-400">Status:</span>
              <span
                className={`font-mono font-bold px-1.5 py-0.5 rounded text-[10px] ${
                  selectedElement.data.status === 'CORRECTED'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                }`}
              >
                {selectedElement.data.status || 'OBSERVED'}
              </span>
            </div>
            {selectedElement.data.repair_note && (
              <span className="text-amber-300/90 italic">Note: {selectedElement.data.repair_note}</span>
            )}
            {selectedElement.data.area_sqm && (
              <span className="text-indigo-300 font-mono font-bold">Area: {selectedElement.data.area_sqm} m²</span>
            )}
          </div>

          <button
            onClick={() => setSelectedElement(null)}
            className="text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-white/10 text-xs"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};
