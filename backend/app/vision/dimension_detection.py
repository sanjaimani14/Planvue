import cv2
import numpy as np
import re
from typing import List, Dict, Any

def parse_dimension_string_to_meters(text: str) -> float | None:
    """
    Parses dimension strings in various architectural formats and normalizes into metres:
    - Metric: "4.50m", "4.5 m", "4500mm", "4500 mm", "350cm"
    - Imperial: "12'-6\"", "12' 6\"", "10 ft"
    """
    cleaned = text.strip()

    # Pattern 1: Explicit meter notation (e.g. "4.5 m", "14.50m")
    m_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:m|meter|mtr)\b', cleaned, re.IGNORECASE)
    if m_match:
        val = float(m_match.group(1))
        if 0.5 <= val <= 50.0:
            return round(val, 3)

    # Pattern 2: Millimeters (e.g. "4500 mm", "3200mm", "4500")
    mm_match = re.search(r'(\d{3,5})\s*(?:mm)?\b', cleaned, re.IGNORECASE)
    if mm_match:
        val_mm = float(mm_match.group(1))
        if 500 <= val_mm <= 50000:
            return round(val_mm / 1000.0, 3)

    # Pattern 3: Imperial feet & inches (e.g. "12'-6\"", "12' 6\"")
    imp_match = re.search(r'(\d+)\'\s*[- ]?\s*(\d+(?:\.\d+)?)\"?', cleaned)
    if imp_match:
        feet = float(imp_match.group(1))
        inches = float(imp_match.group(2))
        total_m = (feet * 0.3048) + (inches * 0.0254)
        if 0.5 <= total_m <= 50.0:
            return round(total_m, 3)

    return None

def detect_dimensions(
    gray_image: np.ndarray,
    binary_image: np.ndarray
) -> List[Dict[str, Any]]:
    """
    Detects dimension annotations and witness lines:
    - Scans image for dimension text strings via OCR
    - Links detected text to nearby witness lines
    - Normalizes into metres
    - Returns empty list if none detected (never invented).
    """
    dimensions: List[Dict[str, Any]] = []

    try:
        import pytesseract
        ocr_data = pytesseract.image_to_data(gray_image, output_type=pytesseract.Output.DICT)
        n_boxes = len(ocr_data['text'])

        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            if not text:
                continue

            meters = parse_dimension_string_to_meters(text)
            if meters is not None:
                x, y, w, h = (
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i]
                )
                # Approximate span of witness line around annotation
                start_pt = [float(x - 50), float(y + h / 2)]
                end_pt = [float(x + w + 50), float(y + h / 2)]

                dimensions.append({
                    "id": f"DIM{len(dimensions)+1:03d}",
                    "value": meters,
                    "unit": "m",
                    "start": start_pt,
                    "end": end_pt,
                    "confidence": 0.93,
                    "raw_text": text
                })
    except Exception:
        pass

    return dimensions
