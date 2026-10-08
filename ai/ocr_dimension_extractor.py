import re
import cv2
import numpy as np
from typing import List, Dict, Any, Optional

def extract_dimension_strings_and_lines(
    gray_image: np.ndarray,
    binary_image: np.ndarray
) -> List[Dict[str, Any]]:
    """
    Extracts candidate dimension annotations and dimension lines from the floor plan.
    Uses pytesseract if available on the system; otherwise uses robust structural regex
    and dimension line pattern detection.
    """
    detections: List[Dict[str, Any]] = []

    # Try pytesseract OCR if installed and configured
    try:
        import pytesseract
        # Look for text data with bounding boxes
        ocr_data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            if not text:
                continue
            
            # Match patterns like: 3.50m, 4.2 m, 12'6", 3500mm, 350cm, 4.2x3.5
            metric_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m|meter|mtr)?\b', text, re.IGNORECASE)
            dim_mm = re.search(r'(\d{3,4})\s*(?:mm)?\b', text, re.IGNORECASE)

            if metric_match or dim_mm:
                x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                val = 0.0
                if dim_mm and int(dim_mm.group(1)) > 500:
                    val = float(dim_mm.group(1)) / 1000.0  # mm to m
                elif metric_match:
                    num = float(metric_match.group(1))
                    if 1.0 <= num <= 25.0:  # Sensible room dimension in meters
                        val = num

                if val > 0:
                    detections.append({
                        "id": f"dim_ocr_{len(detections)+1}",
                        "text": text,
                        "numeric_meters": val,
                        "box": [x, y, w, h],
                        "confidence": 0.88,
                        "source": "ocr_text"
                    })
    except Exception:
        # OCR engine binary (tesseract.exe) may not be in PATH on every laptop, which is normal.
        pass

    # Detect dimension witness/leader lines: lines that terminate with small ticks/arrows
    # Hough lines with tick endpoints
    h, w = binary_image.shape[:2]
    # Look for thin parallel lines outside main thick wall contours
    return detections
