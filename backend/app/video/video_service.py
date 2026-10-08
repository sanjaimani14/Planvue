"""
Video Reconstruction Orchestrator and Asynchronous Job Manager for Mode B.
Coordinates the 10-stage Mode B pipeline with real-time stage telemetry and honest error handling.
"""

import time
import uuid
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import cv2
import numpy as np

from backend.app.video.schemas import (
    VideoMetadata, QualityReport, KeyframeItem, VideoJob, VideoScene
)
from backend.app.video.video_ingestion import validate_and_ingest_video
from backend.app.video.frame_quality import analyze_video_stream_quality
from backend.app.video.frame_extraction import extract_intelligent_keyframes
from backend.app.video.feature_tracking import FeatureTracker
from backend.app.video.camera_estimation import estimate_camera_trajectory
from backend.app.video.reconstruction import triangulate_pairwise_points, fit_planes_ransac
from backend.app.video.coverage import compute_spatial_coverage
from backend.app.video.unseen_detection import detect_unseen_regions
from backend.app.video.completion import complete_unseen_regions
from backend.app.video.scene_fusion import assemble_video_scene
from backend.app.reconstruction.exporter import export_glb, export_json

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEO_DIR = DATA_DIR / "video"
OUTPUTS_DIR = BASE_DIR / "outputs"
SCENES_DIR = OUTPUTS_DIR / "scenes"

for d in [VIDEO_DIR, SCENES_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# In-memory storage for active video jobs and scenes
ACTIVE_VIDEO_JOBS: Dict[str, VideoJob] = {}
ACTIVE_VIDEO_SCENES: Dict[str, Dict[str, Any]] = {}
ACTIVE_VIDEO_RAW: Dict[str, Dict[str, Any]] = {}

class VideoService:
    def __init__(self):
        self.tracker = FeatureTracker(n_features=1200, ratio_thresh=0.76)

    def create_job(self, video_id: str) -> VideoJob:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        now = time.time()
        job = VideoJob(
            job_id=job_id,
            video_id=video_id,
            status="QUEUED",
            progress=0.0,
            stage="INITIALIZING",
            message="Video reconstruction job queued",
            created_at=now,
            updated_at=now
        )
        ACTIVE_VIDEO_JOBS[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[VideoJob]:
        return ACTIVE_VIDEO_JOBS.get(job_id)

    def get_scene(self, video_id: str) -> Optional[Dict[str, Any]]:
        return ACTIVE_VIDEO_SCENES.get(video_id)

    def run_pipeline_sync(
        self,
        video_path: str,
        video_id: str,
        job_id: Optional[str] = None,
        target_keyframes: int = 14
    ) -> Dict[str, Any]:
        """Executes the complete 10-stage Mode B video reconstruction pipeline synchronously."""
        t0 = time.time()

        def update_progress(prog: float, stage: str, msg: str):
            if job_id and job_id in ACTIVE_VIDEO_JOBS:
                job = ACTIVE_VIDEO_JOBS[job_id]
                job.progress = prog
                job.stage = stage
                job.message = msg
                job.updated_at = time.time()

        update_progress(5.0, "INGESTION", "Validating video container and metadata...")
        is_valid, meta, err = validate_and_ingest_video(video_path, video_id=video_id)
        if not is_valid or meta is None:
            raise ValueError(f"Video validation failed: {err}")

        # Stage 2: Video Quality Analysis
        update_progress(15.0, "QUALITY_CHECK", "Evaluating sharpness, exposure, and motion...")
        quality_rep = analyze_video_stream_quality(video_path)

        # Stage 3: Intelligent Keyframe Extraction
        update_progress(30.0, "KEYFRAME_EXTRACTION", "Selecting optimal sharp keyframes...")
        kf_items, kf_matrices = extract_intelligent_keyframes(
            video_path, video_id=video_id, target_keyframes=target_keyframes
        )
        if len(kf_matrices) < 2:
            raise ValueError("Insufficient usable keyframes could be extracted from video.")

        # Stage 4: Feature Extraction and Pairwise Matching
        update_progress(45.0, "FEATURE_TRACKING", "Detecting and matching visual features across views...")
        all_kps, all_des = self.tracker.extract_features(kf_matrices)
        
        pts_pairs = []
        for i in range(len(kf_matrices) - 1):
            p1, p2, _ = self.tracker.match_pair(
                all_kps[i], all_des[i], all_kps[i + 1], all_des[i + 1]
            )
            pts_pairs.append((p1, p2))

        # Stage 5: Camera Motion Estimation
        update_progress(60.0, "CAMERA_ESTIMATION", "Estimating 6-DOF camera trajectory via Essential Matrix...")
        timestamps = [kf.timestamp_s for kf in kf_items]
        cam_poses, K, proj_matrices = estimate_camera_trajectory(
            pts_pairs, timestamps, meta.width, meta.height
        )

        # Stage 6: Triangulation & Surface Planes
        update_progress(72.0, "TRIANGULATION", "Triangulating 3D point cloud and fitting structural planes...")
        all_3d_points = []
        for i in range(len(pts_pairs)):
            p1, p2 = pts_pairs[i]
            if len(p1) >= 8 and len(p2) >= 8:
                tri_pts = triangulate_pairwise_points(
                    proj_matrices[i], proj_matrices[i + 1],
                    p1, p2, i, i + 1, kf_matrices[i]
                )
                all_3d_points.extend(tri_pts)

        # Fit planes via RANSAC
        planes = fit_planes_ransac(all_3d_points, max_planes=4)

        # Stage 7: Spatial Coverage Map
        update_progress(82.0, "COVERAGE_ANALYSIS", "Evaluating frustum ray visibility and spatial coverage...")
        coverage, coverage_grid = compute_spatial_coverage(cam_poses, all_3d_points)

        # Stage 8: Unseen Region Detection
        update_progress(88.0, "UNSEEN_DETECTION", "Identifying occluded sectors and unobserved perimeter walls...")
        unseen_regs = detect_unseen_regions(cam_poses, all_3d_points, planes, coverage)

        # Stage 9: Conservative Completion
        update_progress(94.0, "COMPLETION", "Generating constraint-guided geometric continuation and shell closure...")
        completions = complete_unseen_regions(unseen_regs, planes, coverage)

        # Stage 10: Unified 3D Scene Assembly & GLB Export
        update_progress(98.0, "SCENE_ASSEMBLY", "Compiling 3D scene representation and validating mesh manifold...")
        elapsed_ms = (time.time() - t0) * 1000.0
        
        telemetry_metrics = {
            "total_frames": meta.total_frames,
            "processing_time_ms": round(elapsed_ms, 1),
            "units": "relative",
            "scale_mode": "relative",
            "scale_source": "relative_camera_step"
        }

        video_scene, raw_scene_dict = assemble_video_scene(
            video_id=video_id,
            camera_poses=cam_poses,
            points_3d=all_3d_points,
            planes=planes,
            coverage=coverage,
            unseen_regions=unseen_regs,
            completions=completions,
            metrics_data=telemetry_metrics
        )

        # Persist scene GLB and JSON to outputs/scenes/
        glb_out_path = SCENES_DIR / f"planevue_video_{video_id}.glb"
        json_out_path = SCENES_DIR / f"planevue_video_{video_id}.json"
        export_glb(raw_scene_dict, str(glb_out_path))
        export_json(raw_scene_dict, str(json_out_path))

        video_scene.artifacts = {
            "glb_url": f"/outputs/scenes/planevue_video_{video_id}.glb",
            "json_url": f"/outputs/scenes/planevue_video_{video_id}.json"
        }
        raw_scene_dict["artifacts"] = video_scene.artifacts

        # Cache scene
        ACTIVE_VIDEO_SCENES[video_id] = video_scene.model_dump()
        ACTIVE_VIDEO_RAW[video_id] = raw_scene_dict

        if job_id and job_id in ACTIVE_VIDEO_JOBS:
            job = ACTIVE_VIDEO_JOBS[job_id]
            job.status = "COMPLETED"
            job.progress = 100.0
            job.stage = "COMPLETED"
            job.message = "Video 3D reconstruction and unseen completion completed successfully."
            job.result = video_scene.model_dump()
            job.updated_at = time.time()

        return video_scene.model_dump()

    def start_pipeline_async(self, video_path: str, video_id: str, job_id: str) -> None:
        """Launches video pipeline in a background worker thread."""
        def worker():
            try:
                self.run_pipeline_sync(video_path, video_id, job_id=job_id)
            except Exception as e:
                import traceback
                traceback.print_exc()
                if job_id in ACTIVE_VIDEO_JOBS:
                    job = ACTIVE_VIDEO_JOBS[job_id]
                    job.status = "FAILED"
                    job.stage = "ERROR"
                    job.message = f"Pipeline execution failed: {str(e)}"
                    job.error = str(e)
                    job.updated_at = time.time()

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

video_service = VideoService()
