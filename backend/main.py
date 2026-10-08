import os
import time
import uuid
import json
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from backend.config import (
    BASE_DIR, DEMO_DIR, OUTPUTS_DIR,
    DEFAULT_WALL_HEIGHT_METERS, DEFAULT_WALL_THICKNESS_METERS
)
from backend.schemas import (
    ModeAResponse, ModeBResponse, ScaleCalibration, EvaluationMetrics
)
from ai.image_preprocessing import normalize_and_deskew
from ai.floorplan_detector import detect_floorplan_elements
from ai.ocr_dimension_extractor import extract_dimension_strings_and_lines
from ai.metric_calibration import calibrate_metric_scale
from ai.video_processor import extract_keyframes_from_video

from reconstruction.geometry_constraints import apply_geometry_constraints_and_repair
from reconstruction.scene_builder_3d import build_3d_building_scene
from reconstruction.video_sfm import run_sparse_sfm
from reconstruction.spatial_coverage import compute_camera_spatial_coverage
from reconstruction.unseen_completion import generate_unseen_region_completion, export_mode_b_glb

from evaluation.metrics import compute_mode_a_metrics
from evaluation.baseline_mode_a import run_classical_baseline_mode_a
from evaluation.ablation_framework import run_ablation_experiments
from backend.export_service import export_project_report

app = FastAPI(
    title="PLANE VUE API",
    description="AI-Powered 2D Blueprint & Room Video → 3D Scene Reconstruction Platform",
    version="1.0.0"
)

# Enable CORS for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs and demo directories for static access
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
app.mount("/demo", StaticFiles(directory=str(DEMO_DIR)), name="demo")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "PLANE VUE",
        "tagline": "See the space. Reconstruct the unseen.",
        "modes": ["MODE_A_BLUEPRINT", "MODE_B_ROOM_VIDEO"],
        "demo_available": {
            "sample_floorplan": (DEMO_DIR / "sample_floorplan.png").exists(),
            "sample_room_video": (DEMO_DIR / "sample_room.mp4").exists(),
            "ground_truth": (DEMO_DIR / "expected" / "ground_truth.json").exists()
        }
    }


@app.post("/api/reconstruct/mode-a")
async def reconstruct_mode_a(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False),
    wall_height: float = Form(DEFAULT_WALL_HEIGHT_METERS),
    use_ground_truth: bool = Form(False)
):
    """
    MODE A Pipeline:
    Blueprint Upload → Preprocessing → Detection → Metric Scale Calibration →
    Geometry Constraint Engine → 3D Building Scene Generation → Metrics & Ablations → Export
    """
    start_time = time.time()
    job_id = f"job_a_{uuid.uuid4().hex[:8]}"
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Convert Form objects to primitives if called directly
    try:
        wall_height_val = float(wall_height)
    except Exception:
        wall_height_val = DEFAULT_WALL_HEIGHT_METERS

    is_demo_val = bool(is_demo) if not hasattr(is_demo, 'default') else False
    use_gt_val = bool(use_ground_truth) if not hasattr(use_ground_truth, 'default') else False

    # 1. Determine input file
    input_path = job_dir / "input_plan.png"
    if is_demo_val or file is None:
        demo_sample = DEMO_DIR / "sample_floorplan.png"
        if not demo_sample.exists():
            raise HTTPException(status_code=404, detail="Demo blueprint sample not found")
        shutil.copy(demo_sample, input_path)
    else:
        # Validate format
        suffix = Path(file.filename).suffix.lower()
        if suffix not in [".png", ".jpg", ".jpeg", ".pdf", ".webp"]:
            raise HTTPException(status_code=400, detail="Invalid format. Supported: PNG, JPG, JPEG, PDF")
        input_path = job_dir / f"input_plan{suffix}"
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)

    try:
        # 2. Image Preprocessing
        norm_bgr, binary, prep_meta = normalize_and_deskew(str(input_path))
        import cv2
        proc_img_path = job_dir / "processed_binary.png"
        cv2.imwrite(str(proc_img_path), binary)

        # 3. Floor Plan Semantic Detection
        detected = detect_floorplan_elements(binary, norm_bgr)
        raw_walls = detected["walls"]
        raw_doors = detected["doors"]
        raw_windows = detected["windows"]
        raw_rooms = detected["rooms"]

        # 4. OCR & Dimension extraction
        dimensions = extract_dimension_strings_and_lines(
            cv2.cvtColor(norm_bgr, cv2.COLOR_BGR2GRAY), binary
        )

        # 5. Metric Scale Calibration
        scale_info = calibrate_metric_scale(dimensions, raw_doors, raw_walls, norm_bgr.shape)
        ppm = scale_info["pixels_per_meter"]

        # 6. Geometry Constraint Engine & Repair
        repaired_walls, repaired_doors, repaired_windows, repaired_rooms, val_logs = (
            apply_geometry_constraints_and_repair(
                raw_walls, raw_doors, raw_windows, raw_rooms, ppm
            )
        )

        # 7. 3D Scene Generation (GLB Export)
        glb_filename = f"building_{job_id}.glb"
        glb_path = job_dir / glb_filename
        build_3d_building_scene(
            walls=repaired_walls,
            doors=repaired_doors,
            windows=repaired_windows,
            rooms=repaired_rooms,
            ppm=ppm,
            wall_height=wall_height_val,
            output_glb_path=str(glb_path)
        )

        # 8. Evaluation Metrics & Baselines
        elapsed_ms = (time.time() - start_time) * 1000.0
        gt_data = None
        if use_gt_val or is_demo_val:
            gt_file = DEMO_DIR / "expected" / "ground_truth.json"
            if gt_file.exists():
                with open(gt_file, "r") as f:
                    gt_data = json.load(f)

        metrics = compute_mode_a_metrics(
            walls=repaired_walls,
            doors=repaired_doors,
            windows=repaired_windows,
            rooms=repaired_rooms,
            validation_logs=val_logs,
            scale_info=scale_info,
            processing_time_ms=elapsed_ms,
            ground_truth=gt_data
        )

        # 9. Ablations Table
        ablations = run_ablation_experiments(
            raw_wall_count=len(raw_walls),
            calibrated_scale=scale_info,
            repaired_walls=repaired_walls,
            doors=repaired_doors,
            rooms=repaired_rooms,
            validation_logs=val_logs
        )

        # 10. Generate Markdown Technical Report & Save Metadata
        scene_meta = {
            "job_id": job_id,
            "mode": "BLUEPRINT",
            "image_width": prep_meta["processed_width"],
            "image_height": prep_meta["processed_height"],
            "deskew_degrees": prep_meta.get("skew_angle_degrees", 0.0),
            "scale": scale_info,
            "walls": repaired_walls,
            "doors": repaired_doors,
            "windows": repaired_windows,
            "rooms": repaired_rooms,
            "dimensions": dimensions,
            "validation_logs": val_logs,
            "metrics": metrics,
            "ablations": ablations,
            "glb_file": glb_filename
        }
        with open(job_dir / "scene_metadata.json", "w") as f:
            json.dump(scene_meta, f, indent=2)

        report_path = export_project_report(job_id, "BLUEPRINT", scene_meta, job_dir)

        return {
            "success": True,
            "job_id": job_id,
            "mode": "BLUEPRINT",
            "image_width": prep_meta["processed_width"],
            "image_height": prep_meta["processed_height"],
            "scale": scale_info,
            "walls": repaired_walls,
            "doors": repaired_doors,
            "windows": repaired_windows,
            "rooms": repaired_rooms,
            "dimensions": dimensions,
            "validation_logs": val_logs,
            "metrics": metrics,
            "ablations": ablations,
            "glb_url": f"/outputs/{job_id}/{glb_filename}",
            "processed_image_url": f"/outputs/{job_id}/processed_binary.png",
            "original_image_url": f"/outputs/{job_id}/{input_path.name}",
            "report_url": f"/outputs/{job_id}/{Path(report_path).name}"
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Mode A Reconstruction failed: {str(e)}")


@app.post("/api/reconstruct/mode-b")
async def reconstruct_mode_b(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False)
):
    """
    MODE B Pipeline:
    Room Video Upload → Keyframe Selection → Structure-from-Motion (Camera Tracking & Triangulation)
    → 3D Spatial Coverage Raycast → Unseen Region Procedural Completion Engine → GLB Export
    """
    start_time = time.time()
    job_id = f"job_b_{uuid.uuid4().hex[:8]}"
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    is_demo_val = bool(is_demo) if not hasattr(is_demo, 'default') else False

    input_path = job_dir / "input_room.mp4"
    if is_demo_val or file is None:
        demo_sample = DEMO_DIR / "sample_room.mp4"
        if not demo_sample.exists():
            raise HTTPException(status_code=404, detail="Demo room video sample not found")
        shutil.copy(demo_sample, input_path)
    else:
        suffix = Path(file.filename).suffix.lower()
        if suffix not in [".mp4", ".mov", ".avi", ".webm"]:
            raise HTTPException(status_code=400, detail="Invalid video format. Supported: MP4, MOV, AVI")
        input_path = job_dir / f"input_room{suffix}"
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)

    try:
        # 1. Keyframe Extraction & Filtering
        keyframes, kf_meta = extract_keyframes_from_video(str(input_path), max_keyframes=12)
        if len(keyframes) < 2:
            raise HTTPException(
                status_code=400,
                detail="Video reconstruction could not establish enough valid keyframes. Try a slower walkthrough with more overlapping views."
            )

        # 2. Camera Motion Tracking & Sparse SfM
        camera_poses, points_3d = run_sparse_sfm(keyframes)

        # 3. Spatial Camera Coverage Analysis (Observed vs Partially Observed vs Unseen)
        coverage = compute_camera_spatial_coverage(camera_poses, points_3d)

        # 4. Geometry-Aware Unseen Region Completion Engine
        completed_geoms, scene_3d = generate_unseen_region_completion(
            coverage, points_3d, camera_poses
        )

        # 5. Export 3D Scene GLB
        glb_filename = f"scene_{job_id}.glb"
        glb_path = job_dir / glb_filename
        export_mode_b_glb(scene_3d, str(glb_path))

        elapsed_ms = (time.time() - start_time) * 1000.0

        # Quality metrics (honest rule: no fabricated PSNR/SSIM without held-out ground truth)
        metrics = {
            "keyframes_processed": kf_meta["keyframes_selected"],
            "total_frames_analyzed": kf_meta["total_frames"],
            "mean_sharpness_score": kf_meta["mean_sharpness"],
            "reconstructed_3d_points": len(points_3d),
            "camera_trajectory_views": len(camera_poses),
            "observed_space_volume_m3": coverage["total_space_volume_m3"],
            "processing_time_ms": round(elapsed_ms, 1),
            "psnr_score": "N/A — Held-out camera trajectory frames unavailable",
            "ssim_score": "N/A — Held-out ground truth unavailable",
            "chamfer_distance": "N/A — CAD mesh ground truth not provided"
        }

        # 6. Save Metadata & Report
        scene_meta = {
            "job_id": job_id,
            "mode": "ROOM_VIDEO",
            "total_frames": kf_meta["total_frames"],
            "keyframes_selected": kf_meta["keyframes_selected"],
            "points_count": len(points_3d),
            "camera_poses": camera_poses,
            "coverage": coverage,
            "completed_geometries": completed_geoms,
            "metrics": metrics,
            "glb_file": glb_filename
        }
        with open(job_dir / "scene_metadata.json", "w") as f:
            json.dump(scene_meta, f, indent=2)

        report_path = export_project_report(job_id, "ROOM_VIDEO", scene_meta, job_dir)

        return {
            "success": True,
            "job_id": job_id,
            "mode": "ROOM_VIDEO",
            "total_frames": kf_meta["total_frames"],
            "keyframes_selected": kf_meta["keyframes_selected"],
            "points_count": len(points_3d),
            "camera_poses": camera_poses,
            "sparse_points": points_3d[:1500],  # Return for UI HUD
            "coverage": coverage,
            "completed_geometries": completed_geoms,
            "metrics": metrics,
            "glb_url": f"/outputs/{job_id}/{glb_filename}",
            "report_url": f"/outputs/{job_id}/{Path(report_path).name}"
        }

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Mode B Video Reconstruction failed: {str(e)}")


@app.get("/api/demo/mode-a")
async def demo_mode_a():
    """Direct 1-click execution of Mode A on sample floor plan."""
    return await reconstruct_mode_a(file=None, is_demo=True, wall_height=3.0, use_ground_truth=True)


@app.get("/api/demo/mode-b")
async def demo_mode_b():
    """Direct 1-click execution of Mode B on sample room video."""
    return await reconstruct_mode_b(file=None, is_demo=True)
