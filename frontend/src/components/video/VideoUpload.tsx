import React, { useRef } from 'react';
import { Video, UploadCloud, Film, PlayCircle, Clock, Maximize2, Cpu } from 'lucide-react';
import { VideoMetadataItem } from '../../types';

interface VideoUploadProps {
  metadata: VideoMetadataItem | null;
  isLoading: boolean;
  onUploadFile: (file: File) => void;
  onUseDemoVideo: () => void;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({
  metadata,
  isLoading,
  onUploadFile,
  onUseDemoVideo,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      onUploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-5 backdrop-blur-xl shadow-xl flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/20 text-indigo-400 flex items-center justify-center border border-indigo-500/30">
            <Video className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white tracking-wide">Video Ingestion</h3>
            <p className="text-[11px] text-slate-400">Handheld static room walkthrough (MP4, MOV, WEBM)</p>
          </div>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
          Mode B
        </span>
      </div>

      {/* Drop Zone */}
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-white/15 hover:border-indigo-500/60 rounded-xl p-5 text-center cursor-pointer transition-all bg-white/[0.02] hover:bg-indigo-500/[0.03] group"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="video/mp4,video/quicktime,video/webm,video/avi"
          className="hidden"
          onChange={handleFileChange}
        />
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-slate-800/80 flex items-center justify-center text-slate-400 group-hover:text-indigo-400 group-hover:scale-110 transition-all border border-white/5">
          <UploadCloud className="w-6 h-6" />
        </div>
        <p className="text-xs font-semibold text-slate-200">
          Drop walkthrough video here or <span className="text-indigo-400 underline">browse</span>
        </p>
        <p className="text-[11px] text-slate-500 mt-1">Recommended: 8–60s smooth motion, up to 120MB</p>
      </div>

      {/* Preset Demo Video Button */}
      <button
        onClick={onUseDemoVideo}
        disabled={isLoading}
        className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-indigo-600/30 to-violet-600/30 hover:from-indigo-600/50 hover:to-violet-600/50 border border-indigo-500/40 text-indigo-200 text-xs font-semibold flex items-center justify-center gap-2 transition-all shadow-md disabled:opacity-50"
      >
        <PlayCircle className="w-4 h-4 text-indigo-400" />
        Use Demo Room Walkthrough (Occluded North Wall)
      </button>

      {/* Metadata Telemetry Badges */}
      {metadata && (
        <div className="bg-slate-950/60 border border-white/5 rounded-xl p-3.5 flex flex-col gap-2">
          <div className="flex items-center justify-between text-xs font-medium text-slate-300">
            <span className="truncate max-w-[200px] text-slate-400">{metadata.filename}</span>
            <span className="font-mono text-indigo-400">{(metadata.size_bytes / (1024 * 1024)).toFixed(1)} MB</span>
          </div>
          <div className="grid grid-cols-3 gap-2 pt-1 border-t border-white/5 text-[11px]">
            <div className="flex items-center gap-1.5 text-slate-400">
              <Clock className="w-3.5 h-3.5 text-indigo-400" />
              <span>{metadata.duration_seconds}s</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Film className="w-3.5 h-3.5 text-indigo-400" />
              <span>{metadata.total_frames} frames ({metadata.fps} fps)</span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-400">
              <Maximize2 className="w-3.5 h-3.5 text-indigo-400" />
              <span>{metadata.width}×{metadata.height}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
