import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

from backend.app.evaluation.schemas import DetectionMetric, VisualErrorItem

def compute_segment_properties(p1: List[float], p2: List[float]) -> Tuple[Tuple[float, float], float, float]:
    """Computes midpoint, length, and orientation angle in degrees (0..180)."""
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    mid_x = (x1 + x2) / 2.0
    mid_y = (y1 + y2) / 2.0
    length = math.hypot(x2 - x1, y2 - y1)
    angle_rad = math.atan2(y2 - y1, x2 - x1) % math.pi
    angle_deg = math.degrees(angle_rad)
    return (mid_x, mid_y), length, angle_deg

def compute_angular_difference(deg1: float, deg2: float) -> float:
    """Computes shortest angular difference between two non-directed lines in degrees (0..90)."""
    diff = abs(deg1 - deg2) % 180.0
    if diff > 90.0:
        diff = 180.0 - diff
    return diff

def evaluate_wall_detection(
    predicted_walls: List[Dict[str, Any]],
    ground_truth_walls: List[Any],
    max_midpoint_dist: float = 35.0,
    max_angle_deg: float = 18.0,
    min_length_ratio: float = 0.55
) -> Tuple[DetectionMetric, List[VisualErrorItem]]:
    """
    Section 8: Geometric Wall Matching & Precision/Recall/F1 Computation.
    Uses bipartite geometric similarity matching:
    - Midpoint Euclidean distance <= max_midpoint_dist
    - Orientation difference <= max_angle_deg (0..90 deg)
    - Length ratio >= min_length_ratio
    """
    visual_errors: List[VisualErrorItem] = []
    num_gt = len(ground_truth_walls)
    num_pred = len(predicted_walls)

    if num_gt == 0:
        return DetectionMetric(
            precision=1.0 if num_pred == 0 else 0.0,
            recall=None,
            f1=None,
            true_positives=0,
            false_positives=num_pred,
            false_negatives=0,
            total_ground_truth=0,
            total_predicted=num_pred,
            status="NOT_AVAILABLE" if num_pred == 0 else "COMPUTED"
        ), visual_errors

    # Prepare GT properties
    gt_props = []
    for g in ground_truth_walls:
        s = g.start if hasattr(g, "start") else g["start"]
        e = g.end if hasattr(g, "end") else g["end"]
        gid = g.id if hasattr(g, "id") else g["id"]
        mid, length, angle = compute_segment_properties(s, e)
        gt_props.append({"id": gid, "mid": mid, "length": length, "angle": angle, "start": s, "end": e})

    # Prepare Pred properties
    pred_props = []
    for p in predicted_walls:
        s = p.get("start", [0, 0])
        e = p.get("end", [0, 0])
        pid = p.get("id", "P")
        conf = float(p.get("confidence", 0.90) or 0.90)
        mid, length, angle = compute_segment_properties(s, e)
        pred_props.append({"id": pid, "mid": mid, "length": length, "angle": angle, "start": s, "end": e, "conf": conf})

    # Cost matrix based on composite geometric distance
    matches: List[Tuple[int, int, float]] = []
    for p_idx, p in enumerate(pred_props):
        for g_idx, g in enumerate(gt_props):
            dist = math.hypot(p["mid"][0] - g["mid"][0], p["mid"][1] - g["mid"][1])
            ang_diff = compute_angular_difference(p["angle"], g["angle"])
            len_ratio = min(p["length"], g["length"]) / max(max(p["length"], g["length"]), 1e-4)

            if dist <= max_midpoint_dist and ang_diff <= max_angle_deg and len_ratio >= min_length_ratio:
                # Combined similarity score (lower is better)
                cost = (dist / max_midpoint_dist) * 0.5 + (ang_diff / max_angle_deg) * 0.3 + (1.0 - len_ratio) * 0.2
                matches.append((p_idx, g_idx, cost))

    # Sort greedy by best cost
    matches.sort(key=lambda x: x[2])
    matched_preds = set()
    matched_gts = set()

    for p_idx, g_idx, _ in matches:
        if p_idx not in matched_preds and g_idx not in matched_gts:
            matched_preds.add(p_idx)
            matched_gts.add(g_idx)
            visual_errors.append(VisualErrorItem(
                element_type="wall",
                classification="TRUE_POSITIVE",
                element_id=pred_props[p_idx]["id"],
                coordinates={"start": pred_props[p_idx]["start"], "end": pred_props[p_idx]["end"]},
                confidence=pred_props[p_idx]["conf"],
                error_note=f"Matched GT {gt_props[g_idx]['id']}"
            ))

    tp = len(matched_preds)
    fp = num_pred - tp
    fn = num_gt - len(matched_gts)

    # Record false positives
    for p_idx in range(num_pred):
        if p_idx not in matched_preds:
            visual_errors.append(VisualErrorItem(
                element_type="wall",
                classification="FALSE_POSITIVE",
                element_id=pred_props[p_idx]["id"],
                coordinates={"start": pred_props[p_idx]["start"], "end": pred_props[p_idx]["end"]},
                confidence=pred_props[p_idx]["conf"],
                error_note="Predicted wall has no matching ground-truth structure"
            ))

    # Record false negatives
    for g_idx in range(num_gt):
        if g_idx not in matched_gts:
            visual_errors.append(VisualErrorItem(
                element_type="wall",
                classification="FALSE_NEGATIVE",
                element_id=gt_props[g_idx]["id"],
                coordinates={"start": gt_props[g_idx]["start"], "end": gt_props[g_idx]["end"]},
                confidence=None,
                error_note="Ground-truth wall was missed by detection pipeline"
            ))

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round((2.0 * precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    return DetectionMetric(
        precision=precision,
        recall=recall,
        f1=f1,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        total_ground_truth=num_gt,
        total_predicted=num_pred,
        status="COMPUTED"
    ), visual_errors

def evaluate_point_element_detection(
    predicted_elements: List[Dict[str, Any]],
    ground_truth_elements: List[Any],
    max_distance: float = 45.0,
    element_type: str = "door"
) -> Tuple[DetectionMetric, List[VisualErrorItem]]:
    """
    Section 9: Spatial matching for Doors and Windows.
    Matches predictions against ground truth based on 2D position proximity.
    """
    visual_errors: List[VisualErrorItem] = []
    num_gt = len(ground_truth_elements)
    num_pred = len(predicted_elements)

    if num_gt == 0:
        return DetectionMetric(
            precision=1.0 if num_pred == 0 else 0.0,
            recall=None,
            f1=None,
            true_positives=0,
            false_positives=num_pred,
            false_negatives=0,
            total_ground_truth=0,
            total_predicted=num_pred,
            status="NOT_AVAILABLE" if num_pred == 0 else "COMPUTED"
        ), visual_errors

    gt_positions = []
    for g in ground_truth_elements:
        pos = g.position if hasattr(g, "position") else g.get("position", [0, 0])
        gid = g.id if hasattr(g, "id") else g.get("id", "GT")
        gt_positions.append({"id": gid, "pos": pos})

    pred_positions = []
    for p in predicted_elements:
        pos = p.get("position", [0, 0])
        pid = p.get("id", "P")
        conf = float(p.get("confidence", 0.85) or 0.85)
        pred_positions.append({"id": pid, "pos": pos, "conf": conf})

    matches = []
    for p_idx, p in enumerate(pred_positions):
        for g_idx, g in enumerate(gt_positions):
            dist = math.hypot(p["pos"][0] - g["pos"][0], p["pos"][1] - g["pos"][1])
            if dist <= max_distance:
                matches.append((p_idx, g_idx, dist))

    matches.sort(key=lambda x: x[2])
    matched_preds = set()
    matched_gts = set()

    for p_idx, g_idx, dist in matches:
        if p_idx not in matched_preds and g_idx not in matched_gts:
            matched_preds.add(p_idx)
            matched_gts.add(g_idx)
            visual_errors.append(VisualErrorItem(
                element_type=element_type,
                classification="TRUE_POSITIVE",
                element_id=pred_positions[p_idx]["id"],
                coordinates=pred_positions[p_idx]["pos"],
                confidence=pred_positions[p_idx]["conf"],
                error_note=f"Matched GT {gt_positions[g_idx]['id']} (offset: {dist:.1f}px)"
            ))

    tp = len(matched_preds)
    fp = num_pred - tp
    fn = num_gt - len(matched_gts)

    for p_idx in range(num_pred):
        if p_idx not in matched_preds:
            visual_errors.append(VisualErrorItem(
                element_type=element_type,
                classification="FALSE_POSITIVE",
                element_id=pred_positions[p_idx]["id"],
                coordinates=pred_positions[p_idx]["pos"],
                confidence=pred_positions[p_idx]["conf"],
                error_note=f"Spurious {element_type} detected without ground truth"
            ))

    for g_idx in range(num_gt):
        if g_idx not in matched_gts:
            visual_errors.append(VisualErrorItem(
                element_type=element_type,
                classification="FALSE_NEGATIVE",
                element_id=gt_positions[g_idx]["id"],
                coordinates=gt_positions[g_idx]["pos"],
                confidence=None,
                error_note=f"Ground-truth {element_type} not detected"
            ))

    precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
    recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
    f1 = round((2.0 * precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

    return DetectionMetric(
        precision=precision,
        recall=recall,
        f1=f1,
        true_positives=tp,
        false_positives=fp,
        false_negatives=fn,
        total_ground_truth=num_gt,
        total_predicted=num_pred,
        status="COMPUTED"
    ), visual_errors
