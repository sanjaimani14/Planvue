import React from 'react';
import { KeyframeItemType } from '../../types';
import { Film, Eye, Sparkles } from 'lucide-react';

interface FrameTimelineProps {
  keyframes: KeyframeItemType[];
  selectedKeyframeIndex: number | null;
  onSelectKeyframe: (index: number) => void;
}

export const FrameTimeline: React.FC<FrameTimelineProps> = ({
  keyframes,
  selectedKeyframeIndex,
  onSelectKeyframe,
}) => {
  if (keyframes.length === 0) return null;

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Film className="w-4 h-4 text-indigo-400" />
          <h4 className="text-xs font-bold text-white uppercase tracking-wider">
            Keyframe Timeline ({keyframes.length} Selected)
          </h4>
        </div>
        <span className="text-[10px] text-slate-400 font-mono">
          Click to inspect camera pose
        </span>
      </div>

      {/* Horizontal Scroll of Extracted Keyframes */}
      <div className="flex gap-2.5 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
        {keyframes.map((kf) => {
          const isSelected = selectedKeyframeIndex === kf.index;
          return (
            <div
              key={kf.index}
              onClick={() => onSelectKeyframe(kf.index)}
              className={`flex-shrink-0 w-28 rounded-xl border p-1.5 cursor-pointer transition-all ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-500/20 shadow-lg shadow-indigo-500/20 scale-[1.03]'
                  : 'border-white/10 bg-slate-950/60 hover:border-white/30 hover:bg-white/[0.03]'
              }`}
            >
              <div className="w-full h-16 rounded-lg overflow-hidden bg-slate-900 relative">
                <img
                  src={kf.image_url}
                  alt={`Keyframe ${kf.index}`}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
                <span className="absolute bottom-1 right-1 text-[9px] font-mono px-1 py-0.5 rounded bg-black/70 text-slate-200">
                  {kf.timestamp_s}s
                </span>
              </div>
              <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span>KF {kf.index + 1}</span>
                <span className="flex items-center gap-0.5 text-emerald-400">
                  <Sparkles className="w-2.5 h-2.5" />
                  {Math.round(kf.sharpness)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
