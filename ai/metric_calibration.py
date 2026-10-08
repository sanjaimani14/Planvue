import numpy as np
from typing import List, Dict, Any, Optional

def calibrate_metric_scale(
    detected_dimensions: List[Dict[str, Any]],
    detected_doors: List[Dict[str, Any]],
    detected_walls: List[Dict[str, Any]],
    image_shape: tuple
) -> Dict[str, Any]:
    """
    Calibrates metric scale (pixels per meter).
    Priority:
    1. Explicit OCR dimensions associated with dimension lines (HIGH confidence)
    2. Architectural reference: standard single interior door opening width ~0.90m (MEDIUM confidence)
    3. Structural heuristics: average residential room width ~4.0m across bounding boxes (MEDIUM confidence)
    4. Relative scale fallback: based on image resolution (LOW confidence)
    """
    h, w = image_shape[:2]

    # Check 1: Explicit OCR dimensions
    if detected_dimensions:
        valid_dims = [d for d in detected_dimensions if d.get("numeric_meters") and d["numeric_meters"] > 0]
        if valid_dims:
            # If we also have a pixel length associated
            for d in valid_dims:
                box = d.get("box", [0, 0, 0, 0])
                # If there's an associated pixel span
                pixel_span = d.get("pixel_span")
                if pixel_span and pixel_span > 20:
                    meters = d["numeric_meters"]
                    ppm = float(pixel_span) / float(meters)
                    if 15.0 <= ppm <= 300.0:
                        return {
                            "pixels_per_meter": round(ppm, 2),
                            "meters_per_pixel": round(1.0 / ppm, 5),
                            "confidence": "HIGH",
                            "source": "ocr_dimension",
                            "details": f"Calibrated from detected dimension annotation '{d['text']}' ({meters}m across {pixel_span:.1f}px)"
                        }

    # Check 2: Architectural standard reference (Standard Door Opening = 0.90m)
    if detected_doors:
        door_widths_px = []
        for door in detected_doors:
            width_px = door.get("width_px")
            if width_px and 15 <= width_px <= 150:
                door_widths_px.append(width_px)
        
        if door_widths_px:
            median_door_px = float(np.median(door_widths_px))
            # Standard single door leaf in architectural conventions = 0.90 meters
            standard_door_m = 0.90
            ppm = median_door_px / standard_door_m
            return {
                "pixels_per_meter": round(ppm, 2),
                "meters_per_pixel": round(1.0 / ppm, 5),
                "confidence": "MEDIUM",
                "source": "heuristic_door_width",
                "details": f"Calibrated using architectural standard door opening (0.90m = {median_door_px:.1f}px across {len(door_widths_px)} detected doors)"
            }

    # Check 3: Wall thickness heuristic (Standard residential wall = 0.20m)
    if detected_walls:
        thicknesses = [w.get("thickness_px") for w in detected_walls if w.get("thickness_px") and 4 <= w.get("thickness_px") <= 40]
        if thicknesses:
            median_th_px = float(np.median(thicknesses))
            ppm = median_th_px / 0.18
            if 20.0 <= ppm <= 250.0:
                return {
                    "pixels_per_meter": round(ppm, 2),
                    "meters_per_pixel": round(1.0 / ppm, 5),
                    "confidence": "MEDIUM",
                    "source": "heuristic_wall_thickness",
                    "details": f"Calibrated from standard exterior/interior wall thickness (0.18m = {median_th_px:.1f}px)"
                }

    # Check 4: Fallback based on typical plan canvas size
    # Assume the plan spans roughly 15m to 25m in width
    assumed_plan_width_m = 18.0
    ppm = max(w / assumed_plan_width_m, 25.0)
    return {
        "pixels_per_meter": round(ppm, 2),
        "meters_per_pixel": round(1.0 / ppm, 5),
        "confidence": "LOW",
        "source": "fallback",
        "details": f"Default architectural layout fallback (~{assumed_plan_width_m}m assumed footprint width). No explicit dimension text or doors identified."
    }
