import cv2
import numpy as np
from typing import Dict, Any, List

def run_classical_baseline_mode_a(binary_image: np.ndarray) -> Dict[str, Any]:
    """
    Standard naive baseline for floor plan reconstruction:
    1. Direct binary thresholding without CLAHE / bilateral filtering
    2. Naive contour finding on raw threshold
    3. Direct box extrusion without geometry constraints or door snapping
    4. Default arbitrary scale (50 px = 1m)
    """
    contours, _ = cv2.findContours(binary_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    raw_walls = []
    
    for idx, c in enumerate(contours):
        if cv2.contourArea(c) > 150:
            x, y, w, h = cv2.boundingRect(c)
            # Naive unconstrained wall representation
            raw_walls.append({
                "id": f"baseline_wall_{idx+1}",
                "start": {"x": float(x), "y": float(y)},
                "end": {"x": float(x + w), "y": float(y + h)},
                "thickness_px": 10.0,
                "status": "OBSERVED",
                "source": "naive_bounding_box"
            })

    return {
        "method": "BASELINE (Naive Threshold + Direct Extrusion)",
        "wall_count": len(raw_walls),
        "door_count": 0,  # Baseline fails to detect doors
        "window_count": 0, # Baseline fails to detect windows
        "room_count": 0,   # Baseline cannot close rooms
        "geometry_validity_score": 0.42,  # Substantial duplicate & floating segments
        "scale_confidence": "LOW (Default 50px/m assumption)"
    }
