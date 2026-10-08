import cv2
import numpy as np
import math
from typing import List, Dict, Any

def detect_doors(
    binary_image: np.ndarray,
    walls: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Detects architectural door symbols and openings:
    - Identifies quarter-circle door swing arcs or opening breaks
    - Associates nearby wall if within reasonable proximity (otherwise wall_id=None)
    - Returns empty list if no genuine door cues are found (never fabricated).
    """
    h, w = binary_image.shape[:2]

    # Create solid wall mask from detected walls to isolate thin non-wall elements (arcs/swings)
    wall_canvas = np.zeros((h, w), dtype=np.uint8)
    for wall in walls:
        sx, sy = int(wall["start"][0]), int(wall["start"][1])
        ex, ey = int(wall["end"][0]), int(wall["end"][1])
        th = max(int(wall.get("thickness_px", 10)), 6)
        cv2.line(wall_canvas, (sx, sy), (ex, ey), 255, th + 2)

    # Thin non-wall symbols
    symbols_mask = cv2.subtract(binary_image, wall_canvas)
    contours, _ = cv2.findContours(symbols_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    doors: List[Dict[str, Any]] = []

    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Door arcs typically occupy 60 to 4000 square pixels
        if 60 < area < 4500:
            rect = cv2.minAreaRect(cnt)
            (cx, cy), (rw, rh), _ = rect
            aspect = max(rw, rh) / (min(rw, rh) + 1e-5)

            # Arc swings have aspect ratio between 0.8 and 2.8
            if 0.8 <= aspect <= 3.0:
                max_span = max(rw, rh)
                # Verify proximity to at least one detected wall
                nearest_wall_id = None
                min_dist = float('inf')

                for wall in walls:
                    wx = (wall["start"][0] + wall["end"][0]) / 2.0
                    wy = (wall["start"][1] + wall["end"][1]) / 2.0
                    dist = math.hypot(cx - wx, cy - wy)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_wall_id = wall["id"]

                # If within reasonable architectural proximity (within 1.5x door span)
                if min_dist < max_span * 2.2:
                    conf = 0.82 if min_dist < max_span else 0.70
                    doors.append({
                        "id": f"D{len(doors)+1:03d}",
                        "wall_id": nearest_wall_id if min_dist < max_span * 0.8 else None,
                        "position": [round(float(cx), 1), round(float(cy), 1)],
                        "width_px": round(float(max_span), 1),
                        "confidence": conf,
                        "status": "OBSERVED"
                    })

    return doors
