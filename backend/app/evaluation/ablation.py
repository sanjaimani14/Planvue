import time
import math
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.app.evaluation.baseline import run_baseline_reconstruction
from backend.app.vision.preprocess import load_and_preprocess_image
from backend.app.vision.wall_detection import detect_walls
from backend.app.vision.door_detection import detect_doors
from backend.app.vision.window_detection import detect_windows
from backend.app.vision.room_detection import detect_rooms
from backend.app.vision.dimension_detection import detect_dimensions
from backend.app.geometry.scale import compute_metric_scale, apply_metric_scale_to_scene
from backend.app.geometry.constraints import validate_and_repair_geometry
from backend.app.reconstruction.scene_builder import build_scene
from backend.app.evaluation.detection_metrics import evaluate_wall_detection
from backend.app.evaluation.layout_metrics import evaluate_room_iou
from backend.app.evaluation.geometry_metrics import (
    evaluate_dimensional_accuracy, evaluate_topology_metrics, evaluate_geometry_validity
)
from backend.app.evaluation.schemas import AblationRunResult

def run_ablation_study(
    image_path: str,
    ground_truth: Optional[Any] = None
) -> List[AblationRunResult]:
    """
    Section 18: Real executable ablation study across 6 modular pipeline stages:
    A0: Baseline (Otsu + HoughLinesP)
    A1: + Preprocessing (Bilateral Denoise + CLAHE + Deskewing)
    A2: + Semantic Detection (Wall kernels + Door arcs + Window double-lines + Rooms)
    A3: + Metric Scale (Dimension OCR / Door reference scale engine)
    A4: + Topology Constraints (Duplicate pruning + Corner gap closure + Snapping)
    A5: Full PLANE VUE (Complete refinement + Opening segmentations + 3D assembly)
    """
    results: List[AblationRunResult] = []

    # -------------------------------------------------------------
    # Stage A0: Baseline
    # -------------------------------------------------------------
    t0 = time.time()
    base_res = run_baseline_reconstruction(image_path)
    elapsed_a0 = (time.time() - t0) * 1000.0

    topo_a0 = evaluate_topology_metrics(base_res)
    val_a0 = evaluate_geometry_validity(base_res)

    wall_f1_a0 = None
    room_iou_a0 = None
    dim_err_a0 = None

    if ground_truth:
        w_m, _ = evaluate_wall_detection(base_res["walls"], ground_truth.walls)
        wall_f1_a0 = w_m.f1
        r_m, _ = evaluate_room_iou(base_res["rooms"], ground_truth.rooms)
        room_iou_a0 = r_m.mean_iou
        d_m = evaluate_dimensional_accuracy(base_res["walls"], ground_truth.walls)
        dim_err_a0 = d_m.mae_meters

    results.append(AblationRunResult(
        method_id="A0",
        name="Baseline",
        description="Otsu thresholding + Hough line fitting + primitive geometry extrusion",
        wall_f1=wall_f1_a0,
        room_iou=room_iou_a0,
        dimension_error_m=dim_err_a0,
        topology_errors=topo_a0.total_topology_errors,
        geometry_validity_score=val_a0.validity_score,
        processing_time_ms=round(elapsed_a0, 1),
        metrics={"wall_count": len(base_res["walls"]), "door_count": 0, "room_count": 0}
    ))

    # -------------------------------------------------------------
    # Stage A1: Baseline + Preprocessing
    # -------------------------------------------------------------
    t1 = time.time()
    norm_bgr, prep_bin, _ = load_and_preprocess_image(image_path)
    lines_a1 = cv2.HoughLinesP(prep_bin, 1, np.pi / 180, 60, minLineLength=40, maxLineGap=20)
    walls_a1 = []
    if lines_a1 is not None:
        reshaped = lines_a1.reshape(-1, 4)
        for idx, (x1, y1, x2, y2) in enumerate(reshaped):
            walls_a1.append({
                "id": f"A1_W{idx:03d}",
                "start": [float(x1), float(y1)],
                "end": [float(x2), float(y2)],
                "thickness_px": 12.0,
                "length_px": math.hypot(float(x2 - x1), float(y2 - y1)),
                "confidence": 0.65,
                "status": "OBSERVED"
            })
    elapsed_a1 = (time.time() - t1) * 1000.0

    scene_a1 = {"walls": walls_a1, "doors": [], "windows": [], "rooms": []}
    topo_a1 = evaluate_topology_metrics(scene_a1)
    val_a1 = evaluate_geometry_validity(scene_a1)

    wall_f1_a1 = None
    if ground_truth:
        w_m, _ = evaluate_wall_detection(walls_a1, ground_truth.walls)
        wall_f1_a1 = w_m.f1

    results.append(AblationRunResult(
        method_id="A1",
        name="+ Preprocessing",
        description="Bilateral denoising + CLAHE contrast + Deskewing with Hough lines",
        wall_f1=wall_f1_a1,
        room_iou=0.0 if ground_truth else None,
        dimension_error_m=dim_err_a0,
        topology_errors=topo_a1.total_topology_errors,
        geometry_validity_score=val_a1.validity_score,
        processing_time_ms=round(elapsed_a1, 1),
        metrics={"wall_count": len(walls_a1), "door_count": 0, "room_count": 0}
    ))

    # -------------------------------------------------------------
    # Stage A2: A1 + Semantic Detection
    # -------------------------------------------------------------
    t2 = time.time()
    raw_walls = detect_walls(prep_bin)
    raw_doors = detect_doors(prep_bin, raw_walls)
    raw_windows = detect_windows(prep_bin, raw_walls, raw_doors)
    gray = cv2.cvtColor(norm_bgr, cv2.COLOR_BGR2GRAY)
    raw_rooms = detect_rooms(prep_bin, gray, raw_walls)
    elapsed_a2 = (time.time() - t2) * 1000.0 + elapsed_a1

    scene_a2 = {"walls": raw_walls, "doors": raw_doors, "windows": raw_windows, "rooms": raw_rooms}
    topo_a2 = evaluate_topology_metrics(scene_a2)
    val_a2 = evaluate_geometry_validity(scene_a2)

    wall_f1_a2 = None
    room_iou_a2 = None
    if ground_truth:
        w_m, _ = evaluate_wall_detection(raw_walls, ground_truth.walls)
        wall_f1_a2 = w_m.f1
        r_m, _ = evaluate_room_iou(raw_rooms, ground_truth.rooms)
        room_iou_a2 = r_m.mean_iou

    results.append(AblationRunResult(
        method_id="A2",
        name="+ Semantic Detection",
        description="Specialized morphological wall kernels + door arcs + window glass + rooms",
        wall_f1=wall_f1_a2,
        room_iou=room_iou_a2,
        dimension_error_m=None,
        topology_errors=topo_a2.total_topology_errors,
        geometry_validity_score=val_a2.validity_score,
        processing_time_ms=round(elapsed_a2, 1),
        metrics={"wall_count": len(raw_walls), "door_count": len(raw_doors), "room_count": len(raw_rooms)}
    ))

    # -------------------------------------------------------------
    # Stage A3: A2 + Metric Scale Engine
    # -------------------------------------------------------------
    t3 = time.time()
    raw_dims = detect_dimensions(gray, prep_bin)
    scale_info = compute_metric_scale(raw_dims, raw_doors, raw_walls, norm_bgr.shape)
    
    # Clone elements for scale application
    import copy
    walls_a3 = copy.deepcopy(raw_walls)
    doors_a3 = copy.deepcopy(raw_doors)
    windows_a3 = copy.deepcopy(raw_windows)
    rooms_a3 = copy.deepcopy(raw_rooms)
    apply_metric_scale_to_scene(walls_a3, doors_a3, windows_a3, rooms_a3, scale_info)
    elapsed_a3 = (time.time() - t3) * 1000.0 + elapsed_a2

    scene_a3 = {"walls": walls_a3, "doors": doors_a3, "windows": windows_a3, "rooms": rooms_a3}
    dim_err_a3 = None
    if ground_truth:
        d_m = evaluate_dimensional_accuracy(walls_a3, ground_truth.walls)
        dim_err_a3 = d_m.mae_meters

    results.append(AblationRunResult(
        method_id="A3",
        name="+ Metric Scale",
        description="5-tier priority hierarchy scale calibration (OCR dimension / Door heuristic)",
        wall_f1=wall_f1_a2,
        room_iou=room_iou_a2,
        dimension_error_m=dim_err_a3,
        topology_errors=topo_a2.total_topology_errors,
        geometry_validity_score=val_a2.validity_score,
        processing_time_ms=round(elapsed_a3, 1),
        metrics={"scale_ppm": scale_info.get("pixels_per_meter"), "source": scale_info.get("source")}
    ))

    # -------------------------------------------------------------
    # Stage A4: A3 + Topology Constraints
    # -------------------------------------------------------------
    t4 = time.time()
    rep_walls, rep_doors, rep_windows, rep_rooms, _ = validate_and_repair_geometry(
        copy.deepcopy(raw_walls), copy.deepcopy(raw_doors),
        copy.deepcopy(raw_windows), copy.deepcopy(raw_rooms),
        scale_info
    )
    apply_metric_scale_to_scene(rep_walls, rep_doors, rep_windows, rep_rooms, scale_info)
    elapsed_a4 = (time.time() - t4) * 1000.0 + elapsed_a3

    scene_a4 = {"walls": rep_walls, "doors": rep_doors, "windows": rep_windows, "rooms": rep_rooms}
    topo_a4 = evaluate_topology_metrics(scene_a4)
    val_a4 = evaluate_geometry_validity(scene_a4)

    wall_f1_a4 = None
    room_iou_a4 = None
    dim_err_a4 = None
    if ground_truth:
        w_m, _ = evaluate_wall_detection(rep_walls, ground_truth.walls)
        wall_f1_a4 = w_m.f1
        r_m, _ = evaluate_room_iou(rep_rooms, ground_truth.rooms)
        room_iou_a4 = r_m.mean_iou
        d_m = evaluate_dimensional_accuracy(rep_walls, ground_truth.walls)
        dim_err_a4 = d_m.mae_meters

    results.append(AblationRunResult(
        method_id="A4",
        name="+ Topology Constraints",
        description="Duplicate pruning + corner gap closure + door/window axis projection",
        wall_f1=wall_f1_a4,
        room_iou=room_iou_a4,
        dimension_error_m=dim_err_a4,
        topology_errors=topo_a4.total_topology_errors,
        geometry_validity_score=val_a4.validity_score,
        processing_time_ms=round(elapsed_a4, 1),
        metrics={"wall_count": len(rep_walls), "door_count": len(rep_doors), "room_count": len(rep_rooms)}
    ))

    # -------------------------------------------------------------
    # Stage A5: Full PLANE VUE (3D Synthesis & Lintels)
    # -------------------------------------------------------------
    t5 = time.time()
    full_scene_3d = build_scene(scene_a4, wall_height=3.0, wall_thickness=0.15)
    elapsed_a5 = (time.time() - t5) * 1000.0 + elapsed_a4

    results.append(AblationRunResult(
        method_id="A5",
        name="Full PLANE VUE",
        description="A4 + 3D wall prisms with opening segmentations, lintels, sills, and GLB export",
        wall_f1=wall_f1_a4,
        room_iou=room_iou_a4,
        dimension_error_m=dim_err_a4,
        topology_errors=topo_a4.total_topology_errors,
        geometry_validity_score=val_a4.validity_score,
        processing_time_ms=round(elapsed_a5, 1),
        metrics={"3d_objects": len(full_scene_3d["objects"]), "bounds": full_scene_3d["bounds"]}
    ))

    return results
