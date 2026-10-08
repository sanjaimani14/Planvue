import numpy as np
import shapely.geometry as sg
from typing import List, Dict, Any, Tuple, Optional

from backend.app.evaluation.schemas import RoomIoUMetric, VisualErrorItem

def evaluate_room_iou(
    predicted_rooms: List[Dict[str, Any]],
    ground_truth_rooms: List[Any],
    min_iou_match: float = 0.20
) -> Tuple[RoomIoUMetric, List[VisualErrorItem]]:
    """
    Section 10: Room Intersection-over-Union (IoU) evaluation using Shapely 2D polygon overlap.
    Computes mean, median, min, and max IoU across matched rooms.
    """
    visual_errors: List[VisualErrorItem] = []
    num_gt = len(ground_truth_rooms)
    num_pred = len(predicted_rooms)

    if num_gt == 0 or num_pred == 0:
        return RoomIoUMetric(
            mean_iou=None,
            median_iou=None,
            min_iou=None,
            max_iou=None,
            matched_rooms_count=0,
            unmatched_predicted_count=num_pred,
            unmatched_gt_count=num_gt,
            status="NOT_AVAILABLE" if num_gt == 0 else "COMPUTED"
        ), visual_errors

    # Construct valid Shapely polygons for ground truth
    gt_polys = []
    for g in ground_truth_rooms:
        raw_p = g.polygon if hasattr(g, "polygon") else g.get("polygon", [])
        gid = g.id if hasattr(g, "id") else g.get("id", "GT")
        if len(raw_p) >= 3:
            poly = sg.Polygon(raw_p)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if not poly.is_empty:
                gt_polys.append({"id": gid, "poly": poly, "raw": raw_p})

    # Construct valid Shapely polygons for predictions
    pred_polys = []
    for p in predicted_rooms:
        raw_p = p.get("polygon", [])
        pid = p.get("id", "P")
        conf = float(p.get("confidence", 0.90) or 0.90)
        if len(raw_p) >= 3:
            poly = sg.Polygon(raw_p)
            if not poly.is_valid:
                poly = poly.buffer(0)
            if not poly.is_empty:
                pred_polys.append({"id": pid, "poly": poly, "raw": raw_p, "conf": conf})

    if len(gt_polys) == 0 or len(pred_polys) == 0:
        return RoomIoUMetric(
            mean_iou=0.0,
            median_iou=0.0,
            min_iou=0.0,
            max_iou=0.0,
            matched_rooms_count=0,
            unmatched_predicted_count=num_pred,
            unmatched_gt_count=num_gt,
            status="COMPUTED"
        ), visual_errors

    # Pairwise IoU matrix
    iou_pairs = []
    for p_idx, p in enumerate(pred_polys):
        for g_idx, g in enumerate(gt_polys):
            try:
                intersection = p["poly"].intersection(g["poly"]).area
                union = p["poly"].union(g["poly"]).area
                iou = (intersection / union) if union > 0 else 0.0
                if iou >= min_iou_match:
                    iou_pairs.append((p_idx, g_idx, iou))
            except Exception:
                continue

    # Sort greedy by highest IoU
    iou_pairs.sort(key=lambda x: x[2], reverse=True)
    matched_preds = set()
    matched_gts = set()
    matched_ious: List[float] = []

    for p_idx, g_idx, iou in iou_pairs:
        if p_idx not in matched_preds and g_idx not in matched_gts:
            matched_preds.add(p_idx)
            matched_gts.add(g_idx)
            matched_ious.append(iou)
            visual_errors.append(VisualErrorItem(
                element_type="room",
                classification="TRUE_POSITIVE" if iou >= 0.50 else "GEOMETRIC_MISMATCH",
                element_id=pred_polys[p_idx]["id"],
                coordinates=pred_polys[p_idx]["raw"],
                confidence=pred_polys[p_idx]["conf"],
                error_note=f"Matched GT {gt_polys[g_idx]['id']} with IoU: {iou:.3f}"
            ))

    # Record unmatched rooms
    for p_idx in range(len(pred_polys)):
        if p_idx not in matched_preds:
            visual_errors.append(VisualErrorItem(
                element_type="room",
                classification="FALSE_POSITIVE",
                element_id=pred_polys[p_idx]["id"],
                coordinates=pred_polys[p_idx]["raw"],
                confidence=pred_polys[p_idx]["conf"],
                error_note="Predicted room polygon has no ground-truth match"
            ))

    for g_idx in range(len(gt_polys)):
        if g_idx not in matched_gts:
            visual_errors.append(VisualErrorItem(
                element_type="room",
                classification="FALSE_NEGATIVE",
                element_id=gt_polys[g_idx]["id"],
                coordinates=gt_polys[g_idx]["raw"],
                confidence=None,
                error_note="Ground-truth room was not reconstructed"
            ))

    if matched_ious:
        mean_iou = round(float(np.mean(matched_ious)), 4)
        median_iou = round(float(np.median(matched_ious)), 4)
        min_iou = round(float(min(matched_ious)), 4)
        max_iou = round(float(max(matched_ious)), 4)
    else:
        mean_iou = 0.0
        median_iou = 0.0
        min_iou = 0.0
        max_iou = 0.0

    return RoomIoUMetric(
        mean_iou=mean_iou,
        median_iou=median_iou,
        min_iou=min_iou,
        max_iou=max_iou,
        matched_rooms_count=len(matched_ious),
        unmatched_predicted_count=len(pred_polys) - len(matched_preds),
        unmatched_gt_count=len(gt_polys) - len(matched_gts),
        status="COMPUTED"
    ), visual_errors

def compute_layout_error_score(
    wall_f1: Optional[float],
    room_mean_iou: Optional[float],
    door_f1: Optional[float],
    window_f1: Optional[float],
    scale_relative_error_pct: Optional[float],
    weights: Dict[str, float]
) -> Optional[float]:
    """
    Section 11: Transparent Composite Layout Error Metric.
    Formula:
    Layout Error = w_wall*(1 - Wall_F1) + w_room*(1 - Room_IoU) + w_door*(1 - Door_F1)
                   + w_win*(1 - Win_F1) + w_scale*min(1.0, Scale_Rel_Err / 100)
    Normalized in [0.0, 1.0], lower is better (0.0 = perfect alignment).
    """
    w_wall = weights.get("wall_position_error_weight", 0.35)
    w_room = weights.get("room_iou_error_weight", 0.30)
    w_door = weights.get("door_position_error_weight", 0.15)
    w_win = weights.get("window_position_error_weight", 0.10)
    w_scale = weights.get("scale_error_weight", 0.10)

    total_weight = 0.0
    weighted_error = 0.0

    if wall_f1 is not None:
        weighted_error += w_wall * (1.0 - wall_f1)
        total_weight += w_wall

    if room_mean_iou is not None:
        weighted_error += w_room * (1.0 - room_mean_iou)
        total_weight += w_room

    if door_f1 is not None:
        weighted_error += w_door * (1.0 - door_f1)
        total_weight += w_door

    if window_f1 is not None:
        weighted_error += w_win * (1.0 - window_f1)
        total_weight += w_win

    if scale_relative_error_pct is not None:
        scale_err_norm = min(1.0, scale_relative_error_pct / 100.0)
        weighted_error += w_scale * scale_err_norm
        total_weight += w_scale

    if total_weight > 0:
        return round(weighted_error / total_weight, 4)
    return None
