import cv2
import numpy as np
import re
from typing import List, Dict, Any, Optional

STANDARD_ROOM_KEYWORDS = [
    "LIVING", "BEDROOM", "KITCHEN", "DINING", "BATHROOM", "BATH", "HALL", "STORE", "BALCONY", "OFFICE", "STUDY", "ENTRY", "FOYER"
]

def extract_room_label_at_polygon(
    gray_image: np.ndarray,
    polygon_pts: List[List[float]]
) -> Optional[str]:
    """
    Attempts to read room label inside room polygon using local pytesseract OCR.
    If OCR is not available or detects no valid room keyword, returns None.
    NEVER hallucinates room names.
    """
    try:
        import pytesseract
        # Create bounding box mask
        xs = [p[0] for p in polygon_pts]
        ys = [p[1] for p in polygon_pts]
        min_x, max_x = max(0, int(min(xs))), min(gray_image.shape[1], int(max(xs)))
        min_y, max_y = max(0, int(min(ys))), min(gray_image.shape[0], int(max(ys)))

        if max_x - min_x < 30 or max_y - min_y < 30:
            return None

        crop = gray_image[min_y:max_y, min_x:max_x]
        text = pytesseract.image_to_string(crop, config="--psm 6").upper()
        for kw in STANDARD_ROOM_KEYWORDS:
            if re.search(r'\b' + kw + r'\b', text):
                return kw.capitalize()
    except Exception:
        pass
    return None

def detect_rooms(
    binary_image: np.ndarray,
    gray_image: np.ndarray,
    walls: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Identifies enclosed room regions via wall topological closure:
    - Dilates walls slightly to ensure sealed room cycles
    - Inverts mask: enclosed rooms appear as distinct white connected components
    - Simplifies contour to polygonal vertices
    - Reads genuine label via OCR if present; otherwise label = None (NO hallucinations)
    """
    h, w = binary_image.shape[:2]

    # Draw solid continuous wall mask
    wall_canvas = np.zeros((h, w), dtype=np.uint8)
    for wall in walls:
        sx, sy = int(wall["start"][0]), int(wall["start"][1])
        ex, ey = int(wall["end"][0]), int(wall["end"][1])
        th = max(int(wall.get("thickness_px", 10)), 8)
        cv2.line(wall_canvas, (sx, sy), (ex, ey), 255, th + 4)

    # Dilate to bridge opening gaps for room cycle extraction
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    dilated_walls = cv2.dilate(wall_canvas, kernel)

    # Invert: enclosed spaces become white islands
    inverted = cv2.bitwise_not(dilated_walls)
    contours, hierarchy = cv2.findContours(inverted, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

    rooms: List[Dict[str, Any]] = []
    total_canvas_area = float(w * h)

    for idx, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        # Filter canvas perimeter background (huge) and speckles
        if 2000 < area < 0.65 * total_canvas_area:
            epsilon = 0.02 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)

            if len(approx) >= 3:
                poly = [[round(float(pt[0][0]), 1), round(float(pt[0][1]), 1)] for pt in approx]
                # Extract label strictly through OCR (or None)
                label = extract_room_label_at_polygon(gray_image, poly)

                rooms.append({
                    "id": f"R{len(rooms)+1:03d}",
                    "polygon": poly,
                    "area_px2": round(float(area), 1),
                    "label": label,  # Genuine OCR label or None
                    "confidence": 0.90,
                    "status": "OBSERVED"
                })

    return rooms
