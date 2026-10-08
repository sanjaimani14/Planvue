import os
import time
import uuid
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

# App directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
DEMO_DIR = DATA_DIR / "demo"

OUTPUTS_DIR = BASE_DIR / "outputs"
SCENES_DIR = OUTPUTS_DIR / "scenes"
GEOMETRY_DIR = OUTPUTS_DIR / "geometry"
REPORTS_DIR = OUTPUTS_DIR / "reports"

for d in [UPLOADS_DIR, PROCESSED_DIR, DEMO_DIR, SCENES_DIR, GEOMETRY_DIR, REPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

from backend.app.geometry.schema import (
    Scene, SceneSummary, Scale, Wall, Door, Window, Room, Dimension,
    ValidationReport, CorrectionLog
)
from backend.app.vision.preprocess import load_and_preprocess_image
from backend.app.vision.wall_detection import detect_walls
from backend.app.vision.door_detection import detect_doors
from backend.app.vision.window_detection import detect_windows
from backend.app.vision.room_detection import detect_rooms
from backend.app.vision.dimension_detection import detect_dimensions
from backend.app.geometry.scale import (
    compute_metric_scale, calibrate_manual_scale, apply_metric_scale_to_scene
)
from backend.app.geometry.constraints import validate_and_repair_geometry
from backend.app.reconstruction.scene_builder import build_scene
from backend.app.reconstruction.exporter import export_glb, export_obj, export_json

app = FastAPI(
    title="PLANE VUE API",
    description="AI Spatial Reconstruction — Foundation & Mode A Blueprint Pipeline",
    version="1.0.0"
)

ACTIVE_3D_SCENES: Dict[str, Dict[str, Any]] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve data and outputs statically
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

# In-memory storage for active scenes
ACTIVE_SCENES: Dict[str, Dict[str, Any]] = {}


@app.get("/api/health")
def health_check():
    """System health check endpoint specified in Prompt 1 Section 4."""
    return {
        "status": "ok",
        "service": "plane-vue"
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Validates and stores uploaded blueprint image or PDF.
    Enforces format and size limits.
    """
    filename = file.filename or "uploaded_blueprint.png"
    suffix = Path(filename).suffix.lower()

    if suffix not in [".png", ".jpg", ".jpeg", ".pdf", ".webp"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{suffix}'. Supported formats: PNG, JPG, JPEG, PDF."
        )

    file_id = f"upload_{uuid.uuid4().hex[:8]}"
    saved_path = UPLOADS_DIR / f"{file_id}{suffix}"

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:  # 50 MB limit
        raise HTTPException(status_code=400, detail="File exceeds maximum 50MB size limit.")

    with open(saved_path, "wb") as f:
        f.write(content)

    # Inspect PDF page count if applicable
    total_pages = 1
    if suffix == ".pdf":
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(str(saved_path))
            total_pages = len(pdf)
        except Exception:
            total_pages = 1

    return {
        "success": True,
        "file_id": file_id,
        "filename": filename,
        "size_bytes": len(content),
        "extension": suffix,
        "total_pdf_pages": total_pages,
        "file_url": f"/data/uploads/{saved_path.name}"
    }


class ReconstructRequest(BaseModel):
    file_id: Optional[str] = None
    is_demo: bool = False
    demo_type: str = "simple"  # "simple" | "medium" | "complex"
    page_number: int = 1
    wall_height: float = 3.0
    wall_thickness: float = 0.15


@app.post("/api/blueprint/reconstruct")
async def reconstruct_blueprint(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False),
    demo_type: str = Form("simple"),
    page_number: int = Form(1),
    wall_height: float = Form(3.0),
    wall_thickness: float = Form(0.15),
    file_id: Optional[str] = Form(None)
):
    """
    Executes the 12-step Mode A Core Reconstruction Pipeline:
    1. Load image (with PDF page selection support)
    2. Preprocess (denoising, CLAHE, deskewing, adaptive thresholding)
    3. Detect walls
    4. Detect doors
    5. Detect windows
    6. Detect rooms
    7. Detect dimensions
    8. Calculate scale
    9. Convert coordinates to metric space
    10. Validate geometry constraints
    11. Apply safe logged corrections
    12. Return structured scene and persist outputs/geometry/scene.json
    """
    start_time = time.time()
    scene_id = f"scene_{uuid.uuid4().hex[:8]}"

    # Determine input path
    if is_demo or (file is None and not file_id):
        # Demo sample
        demo_files = {
            "simple": DEMO_DIR / "simple_plan.png",
            "medium": DEMO_DIR / "medium_plan.png",
            "complex": DEMO_DIR / "demo_floorplan.png",
        }
        input_path = demo_files.get(demo_type, DEMO_DIR / "demo_floorplan.png")
        if not input_path.exists():
            # Fallback to demo_floorplan.png
            input_path = DEMO_DIR / "demo_floorplan.png"
            if not input_path.exists():
                raise HTTPException(status_code=404, detail="Demo blueprint sample not found.")
        source_name = input_path.name
    elif file_id:
        matches = list(UPLOADS_DIR.glob(f"{file_id}.*"))
        if not matches:
            raise HTTPException(status_code=404, detail="Uploaded file ID not found.")
        input_path = matches[0]
        source_name = input_path.name
    else:
        # Direct file upload
        suffix = Path(file.filename or "plan.png").suffix.lower()
        input_path = UPLOADS_DIR / f"{scene_id}{suffix}"
        content = await file.read()
        with open(input_path, "wb") as f:
            f.write(content)
        source_name = file.filename or input_path.name

    try:
        # 1 & 2. Preprocess
        norm_bgr, binary, prep_meta = load_and_preprocess_image(
            str(input_path), page_number=page_number
        )

        # Save processed binary image separately into data/processed/
        import cv2
        proc_img_name = f"proc_{scene_id}.png"
        proc_img_path = PROCESSED_DIR / proc_img_name
        cv2.imwrite(str(proc_img_path), binary)

        # 3. Detect walls
        raw_walls = detect_walls(binary)

        # 4. Detect doors
        raw_doors = detect_doors(binary, raw_walls)

        # 5. Detect windows
        raw_windows = detect_windows(binary, raw_walls, raw_doors)

        # 6. Detect rooms
        gray = cv2.cvtColor(norm_bgr, cv2.COLOR_BGR2GRAY)
        raw_rooms = detect_rooms(binary, gray, raw_walls)

        # 7. Detect dimensions
        raw_dimensions = detect_dimensions(gray, binary)

        # 8. Calculate scale
        scale_info = compute_metric_scale(raw_dimensions, raw_doors, raw_walls, norm_bgr.shape)

        # 9 & 10 & 11. Validate geometry & apply safe corrections
        repaired_walls, repaired_doors, repaired_windows, repaired_rooms, val_report = (
            validate_and_repair_geometry(
                raw_walls, raw_doors, raw_windows, raw_rooms, scale_info
            )
        )

        # Convert coordinates to metric space
        apply_metric_scale_to_scene(
            repaired_walls, repaired_doors, repaired_windows, repaired_rooms,
            scale_info, wall_height_m=wall_height
        )

        elapsed_ms = (time.time() - start_time) * 1000.0

        # Build Summary
        total_m2 = sum(r.get("area_m2", 0.0) for r in repaired_rooms) if scale_info.get("meters_per_pixel") else None
        summary = {
            "wall_count": len(repaired_walls),
            "door_count": len(repaired_doors),
            "window_count": len(repaired_windows),
            "room_count": len(repaired_rooms),
            "dimension_count": len(raw_dimensions),
            "total_area_m2": round(total_m2, 2) if total_m2 else None,
            "processing_time_ms": round(elapsed_ms, 1)
        }

        # Build Structured Scene Model
        scene_payload = {
            "mode": "blueprint",
            "scene_id": scene_id,
            "source_file": source_name,
            "image_width": prep_meta["processed_width"],
            "image_height": prep_meta["processed_height"],
            "scale": scale_info,
            "walls": repaired_walls,
            "doors": repaired_doors,
            "windows": repaired_windows,
            "rooms": repaired_rooms,
            "dimensions": raw_dimensions,
            "summary": summary,
            "validation": val_report,
            "metrics": {
                "processing_time_ms": round(elapsed_ms, 1),
                "deskew_degrees": prep_meta.get("skew_angle_degrees", 0.0),
                "geometry_validity_score": val_report.get("geometry_validity_score", 1.0)
            },
            "processed_image_url": f"/data/processed/{proc_img_name}",
            "original_image_url": f"/data/uploads/{input_path.name}" if input_path.parent == UPLOADS_DIR else f"/data/demo/{input_path.name}"
        }

        # Save outputs/geometry/scene.json (current & latest for Prompt 2 consumption)
        latest_scene_file = GEOMETRY_DIR / "scene.json"
        job_scene_file = GEOMETRY_DIR / f"scene_{scene_id}.json"

        with open(latest_scene_file, "w", encoding="utf-8") as f:
            json.dump(scene_payload, f, indent=2)
        with open(job_scene_file, "w", encoding="utf-8") as f:
            json.dump(scene_payload, f, indent=2)

        ACTIVE_SCENES[scene_id] = scene_payload

        # Prompt 2: Real 3D Reconstruction layer
        scene_3d = build_scene(scene_payload, wall_height=wall_height, wall_thickness=0.15)
        glb_filename = f"planevue_scene_{scene_id}.glb"
        glb_path = SCENES_DIR / glb_filename
        export_glb(scene_3d, str(glb_path))
        # Keep latest copy
        shutil.copyfile(str(glb_path), str(SCENES_DIR / "planevue_scene.glb"))

        clean_3d = {k: v for k, v in scene_3d.items() if not k.startswith("_")}
        clean_3d["glb_url"] = f"/outputs/scenes/{glb_filename}"
        ACTIVE_3D_SCENES[scene_id] = scene_3d

        return {
            "success": True,
            "scene_id": scene_id,
            "summary": summary,
            "scale": scale_info,
            "walls": repaired_walls,
            "doors": repaired_doors,
            "windows": repaired_windows,
            "rooms": repaired_rooms,
            "dimensions": raw_dimensions,
            "validation": val_report,
            "metrics": scene_payload["metrics"],
            "processed_image_url": scene_payload["processed_image_url"],
            "original_image_url": scene_payload["original_image_url"],
            "scene_json_url": f"/outputs/geometry/scene_{scene_id}.json",
            "scene_3d": clean_3d,
            "glb_url": clean_3d["glb_url"]
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Floor plan reconstruction failed: {str(e)}")


@app.post("/api/blueprint/analyze")
async def analyze_blueprint(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False),
    demo_type: str = Form("simple"),
    page_number: int = Form(1),
    file_id: Optional[str] = Form(None)
):
    """Alias for blueprint reconstruction pipeline."""
    return await reconstruct_blueprint(
        file=file, is_demo=is_demo, demo_type=demo_type,
        page_number=page_number, file_id=file_id
    )


class ManualScaleRequest(BaseModel):
    scene_id: str
    pt1: List[float]
    pt2: List[float]
    known_distance: float
    unit: str = "m"


@app.post("/api/blueprint/calibrate-scale")
async def calibrate_scale_endpoint(req: ManualScaleRequest):
    """
    Section 18: Manual scale calibration fallback.
    Calculates scale from two user-selected reference points and known distance.
    Re-applies metric coordinates across the active scene.
    """
    scene = ACTIVE_SCENES.get(req.scene_id)
    if not scene:
        # Try loading from disk
        scene_file = GEOMETRY_DIR / f"scene_{req.scene_id}.json"
        if scene_file.exists():
            with open(scene_file, "r") as f:
                scene = json.load(f)
        else:
            raise HTTPException(status_code=404, detail="Scene not found.")

    try:
        new_scale = calibrate_manual_scale(req.pt1, req.pt2, req.known_distance, req.unit)
        scene["scale"] = new_scale

        # Re-apply to geometry
        apply_metric_scale_to_scene(
            scene["walls"], scene["doors"], scene["windows"], scene["rooms"],
            new_scale
        )

        # Update total room area in summary
        total_m2 = sum(r.get("area_m2", 0.0) for r in scene["rooms"])
        scene["summary"]["total_area_m2"] = round(total_m2, 2)

        # Persist updated scene
        with open(GEOMETRY_DIR / f"scene_{req.scene_id}.json", "w") as f:
            json.dump(scene, f, indent=2)
        with open(GEOMETRY_DIR / "scene.json", "w") as f:
            json.dump(scene, f, indent=2)

        ACTIVE_SCENES[req.scene_id] = scene

        return {
            "success": True,
            "scene_id": req.scene_id,
            "scale": new_scale,
            "walls": scene["walls"],
            "doors": scene["doors"],
            "windows": scene["windows"],
            "rooms": scene["rooms"],
            "summary": scene["summary"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/blueprint/validate")
async def validate_geometry_endpoint(scene: Dict[str, Any]):
    """Validates geometry and reports constraint invariants."""
    walls = scene.get("walls", [])
    doors = scene.get("doors", [])
    windows = scene.get("windows", [])
    rooms = scene.get("rooms", [])
    scale_info = scene.get("scale", {})

    _, _, _, _, report = validate_and_repair_geometry(
        walls, doors, windows, rooms, scale_info
    )
    return report


@app.get("/api/blueprint/{scene_id}")
async def get_blueprint_scene(scene_id: str):
    """Fetches stored structured scene JSON."""
    if scene_id in ACTIVE_SCENES:
        return ACTIVE_SCENES[scene_id]

    scene_file = GEOMETRY_DIR / f"scene_{scene_id}.json"
    if scene_file.exists():
        with open(scene_file, "r") as f:
            return json.load(f)

    if scene_id == "latest":
        latest = GEOMETRY_DIR / "scene.json"
        if latest.exists():
            with open(latest, "r") as f:
                return json.load(f)

    raise HTTPException(status_code=404, detail="Scene not found.")


class Reconstruct3DRequest(BaseModel):
    scene_id: str
    wall_height: float = 3.0
    wall_thickness: float = 0.15
    scene_data: Optional[Dict[str, Any]] = None


@app.post("/api/blueprint/reconstruct-3d")
async def reconstruct_3d_endpoint(req: Reconstruct3DRequest):
    """
    Prompt 2: Re-generates 3D scene representation when user adjusts wall height/thickness
    or requests dynamic 3D compilation.
    """
    scene_dict = req.scene_data or ACTIVE_SCENES.get(req.scene_id)
    if not scene_dict:
        scene_file = GEOMETRY_DIR / f"scene_{req.scene_id}.json"
        if scene_file.exists():
            with open(scene_file, "r") as f:
                scene_dict = json.load(f)
        elif req.scene_id == "latest":
            latest = GEOMETRY_DIR / "scene.json"
            if latest.exists():
                with open(latest, "r") as f:
                    scene_dict = json.load(f)

    if not scene_dict:
        raise HTTPException(status_code=404, detail="Floor plan scene data not found.")

    try:
        scene_3d = build_scene(scene_dict, wall_height=req.wall_height, wall_thickness=req.wall_thickness)
        glb_filename = f"planevue_scene_{req.scene_id}.glb"
        glb_path = SCENES_DIR / glb_filename
        export_glb(scene_3d, str(glb_path))
        shutil.copyfile(str(glb_path), str(SCENES_DIR / "planevue_scene.glb"))

        clean_3d = {k: v for k, v in scene_3d.items() if not k.startswith("_")}
        clean_3d["glb_url"] = f"/outputs/scenes/{glb_filename}"
        ACTIVE_3D_SCENES[req.scene_id] = scene_3d

        return {
            "success": True,
            "scene_id": req.scene_id,
            "scene_3d": clean_3d,
            "glb_url": clean_3d["glb_url"]
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"3D reconstruction failed: {str(e)}")


class ExportRequest(BaseModel):
    scene_id: str
    format: str = "glb"  # "glb" | "obj" | "json"
    wall_height: float = 3.0
    wall_thickness: float = 0.15
    scene_data: Optional[Dict[str, Any]] = None


@app.post("/api/blueprint/export")
async def export_blueprint_endpoint(req: ExportRequest):
    """
    Section 33, 34, 35, 36: Exports reconstructed building in GLB, OBJ, or JSON format.
    """
    scene_3d = ACTIVE_3D_SCENES.get(req.scene_id)
    if not scene_3d:
        # Build 3D on the fly
        scene_dict = req.scene_data or ACTIVE_SCENES.get(req.scene_id)
        if not scene_dict:
            scene_file = GEOMETRY_DIR / f"scene_{req.scene_id}.json"
            if scene_file.exists():
                with open(scene_file, "r") as f:
                    scene_dict = json.load(f)
            elif req.scene_id == "latest":
                latest = GEOMETRY_DIR / "scene.json"
                if latest.exists():
                    with open(latest, "r") as f:
                        scene_dict = json.load(f)

        if not scene_dict:
            raise HTTPException(status_code=404, detail="Scene not found for export.")

        scene_3d = build_scene(scene_dict, wall_height=req.wall_height, wall_thickness=req.wall_thickness)
        ACTIVE_3D_SCENES[req.scene_id] = scene_3d

    fmt = req.format.lower()
    if fmt == "glb":
        out_filename = f"planevue_scene_{req.scene_id}.glb"
        out_path = SCENES_DIR / out_filename
        export_glb(scene_3d, str(out_path))
        media_type = "model/gltf-binary"
    elif fmt == "obj":
        out_filename = f"planevue_scene_{req.scene_id}.obj"
        out_path = SCENES_DIR / out_filename
        export_obj(scene_3d, str(out_path))
        media_type = "text/plain"
    elif fmt == "json":
        out_filename = f"planevue_scene_{req.scene_id}.json"
        out_path = SCENES_DIR / out_filename
        export_json(scene_3d, str(out_path))
        media_type = "application/json"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported export format: {fmt}")

    return FileResponse(
        str(out_path),
        media_type=media_type,
        filename=f"planevue_scene.{fmt}"
    )


@app.get("/api/blueprint/export/{scene_id}")
async def export_blueprint_get(
    scene_id: str,
    format: str = Query("glb", pattern="^(glb|obj|json)$"),
    wall_height: float = 3.0,
    wall_thickness: float = 0.15
):
    """Direct GET download endpoint for browser download triggers."""
    req = ExportRequest(scene_id=scene_id, format=format, wall_height=wall_height, wall_thickness=wall_thickness)
    return await export_blueprint_endpoint(req)


# ==============================================================================
# PROMPT 3 — EVALUATION, BASELINE, ABLATION & RESEARCH BENCHMARK ENDPOINTS
# ==============================================================================

from backend.app.evaluation.schemas import EvaluationRun
from backend.app.evaluation.dataset import get_registered_datasets, get_dataset_ground_truth
from backend.app.evaluation.baseline import run_baseline_reconstruction
from backend.app.evaluation.ablation import run_ablation_study
from backend.app.evaluation.evaluation_service import (
    run_evaluation_service, EVALUATION_RUNS, load_evaluation_config
)


class EvaluationRequest(BaseModel):
    dataset_id: str = "demo_simple"
    method: str = "COMPARE"  # "BASELINE" | "PLANEVUE" | "ABLATION" | "COMPARE"
    custom_image_path: Optional[str] = None


@app.get("/api/evaluation/datasets")
async def get_evaluation_datasets_endpoint():
    """Returns directory of registered benchmark datasets and their ground truth availability."""
    return get_registered_datasets()


@app.get("/api/evaluation/dataset/{dataset_id}")
async def get_dataset_details_endpoint(dataset_id: str):
    """Retrieves dataset ground-truth geometry specifications."""
    gt = get_dataset_ground_truth(dataset_id)
    if not gt:
        raise HTTPException(status_code=404, detail="Dataset ground truth not found.")
    return gt.model_dump()


@app.post("/api/evaluation/run")
async def run_evaluation_endpoint(req: EvaluationRequest):
    """Section 6 & 29: Runs full quantitative evaluation against ground truth."""
    try:
        eval_run = run_evaluation_service(
            dataset_id=req.dataset_id,
            method=req.method,
            custom_image_path=req.custom_image_path
        )
        return eval_run.model_dump()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.post("/api/evaluation/baseline")
async def run_baseline_endpoint(req: EvaluationRequest):
    """Section 4: Runs conventional Hough baseline reconstruction."""
    req.method = "BASELINE"
    return await run_evaluation_endpoint(req)


@app.post("/api/evaluation/compare")
async def run_compare_endpoint(req: EvaluationRequest):
    """Section 21: Runs side-by-side Baseline vs PLANE VUE comparison."""
    req.method = "COMPARE"
    return await run_evaluation_endpoint(req)


@app.post("/api/evaluation/ablation")
async def run_ablation_endpoint(req: EvaluationRequest):
    """Section 18 & 19: Executes 6-stage ablation framework (A0 to A5)."""
    req.method = "ABLATION"
    return await run_evaluation_endpoint(req)


@app.get("/api/evaluation/{evaluation_id}")
async def get_evaluation_run_endpoint(evaluation_id: str):
    """Fetches previously computed evaluation run results."""
    if evaluation_id in EVALUATION_RUNS:
        return EVALUATION_RUNS[evaluation_id].model_dump()

    report_file = REPORTS_DIR / f"{evaluation_id}.json"
    if report_file.exists():
        with open(report_file, "r", encoding="utf-8") as f:
            return json.load(f)

    raise HTTPException(status_code=404, detail="Evaluation run ID not found.")


@app.get("/api/evaluation/{evaluation_id}/report")
async def download_evaluation_report_endpoint(
    evaluation_id: str,
    format: str = Query("html", pattern="^(html|md|json)$")
):
    """Section 28: Exports human-readable or structured evaluation report file."""
    report_file = REPORTS_DIR / f"{evaluation_id}.{format}"
    if not report_file.exists():
        raise HTTPException(status_code=404, detail=f"Report file for {evaluation_id} in {format} format not found.")

    media_type = (
        "text/html" if format == "html" else
        "text/markdown" if format == "md" else
        "application/json"
    )

    return FileResponse(
        str(report_file),
        media_type=media_type,
        filename=f"planevue_eval_{evaluation_id}.{format}"
    )


@app.post("/api/evaluation/suite")
async def run_benchmark_suite_endpoint():
    """Section 6 & 25: Runs complete synthetic benchmark suite with statistical aggregation."""
    try:
        from backend.app.evaluation.evaluation_service import run_benchmark_suite
        return run_benchmark_suite()
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Benchmark suite execution failed: {str(e)}")


# =========================================================================
# MODE B — ROOM VIDEO -> 3D SCENE + UNSEEN COMPLETION ENDPOINTS
# =========================================================================

VIDEO_DIR = DATA_DIR / "video"
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

from backend.app.video.video_ingestion import validate_and_ingest_video
from backend.app.video.frame_quality import analyze_video_stream_quality
from backend.app.video.frame_extraction import extract_intelligent_keyframes
from backend.app.video.video_service import video_service, ACTIVE_VIDEO_JOBS, ACTIVE_VIDEO_SCENES, ACTIVE_VIDEO_RAW

class VideoReconstructRequest(BaseModel):
    video_id: str
    target_keyframes: int = 14
    known_reference_dimension_m: Optional[float] = None
    is_async: bool = False

@app.post("/api/video/upload")
async def upload_room_video(
    file: Optional[UploadFile] = File(None),
    is_demo: bool = Form(False)
):
    """
    Uploads or selects a walkthrough video for Mode B reconstruction.
    Validates container, dimensions, duration, and frame count.
    """
    video_id = f"vid_{uuid.uuid4().hex[:8]}"
    if is_demo or file is None:
        demo_video_path = DEMO_DIR / "sample_room.mp4"
        if not demo_video_path.exists():
            from data.demo.generate_demo_room_video import generate_sample_room_walkthrough_video
            generate_sample_room_walkthrough_video(str(demo_video_path))
        target_path = demo_video_path
        video_id = "sample_room_demo"
    else:
        suffix = Path(file.filename or "walkthrough.mp4").suffix.lower()
        target_path = VIDEO_DIR / f"{video_id}{suffix}"
        content = await file.read()
        with open(target_path, "wb") as f:
            f.write(content)

    is_valid, meta, err = validate_and_ingest_video(target_path, video_id=video_id)
    if not is_valid or meta is None:
        raise HTTPException(status_code=400, detail=f"Invalid video upload: {err}")

    return {
        "success": True,
        "video_id": video_id,
        "filename": target_path.name,
        "metadata": meta.model_dump()
    }

@app.post("/api/video/analyze")
async def analyze_video_quality(video_id: str = Form(...)):
    """Runs frame quality assessment (sharpness, blur, exposure, motion disparity)."""
    # Find video file
    matches = list(VIDEO_DIR.glob(f"{video_id}.*")) + list(DEMO_DIR.glob(f"{video_id}.*"))
    if video_id == "sample_room_demo":
        matches = [DEMO_DIR / "sample_room.mp4"]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")
    
    video_path = matches[0]
    quality = analyze_video_stream_quality(str(video_path))
    return {
        "video_id": video_id,
        "quality_report": quality.model_dump()
    }

@app.post("/api/video/frames")
async def get_video_keyframes(
    video_id: str = Form(...),
    target_keyframes: int = Form(14)
):
    """Extracts informative sharp keyframes along the camera trajectory."""
    matches = list(VIDEO_DIR.glob(f"{video_id}.*")) + list(DEMO_DIR.glob(f"{video_id}.*"))
    if video_id == "sample_room_demo":
        matches = [DEMO_DIR / "sample_room.mp4"]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")

    video_path = matches[0]
    kf_items, _ = extract_intelligent_keyframes(
        str(video_path), video_id=video_id, target_keyframes=target_keyframes
    )
    return {
        "video_id": video_id,
        "keyframes_count": len(kf_items),
        "keyframes": [k.model_dump() for k in kf_items]
    }

@app.post("/api/video/reconstruct")
async def reconstruct_video_scene(
    video_id: str = Form(...),
    target_keyframes: int = Form(14),
    known_reference_m: Optional[float] = Form(None),
    is_async: bool = Form(False)
):
    """
    Executes the 10-stage Mode B video reconstruction pipeline:
    Keyframes -> Features -> Camera Trajectory -> Triangulation -> Planes ->
    Coverage -> Unseen Detection -> Conservative Completion -> 3D Scene + GLB.
    """
    matches = list(VIDEO_DIR.glob(f"{video_id}.*")) + list(DEMO_DIR.glob(f"{video_id}.*"))
    if video_id == "sample_room_demo":
        matches = [DEMO_DIR / "sample_room.mp4"]
    if not matches:
        raise HTTPException(status_code=404, detail=f"Video ID '{video_id}' not found.")

    video_path = matches[0]
    job = video_service.create_job(video_id=video_id)

    if is_async:
        video_service.start_pipeline_async(str(video_path), video_id, job.job_id)
        return {
            "job_id": job.job_id,
            "video_id": video_id,
            "status": "QUEUED",
            "message": "Reconstruction job started in background."
        }
    else:
        try:
            scene_data = video_service.run_pipeline_sync(
                str(video_path), video_id, job_id=job.job_id, target_keyframes=target_keyframes
            )
            return {
                "job_id": job.job_id,
                "video_id": video_id,
                "status": "COMPLETED",
                "scene": scene_data
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Video reconstruction failed: {str(e)}")

@app.get("/api/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Polls real-time progress of asynchronous video reconstruction job."""
    job = video_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job ID '{job_id}' not found.")
    return job.model_dump()

@app.get("/api/video/{video_id}/scene")
async def get_video_scene(video_id: str):
    """Retrieves reconstructed Mode B scene for 3D viewer."""
    scene = video_service.get_scene(video_id)
    if not scene:
        raise HTTPException(status_code=404, detail=f"Scene for video '{video_id}' not found. Reconstruct first.")
    return scene

@app.post("/api/video/{video_id}/export")
async def export_video_scene_format(video_id: str, format: str = Form("glb")):
    """Exports reconstructed Mode B 3D scene to GLB or JSON format."""
    raw_scene = ACTIVE_VIDEO_RAW.get(video_id)
    if not raw_scene:
        raise HTTPException(status_code=404, detail=f"Scene for video '{video_id}' not found.")

    if format.lower() == "glb":
        file_path = SCENES_DIR / f"planevue_video_{video_id}.glb"
        return FileResponse(str(file_path), media_type="model/gltf-binary", filename=f"planevue_video_{video_id}.glb")
    elif format.lower() == "json":
        file_path = SCENES_DIR / f"planevue_video_{video_id}.json"
        return FileResponse(str(file_path), media_type="application/json", filename=f"planevue_video_{video_id}.json")
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format '{format}'. Supported: glb, json.")




