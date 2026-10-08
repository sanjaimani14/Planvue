import React, { useState, useEffect } from 'react';
import {
  VideoMetadataItem,
  QualityReportItem,
  KeyframeItemType,
  VideoSceneItem
} from '../types';
import {
  uploadVideoApi,
  analyzeVideoQualityApi,
  getVideoKeyframesApi,
  reconstructVideoSceneApi,
  getVideoJobStatusApi,
  getVideoSceneApi,
  exportVideoSceneApi
} from '../services/api';
import { VideoUpload } from '../components/video/VideoUpload';
import { FrameTimeline } from '../components/video/FrameTimeline';
import { CoverageMap } from '../components/video/CoverageMap';
import { UnseenRegionOverlay } from '../components/video/UnseenRegionOverlay';
import { CompletionControls, ProvenanceFilter } from '../components/video/CompletionControls';
import { VideoSceneViewer } from '../components/video/VideoSceneViewer';
import { VideoMetricsPanel } from '../components/video/VideoMetricsPanel';
import {
  Video,
  Play,
  RotateCcw,
  Sparkles,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  Clock,
  Layers,
  FileCheck
} from 'lucide-react';

export const VideoReconstructionPage: React.FC = () => {
  // Video & File state
  const [videoId, setVideoId] = useState<string | null>(null);
  const [metadata, setMetadata] = useState<VideoMetadataItem | null>(null);
  const [qualityReport, setQualityReport] = useState<QualityReportItem | null>(null);
  const [keyframes, setKeyframes] = useState<KeyframeItemType[]>([]);
  const [selectedKeyframeIndex, setSelectedKeyframeIndex] = useState<number | null>(null);

  // Pipeline & Job state
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<string>('IDLE');
  const [progressPct, setProgressPct] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string>('Upload a room video to begin.');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // 3D Scene state
  const [scene, setScene] = useState<VideoSceneItem | null>(null);
  const [provenanceFilter, setProvenanceFilter] = useState<ProvenanceFilter>('ALL');
  const [showCameras, setShowCameras] = useState<boolean>(true);
  const [showPointCloud, setShowPointCloud] = useState<boolean>(true);
  const [showUnseenVolumes, setShowUnseenVolumes] = useState<boolean>(true);
  const [selectedRegionId, setSelectedRegionId] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState<boolean>(false);

  // Auto-run on Demo Video
  const handleUseDemoVideo = async () => {
    try {
      setIsProcessing(true);
      setErrorMessage(null);
      setStatusMessage('Ingesting demo room walkthrough...');
      setCurrentStage('INGESTION');
      setProgressPct(10);

      const uploadRes = await uploadVideoApi(undefined, true);
      setVideoId(uploadRes.video_id);
      setMetadata(uploadRes.metadata);

      // Analyze Quality
      setStatusMessage('Evaluating frame sharpness and exposure...');
      setCurrentStage('QUALITY_CHECK');
      setProgressPct(25);
      const qualRes = await analyzeVideoQualityApi(uploadRes.video_id);
      setQualityReport(qualRes.quality_report);

      // Extract Keyframes
      setStatusMessage('Extracting sharp visual keyframes...');
      setCurrentStage('KEYFRAME_EXTRACTION');
      setProgressPct(40);
      const kfRes = await getVideoKeyframesApi(uploadRes.video_id, 10);
      setKeyframes(kfRes.keyframes);

      // Reconstruct
      setStatusMessage('Estimating camera trajectory & 3D unseen completion...');
      setCurrentStage('RECONSTRUCTING');
      setProgressPct(70);
      const recRes = await reconstructVideoSceneApi(uploadRes.video_id, 10, undefined, false);
      setScene(recRes.scene);

      setProgressPct(100);
      setCurrentStage('COMPLETED');
      setStatusMessage('Reconstruction and unseen completion completed successfully.');
    } catch (err: any) {
      setErrorMessage(err.message || 'Pipeline execution failed.');
      setCurrentStage('ERROR');
    } finally {
      setIsProcessing(false);
    }
  };

  // Upload user file
  const handleUploadFile = async (file: File) => {
    try {
      setIsProcessing(true);
      setErrorMessage(null);
      setStatusMessage('Uploading and validating video container...');
      setCurrentStage('INGESTION');
      setProgressPct(10);

      const uploadRes = await uploadVideoApi(file, false);
      setVideoId(uploadRes.video_id);
      setMetadata(uploadRes.metadata);

      // Analyze Quality
      setStatusMessage('Evaluating frame sharpness and exposure...');
      setCurrentStage('QUALITY_CHECK');
      setProgressPct(25);
      const qualRes = await analyzeVideoQualityApi(uploadRes.video_id);
      setQualityReport(qualRes.quality_report);

      // Extract Keyframes
      setStatusMessage('Extracting sharp keyframes...');
      setCurrentStage('KEYFRAME_EXTRACTION');
      setProgressPct(45);
      const kfRes = await getVideoKeyframesApi(uploadRes.video_id, 12);
      setKeyframes(kfRes.keyframes);

      // Reconstruct
      setStatusMessage('Running 6-DOF camera tracking & unseen completion...');
      setCurrentStage('RECONSTRUCTING');
      setProgressPct(75);
      const recRes = await reconstructVideoSceneApi(uploadRes.video_id, 12, undefined, false);
      setScene(recRes.scene);

      setProgressPct(100);
      setCurrentStage('COMPLETED');
      setStatusMessage('Reconstruction completed.');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to process uploaded video.');
      setCurrentStage('ERROR');
    } finally {
      setIsProcessing(false);
    }
  };

  // Export handlers
  const handleExportGlb = async () => {
    if (!videoId) return;
    try {
      setIsExporting(true);
      const blob = await exportVideoSceneApi(videoId, 'glb');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `planevue_video_${videoId}.glb`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e: any) {
      alert(`GLB export failed: ${e.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportJson = async () => {
    if (!videoId) return;
    try {
      setIsExporting(true);
      const blob = await exportVideoSceneApi(videoId, 'json');
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `planevue_video_${videoId}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e: any) {
      alert(`JSON export failed: ${e.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="flex-1 max-w-7xl w-full mx-auto p-6 flex flex-col gap-6 animate-fade-in">
      {/* Title Header & Mode B Description */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-black tracking-wide text-white">
              MODE B — Room Video → 3D Scene + Unseen-Region Completion
            </h1>
            <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              Active
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Upload a static room walkthrough. PLANE VUE estimates camera motion, reconstructs observed surfaces, evaluates volumetric visibility, and generates conservative constraint-aware completions with explicit provenance (Observed vs Inferred vs Generated).
          </p>
        </div>

        {/* Status Pill */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-white/10 text-xs">
            {currentStage === 'COMPLETED' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            ) : isProcessing ? (
              <div className="w-3.5 h-3.5 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
            ) : (
              <Clock className="w-4 h-4 text-slate-400" />
            )}
            <span className="font-mono text-slate-200 text-[11px]">{statusMessage}</span>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Progress Bar when running */}
      {isProcessing && (
        <div className="w-full bg-slate-900/80 rounded-xl p-3 border border-white/10 flex flex-col gap-1.5">
          <div className="flex items-center justify-between text-xs text-slate-300 font-mono">
            <span>Stage: {currentStage}</span>
            <span>{progressPct}%</span>
          </div>
          <div className="w-full h-2 rounded-full bg-slate-950 overflow-hidden">
            <div
              style={{ width: `${progressPct}%` }}
              className="bg-indigo-500 h-full transition-all duration-300"
            />
          </div>
        </div>
      )}

      {/* 3-Column Layout: Left (Inputs/Keyframes), Center (3D Viewer), Right (Coverage/Unseen/Controls) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Upload, Quality, Keyframe Timeline (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-5">
          <VideoUpload
            metadata={metadata}
            isLoading={isProcessing}
            onUploadFile={handleUploadFile}
            onUseDemoVideo={handleUseDemoVideo}
          />

          {/* Frame Quality Telemetry */}
          {qualityReport && (
            <div className="bg-slate-900/80 border border-white/10 rounded-2xl p-4 backdrop-blur-xl shadow-xl flex flex-col gap-2.5">
              <div className="flex items-center justify-between text-xs font-bold text-white">
                <span>Frame Quality Assessment</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    qualityReport.quality_grade === 'GOOD'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                  }`}
                >
                  {qualityReport.quality_grade}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                <div className="bg-slate-950/60 p-2 rounded-lg border border-white/5">
                  Mean Sharpness: <strong className="text-white font-mono">{qualityReport.sharpness_score}</strong>
                </div>
                <div className="bg-slate-950/60 p-2 rounded-lg border border-white/5">
                  Exposure: <strong className="text-white font-mono">{qualityReport.exposure_status}</strong>
                </div>
              </div>
              {qualityReport.warnings.length > 0 && (
                <div className="text-[10px] text-amber-300/90 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20 mt-1">
                  {qualityReport.warnings.join(' ')}
                </div>
              )}
            </div>
          )}

          {/* Keyframe Timeline */}
          <FrameTimeline
            keyframes={keyframes}
            selectedKeyframeIndex={selectedKeyframeIndex}
            onSelectKeyframe={(idx) => setSelectedKeyframeIndex(idx)}
          />
        </div>

        {/* Center & Right Column (8 cols) */}
        <div className="lg:col-span-8 flex flex-col gap-5">
          {/* 3D Scene Viewer */}
          {scene ? (
            <VideoSceneViewer
              scene={scene}
              provenanceFilter={provenanceFilter}
              showCameras={showCameras}
              showPointCloud={showPointCloud}
              showUnseenVolumes={showUnseenVolumes}
              selectedKeyframeIndex={selectedKeyframeIndex}
              selectedRegionId={selectedRegionId}
              onSelectElement={(elem) => {
                if (elem && elem.region_id) setSelectedRegionId(elem.region_id);
              }}
            />
          ) : (
            <div className="w-full h-[540px] rounded-2xl border border-white/10 bg-slate-950/80 flex flex-col items-center justify-center text-center p-8 gap-3">
              <div className="w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <Video className="w-8 h-8" />
              </div>
              <h3 className="text-sm font-bold text-white">No 3D Video Reconstruction Active</h3>
              <p className="text-xs text-slate-400 max-w-md">
                Upload a room walkthrough or click &quot;Use Demo Room Walkthrough&quot; on the left to extract keyframes, estimate camera poses, and generate conservative unseen completion.
              </p>
            </div>
          )}

          {/* Controls & Unseen Inspection Row */}
          {scene && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CompletionControls
                provenanceFilter={provenanceFilter}
                onSetProvenanceFilter={(f) => setProvenanceFilter(f)}
                showCameras={showCameras}
                onToggleCameras={() => setShowCameras(!showCameras)}
                showPointCloud={showPointCloud}
                onTogglePointCloud={() => setShowPointCloud(!showPointCloud)}
                showUnseenVolumes={showUnseenVolumes}
                onToggleUnseenVolumes={() => setShowUnseenVolumes(!showUnseenVolumes)}
              />

              <CoverageMap coverage={scene.coverage} />
            </div>
          )}

          {/* Unseen Region List */}
          {scene && (
            <UnseenRegionOverlay
              unseenRegions={scene.unseen_regions}
              completionRegions={scene.completion_regions}
              selectedRegionId={selectedRegionId}
              onSelectRegion={(id) => setSelectedRegionId(id)}
            />
          )}

          {/* Bottom Telemetry & Export */}
          {scene && (
            <VideoMetricsPanel
              metrics={scene.metrics}
              onExportGlb={handleExportGlb}
              onExportJson={handleExportJson}
              isExporting={isExporting}
            />
          )}
        </div>
      </div>

      {/* Judge Mode / Scientific Research Contribution Explanation */}
      <div className="bg-slate-900/60 border border-white/10 rounded-2xl p-5 backdrop-blur-xl flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Judge Mode — Visibility-Aware Constraint Completion
          </h3>
        </div>
        <p className="text-xs text-slate-400 leading-relaxed">
          Rather than silently inventing unobserved spaces with arbitrary generative models, <strong>PLANE VUE</strong> rigorously separates <strong>Observed</strong> visual data (multi-view tracked features and RANSAC planes) from <strong>Inferred</strong> structure (Level 1 geometric continuation and Level 2 symmetry) and <strong>Generated</strong> enclosures (Level 3 room envelope bounding constraints). Every completion carries explainable provenance, camera visibility evidence, and conservative confidence levels.
        </p>
      </div>
    </div>
  );
};
