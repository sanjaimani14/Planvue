import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from typing import Tuple, Dict, Any, Optional

def load_and_preprocess_image(
    file_path: str,
    page_number: int = 1,
    max_dim: int = 2048
) -> Tuple[np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Loads blueprint image or PDF page and applies computer vision preprocessing:
    1. Robust file format loading (PNG, JPG, JPEG, PDF)
    2. Resolution normalization (scaling down huge scans to max_dim)
    3. Grayscale conversion
    4. Bilateral edge-preserving noise reduction
    5. CLAHE contrast enhancement
    6. Hough deskew angle detection and rotation
    7. Adaptive thresholding and morphological cleanup
    
    Returns:
        original_bgr: Unmodified normalized BGR image
        processed_binary: Clean binarized wall topology image
        metadata: Image attributes and preprocessing statistics
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found at: {file_path}")

    suffix = path.suffix.lower()
    total_pages = 1

    if suffix == ".pdf":
        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(str(path))
            total_pages = len(pdf)
            page_idx = max(0, min(page_number - 1, total_pages - 1))
            page = pdf[page_idx]
            pil_image = page.render(scale=2.0).to_pil()
            original_bgr = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            raise ValueError(f"PDF extraction failed: {str(e)}")
    else:
        original_bgr = cv2.imread(str(path))
        if original_bgr is None:
            pil_img = Image.open(str(path)).convert("RGB")
            original_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    if original_bgr is None or original_bgr.size == 0:
        raise ValueError(f"Unable to decode visual data from file: {file_path}")

    orig_h, orig_w = original_bgr.shape[:2]

    # 1. Resolution Normalization
    scale_factor = 1.0
    if max(orig_h, orig_w) > max_dim:
        scale_factor = max_dim / float(max(orig_h, orig_w))
        new_w = int(orig_w * scale_factor)
        new_h = int(orig_h * scale_factor)
        normalized_bgr = cv2.resize(original_bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
    else:
        normalized_bgr = original_bgr.copy()

    # 2. Grayscale Conversion
    gray = cv2.cvtColor(normalized_bgr, cv2.COLOR_BGR2GRAY)

    # 3. Bilateral Filter (Smooths flat texture while retaining sharp wall contours)
    denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

    # 4. Contrast Normalization via CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 5. Deskew Detection via Hough Lines
    edges = cv2.Canny(enhanced, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=80, maxLineGap=10)
    
    skew_angle = 0.0
    if lines is not None and len(lines) > 5:
        angles = []
        for line in lines:
            line_flat = np.array(line).reshape(-1)
            if len(line_flat) < 4:
                continue
            x1, y1, x2, y2 = line_flat[:4]
            dx = x2 - x1
            dy = y2 - y1
            if dx == 0:
                angle_deg = 90.0
            else:
                angle_deg = float(np.degrees(np.arctan2(dy, dx)))
            
            # Align near rectilinear horizontal or vertical
            if -45 < angle_deg <= 45:
                angles.append(angle_deg)
            elif 45 < angle_deg <= 135:
                angles.append(angle_deg - 90)
            elif -135 < angle_deg <= -45:
                angles.append(angle_deg + 90)

        if len(angles) > 5:
            median_angle = float(np.median(angles))
            if 0.3 < abs(median_angle) < 12.0:
                skew_angle = median_angle
                center = (normalized_bgr.shape[1] // 2, normalized_bgr.shape[0] // 2)
                rot_mat = cv2.getRotationMatrix2D(center, skew_angle, 1.0)
                normalized_bgr = cv2.warpAffine(normalized_bgr, rot_mat, (normalized_bgr.shape[1], normalized_bgr.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                enhanced = cv2.warpAffine(enhanced, rot_mat, (enhanced.shape[1], enhanced.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # 6. Adaptive Thresholding (Black ink lines on white paper)
    binary = cv2.adaptiveThreshold(
        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 6
    )

    # Morphological noise opening (removes solitary dust specks)
    clean_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    binary_cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, clean_kernel)

    metadata = {
        "original_width": orig_w,
        "original_height": orig_h,
        "processed_width": normalized_bgr.shape[1],
        "processed_height": normalized_bgr.shape[0],
        "scale_factor": scale_factor,
        "skew_angle_degrees": round(skew_angle, 2),
        "deskew_applied": abs(skew_angle) > 0.3,
        "total_pdf_pages": total_pages,
        "selected_page": page_number
    }

    return normalized_bgr, binary_cleaned, metadata
