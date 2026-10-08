"""
Video Quality Assessment Engine for Mode B.
Analyzes blur, brightness, exposure, frame sharpness, motion disparity, and duplicates.
"""

from typing import List, Tuple, Dict, Any
import cv2
import numpy as np

from backend.app.video.schemas import QualityReport

BLUR_THRESHOLD = 45.0  # Laplacian variance below this indicates motion blur
UNDEREXPOSURE_THRESHOLD = 40.0
OVEREXPOSURE_THRESHOLD = 215.0

def assess_frame_quality(frame: np.ndarray) -> Dict[str, Any]:
    """Computes sharpness and luminance metrics for an individual frame."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    
    is_sharp = sharpness >= BLUR_THRESHOLD
    exposure = "OPTIMAL"
    if brightness < UNDEREXPOSURE_THRESHOLD:
        exposure = "UNDEREXPOSED"
    elif brightness > OVEREXPOSURE_THRESHOLD:
        exposure = "OVEREXPOSED"
        
    return {
        "sharpness": round(sharpness, 2),
        "brightness": round(brightness, 2),
        "is_sharp": is_sharp,
        "exposure": exposure
    }

def analyze_video_stream_quality(
    video_path: str,
    sample_rate: int = 5
) -> QualityReport:
    """
    Samples frames across the video and generates an explainable QualityReport.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return QualityReport(
            sharpness_score=0.0,
            sharp_frames_count=0,
            blurred_frames_count=0,
            brightness_mean=0.0,
            exposure_status="UNDEREXPOSED",
            motion_level="FAST_ERRATIC",
            quality_grade="POOR",
            warnings=["Could not open video stream for quality assessment."]
        )

    sharpness_scores: List[float] = []
    brightness_scores: List[float] = []
    sharp_count = 0
    blur_count = 0
    frame_idx = 0
    prev_gray: np.ndarray = None
    inter_frame_diffs: List[float] = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_rate == 0:
            q = assess_frame_quality(frame)
            sharpness_scores.append(q["sharpness"])
            brightness_scores.append(q["brightness"])
            if q["is_sharp"]:
                sharp_count += 1
            else:
                blur_count += 1

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if prev_gray is not None:
                diff = float(np.mean(np.abs(gray.astype(np.float32) - prev_gray.astype(np.float32))))
                inter_frame_diffs.append(diff)
            prev_gray = gray

        frame_idx += 1

    cap.release()

    total_sampled = max(1, len(sharpness_scores))
    mean_sharpness = float(np.mean(sharpness_scores)) if sharpness_scores else 0.0
    mean_brightness = float(np.mean(brightness_scores)) if brightness_scores else 128.0
    mean_motion_diff = float(np.mean(inter_frame_diffs)) if inter_frame_diffs else 0.0

    # Determine motion level
    if mean_motion_diff < 5.0:
        motion_level = "SMOOTH"
    elif mean_motion_diff < 25.0:
        motion_level = "MODERATE"
    else:
        motion_level = "FAST_ERRATIC"

    # Exposure status
    if mean_brightness < UNDEREXPOSURE_THRESHOLD:
        exposure_status = "UNDEREXPOSED"
    elif mean_brightness > OVEREXPOSURE_THRESHOLD:
        exposure_status = "OVEREXPOSED"
    else:
        exposure_status = "OPTIMAL"

    # Quality Grade and Warnings
    warnings: List[str] = []
    blur_ratio = blur_count / total_sampled

    if blur_ratio > 0.50:
        warnings.append(f"Significant motion blur detected in {int(blur_ratio*100)}% of sampled frames.")
    if exposure_status != "OPTIMAL":
        warnings.append(f"Non-optimal lighting conditions detected: {exposure_status} (mean luminance: {mean_brightness:.1f}).")
    if motion_level == "FAST_ERRATIC":
        warnings.append("Rapid or erratic camera movement detected; may degrade feature matching stability.")

    if blur_ratio > 0.65 or mean_sharpness < 15.0:
        quality_grade = "POOR"
    elif warnings:
        quality_grade = "WARNING"
    else:
        quality_grade = "GOOD"

    return QualityReport(
        sharpness_score=round(mean_sharpness, 2),
        sharp_frames_count=sharp_count,
        blurred_frames_count=blur_count,
        brightness_mean=round(mean_brightness, 2),
        exposure_status=exposure_status,
        motion_level=motion_level,
        quality_grade=quality_grade,
        warnings=warnings
    )
