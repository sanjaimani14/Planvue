import math
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

def compute_metric_scale(
    dimensions: List[Dict[str, Any]],
    doors: List[Dict[str, Any]],
    walls: List[Dict[str, Any]],
    image_shape: tuple
) -> Dict[str, Any]:
    """
    Determines metric scale according to the strict priority hierarchy:
    Priority 1: Explicit OCR dimension annotations with known witness line span
    Priority 2: Dimension lines + parsed meter numbers
    Priority 3: Architectural standard reference (standard single interior door = 0.90m)
    Priority 4: Architectural wall thickness heuristic (standard residential wall = 0.18m)
    Priority 5: Relative / pixel fallback (returns confidence 0.0 and None for meters_per_pixel)
    
    Never falsely claims metric accuracy when no evidence exists.
    """
    h, w = image_shape[:2]

    # Priority 1 & 2: Explicit Dimensions
    if dimensions:
        for dim in dimensions:
            m_val = dim.get("value")
            if m_val and m_val > 0.5:
                sx, sy = dim["start"]
                ex, ey = dim["end"]
                span_px = math.hypot(ex - sx, ey - sy)
                if span_px > 30.0:
                    ppm = span_px / m_val
                    if 15.0 <= ppm <= 400.0:
                        m_per_px = 1.0 / ppm
                        return {
                            "meters_per_pixel": round(m_per_px, 6),
                            "pixels_per_meter": round(ppm, 2),
                            "source": "dimension_annotation",
                            "confidence": "HIGH",
                            "confidence_score": 0.94,
                            "details": f"Calibrated from detected dimension '{dim.get('raw_text', '')}' ({m_val}m across {span_px:.1f}px)"
                        }

    # Priority 3: Architectural Reference (Standard Interior Door Leaf = 0.90m)
    if doors:
        widths_px = [d["width_px"] for d in doors if 18.0 <= d.get("width_px", 0) <= 160.0]
        if widths_px:
            median_door_px = float(np.median(widths_px))
            standard_door_m = 0.90
            ppm = median_door_px / standard_door_m
            m_per_px = 1.0 / ppm
            return {
                "meters_per_pixel": round(m_per_px, 6),
                "pixels_per_meter": round(ppm, 2),
                "source": "architectural_reference",
                "confidence": "MEDIUM",
                "confidence_score": 0.75,
                "details": f"Calibrated from architectural standard door leaf (0.90m = {median_door_px:.1f}px across {len(widths_px)} detected doors)"
            }

    # Priority 4: Wall Thickness Heuristic (Standard Wall = 0.18m)
    if walls:
        thick_pxs = [w["thickness_px"] for w in walls if 5.0 <= w.get("thickness_px", 0) <= 45.0]
        if thick_pxs:
            median_th_px = float(np.median(thick_pxs))
            standard_wall_m = 0.18
            ppm = median_th_px / standard_wall_m
            m_per_px = 1.0 / ppm
            return {
                "meters_per_pixel": round(m_per_px, 6),
                "pixels_per_meter": round(ppm, 2),
                "source": "architectural_reference",
                "confidence": "MEDIUM",
                "confidence_score": 0.65,
                "details": f"Calibrated from standard wall thickness (0.18m = {median_th_px:.1f}px)"
            }

    # Priority 5: Fallback — Transparently reports that scale could not be reliably determined
    return {
        "meters_per_pixel": None,
        "pixels_per_meter": None,
        "source": "relative",
        "confidence": "LOW",
        "confidence_score": 0.0,
        "details": "Metric scale could not be reliably determined from visual evidence. Please calibrate manually."
    }

def calibrate_manual_scale(
    pt1: List[float],
    pt2: List[float],
    known_distance: float,
    unit: str = "m"
) -> Dict[str, Any]:
    """
    Computes scale from user-selected reference points:
    Unit can be "m", "cm", "mm", or "ft".
    """
    dist_m = known_distance
    if unit == "cm":
        dist_m = known_distance / 100.0
    elif unit == "mm":
        dist_m = known_distance / 1000.0
    elif unit in ("ft", "feet"):
        dist_m = known_distance * 0.3048

    if dist_m <= 0:
        raise ValueError("Known distance must be positive.")

    span_px = math.hypot(pt2[0] - pt1[0], pt2[1] - pt1[1])
    if span_px < 5.0:
        raise ValueError("Selected reference points are too close together.")

    ppm = span_px / dist_m
    m_per_px = 1.0 / ppm

    return {
        "meters_per_pixel": round(m_per_px, 6),
        "pixels_per_meter": round(ppm, 2),
        "source": "manual_calibration",
        "confidence": "HIGH",
        "confidence_score": 0.98,
        "details": f"User calibrated: {known_distance}{unit} across {span_px:.1f}px ({ppm:.2f} px/m)"
    }

def apply_metric_scale_to_scene(
    walls: List[Dict[str, Any]],
    doors: List[Dict[str, Any]],
    windows: List[Dict[str, Any]],
    rooms: List[Dict[str, Any]],
    scale_info: Dict[str, Any],
    wall_height_m: float = 3.0
) -> None:
    """
    Converts pixel coordinates to metric space without destroying original pixel coordinates.
    """
    m_per_px = scale_info.get("meters_per_pixel")
    if not m_per_px or m_per_px <= 0:
        return

    # Convert walls
    for w in walls:
        sx, sy = w["start"]
        ex, ey = w["end"]
        w["metric_start"] = [round(sx * m_per_px, 3), round(sy * m_per_px, 3)]
        w["metric_end"] = [round(ex * m_per_px, 3), round(ey * m_per_px, 3)]
        w["length_m"] = round(math.hypot(ex - sx, ey - sy) * m_per_px, 3)
        th_m = round(w.get("thickness_px", 12.0) * m_per_px, 3)
        # Ensure clamped architectural wall bounds (0.10m - 0.45m)
        w["thickness_m"] = max(0.12, min(th_m, 0.40))
        w["height_m"] = wall_height_m

    # Convert doors
    for d in doors:
        px, py = d["position"]
        d["metric_position"] = [round(px * m_per_px, 3), round(py * m_per_px, 3)]
        w_m = round(d.get("width_px", 40.0) * m_per_px, 2)
        d["width_m"] = max(0.70, min(w_m, 1.40))
        d["height_m"] = 2.10

    # Convert windows
    for win in windows:
        px, py = win["position"]
        win["metric_position"] = [round(px * m_per_px, 3), round(py * m_per_px, 3)]
        w_m = round(win.get("width_px", 60.0) * m_per_px, 2)
        win["width_m"] = max(0.60, min(w_m, 3.00))
        win["height_m"] = 1.30
        win["sill_m"] = 0.90

    # Convert rooms
    for r in rooms:
        m_poly = [[round(p[0] * m_per_px, 3), round(p[1] * m_per_px, 3)] for p in r["polygon"]]
        r["metric_polygon"] = m_poly
        r["area_m2"] = round(r["area_px2"] * (m_per_px ** 2), 2)
