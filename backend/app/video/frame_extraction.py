"""
Keyframe Extraction and Frame Timeline Engine for Mode B.
Selects optimal keyframes based on sharpness peaks and inter-frame visual baseline disparities.
"""

from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import cv2
import numpy as np

from backend.app.video.schemas import KeyframeItem
from backend.app.video.frame_quality import assess_frame_quality

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEO_FRAMES_DIR = DATA_DIR / "video" / "frames"
VIDEO_FRAMES_DIR.mkdir(parents=True, exist_ok=True)

def compute_color_histogram(image_bgr: np.ndarray) -> np.ndarray:
    """Computes normalized 3D color histogram for inter-frame disparity comparison."""
    hist = cv2.calcHist([image_bgr], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return hist.flatten()

def extract_intelligent_keyframes(
    video_path: str,
    video_id: str,
    target_keyframes: int = 16,
    max_frames_to_sample: int = 120,
    min_sharpness: float = 20.0
) -> Tuple[List[KeyframeItem], List[np.ndarray]]:
    """
    Decodes video, filters near-duplicates and motion-blurred frames,
    and extracts a clean set of informative keyframes saved to disk.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(cap.get(cv2.CAP_PROP_FPS)) or 30.0
    
    if total_frames <= 0:
        cap.release()
        raise ValueError("Video contains 0 frames.")

    # Sampling step to evaluate candidate frames
    sample_step = max(1, total_frames // max_frames_to_sample)
    
    candidates: List[Dict[str, Any]] = []
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_step == 0:
            q = assess_frame_quality(frame)
            hist = compute_color_histogram(frame)
            candidates.append({
                "frame_idx": frame_idx,
                "timestamp_s": round(frame_idx / fps, 3),
                "frame": frame,
                "sharpness": q["sharpness"],
                "brightness": q["brightness"],
                "hist": hist
            })

        frame_idx += 1

    cap.release()

    if not candidates:
        raise ValueError("Failed to extract any candidate frames from video.")

    # Keyframe selection strategy:
    # 1. Group candidates into temporal bins corresponding to target_keyframes
    # 2. In each bin, select the frame with highest sharpness that has sufficient visual disparity from the previous chosen keyframe
    selected_items: List[KeyframeItem] = []
    selected_matrices: List[np.ndarray] = []
    
    save_dir = VIDEO_FRAMES_DIR / video_id
    save_dir.mkdir(parents=True, exist_ok=True)

    num_bins = min(target_keyframes, len(candidates))
    bin_size = len(candidates) / float(num_bins)

    last_selected_hist: Optional[np.ndarray] = None

    for b in range(num_bins):
        start_idx = int(b * bin_size)
        end_idx = int((b + 1) * bin_size)
        window = candidates[start_idx:end_idx]
        if not window:
            continue

        # Sort window by sharpness
        window_sorted = sorted(window, key=lambda x: x["sharpness"], reverse=True)
        
        # Pick the best frame that is not an identical duplicate of previous selected frame
        chosen = None
        for cand in window_sorted:
            if last_selected_hist is None:
                chosen = cand
                break
            # Histogram correlation: 1.0 = identical, 0.0 = completely different
            similarity = float(cv2.compareHist(cand["hist"], last_selected_hist, cv2.HISTCMP_CORREL))
            if similarity < 0.985 or cand["sharpness"] >= min_sharpness:
                chosen = cand
                break
        
        if chosen is None:
            chosen = window_sorted[0]

        last_selected_hist = chosen["hist"]
        k_idx = len(selected_items)
        
        # Save keyframe image to disk
        kf_filename = f"keyframe_{k_idx:03d}_f{chosen['frame_idx']:05d}.jpg"
        kf_path = save_dir / kf_filename
        cv2.imwrite(str(kf_path), chosen["frame"], [cv2.IMWRITE_JPEG_QUALITY, 88])

        rel_url = f"/data/video/frames/{video_id}/{kf_filename}"
        
        selected_items.append(KeyframeItem(
            index=k_idx,
            frame_number=chosen["frame_idx"],
            timestamp_s=chosen["timestamp_s"],
            sharpness=chosen["sharpness"],
            image_url=rel_url,
            is_keyframe=True,
            selection_reason=f"Sharpness peak ({chosen['sharpness']:.1f}) in temporal window {b+1}/{num_bins}"
        ))
        selected_matrices.append(chosen["frame"])

    return selected_items, selected_matrices
