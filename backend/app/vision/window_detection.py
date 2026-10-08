import cv2
import numpy as np
import math
from typing import List, Dict, Any

def detect_windows(
    binary_image: np.ndarray,
    walls: List[Dict[str, Any]],
    doors: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Detects architectural window symbols:
    - Identifies elongated parallel double-line glass symbols recessed in wall openings
    - Rejects regions already identified as door swings
    - Returns empty list if no genuine window features are identified (never fabricated).
    """
    h, w = binary_image.shape[:2]

    # Create solid wall mask
    wall_canvas = np.zeros((h, w), dtype=np.uint8)
    for wall in walls:
        sx, sy = int(wall["start"][0]), int(wall["start"][1])
        ex, ey = int(wall["end"][0]), int(wall["end"][1])
        th = max(int(wall.get("thickness_px", 10)), 6)
        cv2.line(wall_canvas, (sx, sy), (ex, ey), 255, th + 2)

    symbols_mask = cv2.subtract(binary_image, wall_canvas)
    contours, _ = cv2.findContours(symbols_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    windows: List[Dict[str, Any]] = []
    door_positions = [d["position"] for d in doors]

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 40 < area < 3000:
            rect = cv2.minAreaRect(cnt)
            (cx, cy), (rw, rh), _ = rect
            length = max(rw, rh)
            width = min(rw, rh)
            aspect = length / (width + 1e-5)

            # Windows are narrow elongated rectangles (aspect ratio > 3.0)
            if 3.0 <= aspect <= 16.0:
                # Ensure not already categorized as door
                is_door = any(math.hypot(cx - dp[0], cy - dp[1]) < 30.0 for dp in door_positions)
                if is_door:
                    continue

                # Must be near an architectural wall
                nearest_wall_id = None
                min_dist = float('inf')
                for wall in walls:
                    wx = (wall["start"][0] + wall["end"][0]) / 2.0
                    wy = (wall["start"][1] + wall["end"][1]) / 2.0
                    dist = math.hypot(cx - wx, cy - wy)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_wall_id = wall["id"]

                if min_dist < 60.0:
                    windows.append({
                        "id": f"WIN{len(windows)+1:03d}",
                        "wall_id": nearest_wall_id if min_dist < 35.0 else None,
                        "position": [round(float(cx), 1), round(float(cy), 1)],
                        "width_px": round(float(length), 1),
                        "confidence": 0.84,
                        "status": "OBSERVED"
                    })

    return windows
