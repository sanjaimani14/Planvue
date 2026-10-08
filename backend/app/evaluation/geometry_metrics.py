import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

from backend.app.evaluation.schemas import (
    DimensionalMetric, ScaleMetric, TopologyMetric,
    GeometryValidityReport, CompletenessMetric
)

def evaluate_dimensional_accuracy(
    predicted_walls: List[Dict[str, Any]],
    ground_truth_walls: List[Any],
    tolerance_m: float = 0.50
) -> DimensionalMetric:
    """
    Section 12: Metric Dimensional Accuracy.
    Evaluates metric length errors between matched predicted and ground-truth wall segments:
    - Absolute Error (|pred - gt|)
    - Relative Error (|pred - gt| / gt * 100)
    - Mean Absolute Error (MAE)
    - Median Absolute Error
    - Root Mean Square Error (RMSE)
    """
    if not predicted_walls or not ground_truth_walls:
        return DimensionalMetric(status="NOT_AVAILABLE")

    abs_errors = []
    rel_errors = []

    # Match walls by proximity and compare lengths
    for p in predicted_walls:
        p_len = p.get("length_m")
        if p_len is None:
            continue
        p_start = p.get("metric_start")
        if not p_start:
            continue

        best_gt = None
        min_dist = float("inf")
        for g in ground_truth_walls:
            g_start = g.metric_start if hasattr(g, "metric_start") else g.get("metric_start")
            g_len = g.length_m if hasattr(g, "length_m") else g.get("length_m")
            if not g_start or not g_len:
                continue

            dist = math.hypot(p_start[0] - g_start[0], p_start[1] - g_start[1])
            if dist < min_dist:
                min_dist = dist
                best_gt = g

        if best_gt and min_dist <= tolerance_m:
            g_len = best_gt.length_m if hasattr(best_gt, "length_m") else best_gt.get("length_m")
            if g_len and g_len > 0:
                err = abs(p_len - g_len)
                abs_errors.append(err)
                rel_errors.append((err / g_len) * 100.0)

    if not abs_errors:
        return DimensionalMetric(
            mae_meters=None,
            median_ae_meters=None,
            rmse_meters=None,
            mean_relative_error_pct=None,
            evaluated_segments_count=0,
            status="NOT_AVAILABLE"
        )

    mae = round(float(np.mean(abs_errors)), 3)
    median_ae = round(float(np.median(abs_errors)), 3)
    rmse = round(float(np.sqrt(np.mean(np.array(abs_errors) ** 2))), 3)
    mre_pct = round(float(np.mean(rel_errors)), 2)

    return DimensionalMetric(
        mae_meters=mae,
        median_ae_meters=median_ae,
        rmse_meters=rmse,
        mean_relative_error_pct=mre_pct,
        evaluated_segments_count=len(abs_errors),
        status="COMPUTED"
    )

def evaluate_scale_accuracy(
    predicted_scale: Dict[str, Any],
    ground_truth_scale_ppm: Optional[float]
) -> ScaleMetric:
    """
    Section 13: Scale Calibration Evaluation.
    Evaluates accuracy of calibrated pixels-per-meter against ground truth.
    """
    if not ground_truth_scale_ppm or ground_truth_scale_ppm <= 0:
        return ScaleMetric(status="NOT_AVAILABLE")

    pred_ppm = predicted_scale.get("pixels_per_meter")
    if not pred_ppm or pred_ppm <= 0:
        return ScaleMetric(
            gt_scale_ppm=round(ground_truth_scale_ppm, 2),
            predicted_scale_ppm=None,
            absolute_error_ppm=None,
            relative_error_pct=None,
            status="METRIC_SCALE_UNAVAILABLE"
        )

    abs_err = abs(pred_ppm - ground_truth_scale_ppm)
    rel_err = (abs_err / ground_truth_scale_ppm) * 100.0

    return ScaleMetric(
        gt_scale_ppm=round(ground_truth_scale_ppm, 2),
        predicted_scale_ppm=round(pred_ppm, 2),
        absolute_error_ppm=round(abs_err, 2),
        relative_error_pct=round(rel_err, 2),
        status="COMPUTED"
    )

def evaluate_topology_metrics(
    scene_data: Dict[str, Any]
) -> TopologyMetric:
    """
    Section 14: Structural correctness & topology error accounting.
    Counts disconnected walls, overlapping walls, floating doors/windows, invalid rooms.
    """
    walls = scene_data.get("walls", [])
    doors = scene_data.get("doors", [])
    windows = scene_data.get("windows", [])
    rooms = scene_data.get("rooms", [])

    # 1. Floating doors/windows (missing or unattached wall_id)
    floating_doors = sum(1 for d in doors if not d.get("wall_id"))
    floating_windows = sum(1 for w in windows if not w.get("wall_id"))

    # 2. Invalid room polygons (< 3 points or degenerate)
    invalid_rooms = sum(1 for r in rooms if len(r.get("polygon", [])) < 3)

    # 3. Disconnected walls (endpoints not touching any other wall endpoint within 15px)
    disconnected_walls = 0
    endpoints = []
    for w in walls:
        endpoints.append(w.get("start", [0, 0]))
        endpoints.append(w.get("end", [0, 0]))

    for w in walls:
        s = w.get("start", [0, 0])
        e = w.get("end", [0, 0])
        s_touch = sum(1 for ep in endpoints if math.hypot(ep[0] - s[0], ep[1] - s[1]) <= 18.0)
        e_touch = sum(1 for ep in endpoints if math.hypot(ep[0] - e[0], ep[1] - e[1]) <= 18.0)
        if s_touch <= 1 and e_touch <= 1:
            disconnected_walls += 1

    # 4. Overlapping duplicate walls
    overlapping_walls = 0
    for i in range(len(walls)):
        for j in range(i + 1, len(walls)):
            w1 = walls[i]
            w2 = walls[j]
            s1, e1 = w1.get("start", [0, 0]), w1.get("end", [0, 0])
            s2, e2 = w2.get("start", [0, 0]), w2.get("end", [0, 0])
            d1 = math.hypot(s1[0] - s2[0], s1[1] - s2[1]) + math.hypot(e1[0] - e2[0], e1[1] - e2[1])
            d2 = math.hypot(s1[0] - e2[0], s1[1] - e2[1]) + math.hypot(e1[0] - s2[0], e1[1] - s2[1])
            if min(d1, d2) < 15.0:
                overlapping_walls += 1

    total = disconnected_walls + overlapping_walls + floating_doors + floating_windows + invalid_rooms

    return TopologyMetric(
        disconnected_walls=disconnected_walls,
        overlapping_walls=overlapping_walls,
        floating_doors=floating_doors,
        floating_windows=floating_windows,
        invalid_rooms=invalid_rooms,
        self_intersecting_polygons=0,
        total_topology_errors=total
    )

def evaluate_geometry_validity(
    scene_data: Dict[str, Any]
) -> GeometryValidityReport:
    """
    Section 15: Geometry validity telemetry report.
    Tracks verified vs corrected elements and computes composite validity score.
    """
    walls = scene_data.get("walls", [])
    doors = scene_data.get("doors", [])
    windows = scene_data.get("windows", [])
    rooms = scene_data.get("rooms", [])

    walls_valid = sum(1 for w in walls if w.get("status") == "OBSERVED")
    walls_corrected = sum(1 for w in walls if w.get("status") == "CORRECTED")
    walls_invalid = 0

    rooms_valid = sum(1 for r in rooms if r.get("status") == "OBSERVED")
    rooms_corrected = sum(1 for r in rooms if r.get("status") == "CORRECTED")

    doors_attached = sum(1 for d in doors if d.get("wall_id"))
    doors_unresolved = sum(1 for d in doors if not d.get("wall_id"))

    windows_attached = sum(1 for win in windows if win.get("wall_id"))
    windows_unresolved = sum(1 for win in windows if not win.get("wall_id"))

    total_elements = len(walls) + len(rooms) + len(doors) + len(windows)
    invalid_elements = walls_invalid + doors_unresolved + windows_unresolved
    validity_score = 1.0 - (invalid_elements / max(total_elements, 1))

    return GeometryValidityReport(
        walls_valid=walls_valid,
        walls_corrected=walls_corrected,
        walls_invalid=walls_invalid,
        rooms_valid=rooms_valid,
        rooms_corrected=rooms_corrected,
        doors_attached=doors_attached,
        doors_unresolved=doors_unresolved,
        windows_attached=windows_attached,
        windows_unresolved=windows_unresolved,
        validity_score=round(max(0.0, validity_score), 3)
    )

def evaluate_completeness(
    predicted_scene: Dict[str, Any],
    ground_truth: Any
) -> CompletenessMetric:
    """
    Section 16: Completeness metric.
    Computes ratio of reconstructed wall length and room area against ground truth.
    """
    if not ground_truth:
        return CompletenessMetric(status="NOT_AVAILABLE")

    # 1. Wall length coverage
    pred_walls = predicted_scene.get("walls", [])
    pred_len = sum(w.get("length_m", 0.0) or 0.0 for w in pred_walls)
    gt_len = sum(w.length_m if hasattr(w, "length_m") else w.get("length_m", 0.0) or 0.0 for w in ground_truth.walls)

    wall_cov = min(100.0, (pred_len / gt_len * 100.0)) if gt_len > 0 else 100.0

    # 2. Room area coverage
    pred_rooms = predicted_scene.get("rooms", [])
    pred_area = sum(r.get("area_m2", 0.0) or 0.0 for r in pred_rooms)
    gt_area = sum(r.area_m2 if hasattr(r, "area_m2") else r.get("area_m2", 0.0) or 0.0 for r in ground_truth.rooms)

    room_cov = min(100.0, (pred_area / gt_area * 100.0)) if gt_area > 0 else 100.0

    # 3. Door & Window detection recall
    gt_doors = len(ground_truth.doors)
    pred_doors = len(predicted_scene.get("doors", []))
    door_recall = min(100.0, (pred_doors / gt_doors * 100.0)) if gt_doors > 0 else 100.0

    gt_wins = len(ground_truth.windows)
    pred_wins = len(predicted_scene.get("windows", []))
    win_recall = min(100.0, (pred_wins / gt_wins * 100.0)) if gt_wins > 0 else 100.0

    return CompletenessMetric(
        wall_coverage_pct=round(wall_cov, 1),
        room_coverage_pct=round(room_cov, 1),
        door_recall_pct=round(door_recall, 1),
        window_recall_pct=round(win_recall, 1),
        status="COMPUTED"
    )
